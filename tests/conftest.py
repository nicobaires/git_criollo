import os
import shutil
import subprocess
import tempfile
from collections.abc import Generator

import pytest
from git import Repo

from git_criollo.git_service import GitService
from git_criollo.models import (
    BranchInfo, CommitInfo, StatusInfo, DiffHunk, ConflictRegion,
)


@pytest.fixture
def repo_path() -> Generator[str, None, None]:
    tmp = tempfile.mkdtemp()
    os.chdir(tmp)
    subprocess.run(["git", "init"], capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], capture_output=True)
    yield tmp
    os.chdir("/")
    shutil.rmtree(tmp)


@pytest.fixture
def repo_with_commits(repo_path: str) -> Generator[str, None, None]:
    for i in range(5):
        with open(f"f{i}.txt", "w") as f:
            f.write(f"contenido {i}")
        subprocess.run(["git", "add", f"f{i}.txt"], capture_output=True)
        subprocess.run(["git", "commit", "-m", f"commit {i}"], capture_output=True)
    yield repo_path


@pytest.fixture
def repo_with_branches(repo_with_commits: str) -> Generator[str, None, None]:
    subprocess.run(["git", "branch", "feature/a"], capture_output=True)
    subprocess.run(["git", "branch", "feature/x/y"], capture_output=True)
    subprocess.run(["git", "branch", "otra"], capture_output=True)
    subprocess.run(["git", "tag", "v1.0"], capture_output=True)
    yield repo_with_commits


@pytest.fixture
def gs(repo_with_branches: str) -> GitService:
    return GitService(repo_with_branches)


@pytest.fixture
def repo_detached(repo_with_commits: str) -> Generator[str, None, None]:
    subprocess.run(["git", "checkout", "--detach", "HEAD"], capture_output=True)
    yield repo_with_commits


@pytest.fixture
def gs_detached(repo_detached: str) -> GitService:
    return GitService(repo_detached)
