from app.llm.groq_client import judge_json

_CHUNK_RELEVANCE_SYSTEM = (
    "You judge whether a retrieved context chunk is relevant and useful for "
    "answering a question. If a reference answer is given, a chunk is relevant "
    "if it contains information needed to produce that answer. Respond with "
    "JSON only: {\"relevant\": true|false, \"reasoning\": \"<one sentence>\"}."
)

_RECALL_DECOMPOSE_SYSTEM = (
    "You decompose a reference answer into a list of atomic factual statements, "
    "each verifiable independently. Respond with JSON only: "
    "{\"statements\": [\"statement 1\", ...]}."
)

_ATTRIBUTION_SYSTEM = (
    "You judge whether a factual statement is supported by the given context. "
    "Respond with JSON only: {\"attributable\": true|false}."
)


def _is_chunk_relevant(question: str, chunk: str, ground_truth: str | None) -> dict:
    user = f"Question: {question}\n"
    if ground_truth:
        user += f"Reference answer: {ground_truth}\n"
    user += f"Context chunk: {chunk}"
    result = judge_json(_CHUNK_RELEVANCE_SYSTEM, user)
    return {"relevant": bool(result.get("relevant", False)), "reasoning": result.get("reasoning", "")}


def context_precision(question: str, contexts: list[str], ground_truth: str | None) -> dict:
    """Order-aware precision: average of precision@k taken at each relevant rank."""
    if not contexts:
        return {"score": 0.0, "chunks": []}

    labels = [_is_chunk_relevant(question, chunk, ground_truth) for chunk in contexts]
    relevant_flags = [label["relevant"] for label in labels]

    if not any(relevant_flags):
        return {"score": 0.0, "chunks": labels}

    precisions_at_k = []
    relevant_so_far = 0
    for k, is_relevant in enumerate(relevant_flags, start=1):
        if is_relevant:
            relevant_so_far += 1
            precisions_at_k.append(relevant_so_far / k)

    score = sum(precisions_at_k) / sum(relevant_flags)
    return {"score": score, "chunks": labels}


def context_recall(contexts: list[str], ground_truth: str | None) -> dict | None:
    """Fraction of ground-truth statements attributable to the retrieved contexts."""
    if not ground_truth:
        return None

    decomposed = judge_json(_RECALL_DECOMPOSE_SYSTEM, f"Reference answer:\n{ground_truth}")
    statements = [s for s in decomposed.get("statements", []) if isinstance(s, str) and s.strip()]
    if not statements:
        return {"score": 1.0, "statements": []}

    joined_context = "\n".join(contexts)
    results = []
    attributable_count = 0
    for statement in statements:
        judged = judge_json(
            _ATTRIBUTION_SYSTEM, f"Context:\n{joined_context}\n\nStatement: {statement}"
        )
        attributable = bool(judged.get("attributable", False))
        attributable_count += int(attributable)
        results.append({"statement": statement, "attributable": attributable})

    return {"score": attributable_count / len(statements), "statements": results}
