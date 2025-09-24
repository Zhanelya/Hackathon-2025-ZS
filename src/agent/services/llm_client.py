from __future__ import annotations

import os
from urllib.parse import urlparse
from typing import Protocol, Literal, Optional

from src.agent.models.packing_models import GeneratePackingListRequest, PackingListResponse


class LLMClient(Protocol):
    def generate_explanation(
        self,
        req: GeneratePackingListRequest,
        resp: PackingListResponse,
        *,
        style: Literal["short", "detailed"] = "short",
    ) -> str: ...


class MockLLMClient:
    """Deterministic, offline LLM stub for Phase 2 Iteration 5.

    Produces a short explanation based on inputs without any network calls.
    """

    def generate_explanation(
        self,
        req: GeneratePackingListRequest,
        resp: PackingListResponse,
        *,
        style: Literal["short", "detailed"] = "short",
    ) -> str:
        days = req.tripLengthDays
        acts = ", ".join(req.activities or []) or "(no activities)"
        tod = ", ".join(req.timeOfDayUsage or []) or "(no tod)"
        weather = ", ".join(getattr(req, "weatherHints", []) or []) or "(no weather)"
        item_count = sum(i.qty for i in resp.items)
        base = (
            f"Personalized summary for a {days}d trip to {req.destination}. "
            f"Activities: {acts}; time-of-day: {tod}; weather: {weather}. "
            f"The list contains {len(resp.items)} line items totaling {item_count} units."
        )
        if style == "short":
            return base + " (style=short)"
        # detailed: include categories and top 3 heaviest items
        from collections import Counter

        cats = Counter(i.category for i in resp.items)
        top_heavy = sorted(resp.items, key=lambda x: x.estimatedWeightKg, reverse=True)[:3]
        removed = next((n for n in resp.notes if n.lower().startswith("removed items:")), None)
        details = (
            f" Categories: "
            + ", ".join(f"{k}={v}" for k, v in sorted(cats.items()))
            + "; Top heavy: "
            + ", ".join(i.name for i in top_heavy)
        )
        if removed:
            details += f"; {removed}"
        return base + details + " (style=detailed)"


class AzureLLMClient:
    """Azure OpenAI-backed LLM client (optional, opt-in via env).

        Uses the OpenAI Python SDK's AzureOpenAI client. Requires the following env vars:
      - AZURE_OPENAI_ENDPOINT (e.g., https://<resource>.openai.azure.com)
      - AZURE_OPENAI_API_KEY
            - AZURE_API_VERSION (e.g., 2024-10-21)
            - DEPLOYMENT_NAME (deployment name of your chat model) [or AZURE_OPENAI_CHAT_DEPLOYMENT/AZURE_OPENAI_CHATGPT_DEPLOYMENT]

    Falls back to a terse failure message if invocation errors occur.
    """

    def __init__(
        self,
        *,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: Optional[str] = None,
        deployment: Optional[str] = None,
        timeout: float = 15.0,
    ) -> None:
        raw_endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        # Normalize endpoint to base URL (strip any paths like /openai/deployments/...)
        if raw_endpoint:
            parsed = urlparse(raw_endpoint)
            self.endpoint = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else raw_endpoint
        else:
            self.endpoint = raw_endpoint
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("AZURE_INFERENCE_CREDENTIAL")
        self.api_version = (
            api_version
            or os.getenv("AZURE_API_VERSION")
            or "2024-10-21"
        )
        self.deployment = (
            deployment
            or os.getenv("DEPLOYMENT_NAME")
            or os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
            or os.getenv("AZURE_OPENAI_CHATGPT_DEPLOYMENT")
        )
        self.timeout = timeout

        # Lazy import to avoid hard dependency when unused
        try:
            from openai import AzureOpenAI  # type: ignore
        except Exception as e:  # pragma: no cover - only hit if package missing
            raise RuntimeError(
                "openai package not available. Install 'openai>=1.0.0' to use AzureLLMClient."
            ) from e

        if not (self.endpoint and self.api_key and self.deployment):
            raise RuntimeError(
                "AzureLLMClient requires AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and DEPLOYMENT_NAME (or compatible) env vars."
            )

        # Initialize client
        self._client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
            timeout=self.timeout,
        )

    def generate_explanation(
        self,
        req: GeneratePackingListRequest,
        resp: PackingListResponse,
        *,
        style: Literal["short", "detailed"] = "short",
    ) -> str:
        # Build a concise, deterministic prompt shape; model provides prose
        days = req.tripLengthDays
        acts = ", ".join(req.activities or []) or "(no activities)"
        tod = ", ".join(req.timeOfDayUsage or []) or "(no tod)"
        weather = ", ".join(getattr(req, "weatherHints", []) or []) or "(no weather)"
        item_count = sum(i.qty for i in resp.items)

        sys_prompt = (
            "You are a helpful travel assistant. Summarize the packing list decision succinctly. "
            "Always end your response with ' (style=" + style + ")'."
        )
        user_prompt = (
            f"Trip: {days}d to {req.destination}. Activities: {acts}. ToD: {tod}. Weather: {weather}. "
            f"Items: {len(resp.items)} lines, total units={item_count}. "
        )
        if style == "detailed":
            # Include categories and any removed notes for richer context
            from collections import Counter

            cats = Counter(i.category for i in resp.items)
            removed = next((n for n in resp.notes if n.lower().startswith("removed items:")), None)
            user_prompt += " Categories: " + ", ".join(f"{k}={v}" for k, v in sorted(cats.items()))
            if removed:
                user_prompt += "; " + removed

        try:
            completion = self._client.chat.completions.create(
                model=self.deployment,  # Azure uses deployment name here
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3 if style == "short" else 0.6,
                max_tokens=180 if style == "short" else 400,
            )
            text = completion.choices[0].message.content or ""
            # Ensure the style marker is present for consistency
            marker = f" (style={style})"
            if not text.endswith(marker):
                text = text.rstrip() + marker
            return text
        except Exception as e:  # pragma: no cover - network/credentials errors not unit-tested
            # Fail safely with a brief local summary indicating Azure path failed
            base = (
                f"Personalized summary for a {days}d trip to {req.destination}. "
                f"Activities: {acts}; time-of-day: {tod}; weather: {weather}. "
                f"The list contains {len(resp.items)} line items totaling {item_count} units."
            )
            return base + f" [AzureLLMClient error: {type(e).__name__}] (style={style})"


def get_llm_client_from_env(backend: Optional[str] = None) -> LLMClient:
    """Factory: returns an LLM client based on env var LLM_BACKEND.

    - LLM_BACKEND=azure -> AzureLLMClient (requires Azure env vars)
    - default or anything else -> MockLLMClient
    """
    backend = (backend or os.getenv("LLM_BACKEND") or "mock").strip().lower()
    if backend == "azure":
        try:
            return AzureLLMClient()
        except Exception:
            # If misconfigured, fall back to mock to avoid hard failures
            return MockLLMClient()
    return MockLLMClient()
