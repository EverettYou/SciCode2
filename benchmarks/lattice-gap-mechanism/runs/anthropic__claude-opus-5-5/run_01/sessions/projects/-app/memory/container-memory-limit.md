---
name: container-memory-limit
description: "Sandbox has a 32 GiB cgroup memory cap although `free` reports ~1.4 TB; big jobs get silently OOM-killed"
metadata:
  node_type: memory
  type: reference
  originSessionId: 842364dd-85bc-4fa9-8fea-264336a7a5e5
  modified: 2026-10-29T21:57:14.447Z
---

`free -g` shows the host (~1.4 TB), but `/sys/fs/cgroup/memory.max` = 34359738368 (32 GiB). Exceeding it SIGKILLs
the process with no Python traceback (exit 137); check `/sys/fs/cgroup/memory.events` (oom_kill counter).

Seen 2026-10-29: block-Lanczos with 8 vectors of dim 1.47e8 (~9.4 GB per block) died repeatedly; plain Lanczos on
the same 1.66e8-dim Hilbert space (a few vectors, ~1.3 GB each) was fine. 8 cores available.

**How to apply:** budget memory against 32 GiB (minus concurrent jobs) before launching large ED/linear-algebra
runs; see also [[pip-install-dns-workaround]].
