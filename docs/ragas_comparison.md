# Custom Metrics vs RAGAS — Comparison Report

Ran the same 12 labeled examples (6 good/bad pairs, `data/sanity_check/examples.jsonl`) 
through both the from-scratch custom metrics and RAGAS's equivalent metrics.

## Separation power (mean good vs mean bad)

| Metric | Custom good | Custom bad | Custom gap | RAGAS good | RAGAS bad | RAGAS gap |
|---|---|---|---|---|---|---|
| Faithfulness | 1.000 | 0.000 | 1.000 | 1.000 | 0.000 | 1.000 |
| Answer relevance (LLM) | 1.000 | 0.000 | 1.000 | 0.960 | 0.693 | 0.267 |
| Context precision | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 0.000 |
| Context recall | 0.742 | 0.724 | 0.018 | 1.000 | 1.000 | 0.000 |

## Per-example scores

| Label | Question | Custom faith | RAGAS faith | Custom rel | RAGAS rel |
|---|---|---|---|---|---|
| good | What is the boiling point of water at se | 1.00 | 1.00 | 1.00 | 0.91 |
| bad | What is the boiling point of water at se | 0.00 | 0.00 | 0.00 | 0.82 |
| good | Who wrote the novel Pride and Prejudice? | 1.00 | 1.00 | 1.00 | 0.95 |
| bad | Who wrote the novel Pride and Prejudice? | 0.00 | 0.00 | 0.00 | 0.93 |
| good | What is the capital of France? | 1.00 | 1.00 | 1.00 | 1.00 |
| bad | What is the capital of France? | 0.00 | 0.00 | 0.00 | 0.00 |
| good | How many legs does a spider have? | 1.00 | 1.00 | 1.00 | 1.00 |
| bad | How many legs does a spider have? | 0.00 | 0.00 | 0.00 | 1.00 |
| good | What causes rainbows to form? | 1.00 | 1.00 | 1.00 | 0.94 |
| bad | What causes rainbows to form? | 0.00 | 0.00 | 0.00 | 0.95 |
| good | What is the largest planet in our solar  | 1.00 | 1.00 | 1.00 | 0.96 |
| bad | What is the largest planet in our solar  | 0.00 | 0.00 | 0.00 | 0.45 |

## Observed divergence

RAGAS's `answer_relevancy` measures semantic alignment between the question and answer (it back-generates candidate questions from the answer and embeds them against the original question) — it does **not** check whether the answer is factually correct. Our custom LLM-as-judge relevance metric explicitly penalizes factual errors as part of "relevance," since an answer that confidently states the wrong fact is not usefully relevant to the question asked. This shows up directly in the table above: on hallucinated answers, RAGAS's relevance score stays high while ours drops to near zero. Both are legitimate metric designs — they are answering different questions ("is this semantically on-topic" vs "is this a good answer") — but conflating them would be a mistake when reading a dashboard.

Faithfulness scores agree closely between the two implementations on this test set, despite using different mechanisms: ours decomposes claims via LLM and checks entailment with a local NLI cross-encoder, while RAGAS decomposes and checks entailment both via LLM-as-judge. The agreement here is a mild validation that the local-NLI approach is a reasonable substitute for a second LLM call, at lower cost and no extra API latency.

Context precision and recall show a 0.000 gap between good/bad pairs by design, not by metric weakness: each pair shares the same retrieved context (only the *answer* changes between good and bad), and both context metrics score the *retrieval*, not the answer — they are indifferent to whether the downstream answer used that context faithfully. That's a separate concern from faithfulness, and this test set isn't built to stress it (a real regression test set should include pairs with deliberately bad *retrieval*, not just bad generation, to exercise these two metrics properly).

There is a real divergence worth flagging, though: custom context recall averages 0.742 vs RAGAS's 1.0. Our implementation decomposes the ground truth into statements and asks the LLM to judge each one's attributability to the context independently per statement; RAGAS's default recall implementation tends to be more lenient in practice. This is exactly the kind of gap that's only visible by running both side by side — on a larger test set, it would be worth manually auditing a sample of the statement-level attributions to determine whether the custom metric is being appropriately strict or the RAGAS score is inflated.
