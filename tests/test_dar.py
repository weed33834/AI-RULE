"""DAR (Domain Authority Registry) structure validation tests.

Validates:
- dar-spec.md exists with required sections
- 6 domain configs exist and are valid YAML
- Each config has required modules (source_registry, scoring_protocol, etc.)
- Scoring weights sum to 1.0
- Freshness tables have >=3 entries
- Routing rules have >=3 rules
- Domain knowledge has terminology, conventions, pitfalls
- All manifests enable dar capability
- Spec defines integration points
"""

import os
import pytest

try:
    import yaml
except ImportError:
    pytest.skip("pyyaml not installed", allow_module_level=True)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAR_DIR = os.path.join(REPO_ROOT, "capabilities", "dar")
SPEC_FILE = os.path.join(REPO_ROOT, "core", "dar-spec.md")
MANIFEST_DIR = os.path.join(REPO_ROOT, "manifests")

DOMAINS = ["paper", "coding", "conversation", "novel", "interactive-novel", "agent-builder"]


def _load_yaml(domain):
    path = os.path.join(DAR_DIR, f"dar-{domain}.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# --- Spec tests ---

def test_dar_spec_exists():
    assert os.path.isfile(SPEC_FILE), "core/dar-spec.md must exist"


def test_dar_spec_integration_points():
    with open(SPEC_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    assert "deep-search" in content.lower()
    assert "truth-protocol" in content.lower()
    assert "source-credibility" in content.lower()
    assert "profile-router" in content.lower()


# --- Config existence ---

def test_dar_configs_exist():
    for domain in DOMAINS:
        path = os.path.join(DAR_DIR, f"dar-{domain}.yaml")
        assert os.path.isfile(path), f"dar-{domain}.yaml must exist"


def test_dar_configs_valid_yaml():
    for domain in DOMAINS:
        data = _load_yaml(domain)
        assert isinstance(data, dict), f"dar-{domain}.yaml must be a valid YAML dict"


# --- Source registry ---

def test_dar_source_registry():
    for domain in DOMAINS:
        data = _load_yaml(domain)
        sr = data.get("source_registry", {})
        assert "T1" in sr, f"{domain}: source_registry must have T1"
        assert len(sr["T1"]) >= 5, f"{domain}: T1 must have >=5 sources"


# --- Scoring weights ---

def test_dar_scoring_weights():
    for domain in DOMAINS:
        data = _load_yaml(domain)
        sp = data.get("scoring_protocol", {})
        weights = sp.get("weights", {})
        total = (
            weights.get("relevance", 0)
            + weights.get("credibility", 0)
            + weights.get("freshness", 0)
            + weights.get("consensus", 0)
        )
        assert abs(total - 1.0) < 0.01, f"{domain}: weights must sum to 1.0, got {total}"


# --- Freshness table ---

def test_dar_freshness_table():
    for domain in DOMAINS:
        data = _load_yaml(domain)
        ft = data.get("freshness_table", [])
        assert len(ft) >= 3, f"{domain}: freshness_table must have >=3 entries"


# --- Routing rules ---

def test_dar_routing_rules():
    for domain in DOMAINS:
        data = _load_yaml(domain)
        rr = data.get("routing_rules", [])
        assert len(rr) >= 3, f"{domain}: routing_rules must have >=3 rules"
        for rule in rr:
            assert "trigger" in rule
            assert "priority_sources" in rule


# --- Domain knowledge ---

def test_dar_domain_knowledge():
    for domain in DOMAINS:
        data = _load_yaml(domain)
        dk = data.get("domain_knowledge", {})
        assert len(dk.get("terminology", [])) >= 5, f"{domain}: terminology must have >=5 entries"
        assert len(dk.get("conventions", [])) >= 2, f"{domain}: conventions must have >=2 entries"
        assert len(dk.get("common_pitfalls", [])) >= 2, f"{domain}: common_pitfalls must have >=2 entries"


# --- Conflict policy ---

def test_dar_conflict_policy():
    for domain in DOMAINS:
        data = _load_yaml(domain)
        cp = data.get("conflict_policy", {})
        assert isinstance(cp, dict), f"{domain}: conflict_policy must be a dict"
        assert len(cp) >= 2, f"{domain}: conflict_policy must have >=2 keys"


# --- Manifests enable dar ---

def test_manifests_enable_dar():
    for domain in DOMAINS:
        path = os.path.join(MANIFEST_DIR, f"{domain}.yaml")
        with open(path, "r", encoding="utf-8") as f:
            manifest = yaml.safe_load(f)
        caps = manifest.get("enables_capabilities", [])
        assert "dar" in caps, f"manifests/{domain}.yaml must enable 'dar' capability"
