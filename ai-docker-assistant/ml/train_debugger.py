import pickle
import pathlib
from typing import List, Tuple, cast, Any

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report

TRAINING_DATA: List[Tuple[str, str]] = [

    ("OOMKilled: container exceeded memory limit", "Out of Memory (OOM)"),
    ("fatal error: runtime: out of memory", "Out of Memory (OOM)"),
    ("Killed process 12345 (python) total-vm:2048MB", "Out of Memory (OOM)"),
    ("Container memory limit exceeded: 512Mi", "Out of Memory (OOM)"),
    ("java.lang.OutOfMemoryError: Java heap space", "Out of Memory (OOM)"),
    ("Cannot allocate memory in static TLS block", "Out of Memory (OOM)"),
    ("malloc failed: out of memory", "Out of Memory (OOM)"),
    ("oom-kill event in memory cgroup", "Out of Memory (OOM)"),

    ("Error: listen EADDRINUSE :::3000", "Port conflict"),
    ("bind: address already in use", "Port conflict"),
    ("port 8080 is already in use", "Port conflict"),
    ("Error starting userland proxy: listen tcp 0.0.0.0:80: bind: address already in use", "Port conflict"),
    ("Bind for 0.0.0.0:5432 failed: port is already allocated", "Port conflict"),
    ("address already in use: 127.0.0.1:6379", "Port conflict"),

    ("permission denied: /var/run/docker.sock", "Permission denied"),
    ("open /app/config.yaml: permission denied", "Permission denied"),
    ("EACCES: permission denied, open '/etc/ssl/private/key.pem'", "Permission denied"),
    ("Operation not permitted: cannot read /proc/sys/kernel", "Permission denied"),
    ("error: cannot open /dev/net/tun: Permission denied", "Permission denied"),
    ("failed to bind port 80: permission denied (privileged port)", "Permission denied"),

    ("dial tcp 127.0.0.1:5432: connect: connection refused", "Connection refused / network error"),
    ("Error: connect ECONNREFUSED 127.0.0.1:6379", "Connection refused / network error"),
    ("connection to database failed: connection refused", "Connection refused / network error"),
    ("could not connect to server: Connection refused at localhost:5432", "Connection refused / network error"),
    ("no route to host: 10.0.0.5:3306", "Connection refused / network error"),
    ("failed to connect to redis: connection refused", "Connection refused / network error"),

    ("Error response from daemon: pull access denied for myapp", "Image not found"),
    ("manifest for myimage:latest not found: manifest unknown", "Image not found"),
    ("Error: No such image: python:3.99", "Image not found"),
    ("repository does not exist or may require 'docker login'", "Image not found"),
    ("Unable to find image 'myapp:dev' locally", "Image not found"),
    ("error pulling image: 404 Not Found", "Image not found"),

    ("write /var/lib/docker/overlay2: no space left on device", "Disk full"),
    ("ENOSPC: no space left on device, write", "Disk full"),
    ("error creating overlay mount: no space left on device", "Disk full"),
    ("disk quota exceeded for /data", "Disk full"),
    ("failed to allocate directory watch: no space left on device", "Disk full"),

    ("KeyError: 'DATABASE_URL'", "Missing environment variable"),
    ("Environment variable DATABASE_URL is not set", "Missing environment variable"),
    ("Error: required environment variable SECRET_KEY is missing", "Missing environment variable"),
    ("Cannot read properties of undefined: process.env.API_KEY", "Missing environment variable"),
    ("RuntimeError: missing required config: REDIS_URL", "Missing environment variable"),

    ("container is unhealthy after 3 retries", "Health check failing"),
    ("healthcheck failed: curl: (7) Failed to connect to localhost", "Health check failing"),
    ("Health check timed out after 30s", "Health check failing"),
    ("starting... (health: starting)", "Health check failing"),
    ("Status: unhealthy", "Health check failing"),

    ("exited with code 1", "Container crash (non-zero exit code)"),
    ("exited with code 137", "Container crash (non-zero exit code)"),
    ("container died unexpectedly", "Container crash (non-zero exit code)"),
    ("Process killed with signal 9", "Container crash (non-zero exit code)"),
    ("non-zero exit (1) from container", "Container crash (non-zero exit code)"),
    ("Segmentation fault (core dumped)", "Container crash (non-zero exit code)"),

    ("SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed", "SSL / TLS certificate error"),
    ("x509: certificate has expired or is not yet valid", "SSL / TLS certificate error"),
    ("TLS handshake timeout", "SSL / TLS certificate error"),
    ("ssl.SSLCertVerificationError: certificate verify failed", "SSL / TLS certificate error"),
    ("Error: unable to verify the first certificate", "SSL / TLS certificate error"),

    ("context deadline exceeded (Client.Timeout exceeded)", "Timeout"),
    ("read timeout after 30s waiting for response", "Timeout"),
    ("database query timed out after 30000ms", "Timeout"),
    ("Error: Request timeout: 504 Gateway Timeout", "Timeout"),
    ("connection timed out: redis://redis:6379", "Timeout"),
]


def construct_pipeline_unit() -> Pipeline:
    return Pipeline([
        ("tfidf_block", TfidfVectorizer(
            ngram_range=(1, 3),
            min_df=1,
            max_features=10000,
            sublinear_tf=True
        )),
        ("classifier_block", LogisticRegression(
            max_iter=1000,
            C=5.0,
            class_weight="balanced",
            solver="lbfgs",
            multi_class="multinomial"
        ))
    ])


def execute_training_flow():
    text_samples = [a for a, _ in TRAINING_DATA]
    label_targets = [b for _, b in TRAINING_DATA]

    X_train_unit, X_test_unit, y_train_unit, y_test_unit = train_test_split(
        text_samples,
        label_targets,
        test_size=0.2,
        random_state=42,
        stratify=label_targets
    )

    pipeline_unit = construct_pipeline_unit()
    pipeline_unit.fit(X_train_unit, y_train_unit)

    prediction_unit = pipeline_unit.predict(X_test_unit)

    print("=" * 60)
    print("Debugger Model — Classification Report")
    print("=" * 60)
    print(classification_report(y_test_unit, prediction_unit))

    cv_result_unit = cross_val_score(
        pipeline_unit,
        cast(Any, text_samples),
        label_targets,
        cv=3,
        scoring="accuracy"
    )

    print(f"3-fold CV accuracy: {cv_result_unit.mean():.3f} ± {cv_result_unit.std():.3f}")

    output_path_unit = pathlib.Path("ml/debugger_model.pkl")
    output_path_unit.parent.mkdir(exist_ok=True)

    with open(output_path_unit, "wb") as file_unit:
        pickle.dump(pipeline_unit, file_unit)

    print(f"\nModel saved to {output_path_unit}")
    print("Set USE_ML_CLASSIFIER=true to activate it in the API.")


if __name__ == "__main__":
    execute_training_flow()