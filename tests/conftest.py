"""Pytest configuration using ONLY real data.

No mocks. All fixtures are produced by running the actual AURA engines
on a real, small, version-controlled Python application that we create
with real git history at test time.
"""
import os
import sys
import tempfile
import subprocess
import shutil
from pathlib import Path
from dataclasses import asdict

# Make aura importable
AURA_ROOT = Path(__file__).parent.parent / "aura"
if str(AURA_ROOT) not in sys.path:
    sys.path.insert(0, str(AURA_ROOT))

import pytest

from workspace_scanner import WorkspaceScanner, ProjectScanResult
from ast_static_engine import build_dependency_matrix
from chronos_git_engine import extract_git_commits, calculate_temporal_coupling
from core.evidence_engine import EvidenceEngine
from core.risk_engine import RiskEngine
from core.subsystem_engine import SubsystemEngine
from core.architecture_intelligence import ArchitectureIntelligence


FIXTURE_SRC = Path(__file__).parent / "fixtures" / "mini_real_app"


def _copy_tree(src: Path, dst: Path):
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def _init_real_git_history(repo_path: Path):
    """Create a real git repository with multiple commits that produce
    genuine temporal coupling data (no mocks).
    """
    env = {**os.environ, "GIT_AUTHOR_NAME": "AURA Test", "GIT_AUTHOR_EMAIL": "test@aura.local",
           "GIT_COMMITTER_NAME": "AURA Test", "GIT_COMMITTER_EMAIL": "test@aura.local"}

    subprocess.check_call(["git", "init"], cwd=repo_path, env=env)
    subprocess.check_call(["git", "config", "user.name", "AURA Test"], cwd=repo_path, env=env)
    subprocess.check_call(["git", "config", "user.email", "test@aura.local"], cwd=repo_path, env=env)

    # Commit 1: core foundation (main + database + models)
    subprocess.check_call(["git", "add", "main.py", "database.py", "models/"], cwd=repo_path, env=env)
    subprocess.check_call(["git", "commit", "-m", "Initial core: main, database and user model"], cwd=repo_path, env=env)

    # Commit 2: authentication layer (touches database + new auth)
    subprocess.check_call(["git", "add", "auth.py"], cwd=repo_path, env=env)
    subprocess.check_call(["git", "commit", "-m", "Add real auth service with database dependency"], cwd=repo_path, env=env)

    # Commit 3: API surface + payment (cross-cutting)
    subprocess.check_call(["git", "add", "api/", "services/"], cwd=repo_path, env=env)
    subprocess.check_call(["git", "commit", "-m", "Expose API routes and payment service (couples auth + db)"], cwd=repo_path, env=env)

    # Commit 4: small change to auth + database together (strong temporal signal)
    with open(repo_path / "auth.py", "a", encoding="utf-8") as f:
        f.write("\n# Minor security tweak\n")
    with open(repo_path / "database.py", "a", encoding="utf-8") as f:
        f.write("\n# Added index helper\n")
    subprocess.check_call(["git", "add", "auth.py", "database.py"], cwd=repo_path, env=env)
    subprocess.check_call(["git", "commit", "-m", "Security tweak + db helper (real co-change)"], cwd=repo_path, env=env)


@pytest.fixture(scope="session")
def real_repo_path(tmp_path_factory):
    """A real temporary checkout of the mini_real_app with genuine git history."""
    base = tmp_path_factory.mktemp("real_aura_test_repo")
    repo_path = base / "mini_real_app"
    _copy_tree(FIXTURE_SRC, repo_path)
    _init_real_git_history(repo_path)
    return str(repo_path)


@pytest.fixture(scope="session")
def real_scan_result(real_repo_path):
    """Real ProjectScanResult from WorkspaceScanner on real source."""
    scanner = WorkspaceScanner(real_repo_path)
    return scanner.scan()


@pytest.fixture(scope="session")
def real_file_contents(real_repo_path):
    """Dict of {rel_path: source_code} for real static analysis."""
    contents = {}
    for py_file in Path(real_repo_path).rglob("*.py"):
        rel = py_file.relative_to(real_repo_path).as_posix()
        contents[rel] = py_file.read_text(encoding="utf-8", errors="ignore")
    return contents


@pytest.fixture(scope="session")
def real_static_matrix(real_file_contents):
    """Real static dependency matrix produced by the actual AST engine."""
    return build_dependency_matrix(real_file_contents)


@pytest.fixture(scope="session")
def real_temporal_matrix(real_repo_path):
    """Real temporal coupling matrix from actual git log (no synthetic data)."""
    commits = extract_git_commits(real_repo_path)
    if not commits:
        return {}
    return calculate_temporal_coupling(commits)


@pytest.fixture(scope="session")
def real_evidence_engine(real_scan_result, real_static_matrix, real_temporal_matrix, real_repo_path):
    """Fully real EvidenceEngine built from real scan + real matrices + real git history."""
    engine = EvidenceEngine(
        scan_result=real_scan_result,
        static_matrix=real_static_matrix,
        temporal_matrix=real_temporal_matrix,
        repo_path=real_repo_path,
        is_demo=False  # Full real mode
    )
    return engine


@pytest.fixture(scope="session")
def real_risk_engine(real_evidence_engine):
    """Real RiskEngine running on the real evidence."""
    return RiskEngine(real_evidence_engine)


@pytest.fixture(scope="session")
def real_subsystem_engine(real_evidence_engine, real_static_matrix, real_scan_result):
    return SubsystemEngine(
        real_evidence_engine.file_facts,
        real_static_matrix,
        real_scan_result
    )


@pytest.fixture(scope="session")
def real_session_data(real_scan_result, real_static_matrix, real_temporal_matrix,
                      real_evidence_engine, real_risk_engine, real_subsystem_engine, real_repo_path):
    """Complete real session_data dict exactly as the server would build it."""
    risks_list = real_risk_engine.detect_risks()

    session = {
        "scan_result": real_scan_result,
        "file_facts": real_evidence_engine.file_facts,   # Real enriched facts
        "static_matrix": real_static_matrix,
        "temporal_matrix": real_temporal_matrix,
        "risks_list": risks_list,
        "evidence_records": real_evidence_engine.evidence_records,
        "health_scores": real_evidence_engine.calculate_health_scores(),
        "subsystem_assignments": real_subsystem_engine.file_assignments,
        "subsystem_summary": real_subsystem_engine.get_subsystem_summary(),
        "confidence": real_evidence_engine.confidence,
        "repo_path": real_repo_path,
        "is_demo": False,
    }
    return session


@pytest.fixture(scope="session")
def real_ai(real_session_data):
    """Fully initialized ArchitectureIntelligence with 100% real data."""
    return ArchitectureIntelligence(real_session_data)


# Convenience fixtures for individual tests
@pytest.fixture
def real_file_facts(real_session_data):
    return real_session_data["file_facts"]


@pytest.fixture
def real_risks(real_session_data):
    return real_session_data["risks_list"]
