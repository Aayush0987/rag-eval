import json
from functools import lru_cache

from groq import Groq

from app.config import settings


@lru_cache
def _client() -> Groq:
    return Groq(api_key=settings.groq_api_key)


def judge_json(system_prompt: str, user_prompt: str) -> dict:
    """Call the LLM-as-judge with a prompt that must return a single JSON object.

    Judge output is external, untrusted data — callers must not assume keys exist.
    """
    response = _client().chat.completions.create(
        model=settings.groq_model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = response.choices[0].message.content or "{}"
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {}
