from app.metrics.answer_relevance import answer_relevance_embedding, answer_relevance_llm
from app.metrics.context_precision_recall import context_precision, context_recall
from app.metrics.faithfulness import faithfulness
from app.models.schema import EvalExample


def run_custom_metrics(example: EvalExample) -> dict:
    faith = faithfulness(example.answer, example.contexts)
    relevance_llm = answer_relevance_llm(example.question, example.answer)
    precision = context_precision(example.question, example.contexts, example.ground_truth)
    recall = context_recall(example.contexts, example.ground_truth)

    return {
        "custom_faithfulness": faith["score"],
        "custom_answer_relevance_embedding": answer_relevance_embedding(
            example.question, example.answer
        ),
        "custom_answer_relevance_llm": relevance_llm["score"],
        "custom_context_precision": precision["score"],
        "custom_context_recall": recall["score"] if recall else None,
        "details": {
            "faithfulness": faith,
            "answer_relevance_llm": relevance_llm,
            "context_precision": precision,
            "context_recall": recall,
        },
    }
