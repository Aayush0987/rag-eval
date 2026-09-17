from app.llm.groq_client import judge_json
from app.metrics.nli import entailment_score

_DECOMPOSE_SYSTEM = (
    "You decompose an answer into a list of atomic, self-contained factual claims. "
    "Each claim must be verifiable on its own, without pronouns or references back to "
    "other claims. Respond with JSON only: {\"claims\": [\"claim 1\", \"claim 2\", ...]}. "
    "If the answer makes no factual claims (e.g. it's a refusal or a question), return "
    "an empty list."
)


def decompose_claims(answer: str) -> list[str]:
    result = judge_json(_DECOMPOSE_SYSTEM, f"Answer:\n{answer}")
    claims = result.get("claims", [])
    return [c for c in claims if isinstance(c, str) and c.strip()]


def faithfulness(answer: str, contexts: list[str]) -> dict:
    """Faithfulness = fraction of claims in `answer` entailed by `contexts`.

    Each claim is checked against the full concatenated context using a local
    NLI cross-encoder (entailment/neutral/contradiction), not an LLM judge —
    this is the "from scratch, NLI-based" half of the metric.
    """
    claims = decompose_claims(answer)
    if not claims:
        return {"score": 1.0, "claims": []}

    premise = "\n".join(contexts)
    claim_results = []
    entailed_count = 0
    for claim in claims:
        result = entailment_score(premise, claim)
        is_entailed = result["label"] == "entailment"
        entailed_count += int(is_entailed)
        claim_results.append({"claim": claim, **result, "entailed": is_entailed})

    return {"score": entailed_count / len(claims), "claims": claim_results}
