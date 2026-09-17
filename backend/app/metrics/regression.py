from app.db.models import ExampleResult

_METRIC_FIELDS = [
    "custom_faithfulness",
    "custom_answer_relevance_embedding",
    "custom_answer_relevance_llm",
    "custom_context_precision",
    "custom_context_recall",
]

REGRESSION_THRESHOLD = 0.1


def compare_runs(baseline_examples: list[ExampleResult], new_examples: list[ExampleResult]) -> dict:
    """Match examples by question text and diff metric scores.

    A drop of more than REGRESSION_THRESHOLD on any metric flags that example
    as a regression. Examples present in only one run are reported separately
    rather than silently ignored.
    """
    baseline_by_question = {e.question: e for e in baseline_examples}
    new_by_question = {e.question: e for e in new_examples}

    common_questions = set(baseline_by_question) & set(new_by_question)
    only_in_baseline = set(baseline_by_question) - set(new_by_question)
    only_in_new = set(new_by_question) - set(baseline_by_question)

    per_example = []
    for question in common_questions:
        base = baseline_by_question[question]
        new = new_by_question[question]
        deltas = {}
        is_regression = False
        for field in _METRIC_FIELDS:
            base_val = getattr(base, field)
            new_val = getattr(new, field)
            if base_val is None or new_val is None:
                deltas[field] = None
                continue
            delta = new_val - base_val
            deltas[field] = delta
            if delta < -REGRESSION_THRESHOLD:
                is_regression = True

        per_example.append(
            {
                "question": question,
                "deltas": deltas,
                "is_regression": is_regression,
            }
        )

    regressions = [e for e in per_example if e["is_regression"]]

    aggregate = {}
    for field in _METRIC_FIELDS:
        deltas = [e["deltas"][field] for e in per_example if e["deltas"][field] is not None]
        aggregate[field] = sum(deltas) / len(deltas) if deltas else None

    return {
        "per_example": per_example,
        "regressions": regressions,
        "regression_count": len(regressions),
        "aggregate_deltas": aggregate,
        "only_in_baseline": sorted(only_in_baseline),
        "only_in_new": sorted(only_in_new),
    }
