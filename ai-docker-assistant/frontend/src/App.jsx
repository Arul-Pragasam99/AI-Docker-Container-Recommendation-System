import { useState } from "react";
import RecommendPage from "./pages/RecommendPage";
import DebugPage from "./pages/DebugPage";
import "./App.css";

const TABS = [
  { id: "recommend", label: "Image Recommender", icon: "📦" },
  { id: "debug",     label: "Log Debugger",      icon: "🔍" },
];

export default function App() {
  const [tab, setTab] = useState("recommend");

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header-inner">
          <div className="app-logo">
            <span className="app-logo-icon">🐳</span>
            <div>
              <div className="app-logo-title">AI Docker Assistant</div>
              <div className="app-logo-sub">Intelligent container recommendations &amp; log debugging</div>
            </div>
          </div>
          <nav className="app-tabs">
            {TABS.map((t) => (
              <button
                key={t.id}
                className={`tab-btn${tab === t.id ? " active" : ""}`}
                onClick={() => setTab(t.id)}
              >
                <span>{t.icon}</span>
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
        <span className="muted">AI Docker Assistant · FastAPI + Scikit-learn + React</span>
      </footer>
    </div>
  );
}
