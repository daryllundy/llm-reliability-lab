import yaml
import os


def load_yaml(filepath):
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)

def test_docker_compose_services():
    compose = load_yaml("docker-compose.yml")
    services = compose.get("services", {})
    
    assert "prometheus" in services
    assert "grafana" in services
    
    # Check Prometheus config
    prom = services["prometheus"]
    assert prom["image"] == "prom/prometheus:latest"
    assert "9090:9090" in prom["ports"]
    assert "healthcheck" in prom
    
    # Check Grafana config
    grafana = services["grafana"]
    assert grafana["image"] == "grafana/grafana:latest"
    assert "3000:3000" in grafana["ports"]
    assert "healthcheck" in grafana
    assert "prometheus" in grafana["depends_on"]

def test_prometheus_config_exists():
    assert os.path.exists("prometheus/prometheus.yml")
    config = load_yaml("prometheus/prometheus.yml")
    
    scrape_configs = config.get("scrape_configs", [])
    job_names = [job["job_name"] for job in scrape_configs]
    
    assert "llm-api" in job_names
    assert "prometheus" in job_names

def test_grafana_provisioning_exists():
    assert os.path.exists("grafana/provisioning/datasources/datasource.yml")
    assert os.path.exists("grafana/provisioning/dashboards/dashboard.yml")
    
    # Check datasource config
    ds_config = load_yaml("grafana/provisioning/datasources/datasource.yml")
    datasources = ds_config.get("datasources", [])
    assert any(ds["name"] == "Prometheus" for ds in datasources)
    
    # Check dashboard config
    dash_config = load_yaml("grafana/provisioning/dashboards/dashboard.yml")
    providers = dash_config.get("providers", [])
    assert any(p["name"] == "Default" for p in providers)
