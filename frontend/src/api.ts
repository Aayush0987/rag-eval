const API_BASE = "http://localhost:8000";

export interface RunSummary {
  id: number;
  name: string;
  created_at: string;
  source: string;
  is_baseline: boolean;
  num_examples: number;
  avg_custom_faithfulness: number | null;
  avg_ragas_faithfulness: number | null;
}

export interface ExampleResult {
  id: number;
  question: string;
  contexts: string[];
  answer: string;
  ground_truth: string | null;
  custom_faithfulness: number | null;
  custom_answer_relevance_embedding: number | null;
  custom_answer_relevance_llm: number | null;
  custom_context_precision: number | null;
  custom_context_recall: number | null;
  ragas_faithfulness: number | null;
  ragas_answer_relevancy: number | null;
  ragas_context_precision: number | null;
  ragas_context_recall: number | null;
  details: Record<string, unknown>;
}

export interface RunDetail {
  id: number;
  name: string;
  created_at: string;
  source: string;
  is_baseline: boolean;
  examples: ExampleResult[];
}

export interface RegressionExample {
  question: string;
  deltas: Record<string, number | null>;
  is_regression: boolean;
}

export interface RegressionResult {
  per_example: RegressionExample[];
  regressions: RegressionExample[];
  regression_count: number;
  aggregate_deltas: Record<string, number | null>;
  only_in_baseline: string[];
  only_in_new: string[];
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  listRuns: () => request<RunSummary[]>("/runs"),
  getRun: (id: number) => request<RunDetail>(`/runs/${id}`),
  markBaseline: (id: number) =>
    request<RunSummary>(`/runs/${id}/baseline`, { method: "POST" }),
  regression: (baselineId: number, runId: number) =>
    request<RegressionResult>(
      `/regression?baseline_id=${baselineId}&run_id=${runId}`
    ),
  submitSingle: (payload: {
    question: string;
    contexts: string[];
    answer: string;
    ground_truth?: string;
    run_name: string;
  }) =>
    request<RunSummary>("/runs/single", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  submitBatch: (file: File, runName: string) => {
    const form = new FormData();
    form.append("file", file);
    form.append("run_name", runName);
    return request<RunSummary>("/runs/batch", { method: "POST", body: form });
  },
};
