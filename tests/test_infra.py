import json
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path):
    with path.open() as f:
        return yaml.safe_load(f)


def test_docker_compose_wires_native_ollama_by_default():
    compose = load_yaml(ROOT / "docker-compose.yml")
    services = compose["services"]

    assert {"api", "prometheus", "grafana", "llm"} <= set(services)
    assert services["llm"]["profiles"] == ["docker-ollama"]
    assert "depends_on" not in services["api"]
    assert "MODEL_NAME=${MODEL_NAME:-smollm}" in services["api"]["environment"]
    assert (
        "OLLAMA_URL=${OLLAMA_URL:-http://host.docker.internal:11434/api/generate}"
        in services["api"]["environment"]
    )


def test_grafana_uses_local_default_password_override():
    compose = load_yaml(ROOT / "docker-compose.yml")
    grafana_env = compose["services"]["grafana"]["environment"]

    assert "GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-admin}" in grafana_env


def test_prometheus_scrapes_api_and_prometheus():
    config = load_yaml(ROOT / "prometheus/prometheus.yml")
    job_names = {job["job_name"] for job in config["scrape_configs"]}

    assert {"llm-api", "prometheus"} <= job_names


def test_grafana_dashboard_contains_latency_panels():
    dashboard = json.loads((ROOT / "dashboards/grafana.json").read_text())
    dashboard_text = json.dumps(dashboard)

    assert "histogram_quantile(0.95" in dashboard_text
    assert "histogram_quantile(0.99" in dashboard_text
    assert "llm_request_latency_seconds_bucket" in dashboard_text


def test_chaos_import_has_no_side_effects():
    result = subprocess.run(
        [sys.executable, "-c", "import chaos; print('imported')"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=2,
        check=True,
    )

    assert result.stdout.strip() == "imported"
