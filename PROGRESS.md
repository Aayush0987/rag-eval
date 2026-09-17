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
- [x] Verify each metric behaves correctly on sanity set — PASSED. `uv run python scripts/sanity_check.py`: faithfulness good=1.000/bad=0.000, LLM relevance good=1.000/bad=0.000, embedding relevance good=0.824/bad=0.690 (weaker signal as expected, still separates)

## Phase 3 — RAGAS Integration
- [x] Run same inputs through RAGAS equivalents (`app/ragas_integration/run_ragas.py`, via Groq's OpenAI-compatible endpoint)
- [x] Persist custom + RAGAS scores side by side per example (DB schema + crud.create_run)
- [x] Live end-to-end validation — confirmed working. Early divergence spotted: RAGAS `answer_relevancy` scored a factually-wrong answer 0.82 (measures question/answer semantic alignment only) vs our LLM-judge's 0.0 (penalizes factual correctness) — good material for Phase 4

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
- [x] Live smoke test of all endpoints against a real Groq key — batch upload, run detail, baseline marking, and regression comparison all verified against real Groq calls

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
- **Groq model**: `openai/gpt-oss-20b` — `llama-3.3-70b-versatile` from the original brief is not available on this account/key (404); verified working via `client.models.list()`
- **Faithfulness design**: LLM decomposes answer into atomic claims, then a **local NLI cross-encoder** (`cross-encoder/nli-deberta-v3-base`) checks entailment against context — genuinely different methodology from RAGAS (which uses LLM-as-judge for both steps), not just a reimplementation
- **RAGAS + Groq wiring**: `langchain-groq` has an unresolvable dependency conflict with the `groq` SDK version we need, so RAGAS talks to Groq via `langchain-openai`'s `ChatOpenAI` pointed at Groq's OpenAI-compatible endpoint (`https://api.groq.com/openai/v1`) instead
- **ragas version pin**: `ragas==0.2.15` (latest 0.4.3 has a broken import chain — `langchain_community.chat_models.vertexai` was removed upstream); paired with `langchain-community<0.4` to keep that module available
- **Storage**: SQLite
- **Package manager (backend)**: uv
- **Git**: local repo only, no commits/pushes until user says so

## Setup Notes
- Backend: `cd backend && uv sync` (or `uv run <cmd>`)
- Env vars: copy `.env.example` to `.env`, add `GROQ_API_KEY`
