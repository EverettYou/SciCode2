#!/bin/sh
set -eu

project_root=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
cd "$project_root"

dashboard_port="${SCICODE_DASHBOARD_PORT:-8765}"
runtime_dir="$project_root/.tmp"
pid_file="$runtime_dir/dashboard-${dashboard_port}.pid"
state_file="$runtime_dir/dashboard-${dashboard_port}.state"
log_file="$runtime_dir/dashboard-${dashboard_port}.log"
command="${1:-start}"
takeover_option="${2:-}"
case "$takeover_option" in
    ''|--takeover) ;;
    *)
        printf 'Unknown option: %s\n' "$takeover_option" >&2
        exit 2
        ;;
esac
python_command="python3"
if [ -x "$project_root/.venv/bin/python" ]; then
    if "$project_root/.venv/bin/python" -c 'import fastapi, numpy, uvicorn, yaml' >/dev/null 2>&1; then
        python_command="$project_root/.venv/bin/python"
    fi
fi

mkdir -p "$runtime_dir"

saved_pid() {
    if [ -f "$pid_file" ]; then
        sed -n '1p' "$pid_file"
    fi
}

listener_pid_from_proc() {
    hex=$(printf '%04X' "$dashboard_port")
    inodes=$(
        for table in /proc/net/tcp /proc/net/tcp6; do
            [ -r "$table" ] || continue
            awk -v hex="$hex" '
                NR == 1 { next }
                $4 == "0A" {
                    n = split($2, parts, ":")
                    if (n >= 2 && parts[n] == hex) print $10
                }
            ' "$table"
        done
    )
    for inode in $inodes; do
        [ -n "$inode" ] || continue
        for fd in /proc/[0-9]*/fd/*; do
            case "$(readlink "$fd" 2>/dev/null || true)" in
                "socket:[$inode]")
                    printf '%s\n' "$fd" | sed -n 's|^/proc/\([0-9][0-9]*\)/fd/.*|\1|p'
                    return 0
                    ;;
            esac
        done
    done
}

listener_pid() {
    if command -v lsof >/dev/null 2>&1; then
        pid=$(lsof -tiTCP:"$dashboard_port" -sTCP:LISTEN 2>/dev/null | sed -n '1p')
        if [ -n "$pid" ]; then
            printf '%s\n' "$pid"
            return 0
        fi
    fi
    listener_pid_from_proc || true
}

process_command() {
    ps -p "$1" -o command= 2>/dev/null | sed -n '1p'
}

process_cwd() {
    cwd=$(readlink "/proc/$1/cwd" 2>/dev/null || true)
    if [ -n "$cwd" ]; then
        printf '%s\n' "$cwd"
        return 0
    fi
    lsof -a -p "$1" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p' | sed -n '1p'
}

is_this_dashboard_process() {
    candidate_pid=$1
    candidate_command=$(process_command "$candidate_pid")
    [ "$(process_cwd "$candidate_pid")" = "$project_root" ] && \
        printf '%s' "$candidate_command" | grep -F -- '-m dashboard.server' >/dev/null
}

dashboard_is_tracked() {
    pid=$(saved_pid)
    listener=$(listener_pid)
    [ -n "$pid" ] && [ "$pid" = "$listener" ] && kill -0 "$pid" 2>/dev/null
}

stop_process() {
    pid_to_stop=$1
    kill "$pid_to_stop"
    attempts=0
    while kill -0 "$pid_to_stop" 2>/dev/null && [ "$attempts" -lt 25 ]; do
        attempts=$((attempts + 1))
        sleep 0.2
    done
    if kill -0 "$pid_to_stop" 2>/dev/null; then
        print_dashboard_card "FAILED" "process did not stop" "PID $pid_to_stop" >&2
        return 1
    fi
}

dashboard_fingerprint() {
    (
        printf '%s\n' dashboard/server.py
        find dashboard/backend -type f -name '*.py' -print | sort
    ) | while IFS= read -r path; do
        shasum "$path"
    done | shasum | awk '{print $1}'
}

saved_fingerprint() {
    if [ -f "$state_file" ]; then
        sed -n 's/^fingerprint=//p' "$state_file" | sed -n '1p'
    fi
}

saved_catalog_summary() {
    if [ -f "$state_file" ]; then
        sed -n 's/^catalog=//p' "$state_file" | sed -n '1p'
    fi
}

write_state() {
    printf 'pid=%s\nfingerprint=%s\ncatalog=%s\n' \
        "$1" "$(dashboard_fingerprint)" "${2:-}" >"$state_file"
}

dashboard_is_current() {
    dashboard_is_tracked && [ -n "$(saved_fingerprint)" ] && \
        [ "$(saved_fingerprint)" = "$(dashboard_fingerprint)" ]
}

remove_dashboard_state() {
    rm -f "$pid_file" "$state_file"
}

print_dashboard_card() {
    status_label=$1
    code_label=$2
    pid_label=${3:-—}
    catalog_label=${4:-}
    printf '\n┌─ SciCode2 Dashboard ─────────────────────────\n'
    printf '│ Status    %s\n' "$status_label"
    printf '│ Address   http://localhost:%s\n' "$dashboard_port"
    printf '│ Process   %s\n' "$pid_label"
    printf '│ Code      %s\n' "$code_label"
    if [ -n "$catalog_label" ]; then
        printf '│ Catalog   %s\n' "$catalog_label"
    fi
    printf '│\n'
    printf '│ Commands  start · status · restart · stop · logs\n'
    printf '└─────────────────────────────────────────────\n'
}

print_usage_card() {
    printf '\nSciCode2 Dashboard launcher\n\n'
    printf '  ./run_dashboard.sh           Start, or refresh a previous SciCode2 instance\n'
    printf '  ./run_dashboard.sh status    Show service health\n'
    printf '  ./run_dashboard.sh restart   Stop and start the service\n'
    printf '  ./run_dashboard.sh stop      Stop the tracked service\n'
    printf '  ./run_dashboard.sh logs      Show the last 100 log lines\n\n'
    printf '  Add --takeover to start or stop an unrelated process on the selected port.\n'
    printf 'Optional: SCICODE_DASHBOARD_PORT=<port> before any command\n'
}

start_dashboard() {
    if dashboard_is_tracked; then
        if dashboard_is_current; then
            print_dashboard_card "RUNNING" "current" "PID $(saved_pid)" "$(saved_catalog_summary)"
            return 0
        fi
        stop_dashboard quiet
    fi

    listener=$(listener_pid)
    if [ -n "$listener" ]; then
        if is_this_dashboard_process "$listener"; then
            printf 'Refreshing previous SciCode2 Dashboard (PID %s)…\n' "$listener"
            stop_process "$listener"
            remove_dashboard_state
        elif [ "$takeover_option" = --takeover ]; then
            printf 'Taking over port %s from PID %s…\n' "$dashboard_port" "$listener"
            stop_process "$listener"
            remove_dashboard_state
        else
            print_dashboard_card "UNAVAILABLE" "port $dashboard_port is owned by another process" "PID $listener" >&2
            printf 'Owner: %s\n' "$(process_command "$listener")" >&2
            printf 'Run ./run_dashboard.sh start --takeover to replace it, or choose another port.\n' >&2
            return 1
        fi
    fi

    remove_dashboard_state
    if ! build_output=$("$python_command" skills/assess-paper/scripts/build_dashboard_data.py 2>&1); then
        print_dashboard_card "FAILED" "catalog build failed" "—" >&2
        printf '\nBuild details:\n%s\n' "$build_output" >&2
        return 1
    fi
    catalog_summary=$(printf '%s\n' "$build_output" | sed -n 's/^Wrote \(.*\) to .*$/\1/p' | sed -n '1p')
    nohup env SCICODE_DASHBOARD_PORT="$dashboard_port" "$python_command" -m dashboard.server \
        >>"$log_file" 2>&1 </dev/null &
    pid=$!
    printf '%s\n' "$pid" >"$pid_file"
    write_state "$pid" "$catalog_summary"

    attempts=0
    while [ "$attempts" -lt 25 ]; do
        if dashboard_is_tracked; then
            print_dashboard_card "RUNNING" "current" "PID $pid" "$catalog_summary"
            return 0
        fi
        if ! kill -0 "$pid" 2>/dev/null; then
            print_dashboard_card "FAILED" "server exited during startup" "PID $pid" "$catalog_summary" >&2
            printf '\nLast 30 log lines:\n' >&2
            tail -n 30 "$log_file" >&2 || true
            remove_dashboard_state
            return 1
        fi
        attempts=$((attempts + 1))
        sleep 0.2
    done

    print_dashboard_card "FAILED" "server did not bind to port $dashboard_port" "PID $pid" "$catalog_summary" >&2
    printf '\nRun ./run_dashboard.sh logs for details.\n' >&2
    return 1
}

stop_dashboard() {
    quiet=${1:-}
    if ! dashboard_is_tracked; then
        listener=$(listener_pid)
        if [ -n "$listener" ]; then
            if is_this_dashboard_process "$listener" || [ "$takeover_option" = --takeover ]; then
                stop_process "$listener"
                remove_dashboard_state
                if [ "$quiet" != quiet ]; then
                    print_dashboard_card "STOPPED" "previous dashboard instance stopped" "—"
                fi
                return 0
            fi
            print_dashboard_card "UNAVAILABLE" "port $dashboard_port is owned by another process" "PID $listener" >&2
            printf 'Owner: %s\n' "$(process_command "$listener")" >&2
            printf 'Run ./run_dashboard.sh stop --takeover to stop it explicitly.\n' >&2
            return 1
        fi
        remove_dashboard_state
        if [ "$quiet" != quiet ]; then
            print_dashboard_card "STOPPED" "not running" "—"
        fi
        return 0
    fi

    pid=$(saved_pid)
    kill "$pid"
    attempts=0
    while kill -0 "$pid" 2>/dev/null && [ "$attempts" -lt 25 ]; do
        attempts=$((attempts + 1))
        sleep 0.2
    done
    remove_dashboard_state
    if [ "$quiet" != quiet ]; then
        print_dashboard_card "STOPPED" "not running" "—"
    fi
}

status_dashboard() {
    if dashboard_is_tracked; then
        if dashboard_is_current; then
            print_dashboard_card "RUNNING" "current" "PID $(saved_pid)" "$(saved_catalog_summary)"
            return 0
        else
            print_dashboard_card "STALE" "changed — run ./run_dashboard.sh start" "PID $(saved_pid)" "$(saved_catalog_summary)"
            return 1
        fi
    fi

    listener=$(listener_pid)
    if [ -n "$listener" ]; then
        if is_this_dashboard_process "$listener"; then
            print_dashboard_card "STALE" "previous dashboard instance — run start to refresh" "PID $listener"
        else
            print_dashboard_card "UNAVAILABLE" "port $dashboard_port is owned by another process" "PID $listener"
            printf 'Owner: %s\n' "$(process_command "$listener")"
        fi
        return 1
    fi
    print_dashboard_card "STOPPED" "not running" "—"
    return 1
}

case "$command" in
    start)
        start_dashboard
        ;;
    stop)
        stop_dashboard
        ;;
    restart)
        stop_dashboard quiet
        start_dashboard
        ;;
    status)
        status_dashboard
        ;;
    logs)
        if [ -f "$log_file" ]; then
            log_pid=$(saved_pid)
            if [ -z "$log_pid" ]; then
                log_pid='—'
            else
                log_pid="PID $log_pid"
            fi
            print_dashboard_card "LOGS" "last 100 lines" "$log_pid" "$(saved_catalog_summary)"
            tail -n 100 "$log_file"
        else
            print_dashboard_card "NO LOG" "the dashboard has not been started on this port" "—"
        fi
        ;;
    *)
        print_usage_card >&2
        exit 2
        ;;
esac
