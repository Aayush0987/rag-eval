import json
from functools import lru_cache

import httpx
from groq import Groq, RateLimitError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_random_exponential

from app.config import settings

_GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"


@lru_cache
def _client() -> Groq:
    return Groq(api_key=settings.groq_api_key)


@retry(
    retry=retry_if_exception_type(RateLimitError),
    wait=wait_random_exponential(multiplier=1, max=30),
    stop=stop_after_attempt(6),
    reraise=True,
)
def _call_groq(system_prompt: str, user_prompt: str) -> str:
    response = _client().chat.completions.create(
        model=settings.groq_model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content or "{}"


def _call_gemini(system_prompt: str, user_prompt: str) -> str:
    response = httpx.post(
        _GEMINI_URL,
        headers={"Authorization": f"Bearer {settings.gemini_api_key}"},
        json={
            "model": settings.gemini_model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"] or "{}"


def judge_json(system_prompt: str, user_prompt: str) -> dict:
    """Call the LLM-as-judge with a prompt that must return a single JSON object.

    Groq is primary, retried with backoff on its per-minute rate limit. If Groq
    is still rate-limited after retries (typically its *daily* cap, which isn't
    reasonably retryable) and a Gemini key is configured, falls back to Gemini's
    OpenAI-compatible endpoint so a single provider's quota doesn't block runs.
    Judge output is external, untrusted data — callers must not assume keys exist.
    """
    try:
        content = _call_groq(system_prompt, user_prompt)
    except RateLimitError:
        if not settings.gemini_api_key:
            raise
        content = _call_gemini(system_prompt, user_prompt)

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {}
