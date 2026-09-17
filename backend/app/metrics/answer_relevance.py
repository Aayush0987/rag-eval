from app.llm.groq_client import judge_json
from app.metrics.embeddings import cosine_similarity

_RELEVANCE_SYSTEM = (
    "You judge how relevant an answer is to a question, on a 0.0-1.0 scale. "
    "1.0 means the answer directly and completely addresses the question. "
    "0.0 means the answer is off-topic or does not address the question at all. "
    "Penalize answers that are evasive, incomplete, or that answer a different "
    "question than the one asked. Respond with JSON only: "
    "{\"score\": <float 0-1>, \"reasoning\": \"<one sentence>\"}."
)


def answer_relevance_embedding(question: str, answer: str) -> float:
    """Cosine similarity between question and answer embeddings."""
    return cosine_similarity(question, answer)


def answer_relevance_llm(question: str, answer: str) -> dict:
    result = judge_json(_RELEVANCE_SYSTEM, f"Question: {question}\nAnswer: {answer}")
    score = result.get("score")
    if not isinstance(score, (int, float)):
        score = 0.0
    return {"score": max(0.0, min(1.0, float(score))), "reasoning": result.get("reasoning", "")}
