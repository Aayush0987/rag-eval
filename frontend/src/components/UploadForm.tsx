import { useState } from "react";
import { api } from "../api";

interface Props {
  onSubmitted: () => void;
}

export function UploadForm({ onSubmitted }: Props) {
  const [runName, setRunName] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [question, setQuestion] = useState("");
  const [contexts, setContexts] = useState("");
  const [answer, setAnswer] = useState("");
  const [groundTruth, setGroundTruth] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleBatchSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    setBusy(true);
    setStatus("Evaluating batch — this calls the LLM judge for every example, may take a while…");
    try {
      const run = await api.submitBatch(file, runName || "batch-run");
      setStatus(`Run #${run.id} created with ${run.num_examples} examples.`);
      onSubmitted();
    } catch (err) {
      setStatus(`Error: ${err}`);
    } finally {
      setBusy(false);
    }
  }

  async function handleSingleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setStatus("Evaluating…");
    try {
      const run = await api.submitSingle({
        question,
        contexts: contexts.split("\n").filter((c) => c.trim()),
        answer,
        ground_truth: groundTruth || undefined,
        run_name: runName || "single-example",
      });
      setStatus(`Run #${run.id} created.`);
      onSubmitted();
    } catch (err) {
      setStatus(`Error: ${err}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="upload-forms">
      <div className="form-card">
        <h3>Batch upload (JSONL)</h3>
        <form onSubmit={handleBatchSubmit}>
          <label>
            Run name
            <input value={runName} onChange={(e) => setRunName(e.target.value)} placeholder="batch-run" />
          </label>
          <label>
            JSONL file
            <input
              type="file"
              accept=".jsonl"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </label>
          <button type="submit" disabled={!file || busy}>
            Submit batch
          </button>
        </form>
      </div>

      <div className="form-card">
        <h3>Single example</h3>
        <form onSubmit={handleSingleSubmit}>
          <label>
            Question
            <textarea value={question} onChange={(e) => setQuestion(e.target.value)} required />
          </label>
          <label>
            Contexts (one per line)
            <textarea value={contexts} onChange={(e) => setContexts(e.target.value)} required />
          </label>
          <label>
            Answer
            <textarea value={answer} onChange={(e) => setAnswer(e.target.value)} required />
          </label>
          <label>
            Ground truth (optional)
            <textarea value={groundTruth} onChange={(e) => setGroundTruth(e.target.value)} />
          </label>
          <button type="submit" disabled={busy}>
            Submit example
          </button>
        </form>
      </div>

      {status && <p className="status">{status}</p>}
    </div>
  );
}
