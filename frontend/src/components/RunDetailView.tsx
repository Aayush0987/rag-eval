import { useEffect, useState } from "react";
import { api, type RunDetail } from "../api";
import { formatScore } from "./RunHistory";

interface Props {
  runId: number;
  onBack: () => void;
}

const METRIC_ROWS: Array<{
  label: string;
  custom: keyof RunDetail["examples"][number];
  ragas: keyof RunDetail["examples"][number] | null;
}> = [
  { label: "Faithfulness", custom: "custom_faithfulness", ragas: "ragas_faithfulness" },
  {
    label: "Answer relevance (LLM)",
    custom: "custom_answer_relevance_llm",
    ragas: "ragas_answer_relevancy",
  },
  {
    label: "Answer relevance (embedding)",
    custom: "custom_answer_relevance_embedding",
    ragas: null,
  },
  { label: "Context precision", custom: "custom_context_precision", ragas: "ragas_context_precision" },
  { label: "Context recall", custom: "custom_context_recall", ragas: "ragas_context_recall" },
];

export function RunDetailView({ runId, onBack }: Props) {
  const [run, setRun] = useState<RunDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<number | null>(null);

  useEffect(() => {
    api
      .getRun(runId)
      .then(setRun)
      .catch((e) => setError(String(e)));
  }, [runId]);

  if (error) return <p className="error">{error}</p>;
  if (!run) return <p>Loading…</p>;

  return (
    <div>
      <button className="link" onClick={onBack}>
        ← Back to run history
      </button>
      <h2>
        {run.name} (#{run.id})
      </h2>
      <p className="meta">
        {run.source} · {new Date(run.created_at).toLocaleString()}
        {run.is_baseline && <span className="badge">baseline</span>}
      </p>

      {run.examples.map((ex) => (
        <div key={ex.id} className="example-card">
          <button
            className="example-header"
            onClick={() => setExpanded(expanded === ex.id ? null : ex.id)}
          >
            <span>{expanded === ex.id ? "▾" : "▸"}</span> {ex.question}
          </button>

          <table className="metric-table">
            <thead>
              <tr>
                <th>Metric</th>
                <th>Custom</th>
                <th>RAGAS</th>
              </tr>
            </thead>
            <tbody>
              {METRIC_ROWS.map((row) => (
                <tr key={row.label}>
                  <td>{row.label}</td>
                  <td>{formatScore(ex[row.custom] as number | null)}</td>
                  <td>{row.ragas ? formatScore(ex[row.ragas] as number | null) : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {expanded === ex.id && (
            <div className="example-body">
              <p>
                <strong>Answer:</strong> {ex.answer}
              </p>
              {ex.ground_truth && (
                <p>
                  <strong>Ground truth:</strong> {ex.ground_truth}
                </p>
              )}
              <p>
                <strong>Contexts:</strong>
              </p>
              <ul>
                {ex.contexts.map((c, i) => (
                  <li key={i}>{c}</li>
                ))}
              </ul>
              <details>
                <summary>Raw judge details</summary>
                <pre>{JSON.stringify(ex.details, null, 2)}</pre>
              </details>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
