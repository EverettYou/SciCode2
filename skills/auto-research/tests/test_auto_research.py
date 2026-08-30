from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"


class AutoResearchScriptsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.benchmark = Path(self.temporary.name) / "fixture-benchmark"
        for folder in ("problem", "wiki", "labs", "src", "note"):
            (self.benchmark / folder).mkdir(parents=True, exist_ok=True)
        (self.benchmark / "wiki" / "ideas").mkdir(parents=True, exist_ok=True)
        (self.benchmark / "metadata.yml").write_text(
            "benchmark_id: fixture-benchmark\nexpert_review: approved\n", encoding="utf-8"
        )
        (self.benchmark / "wiki" / "ideas" / "research-frontier.md").write_text(
            "# Research frontier\n", encoding="utf-8"
        )
        (self.benchmark / "wiki" / "index.md").write_text("# Index\n", encoding="utf-8")
        (self.benchmark / "wiki" / "thesis.md").write_text("# Thesis\n", encoding="utf-8")
        self.run_script("loop_state.py", "init", str(self.benchmark))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_script(self, script: str, *arguments: str, check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *arguments],
            check=check,
            capture_output=True,
            text=True,
        )

    def state(self) -> dict:
        return yaml.safe_load(
            (self.benchmark / ".auto-research" / "state.yml").read_text(encoding="utf-8")
        )

    def evidence_digest(self) -> str:
        output = self.run_script("evidence_digest.py", str(self.benchmark))
        return json.loads(output.stdout)["digest"]

    def test_initialization_and_idempotency(self) -> None:
        initial = self.state()
        self.assertEqual(initial["status"], "paused")
        self.assertEqual(initial["automations"]["research"]["interval_minutes"], 10)

        self.run_script("loop_state.py", "init", str(self.benchmark))
        events = (self.benchmark / ".auto-research" / "events.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
        self.assertEqual(len(events), 1)

    def test_lease_rejects_overlap_and_requires_token(self) -> None:
        acquired = self.run_script(
            "loop_state.py", "acquire", str(self.benchmark),
            "--worker", "research", "--ttl-minutes", "9",
        )
        token = json.loads(acquired.stdout)["token"]
        overlap = self.run_script(
            "loop_state.py", "acquire", str(self.benchmark),
            "--worker", "research", "--ttl-minutes", "9", check=False,
        )
        self.assertNotEqual(overlap.returncode, 0)
        self.run_script(
            "loop_state.py", "release", str(self.benchmark),
            "--worker", "research", "--token", token,
        )

    def test_partial_schedule_reconciliation_preserves_other_id(self) -> None:
        self.run_script(
            "loop_state.py", "set-schedules", str(self.benchmark),
            "--research-id", "research-123",
        )
        state = self.state()
        self.assertEqual(state["automations"]["research"]["id"], "research-123")
        self.assertIsNone(state["automations"]["supervisor_synthesis"]["id"])
        self.run_script(
            "loop_state.py", "set-schedules", str(self.benchmark),
            "--synthesis-id", "synthesis-456",
        )
        state = self.state()
        self.assertEqual(state["automations"]["research"]["id"], "research-123")
        self.assertEqual(
            state["automations"]["supervisor_synthesis"]["id"], "synthesis-456"
        )

    def test_digest_ignores_prospective_lab_and_includes_completed_lab(self) -> None:
        lab = self.benchmark / "labs" / "lab-001-fixture"
        lab.mkdir()
        report = lab / "REPORT.md"
        report.write_text("# Lab\n\n- Status: designed\n", encoding="utf-8")
        before = self.evidence_digest()
        report.write_text("# Lab\n\n- Status: designed\n\nMore prose.\n", encoding="utf-8")
        self.assertEqual(before, self.evidence_digest())

        report.write_text("# Lab\n\n- Status: completed\n\nControlled negative result.\n", encoding="utf-8")
        self.assertNotEqual(before, self.evidence_digest())

    def test_digest_ignores_idea_graph_changes(self) -> None:
        before = self.evidence_digest()
        (self.benchmark / "wiki" / "ideas" / "research-frontier.md").write_text(
            "# Changed frontier\n", encoding="utf-8"
        )
        self.assertEqual(before, self.evidence_digest())

    def test_lab_audit_rejects_prospective_report_and_accepts_complete_sections(self) -> None:
        lab = self.benchmark / "labs" / "lab-001-fixture"
        lab.mkdir()
        report = lab / "REPORT.md"
        report.write_text(
            "# Lab\n\n- Status: completed\n\n## Findings\n\nNo experiment has been run.\n",
            encoding="utf-8",
        )
        rejected = self.run_script("audit_lab_evidence.py", str(report), check=False)
        self.assertNotEqual(rejected.returncode, 0)

        report.write_text(
            """# Lab

- Status: completed

## Methods and execution

Ran the recorded command with configuration, seed, environment, and revision.

## Findings

The controlled result was negative.

## Analysis and limitations

Finite-size coverage remains limited.

## Search decision

Prune the tested branch.

## Wiki ingest handoff

Ingest the controlled negative result and limitation.
""",
            encoding="utf-8",
        )
        accepted = self.run_script("audit_lab_evidence.py", str(report))
        self.assertTrue(json.loads(accepted.stdout)["passes_deterministic_checks"])

    def test_three_quiet_cycles_trigger_stall(self) -> None:
        self.run_script("loop_state.py", "transition", str(self.benchmark), "active")
        digest = self.evidence_digest()
        self.run_script(
            "loop_state.py", "record-run", str(self.benchmark),
            "--worker", "supervisor-synthesis", "--outcome", "evidence",
            "--evidence-digest", digest,
        )
        for _ in range(3):
            self.run_script(
                "loop_state.py", "record-run", str(self.benchmark),
                "--worker", "supervisor-synthesis", "--outcome", "no-progress",
            )
        result = json.loads(
            self.run_script("detect_stall.py", str(self.benchmark)).stdout
        )
        self.assertEqual(result["classification"], "stalled")
        self.assertTrue(result["diagnostic_required"])

    def test_steering_decision_updates_ledger_and_pending_thread(self) -> None:
        self.run_script(
            "record_steering_decision.py", str(self.benchmark),
            "--diagnosis", "scope-decision", "--action", "consult-human",
            "--summary", "Two consequential directions remain.",
            "--recommendation", "Ask the user to select the primary scope.",
            "--requires-human", "--thread-id", "T-0007",
        )
        decisions = yaml.safe_load(
            (self.benchmark / ".auto-research" / "steering-decisions.yml").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(decisions[0]["decision_id"], "steer-0001")
        self.assertEqual(self.state()["progress"]["pending_human_thread_id"], "T-0007")


if __name__ == "__main__":
    unittest.main()
