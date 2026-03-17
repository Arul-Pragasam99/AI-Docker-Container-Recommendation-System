import { useState } from "react";
import { api } from "../api";
import {
  Button, Card, Label, CodeBlock,
  Badge, ConfidenceBar, ErrorBox,
  Select, NumberInput, Toggle,
} from "../components";
import "./RecommendPage.css";

const PROJECT_TYPES = [
  "fastapi", "django", "flask",
  "node", "react", "nextjs",
  "ml", "postgres", "redis",
  "nginx", "go", "rust",
];

const LOAD_PRESETS = [
  { label: "< 500",   value: 200    },
  { label: "1–5k",    value: 2000   },
  { label: "5–25k",   value: 10000  },
  { label: "25–100k", value: 50000  },
  { label: "100k+",   value: 200000 },
];

export default function RecommendPage() {
  const [form, setForm] = useState({
    project_type: "fastapi",
    expected_users: 10000,
    has_gpu: false,
  });
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  const submit = async () => {
    setLoading(true);
    setError(null);
    try {
      setResult(await api.recommend(form));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="page-title">
        <h1>Image Recommender</h1>
        <p className="muted">
          Describe your project and expected load to get the optimal base image,
          Dockerfile, and runtime configuration.
        </p>
      </div>

      <div className="recommend-layout">
        <Card className="form-card">
          <div className="form-group">
            <Label>Project type</Label>
            <Select
              value={form.project_type}
              onChange={(v) => setForm({ ...form, project_type: v })}
              options={PROJECT_TYPES}
            />
          </div>

          <div className="form-group">
            <Label>Expected concurrent users</Label>
            <NumberInput
              value={form.expected_users}
              onChange={(v) => setForm({ ...form, expected_users: v })}
              min={1}
              placeholder="e.g. 10000"
            />
            <div className="presets">
              {LOAD_PRESETS.map((p) => (
                <button
                  key={p.value}
                  className={`preset-btn${form.expected_users === p.value ? " active" : ""}`}
                  onClick={() => setForm({ ...form, expected_users: p.value })}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          <div className="form-group">
            <Toggle
              checked={form.has_gpu}
              onChange={(v) => setForm({ ...form, has_gpu: v })}
              label="GPU workload (ML / CUDA)"
            />
          </div>

          <ErrorBox message={error} />

          <Button loading={loading} onClick={submit}>
            Get Recommendation
          </Button>
        </Card>

        {result && (
          <div className="result-col">
            <div className="result-summary">
              <div className="summary-item">
                <span className="field-label">Base image</span>
                <span className="summary-value mono">{result.base_image}</span>
              </div>
              <div className="summary-item">
                <span className="field-label">Memory</span>
                <span className="summary-value mono">{result.runtime_params.memory}</span>
              </div>
              <div className="summary-item">
                <span className="field-label">CPUs</span>
                <span className="summary-value mono">{result.runtime_params.cpus}</span>
              </div>
              <div className="summary-item">
                <span className="field-label">Confidence</span>
                <ConfidenceBar value={result.confidence} />
              </div>
            </div>

            <Card>
              <h3 className="section-heading">Runtime parameters</h3>
              <div className="param-grid">
                <div className="param-row">
                  <span className="muted">Restart policy</span>
                  <Badge color="default">{result.runtime_params.restart_policy}</Badge>
                </div>
                {result.runtime_params.env_vars.map((v) => (
                  <div className="param-row" key={v}>
                    <span className="muted">Env var</span>
                    <code className="mono">{v}</code>
                  </div>
                ))}
                {result.runtime_params.extra_flags.map((f) => (
                  <div className="param-row" key={f}>
                    <span className="muted">Flag</span>
                    <code className="mono">{f}</code>
                  </div>
                ))}
              </div>
            </Card>

            <Card>
              <h3 className="section-heading">docker run command</h3>
              <CodeBlock code={result.docker_run_command} language="bash" />
            </Card>

            <Card>
              <h3 className="section-heading">Dockerfile</h3>
              <CodeBlock code={result.dockerfile_snippet} language="dockerfile" />
            </Card>

            <Card>
              <h3 className="section-heading">Reasoning</h3>
              <p className="reasoning-text">{result.reasoning}</p>
              {result.alternatives.length > 0 && (
                <div className="alternatives">
                  <span className="field-label">Alternatives</span>
                  {result.alternatives.map((a) => (
                    <code key={a} className="alt-tag mono">{a}</code>
                  ))}
                </div>
              )}
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}