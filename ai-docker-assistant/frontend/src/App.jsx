import { useState } from "react";
import RecommendPage from "./pages/RecommendPage";
import DebugPage from "./pages/DebugPage";
import "./App.css";

const TABS = [
  { id: "recommend", label: "recommend" },
  { id: "debug",     label: "debug" },
];

export default function App() {
  const [tab, setTab] = useState("recommend");

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header-inner">
          <div>
            <div className="app-logo-title">AI Docker Assistant</div>
            <div className="app-logo-sub">container recommendations + log analysis</div>
          </div>
          <nav className="app-tabs">
            {TABS.map((t) => (
              <button
                key={t.id}
                className={`tab-btn${tab === t.id ? " active" : ""}`}
                onClick={() => setTab(t.id)}
              >
                {t.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <main className="app-main">
        {tab === "recommend" && <RecommendPage />}
        {tab === "debug"     && <DebugPage />}
      </main>

      <footer className="app-footer">
        AI Docker Assistant 
      </footer>
    </div>
  );
}