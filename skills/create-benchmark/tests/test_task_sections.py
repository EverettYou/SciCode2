from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_benchmark.py"
SPEC = importlib.util.spec_from_file_location("validate_benchmark", SCRIPT)
VALIDATOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VALIDATOR)


def write_task(root: Path, unresolved: str, scope: str, question: str) -> None:
    problem = root / "problem"
    problem.mkdir()
    (problem / "TASK.md").write_text(
        "\n".join(
            (
                "# Test benchmark",
                "",
                "## Why this is unresolved",
                "",
                unresolved,
                "",
                "## Research question",
                "",
                question,
                "",
                "## Scope and approach",
                "",
                scope,
                "",
            )
        ),
        encoding="utf-8",
    )


class TaskSectionValidationTests(unittest.TestCase):
    def test_task_section_word_limit_accepts_250_words(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            question = "Can the bounded proposal remain concise?"
            write_task(root, "word " * 250, "scope " * 250, question)
            errors: list[str] = []
            VALIDATOR.validate_task(errors, root, {"research_question": question})
            self.assertEqual(errors, [])

    def test_task_section_word_limit_rejects_251_words(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            question = "Can the bounded proposal remain concise?"
            write_task(root, "word " * 251, "scope", question)
            errors: list[str] = []
            VALIDATOR.validate_task(errors, root, {"research_question": question})
            self.assertTrue(
                any(
                    "Why this is unresolved' exceeds 250 words (251)" in item
                    for item in errors
                )
            )

    def test_research_question_must_match_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_task(root, "unknown", "bounded", "Question in task?")
            errors: list[str] = []
            VALIDATOR.validate_task(
                errors, root, {"research_question": "Different metadata question?"}
            )
            self.assertTrue(
                any("Research question must match metadata.yml" in item for item in errors)
            )


if __name__ == "__main__":
    unittest.main()
