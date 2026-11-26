"""
Unit and Integration Tests for Phase 13: Docker Containerization & Network Isolation
Verifies compose syntax, service definitions, network isolation boundaries,
and zero-host-port exposure for protected upstream services.
"""

import pathlib
import pytest
import yaml

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
COMPOSE_FILE = ROOT_DIR / "docker-compose.yml"
REQUIREMENTS_FILE = ROOT_DIR / "requirements.txt"


def test_requirements_file_validity():
    """FR-08: Ensure requirements.txt exists and contains all production dependencies."""
    assert REQUIREMENTS_FILE.is_file(), "requirements.txt must exist at project root."
    content = REQUIREMENTS_FILE.read_text(encoding="utf-8")
    
    core_packages = [
        "fastapi",
        "uvicorn",
        "streamlit",
        "torch",
        "xgboost",
        "scikit-learn",
        "shap",
        "lime",
        "scipy",
        "pandas"
    ]
    for pkg in core_packages:
        assert pkg in content, f"Dependency '{pkg}' must be pinned in requirements.txt"


def test_docker_compose_yaml_syntax():
    """Verify docker-compose.yml parses as valid YAML."""
    assert COMPOSE_FILE.is_file(), "docker-compose.yml must exist at project root."
    with open(COMPOSE_FILE, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    assert isinstance(config, dict), "docker-compose.yml must parse to a dictionary."
    assert "services" in config, "Compose file must define 'services'."
    assert "networks" in config, "Compose file must define 'networks'."
    assert "volumes" in config, "Compose file must define 'volumes'."


def test_services_and_dockerfiles_exist():
    """Verify all 4 core services are declared and their Dockerfiles exist on disk."""
    with open(COMPOSE_FILE, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        
    services = config["services"]
    expected_services = ["waf_service", "protected_app", "nginx_proxy", "waf_dashboard"]
    for svc in expected_services:
        assert svc in services, f"Service '{svc}' must be declared in docker-compose.yml"
        
        # Verify dockerfile path exists
        build_info = services[svc].get("build", {})
        dockerfile_rel = build_info.get("dockerfile")
        assert dockerfile_rel, f"Service '{svc}' must define a dockerfile"
        dockerfile_path = ROOT_DIR / dockerfile_rel
        assert dockerfile_path.is_file(), f"Dockerfile {dockerfile_path} must exist on disk"
        
        # Verify basic Dockerfile structure
        df_content = dockerfile_path.read_text(encoding="utf-8")
        assert "FROM " in df_content, f"Dockerfile for {svc} must have a FROM directive"


def test_origin_isolation_no_host_port_for_protected_app():
    """
    CRITICAL SECURITY TEST:
    The protected backend ('protected_app') must NOT expose any ports to the host.
    Public traffic must be physically incapable of bypassing the WAF reverse proxy.
    """
    with open(COMPOSE_FILE, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        
    services = config["services"]
    protected = services["protected_app"]
    
    # Assert 'ports' is either not present or empty
    assert "ports" not in protected or not protected["ports"], (
        "SECURITY VIOLATION: protected_app must NOT expose host ports! "
        "It must remain strictly isolated behind the WAF."
    )
    
    # Verify waf_service is also internal-only
    waf_svc = services["waf_service"]
    assert "ports" not in waf_svc or not waf_svc["ports"], (
        "SECURITY VIOLATION: waf_service must NOT expose host ports! "
        "It must be queried strictly internally by the reverse proxy."
    )


def test_network_isolation_topology():
    """
    Verify dual-network topology:
    - protected_app and waf_service reside solely on waf_internal
    - nginx_proxy bridges waf_public and waf_internal
    - waf_dashboard bridges waf_public and waf_internal
    """
    with open(COMPOSE_FILE, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        
    networks = config["networks"]
    assert "waf_public" in networks, "waf_public network must be declared"
    assert "waf_internal" in networks, "waf_internal network must be declared"
    
    services = config["services"]
    
    # protected_app isolation
    protected_nets = services["protected_app"].get("networks", [])
    assert "waf_internal" in protected_nets, "protected_app must join waf_internal"
    assert "waf_public" not in protected_nets, "protected_app MUST NOT join waf_public"
    
    # waf_service isolation
    waf_nets = services["waf_service"].get("networks", [])
    assert "waf_internal" in waf_nets, "waf_service must join waf_internal"
    assert "waf_public" not in waf_nets, "waf_service MUST NOT join waf_public"
    
    # nginx_proxy bridging
    proxy_nets = services["nginx_proxy"].get("networks", [])
    assert "waf_public" in proxy_nets, "nginx_proxy must join waf_public"
    assert "waf_internal" in proxy_nets, "nginx_proxy must join waf_internal"
    
    # waf_dashboard bridging
    dash_nets = services["waf_dashboard"].get("networks", [])
    assert "waf_public" in dash_nets, "waf_dashboard must join waf_public"
    assert "waf_internal" in dash_nets, "waf_dashboard must join waf_internal"


def test_service_dependencies_and_healthchecks():
    """Verify healthcheck definitions and startup ordering."""
    with open(COMPOSE_FILE, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        
    services = config["services"]
    
    # Nginx must wait for WAF and Target App
    nginx_deps = services["nginx_proxy"].get("depends_on", {})
    assert "waf_service" in nginx_deps, "nginx_proxy must depend on waf_service"
    assert "protected_app" in nginx_deps, "nginx_proxy must depend on protected_app"
    
    # Dashboard must wait for WAF
    dash_deps = services["waf_dashboard"].get("depends_on", {})
    assert "waf_service" in dash_deps, "waf_dashboard must depend on waf_service"
    
    # Healthchecks must be present
    for svc_name in ["waf_service", "protected_app", "nginx_proxy", "waf_dashboard"]:
        svc = services[svc_name]
        # Has either compose healthcheck or Dockerfile healthcheck
        df_path = ROOT_DIR / svc["build"]["dockerfile"]
        has_compose_hc = "healthcheck" in svc
        has_df_hc = "HEALTHCHECK" in df_path.read_text(encoding="utf-8")
        assert has_compose_hc or has_df_hc, f"Service {svc_name} must have a healthcheck"
