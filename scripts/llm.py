"""Small, reusable OpenAI Responses runtime with durable local caching."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from dotenv import load_dotenv
from openai import OpenAI


class LLMConfigurationError(RuntimeError):
    """Raised when an explicitly requested LLM operation is not configured."""


class LLMResponseError(RuntimeError):
    """Raised when a model response cannot be decoded as the requested structure."""


@dataclass(frozen=True)
class LLMSettings:
    api_key: str
    model: str
    timeout_seconds: float = 30.0
    max_retries: int = 2

    @classmethod
    def from_project(
        cls,
        project_root: Path,
        *,
        model_env: str,
        default_model: str = "gpt-5.6-luna",
    ) -> "LLMSettings":
        load_dotenv(project_root / ".env", override=False)
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise LLMConfigurationError(
                "OPENAI_API_KEY is required for this operation; add it to the project .env file"
            )
        model = (
            os.getenv(model_env, "").strip()
            or os.getenv("OPENAI_MODEL", "").strip()
            or default_model
        )
        try:
            timeout = float(os.getenv("OPENAI_API_TIMEOUT_SECONDS", "30"))
            retries = int(os.getenv("OPENAI_API_MAX_RETRIES", "2"))
        except ValueError as error:
            raise LLMConfigurationError(
                "OPENAI_API_TIMEOUT_SECONDS and OPENAI_API_MAX_RETRIES must be numeric"
            ) from error
        return cls(api_key=api_key, model=model, timeout_seconds=timeout, max_retries=retries)


@dataclass(frozen=True)
class StructuredResult:
    data: dict[str, Any]
    cached: bool
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    request_id: str | None = None


@dataclass(frozen=True)
class EmbeddingResult:
    vectors: list[list[float]]
    model: str
    input_tokens: int = 0
    total_tokens: int = 0
    request_id: str | None = None


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False, suffix=".tmp"
    ) as handle:
        handle.write(rendered)
        temporary = Path(handle.name)
    temporary.replace(path)


def _load_cache(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"version": 1, "entries": {}}
    if not isinstance(payload, dict) or not isinstance(payload.get("entries"), dict):
        return {"version": 1, "entries": {}}
    return payload


def _usage_value(usage: Any, name: str) -> int:
    value = getattr(usage, name, 0) if usage is not None else 0
    return value if isinstance(value, int) else 0


class StructuredLLM:
    """Run stateless structured prompts and cache successful parsed responses."""

    def __init__(
        self,
        settings: LLMSettings,
        *,
        cache_path: Path,
        usage_path: Path | None = None,
        client_factory: Callable[..., Any] = OpenAI,
    ) -> None:
        self.settings = settings
        self.cache_path = cache_path
        self.usage_path = usage_path
        self.client_factory = client_factory

    def _key(
        self,
        *,
        task: str,
        prompt_version: str,
        instructions: str,
        input_text: str,
        schema: dict[str, Any],
    ) -> str:
        payload = json.dumps(
            {
                "task": task,
                "prompt_version": prompt_version,
                "model": self.settings.model,
                "instructions": instructions,
                "input": input_text,
                "schema": schema,
            },
            ensure_ascii=False,
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def _record_usage(self, record: dict[str, Any]) -> None:
        if self.usage_path is None:
            return
        self.usage_path.parent.mkdir(parents=True, exist_ok=True)
        with self.usage_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def run(
        self,
        *,
        task: str,
        prompt_version: str,
        instructions: str,
        input_text: str,
        schema: dict[str, Any],
        schema_name: str,
        max_output_tokens: int = 2000,
        refresh: bool = False,
    ) -> StructuredResult:
        key = self._key(
            task=task,
            prompt_version=prompt_version,
            instructions=instructions,
            input_text=input_text,
            schema=schema,
        )
        cache = _load_cache(self.cache_path)
        entry = cache["entries"].get(key)
        if not refresh and isinstance(entry, dict) and isinstance(entry.get("data"), dict):
            return StructuredResult(data=entry["data"], cached=True, model=self.settings.model)

        client = self.client_factory(
            api_key=self.settings.api_key,
            timeout=self.settings.timeout_seconds,
            max_retries=self.settings.max_retries,
        )
        response = client.responses.create(
            model=self.settings.model,
            instructions=instructions,
            input=input_text,
            text={
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "strict": True,
                    "schema": schema,
                }
            },
            max_output_tokens=max_output_tokens,
            store=False,
        )
        try:
            data = json.loads(response.output_text)
        except (AttributeError, TypeError, json.JSONDecodeError) as error:
            raise LLMResponseError(f"{task} returned invalid structured output") from error
        if not isinstance(data, dict):
            raise LLMResponseError(f"{task} returned a non-object structured response")

        usage = getattr(response, "usage", None)
        input_tokens = _usage_value(usage, "input_tokens")
        output_tokens = _usage_value(usage, "output_tokens")
        total_tokens = _usage_value(usage, "total_tokens") or input_tokens + output_tokens
        request_id = getattr(response, "_request_id", None)
        cache["entries"][key] = {
            "data": data,
            "model": self.settings.model,
            "prompt_version": prompt_version,
            "cached_at": datetime.now(timezone.utc).isoformat(),
        }
        _atomic_json(self.cache_path, cache)
        self._record_usage(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "task": task,
                "model": self.settings.model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "request_id": request_id,
            }
        )
        return StructuredResult(
            data=data,
            cached=False,
            model=self.settings.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            request_id=request_id,
        )


class EmbeddingLLM:
    """Create float embeddings and record aggregate credential-free usage."""

    def __init__(
        self,
        settings: LLMSettings,
        *,
        dimensions: int | None = None,
        usage_path: Path | None = None,
        client_factory: Callable[..., Any] = OpenAI,
    ) -> None:
        self.settings = settings
        self.dimensions = dimensions
        self.usage_path = usage_path
        self.client_factory = client_factory

    def embed(self, texts: list[str], *, task: str) -> EmbeddingResult:
        if not texts:
            return EmbeddingResult(vectors=[], model=self.settings.model)
        client = self.client_factory(
            api_key=self.settings.api_key,
            timeout=self.settings.timeout_seconds,
            max_retries=self.settings.max_retries,
        )
        arguments: dict[str, Any] = {
            "input": texts,
            "model": self.settings.model,
            "encoding_format": "float",
        }
        if self.dimensions is not None:
            arguments["dimensions"] = self.dimensions
        response = client.embeddings.create(**arguments)
        ordered = sorted(response.data, key=lambda item: item.index)
        vectors = [list(item.embedding) for item in ordered]
        if len(vectors) != len(texts):
            raise LLMResponseError(
                f"{task} returned {len(vectors)} embeddings for {len(texts)} inputs"
            )
        usage = getattr(response, "usage", None)
        input_tokens = _usage_value(usage, "prompt_tokens") or _usage_value(usage, "input_tokens")
        total_tokens = _usage_value(usage, "total_tokens") or input_tokens
        request_id = getattr(response, "_request_id", None)
        if self.usage_path is not None:
            self.usage_path.parent.mkdir(parents=True, exist_ok=True)
            with self.usage_path.open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        {
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "task": task,
                            "model": self.settings.model,
                            "input_count": len(texts),
                            "input_tokens": input_tokens,
                            "output_tokens": 0,
                            "total_tokens": total_tokens,
                            "request_id": request_id,
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    )
                    + "\n"
                )
        return EmbeddingResult(
            vectors=vectors,
            model=self.settings.model,
            input_tokens=input_tokens,
            total_tokens=total_tokens,
            request_id=request_id,
        )
