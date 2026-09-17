import { useState } from "react";
import "./App.css";
import { RunHistory } from "./components/RunHistory";
import { RunDetailView } from "./components/RunDetailView";
import { RegressionView } from "./components/RegressionView";
import { UploadForm } from "./components/UploadForm";

type Tab = "history" | "upload" | "regression";

function App() {
  const [tab, setTab] = useState<Tab>("history");
  const [selectedRunId, setSelectedRunId] = useState<number | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  function selectRun(id: number) {
    setSelectedRunId(id);
  }

  function backToHistory() {
    setSelectedRunId(null);
    setTab("history");
  }

  return (
    <div className="app">
      <header>
        <h1>RAG Eval</h1>
        <nav>
          <button
            className={tab === "history" ? "active" : ""}
            onClick={() => {
              setTab("history");
              setSelectedRunId(null);
            }}
          >
            Run History
          </button>
          <button className={tab === "upload" ? "active" : ""} onClick={() => setTab("upload")}>
            Submit Run
          </button>
          <button
            className={tab === "regression" ? "active" : ""}
            onClick={() => setTab("regression")}
          >
            Regression
          </button>
        </nav>
      </header>

      <main>
        {tab === "history" &&
          (selectedRunId === null ? (
            <RunHistory onSelectRun={selectRun} refreshKey={refreshKey} />
          ) : (
            <RunDetailView runId={selectedRunId} onBack={backToHistory} />
          ))}
        {tab === "upload" && (
          <UploadForm
            onSubmitted={() => {
              setRefreshKey((k) => k + 1);
              setTab("history");
            }}
          />
        )}
        {tab === "regression" && <RegressionView />}
      </main>
    </div>
  );
}

export default App;
