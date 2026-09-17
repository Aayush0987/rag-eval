import { useEffect, useState } from "react";
import { api, type RunSummary } from "../api";

interface Props {
  onSelectRun: (id: number) => void;
  refreshKey: number;
}

export function RunHistory({ onSelectRun, refreshKey }: Props) {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);

  useEffect(() => {
    api
      .listRuns()
      .then(setRuns)
      .catch((e) => setError(String(e)));
  }, [refreshKey]);

  async function handleMarkBaseline(id: number) {
    setBusyId(id);
    try {
      await api.markBaseline(id);
      setRuns(await api.listRuns());
    } catch (e) {
      setError(String(e));
    } finally {
      setBusyId(null);
    }
  }

  if (error) return <p className="error">{error}</p>;

  return (
    <table className="run-table">
      <thead>
        <tr>
          <th>Run</th>
          <th>Created</th>
          <th>Source</th>
          <th># Examples</th>
          <th>Custom Faithfulness</th>
          <th>RAGAS Faithfulness</th>
          <th>Baseline</th>
        </tr>
      </thead>
      <tbody>
        {runs.map((run) => (
          <tr key={run.id}>
            <td>
              <button className="link" onClick={() => onSelectRun(run.id)}>
                {run.name} (#{run.id})
              </button>
            </td>
            <td>{new Date(run.created_at).toLocaleString()}</td>
            <td>{run.source}</td>
            <td>{run.num_examples}</td>
            <td>{formatScore(run.avg_custom_faithfulness)}</td>
            <td>{formatScore(run.avg_ragas_faithfulness)}</td>
            <td>
              {run.is_baseline ? (
                <span className="badge">baseline</span>
              ) : (
                <button
                  disabled={busyId === run.id}
                  onClick={() => handleMarkBaseline(run.id)}
                >
                  Mark baseline
                </button>
              )}
            </td>
          </tr>
        ))}
        {runs.length === 0 && (
          <tr>
            <td colSpan={7} className="empty">
              No runs yet. Submit one via the Upload tab.
            </td>
          </tr>
        )}
      </tbody>
    </table>
  );
}

export function formatScore(value: number | null): string {
  return value === null ? "—" : value.toFixed(2);
}
