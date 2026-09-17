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
- [x] Pydantic schema for (question, contexts, answer, ground_truth?)
- [x] Batch JSONL upload endpoint (`POST /runs/batch`)
- [x] Single-example API endpoint (`POST /runs/single`)

## Phase 2 — Build Custom Metrics (from scratch)
- [x] Faithfulness (LLM claim decomposition + local NLI cross-encoder entailment)
- [x] Answer Relevance — embedding similarity approach (sentence-transformers)
- [x] Answer Relevance — LLM-as-judge approach (Groq)
- [x] Context Precision/Recall — LLM-as-judge relevance labeling (Groq)
- [x] Synthetic sanity-check set (`data/sanity_check/examples.jsonl`, 6 good/bad pairs)
- [ ] Verify each metric behaves correctly on sanity set — **blocked on GROQ_API_KEY**, script ready at `backend/scripts/sanity_check.py`

## Phase 3 — RAGAS Integration
- [x] Run same inputs through RAGAS equivalents (`app/ragas_integration/run_ragas.py`, via Groq's OpenAI-compatible endpoint)
- [x] Persist custom + RAGAS scores side by side per example (DB schema + crud.create_run)
- [ ] Live end-to-end validation — blocked on GROQ_API_KEY

## Phase 4 — Comparison & Validation
- [ ] Labeled test set with clear-cut good/bad examples
- [ ] Compare custom vs RAGAS separation quality
- [ ] Document agreement/divergence with concrete examples

## Phase 5 — Regression Testing
- [x] Mark a run as baseline (`POST /runs/{id}/baseline`)
- [x] Re-run test set and diff against baseline (`app/metrics/regression.py`)
- [x] Flag score drops as regressions (per-example + aggregate, threshold=0.1)

## Phase 6 — Backend API (FastAPI)
- [x] Submit run (batch or single)
- [x] Fetch run history (`GET /runs`)
- [x] Fetch per-example scores for a run (`GET /runs/{id}`)
- [x] Trigger regression comparison between two runs (`GET /regression`)
- [ ] Live smoke test of all endpoints against a real Groq key

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
