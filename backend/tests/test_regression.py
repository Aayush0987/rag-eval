from types import SimpleNamespace

from app.metrics.regression import REGRESSION_THRESHOLD, compare_runs


def ex(question, **scores):
    base = dict(
        custom_faithfulness=1.0,
        custom_answer_relevance_embedding=0.8,
        custom_answer_relevance_llm=1.0,
        custom_context_precision=1.0,
        custom_context_recall=1.0,
    )
    base.update(scores)
    return SimpleNamespace(question=question, **base)


def test_no_change_is_not_regression():
    result = compare_runs([ex("q")], [ex("q")])
    assert result["regression_count"] == 0
    assert result["aggregate_deltas"]["custom_faithfulness"] == 0


def test_large_drop_flags_regression():
    result = compare_runs([ex("q")], [ex("q", custom_faithfulness=0.0)])
    assert result["regression_count"] == 1
    assert result["aggregate_deltas"]["custom_faithfulness"] == -1.0


def test_drop_within_threshold_is_ignored():
    small = 1.0 - REGRESSION_THRESHOLD / 2
    result = compare_runs([ex("q")], [ex("q", custom_faithfulness=small)])
    assert result["regression_count"] == 0


def test_improvement_is_not_regression():
    result = compare_runs([ex("q", custom_faithfulness=0.2)], [ex("q")])
    assert result["regression_count"] == 0


def test_none_scores_are_skipped():
    result = compare_runs([ex("q", custom_context_recall=None)], [ex("q")])
    assert result["per_example"][0]["deltas"]["custom_context_recall"] is None
    assert result["aggregate_deltas"]["custom_context_recall"] is None


def test_unmatched_questions_reported():
    result = compare_runs([ex("a"), ex("b")], [ex("b"), ex("c")])
    assert result["only_in_baseline"] == ["a"]
    assert result["only_in_new"] == ["c"]
    assert len(result["per_example"]) == 1
