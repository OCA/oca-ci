from pathlib import Path
import subprocess

import pytest


@pytest.fixture(scope="module")
def repo_dir(tmp_path_factory) -> str:
    repo_path = tmp_path_factory.mktemp("repo")
    subprocess.check_call(["git", "init"], cwd=repo_path)
    subprocess.check_call(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
    )
    subprocess.check_call(
        ["git", "config", "user.name", "test"],
        cwd=repo_path,
    )
    (repo_path / "README").touch()
    subprocess.check_call(["git", "add", "."], cwd=repo_path)
    subprocess.check_call(["git", "commit", "-m", "initial commit"], cwd=repo_path)
    bare_repo_path = tmp_path_factory.mktemp("bare_repo")
    subprocess.check_call(
        ["git", "clone", "--bare", str(repo_path), str(bare_repo_path)]
    )
    return str(bare_repo_path)


@pytest.fixture()
def git_clone_path(repo_dir: str, tmp_path) -> Path:
    clone_path = tmp_path / "clone"
    subprocess.check_call(
        ["git", "clone", "--depth=1", "file://" + repo_dir, str(clone_path)]
    )
    subprocess.check_call(
        ["git", "config", "user.email", "test@example.com"],
        cwd=clone_path,
    )
    subprocess.check_call(
        ["git", "config", "user.name", "test"],
        cwd=clone_path,
    )
    return clone_path


def test_no_change(git_clone_path: Path):
    output = subprocess.check_output(
        ["oca_git_push_if_remote_did_not_change", "origin"],
        cwd=git_clone_path,
        text=True,
    )
    assert "No local change to push" in output


def test_local_change(git_clone_path: Path):
    (git_clone_path / "local-change-1").touch()
    subprocess.check_call(["git", "add", "."], cwd=git_clone_path)
    subprocess.check_call(["git", "commit", "-m", "local-change-1"], cwd=git_clone_path)
    output = subprocess.check_output(
        ["oca_git_push_if_remote_did_not_change", "origin"],
        cwd=git_clone_path,
        text=True,
    )
    assert "Pushing changes" in output


def test_remote_change(git_clone_path: Path):
    # push a change and reset
    (git_clone_path / "remote-change").touch()
    subprocess.check_call(["git", "add", "."], cwd=git_clone_path)
    subprocess.check_call(["git", "commit", "-m", "remote-change"], cwd=git_clone_path)
    subprocess.check_call(["git", "push"], cwd=git_clone_path)
    subprocess.check_call(["git", "reset", "--hard", "HEAD^"], cwd=git_clone_path)
    # create a local change
    (git_clone_path / "local-change-2").touch()
    subprocess.check_call(["git", "add", "."], cwd=git_clone_path)
    subprocess.check_call(["git", "commit", "-m", "local-change-2"], cwd=git_clone_path)
    output = subprocess.check_output(
        ["oca_git_push_if_remote_did_not_change", "origin"],
        cwd=git_clone_path,
        text=True,
    )
    assert "Remote has evolved since we cloned, not pushing" in output
