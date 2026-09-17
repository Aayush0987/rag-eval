# Progress Tracker — RAG Evaluation & Observability Tool

Local-only for now. Nothing gets committed/pushed to GitHub until explicitly requested.

Legend: `[ ]` not started · `[~]` in progress · `[x]` done

## Phase 0 — Study
- [ ] RAG evaluation theory: faithfulness, answer relevance, context precision/recall
- [ ] NLI (entailment/contradiction/neutral) for faithfulness
- [ ] LLM-as-judge methodology: prompt design, rubrics, biases
- [ ] RAGAS internals per metric
- [ ] Observability/dashboard design principles

## Phase 1 — Input Format & Ingestion
- [ ] Pydantic schema for (question, contexts, answer, ground_truth?)
- [ ] Batch JSONL upload endpoint
- [ ] Single-example API endpoint

## Phase 2 — Build Custom Metrics (from scratch)
- [ ] Faithfulness (claim decomposition + NLI/LLM-judge entailment)
- [ ] Answer Relevance — embedding similarity approach
- [ ] Answer Relevance — LLM-as-judge approach
- [ ] Context Precision/Recall — LLM-as-judge relevance labeling
- [ ] Synthetic sanity-check set (obviously faithful vs hallucinated)
- [ ] Verify each metric behaves correctly on sanity set

## Phase 3 — RAGAS Integration
- [ ] Run same inputs through RAGAS equivalents
- [ ] Persist custom + RAGAS scores side by side per example

## Phase 4 — Comparison & Validation
- [ ] Labeled test set with clear-cut good/bad examples
- [ ] Compare custom vs RAGAS separation quality
- [ ] Document agreement/divergence with concrete examples

## Phase 5 — Regression Testing
- [ ] Mark a run as baseline (fixed test set + scores)
- [ ] Re-run test set and diff against baseline
- [ ] Flag score drops as regressions (per-example + aggregate)

## Phase 6 — Backend API (FastAPI)
- [ ] Submit run (batch or single)
- [ ] Fetch run history
- [ ] Fetch per-example scores for a run
- [ ] Trigger regression comparison between two runs

## Phase 7 — Frontend Dashboard (React)
- [ ] Run history view
- [ ] Detail view (per-example, custom vs RAGAS side by side)
- [ ] Regression view (baseline vs new run, degraded examples highlighted)

## Phase 8 — Documentation
- [ ] README: metrics explained, architecture diagram
- [ ] Custom vs RAGAS validation results/analysis
- [ ] Dashboard screenshots
- [ ] Example regression-catch walkthrough
- [ ] Known limitations (LLM-as-judge cost/latency/bias)

---

## Decisions Log
- **LLM-as-judge provider**: Groq (free tier) — decided 2026-09-17
- **Storage**: SQLite
- **Package manager (backend)**: uv
- **Git**: local repo only, no commits/pushes until user says so

## Setup Notes
- Backend: `cd backend && uv sync` (or `uv run <cmd>`)
- Env vars: copy `.env.example` to `.env`, add `GROQ_API_KEY`
