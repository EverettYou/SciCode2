from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.llm import LLMSettings, StructuredLLM


class FakeResponses:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            output_text=json.dumps({"value": "ok"}),
            usage=SimpleNamespace(input_tokens=12, output_tokens=4, total_tokens=16),
            _request_id="req_test",
        )


class FakeClient:
    def __init__(self, responses: FakeResponses) -> None:
        self.responses = responses


class StructuredLLMTests(unittest.TestCase):
    def test_structured_response_is_cached_and_usage_is_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            responses = FakeResponses()
            factory_calls: list[dict] = []

            def factory(**kwargs):
                factory_calls.append(kwargs)
                return FakeClient(responses)

            runtime = StructuredLLM(
                LLMSettings(api_key="test-key", model="test-model"),
                cache_path=root / "cache.json",
                usage_path=root / "usage.jsonl",
                client_factory=factory,
            )
            arguments = {
                "task": "test-task",
                "prompt_version": "v1",
                "instructions": "Return a value.",
                "input_text": "evidence",
                "schema": {
                    "type": "object",
                    "properties": {"value": {"type": "string"}},
                    "required": ["value"],
                    "additionalProperties": False,
                },
                "schema_name": "test_result",
            }
            first = runtime.run(**arguments)
            second = runtime.run(**arguments)

            self.assertEqual(first.data, {"value": "ok"})
            self.assertFalse(first.cached)
            self.assertTrue(second.cached)
            self.assertEqual(len(responses.calls), 1)
            self.assertEqual(len(factory_calls), 1)
            self.assertFalse(responses.calls[0]["store"])
            self.assertEqual(responses.calls[0]["text"]["format"]["type"], "json_schema")
            usage = json.loads((root / "usage.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(usage["total_tokens"], 16)
            self.assertNotIn("api_key", usage)


if __name__ == "__main__":
    unittest.main()
