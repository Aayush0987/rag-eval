import { useEffect, useState } from "react";
import { api, type RegressionResult, type RunSummary } from "../api";

const METRIC_LABELS: Record<string, string> = {
  custom_faithfulness: "Faithfulness",
  custom_answer_relevance_embedding: "Relevance (embedding)",
  custom_answer_relevance_llm: "Relevance (LLM)",
  custom_context_precision: "Context precision",
  custom_context_recall: "Context recall",
};

export function RegressionView() {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [baselineId, setBaselineId] = useState<number | "">("");
  const [runId, setRunId] = useState<number | "">("");
  const [result, setResult] = useState<RegressionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listRuns().then(setRuns).catch((e) => setError(String(e)));
  }, []);

  const baselines = runs.filter((r) => r.is_baseline);

  async function handleCompare() {
    if (baselineId === "" || runId === "") return;
    setError(null);
    setResult(null);
    try {
      setResult(await api.regression(baselineId, runId));
    } catch (e) {
      setError(String(e));
    }
  }

  return (
    <div>
      <div className="controls">
        <label>
          Baseline run:
          <select value={baselineId} onChange={(e) => setBaselineId(Number(e.target.value) || "")}>
            <option value="">Select…</option>
            {baselines.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name} (#{r.id})
              </option>
            ))}
          </select>
        </label>
        <label>
          Compare against:
          <select value={runId} onChange={(e) => setRunId(Number(e.target.value) || "")}>
            <option value="">Select…</option>
            {runs.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name} (#{r.id})
              </option>
            ))}
          </select>
        </label>
        <button onClick={handleCompare} disabled={baselineId === "" || runId === ""}>
          Compare
        </button>
      </div>

      {baselines.length === 0 && (
        <p className="empty">No baseline run marked yet — mark one from the Run History tab.</p>
      )}
      {error && <p className="error">{error}</p>}

      {result && (
        <div>
          <h3>
            {result.regression_count} regression{result.regression_count === 1 ? "" : "s"} detected
          </h3>

          <table className="metric-table">
            <thead>
              <tr>
                <th>Metric</th>
                <th>Aggregate delta</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(result.aggregate_deltas).map(([field, delta]) => (
                <tr key={field}>
                  <td>{METRIC_LABELS[field] ?? field}</td>
                  <td className={delta !== null && delta < 0 ? "negative" : ""}>
                    {delta === null ? "—" : delta.toFixed(3)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <h4>Per-example</h4>
          <table className="metric-table">
            <thead>
              <tr>
                <th>Question</th>
                <th>Status</th>
                {Object.keys(result.aggregate_deltas).map((field) => (
                  <th key={field}>{METRIC_LABELS[field] ?? field}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {result.per_example.map((ex) => (
                <tr key={ex.question} className={ex.is_regression ? "regressed-row" : ""}>
                  <td>{ex.question}</td>
                  <td>{ex.is_regression ? "⚠ regressed" : "ok"}</td>
                  {Object.keys(result.aggregate_deltas).map((field) => (
                    <td key={field} className={(ex.deltas[field] ?? 0) < 0 ? "negative" : ""}>
                      {ex.deltas[field] === null ? "—" : ex.deltas[field]!.toFixed(2)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>

          {(result.only_in_baseline.length > 0 || result.only_in_new.length > 0) && (
            <p className="meta">
              {result.only_in_baseline.length > 0 &&
                `${result.only_in_baseline.length} question(s) only in baseline. `}
              {result.only_in_new.length > 0 && `${result.only_in_new.length} question(s) only in new run.`}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
