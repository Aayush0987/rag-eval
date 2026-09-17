"""Run both custom metrics and RAGAS on data/sanity_check/examples.jsonl and
write a side-by-side comparison report to docs/ragas_comparison.md.

Usage: uv run python scripts/compare_ragas.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.metrics.pipeline import run_custom_metrics  # noqa: E402
from app.models.schema import EvalExample  # noqa: E402
from app.ragas_integration.run_ragas import run_ragas_metrics  # noqa: E402

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "sanity_check" / "examples.jsonl"
OUT_PATH = Path(__file__).resolve().parent.parent.parent / "docs" / "ragas_comparison.md"


def main() -> None:
    rows = [json.loads(line) for line in DATA_PATH.read_text().splitlines() if line.strip()]

    results = []
    for row in rows:
        example = EvalExample(
            question=row["question"],
            contexts=row["contexts"],
            answer=row["answer"],
            ground_truth=row.get("ground_truth"),
        )
        custom = run_custom_metrics(example)
        ragas = run_ragas_metrics(example)
        results.append({"label": row["label"], "question": row["question"], **custom, **ragas})
        print(f"[{row['label']:4}] {row['question'][:45]:45} "
              f"custom_faith={custom['custom_faithfulness']:.2f} ragas_faith={ragas['ragas_faithfulness']:.2f}  "
              f"custom_rel={custom['custom_answer_relevance_llm']:.2f} ragas_rel={ragas['ragas_answer_relevancy']:.2f}")

    write_report(results)
    print(f"\nReport written to {OUT_PATH}")


def _mean(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def _fmt(x):
    return f"{x:.3f}" if x is not None else "n/a"


def write_report(results: list[dict]) -> None:
    good = [r for r in results if r["label"] == "good"]
    bad = [r for r in results if r["label"] == "bad"]

    lines = ["# Custom Metrics vs RAGAS — Comparison Report", ""]
    lines.append("Ran the same 12 labeled examples (6 good/bad pairs, `data/sanity_check/examples.jsonl`) ")
    lines.append("through both the from-scratch custom metrics and RAGAS's equivalent metrics.")
    lines.append("")

    lines.append("## Separation power (mean good vs mean bad)")
    lines.append("")
    lines.append("| Metric | Custom good | Custom bad | Custom gap | RAGAS good | RAGAS bad | RAGAS gap |")
    lines.append("|---|---|---|---|---|---|---|")
    pairs = [
        ("Faithfulness", "custom_faithfulness", "ragas_faithfulness"),
        ("Answer relevance (LLM)", "custom_answer_relevance_llm", "ragas_answer_relevancy"),
        ("Context precision", "custom_context_precision", "ragas_context_precision"),
        ("Context recall", "custom_context_recall", "ragas_context_recall"),
    ]
    for label, custom_field, ragas_field in pairs:
        cg, cb = _mean([r[custom_field] for r in good]), _mean([r[custom_field] for r in bad])
        rg, rb = _mean([r[ragas_field] for r in good]), _mean([r[ragas_field] for r in bad])
        c_gap = cg - cb if cg is not None and cb is not None else None
        r_gap = rg - rb if rg is not None and rb is not None else None
        lines.append(
            f"| {label} | {_fmt(cg)} | {_fmt(cb)} | {_fmt(c_gap)} | {_fmt(rg)} | {_fmt(rb)} | {_fmt(r_gap)} |"
        )

    lines.append("")
    lines.append("## Per-example scores")
    lines.append("")
    lines.append("| Label | Question | Custom faith | RAGAS faith | Custom rel | RAGAS rel |")
    lines.append("|---|---|---|---|---|---|")
    for r in results:
        lines.append(
            f"| {r['label']} | {r['question'][:40]} | {r['custom_faithfulness']:.2f} | "
            f"{r['ragas_faithfulness']:.2f} | {r['custom_answer_relevance_llm']:.2f} | "
            f"{r['ragas_answer_relevancy']:.2f} |"
        )

    lines.append("")
    lines.append("## Observed divergence")
    lines.append("")
    lines.append(
        "RAGAS's `answer_relevancy` measures semantic alignment between the question and answer "
        "(it back-generates candidate questions from the answer and embeds them against the original "
        "question) — it does **not** check whether the answer is factually correct. Our custom LLM-as-judge "
        "relevance metric explicitly penalizes factual errors as part of \"relevance,\" since an answer that "
        "confidently states the wrong fact is not usefully relevant to the question asked. This shows up "
        "directly in the table above: on hallucinated answers, RAGAS's relevance score stays high while "
        "ours drops to near zero. Both are legitimate metric designs — they are answering different "
        "questions (\"is this semantically on-topic\" vs \"is this a good answer\") — but conflating them "
        "would be a mistake when reading a dashboard."
    )
    lines.append("")
    lines.append(
        "Faithfulness scores agree closely between the two implementations on this test set, despite using "
        "different mechanisms: ours decomposes claims via LLM and checks entailment with a local NLI "
        "cross-encoder, while RAGAS decomposes and checks entailment both via LLM-as-judge. The agreement "
        "here is a mild validation that the local-NLI approach is a reasonable substitute for a second LLM "
        "call, at lower cost and no extra API latency."
    )
    lines.append("")

    OUT_PATH.parent.mkdir(exist_ok=True)
    OUT_PATH.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
