# Build Brief: General-Purpose RAG Evaluation & Observability Tool

## Project Summary
A general-purpose tool that evaluates any RAG system's outputs. Users submit
(question, retrieved_context, generated_answer, ground_truth[optional]) triples,
and receive a full evaluation report. Core metrics (faithfulness, answer relevance,
context precision/recall) are implemented from scratch, and validated by running
the same inputs through RAGAS for side-by-side comparison. Results are viewable
in a React web dashboard, with support for regression testing across runs over time.

## Tech Stack
- **Core metrics**: Python, built from scratch (NLI-based faithfulness, embedding +
  LLM-as-judge relevance, LLM-as-judge context precision/recall)
- **Comparison framework**: RAGAS
- **Backend**: FastAPI
- **Frontend**: React
- **Storage**: SQLite (run history, per-example scores)
- **LLM-as-judge**: to be selected at build time — must remain free/local or
  free-tier (e.g., Groq) consistent with prior projects' cost constraints

## Input Schema
```
{
  "question": str,
  "contexts": [str, ...],
  "answer": str,
  "ground_truth": str (optional)
}
```
Support both batch JSONL upload and single-example API submission.

---

## Phase 0 — Study
- RAG evaluation theory: faithfulness, answer relevance, context precision/recall
- NLI (Natural Language Inference): entailment/contradiction/neutral — faithfulness
  checking is fundamentally an NLI problem
- LLM-as-judge methodology: prompt design, scoring rubrics, known biases
  (position bias, verbosity bias, self-preference bias)
- RAGAS internals — how each of its metrics is computed, so the comparison in
  Phase 4 is meaningful rather than superficial
- Observability/dashboard design principles — what makes eval results actionable

## Phase 1 — Input Format & Ingestion
- Implement the schema above
- Batch JSONL upload endpoint + single-example API endpoint

## Phase 2 — Build Custom Metrics (from scratch)
- **Faithfulness**: decompose the answer into individual claims (LLM-based),
  check each claim against the provided context for entailment (NLI model or
  LLM-as-judge), aggregate into a faithfulness score
- **Answer Relevance**: implement two approaches — (a) embedding similarity
  between question and answer, (b) LLM-as-judge relevance scoring — compare both
- **Context Precision/Recall**: LLM-as-judge relevance labeling of each retrieved
  chunk against the question (and ground truth, if provided)
- Build a small synthetic sanity-check set (obviously faithful vs. obviously
  hallucinated examples) and verify each metric behaves correctly before trusting
  it on real data

## Phase 3 — RAGAS Integration
- Run the same input triples through RAGAS's equivalent metrics
- Persist both your custom scores and RAGAS's scores per example, side by side

## Phase 4 — Comparison & Validation
- Build a labeled test set with clear-cut good/bad examples
- Compare how well custom metrics vs. RAGAS metrics separate good from bad
- Document agreement and divergence patterns with concrete examples — this
  analysis is a core deliverable, not a side note

## Phase 5 — Regression Testing
- Allow marking a run as a "baseline" (fixed test set + its scores)
- Support re-running the same test set and diffing against the baseline
- Flag score drops as regressions, surfaced per-example and in aggregate

## Phase 6 — Backend API (FastAPI)
- Submit a run (batch or single example)
- Fetch run history
- Fetch detailed per-example scores for a given run
- Trigger regression comparison between two runs

## Phase 7 — Frontend Dashboard (React)
- **Run history view**: list of past runs with summary scores
- **Detail view**: per-example breakdown — question, context, answer, all metric
  scores, custom-metric vs. RAGAS shown side by side
- **Regression view**: comparison between a baseline and a new run, with
  degraded examples highlighted
- Prioritize clarity over visual complexity — this dashboard needs to read well
  in a live demo/interview screen-share

## Phase 8 — Documentation
- README covering: what each metric measures and why, architecture diagram,
  custom-metric vs. RAGAS validation results and analysis, dashboard screenshots,
  an example regression-catch walkthrough, known limitations (LLM-as-judge cost/
  latency, known biases in LLM-as-judge scoring)

---

## Success Criteria
- Custom metrics correctly separate obviously-good from obviously-bad examples
  in the validation set
- Documented, evidence-backed comparison against RAGAS (agreement or meaningful
  divergence — either is a valid, discussable finding)
- Working regression detection between two runs, correctly flagging degraded examples
- Functional React dashboard covering run history, per-example detail, and
  regression comparison views
