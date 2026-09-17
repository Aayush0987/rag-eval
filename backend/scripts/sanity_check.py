"""Run custom metrics against data/sanity_check/examples.jsonl and verify that
'good' (faithful/relevant) examples clearly separate from 'bad' (hallucinated/
off-topic) ones. Exits non-zero if separation fails.

Usage: uv run python scripts/sanity_check.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.metrics.pipeline import run_custom_metrics  # noqa: E402
from app.models.schema import EvalExample  # noqa: E402

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "sanity_check" / "examples.jsonl"
FIELDS = [
    "custom_faithfulness",
    "custom_answer_relevance_embedding",
    "custom_answer_relevance_llm",
]


def main() -> int:
    rows = [json.loads(line) for line in DATA_PATH.read_text().splitlines() if line.strip()]

    good_scores = {f: [] for f in FIELDS}
    bad_scores = {f: [] for f in FIELDS}

    failures = []
    for row in rows:
        example = EvalExample(
            question=row["question"],
            contexts=row["contexts"],
            answer=row["answer"],
            ground_truth=row.get("ground_truth"),
        )
        result = run_custom_metrics(example)
        bucket = good_scores if row["label"] == "good" else bad_scores
        for field in FIELDS:
            bucket[field].append(result[field])

        print(f"[{row['label']:4}] {row['question'][:50]:50} "
              f"faith={result['custom_faithfulness']:.2f} "
              f"rel_emb={result['custom_answer_relevance_embedding']:.2f} "
              f"rel_llm={result['custom_answer_relevance_llm']:.2f}")

    print("\n--- Separation check (mean good vs mean bad) ---")
    for field in FIELDS:
        good_mean = sum(good_scores[field]) / len(good_scores[field])
        bad_mean = sum(bad_scores[field]) / len(bad_scores[field])
        separated = good_mean > bad_mean
        status = "OK" if separated else "FAIL"
        print(f"{field}: good={good_mean:.3f} bad={bad_mean:.3f} -> {status}")
        if not separated:
            failures.append(field)

    if failures:
        print(f"\nSanity check FAILED for: {failures}")
        return 1

    print("\nSanity check PASSED: custom metrics separate good from bad examples.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
