# Progress Tracker — RAG Evaluation & Observability Tool

Local-only for now. Nothing gets committed/pushed to GitHub until explicitly requested.

Legend: `[ ]` not started · `[~]` in progress · `[x]` done

## Phase 0 — Study (owned by user, not part of the code deliverable)
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
- [x] Labeled test set with clear-cut good/bad examples (reused `data/sanity_check/examples.jsonl`, 6 pairs)
- [x] Compare custom vs RAGAS separation quality (`backend/scripts/compare_ragas.py`)
- [x] Document agreement/divergence with concrete examples — `docs/ragas_comparison.md`. Headline finding: faithfulness agrees closely between the two implementations; answer relevance diverges sharply (RAGAS's `answer_relevancy` doesn't penalize factual incorrectness, ours does) — both are legitimate but answer different questions

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
- [x] Run history view (`RunHistory.tsx`) — mark-baseline action included
- [x] Detail view (`RunDetailView.tsx`) — per-example, custom vs RAGAS side by side, expandable raw judge details
- [x] Regression view (`RegressionView.tsx`) — baseline vs new run picker, degraded examples highlighted
- [x] Submit-run view (`UploadForm.tsx`) — batch JSONL + single example, not in the original phase list but needed to drive the other three views
- [x] Visually verified in Chrome (2026-09-27) — all four views render correctly against the live backend; screenshots in `docs/screenshots/`

## Phase 8 — Documentation
- [x] README: metrics explained, architecture diagram (root `README.md`)
- [x] Custom vs RAGAS validation results/analysis (linked from README, full detail in `docs/ragas_comparison.md`)
- [x] Dashboard screenshots — captured in the browser, embedded in README
- [x] Example regression-catch walkthrough (real data from the live regression test)
- [x] Known limitations (LLM-as-judge cost/latency/bias, Groq free-tier daily cap hit live, custom-vs-RAGAS agreement caveat)

---

## Bugs found and fixed (live, hit during build)
- **`uvloop` + RAGAS incompatibility**: uvicorn's default event loop (`uvloop`) can't be patched by RAGAS's internal `nest_asyncio` call (`ValueError: Can't patch loop of type uvloop.Loop`) — only surfaced once RAGAS ran *inside* the actual server, not in standalone test scripts. Fixed by running uvicorn with `--loop asyncio`. **Anyone running this server must include that flag** — see updated "Running it" section in the README.
- **`run_name` silently ignored on batch upload**: `run_name: str = "batch-run"` alongside an `UploadFile` param isn't bound to multipart form data without an explicit `Form(...)` annotation — FastAPI just quietly kept the default instead of erroring. Found by submitting a batch named `"demo-pair"` and seeing it come back as `"batch-run"`. Fixed in `backend/app/api/runs.py`.
- **Gemini fallback needed its own retry/backoff**: initially only Groq had retry logic; Gemini's free tier (15 RPM on the lite model) got hit directly once Groq was exhausted, with no retry. Added the same tenacity backoff to `_call_gemini`.

## Known Limitations (live, hit during build)
- **Groq free tier has both a per-minute (8000 TPM) and a per-day (200,000 TPD) token cap.** The per-minute one is handled with retry+backoff (`app/llm/groq_client.py`, tenacity, up to 6 attempts / 30s max wait). The **daily** cap is not retryable in any reasonable way — it was exhausted during today's testing (sanity check + comparison script + one batch submission, ~12 examples each doing 5-10+ LLM calls). A real evaluation run against hundreds of examples will need either a paid Groq tier or spreading runs across days. Worth a callout in the Phase 8 README's limitations section.

## Decisions Log
- **LLM-as-judge provider**: Groq (free tier) — decided 2026-09-17
- **Groq model**: `openai/gpt-oss-20b` — `llama-3.3-70b-versatile` from the original brief is not available on this account/key (404); verified working via `client.models.list()`
- **Faithfulness design**: LLM decomposes answer into atomic claims, then a **local NLI cross-encoder** (`cross-encoder/nli-deberta-v3-base`) checks entailment against context — genuinely different methodology from RAGAS (which uses LLM-as-judge for both steps), not just a reimplementation
- **RAGAS + Groq wiring**: `langchain-groq` has an unresolvable dependency conflict with the `groq` SDK version we need, so RAGAS talks to Groq via `langchain-openai`'s `ChatOpenAI` pointed at Groq's OpenAI-compatible endpoint (`https://api.groq.com/openai/v1`) instead
- **ragas version pin**: `ragas==0.2.15` (latest 0.4.3 has a broken import chain — `langchain_community.chat_models.vertexai` was removed upstream); paired with `langchain-community<0.4` to keep that module available
- **Storage**: SQLite
- **Package manager (backend)**: uv
- **Git**: pushed to https://github.com/Aayush0987/rag-eval (public) on 2026-09-27 at user's request; history scanned for keys first

## Setup Notes
- Backend: `cd backend && uv sync` (or `uv run <cmd>`)
- Env vars: copy `.env.example` to `.env`, add `GROQ_API_KEY`
