import { useState } from "react";
import { api } from "../api";
import {
  Button, Card, Label, CodeBlock,
  SeverityBadge, ConfidenceBar, ErrorBox,
} from "../components";
import "./DebugPage.css";

const EXAMPLE_LOGS = [
  {
    label: "OOM kill",
    log: "OOMKilled: container exceeded memory limit of 512Mi\nKilled process 1234 total-vm:1024000kB",
  },
  {
    label: "Port conflict",
    log: "Error starting userland proxy: listen tcp 0.0.0.0:8000: bind: address already in use",
  },
  {
    label: "Connection refused",
    log: "dial tcp 127.0.0.1:5432: connect: connection refused\nFailed to connect to database after 3 retries",
  },
  {
    label: "Permission denied",
    log: "open /var/run/docker.sock: permission denied\nError response from daemon: permission denied",
  },
  {
    label: "Missing env var",
    log: "KeyError: 'DATABASE_URL'\nTraceback (most recent call last):\n  File 'app/db.py', line 12",
  },
  {
    label: "Disk full",
    log: "write /var/lib/docker/overlay2/abc123/diff/tmp: no space left on device",
  },
  {
    label: "SSL error",
    log: "ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate",
  },
  {
    label: "Exit code 1",
    log: "container exited with code 1\nModuleNotFoundError: No module named 'uvicorn'",
  },
];

export default function DebugPage() {
  const [logText, setLogText]         = useState("");
  const [containerName, setContainer] = useState("");
  const [result, setResult]           = useState(null);
  const [loading, setLoading]         = useState(false);
  const [error, setError]             = useState(null);

  const submit = async () => {
    if (!logText.trim()) return;
    setLoading(true);
    setError(null);
    try {
      setResult(await api.debug({ log_text: logText, container_name: containerName || undefined }));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="page-title">
        <h1>🔍 Log Debugger</h1>
        <p className="muted">
          Paste raw Docker logs and get instant root cause analysis,
          severity rating, fix suggestions, and ready-to-run commands.
        </p>
      </div>

      <div className="debug-layout">
        {/* ── Input panel ────────────────────────────────────────────────── */}
        <div className="input-col">
          <Card>
            <div className="form-group">
              <Label>Container name (optional)</Label>
              <input
                className="field-input"
                value={containerName}
                onChange={(e) => setContainer(e.target.value)}
                placeholder="my-api"
              />
            </div>

            <div className="form-group" style={{ marginTop: 16 }}>
              <Label>Docker log output</Label>
              <textarea
                className="log-textarea"
                value={logText}
                onChange={(e) => setLogText(e.target.value)}
                placeholder="Paste your Docker logs here…&#10;&#10;e.g.&#10;OOMKilled: container exceeded memory limit&#10;Error: listen EADDRINUSE :::3000"
                rows={10}
              />
            </div>

            <ErrorBox message={error} />

            <div className="form-actions">
              <Button loading={loading} disabled={!logText.trim()} onClick={submit}>
                Analyse Logs
              </Button>
              {logText && (
                <Button variant="ghost" onClick={() => { setLogText(""); setResult(null); }}>
                  Clear
                </Button>
              )}
            </div>
          </Card>

          {/* Example logs */}
          <Card>
            <h3 className="section-heading">Try an example</h3>
            <div className="examples-grid">
              {EXAMPLE_LOGS.map((ex) => (
                <button
                  key={ex.label}
                  className="example-btn"
                  onClick={() => { setLogText(ex.log); setResult(null); }}
                >
                  {ex.label}
                </button>
              ))}
            </div>
          </Card>
        </div>

        {/* ── Result panel ───────────────────────────────────────────────── */}
        {result && (
          <div className="result-col">

            {/* Header */}
            <Card className="result-header-card">
              <div className="result-header">
                <div>
                  <div className="field-label">Root cause</div>
                  <div className="root-cause-title">{result.root_cause}</div>
                </div>
                <SeverityBadge severity={result.severity} />
              </div>
              <div style={{ marginTop: 14 }}>
                <div className="field-label" style={{ marginBottom: 6 }}>Confidence</div>
                <ConfidenceBar value={result.confidence} />
              </div>
            </Card>

            {/* Fix suggestion */}
            <Card>
              <h3 className="section-heading">Fix suggestion</h3>
              <p className="fix-text">{result.fix_suggestion}</p>
            </Card>

            {/* Explanation */}
            <Card>
              <h3 className="section-heading">Why this happens</h3>
              <p className="explanation-text">{result.explanation}</p>
            </Card>

            {/* Commands */}
            <Card>
              <h3 className="section-heading">Commands to run</h3>
              <div className="commands-list">
                {result.commands.map((cmd, i) => (
                  cmd.startsWith("#")
                    ? <p key={i} className="cmd-comment">{cmd}</p>
                    : <CodeBlock key={i} code={cmd} language="bash" />
                ))}
              </div>
            </Card>

            {/* Prevention tip */}
            <Card className="tip-card">
              <span className="tip-icon">💡</span>
              <div>
                <div className="field-label" style={{ marginBottom: 4 }}>Prevention tip</div>
                <p className="tip-text">{result.prevention_tip}</p>
              </div>
            </Card>

          </div>
        )}
      </div>
    </div>
  );
}
