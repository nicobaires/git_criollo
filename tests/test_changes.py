import os
import subprocess

import pytest

from git_criollo.models import DiffHunk


class TestGetStatus:
    def test_clean_repo(self, gs):
        status = gs.get_status()
        assert isinstance(status.staged, list)
        assert isinstance(status.unstaged, list)
        assert isinstance(status.untracked, list)

    def test_staged_file(self, gs):
        with open("nuevo.txt", "w") as f:
            f.write("test")
        subprocess.run(["git", "add", "nuevo.txt"], capture_output=True)
        status = gs.get_status()
        assert "nuevo.txt" in status.staged

    def test_unstaged_file(self, gs):
        with open("f0.txt", "a") as f:
            f.write("modificado")
        status = gs.get_status()
        assert "f0.txt" in status.unstaged

    def test_untracked_file(self, gs):
        with open("untracked.txt", "w") as f:
            f.write("test")
        status = gs.get_status()
        assert "untracked.txt" in status.untracked

    def test_empty_repo(self, repo_path):
        subprocess.run(["git", "commit", "--allow-empty", "-m", "init"], capture_output=True)
        subprocess.run(["git", "update-ref", "-d", "HEAD"], capture_output=True)
        gs_empty = __import__("git_criollo.git_service", fromlist=["GitService"]).GitService(repo_path)
        status = gs_empty.get_status()
        assert status.is_empty_repo is True


class TestGetDiff:
    def test_staged_diff(self, gs):
        with open("nuevo.txt", "w") as f:
            f.write("contenido")
        subprocess.run(["git", "add", "nuevo.txt"], capture_output=True)
        diff = gs.get_diff("nuevo.txt", staged=True)
        assert "contenido" in diff

    def test_unstaged_diff(self, gs):
        with open("f0.txt", "a") as f:
            f.write("adicional")
        diff = gs.get_diff("f0.txt", staged=False)
        assert "adicional" in diff or diff != "(sin cambios)"

    def test_untracked_diff(self, gs):
        with open("nuevo_untracked.txt", "w") as f:
            f.write("test")
        diff = gs.get_diff("nuevo_untracked.txt", staged=False)
        assert diff != "(sin cambios)"


class TestStageUnstage:
    def test_stage_file(self, gs):
        with open("stage_test.txt", "w") as f:
            f.write("test")
        gs.stage_file("stage_test.txt")
        assert "stage_test.txt" in [item.a_path for item in gs.repo.index.diff("HEAD")]

    def test_unstage_file(self, gs):
        with open("unstage_test.txt", "w") as f:
            f.write("test")
        subprocess.run(["git", "add", "unstage_test.txt"], capture_output=True)
        gs.unstage_file("unstage_test.txt")
        assert "unstage_test.txt" not in [item.a_path for item in gs.repo.index.diff("HEAD")]

    def test_stage_all(self, gs):
        for fname in ["s1.txt", "s2.txt"]:
            with open(fname, "w") as f:
                f.write("test")
        gs.stage_all()
        status = gs.get_status()
        assert "s1.txt" in status.staged
        assert "s2.txt" in status.staged

    def test_discard_changes_tracked(self, gs):
        with open("f0.txt", "w") as f:
            f.write("original")
        subprocess.run(["git", "add", "f0.txt"], capture_output=True)
        subprocess.run(["git", "commit", "-m", "base"], capture_output=True)
        with open("f0.txt", "w") as f:
            f.write("modificado")
        gs.discard_changes("f0.txt")
        with open("f0.txt") as f:
            assert f.read() == "original"

    def test_discard_changes_untracked(self, gs):
        with open("descartar.txt", "w") as f:
            f.write("temporal")
        gs.discard_changes("descartar.txt")
        assert not os.path.exists(os.path.join(gs.repo.working_tree_dir, "descartar.txt"))


class TestCommit:
    def test_commit(self, gs):
        with open("commit_test.txt", "w") as f:
            f.write("test")
        gs.stage_file("commit_test.txt")
        gs.commit("feat: test commit")
        assert "commit_test.txt" in [item.a_path for item in gs.repo.index.diff("HEAD~1")]

    def test_amend(self, gs):
        with open("amend_test.txt", "w") as f:
            f.write("test")
        gs.stage_file("amend_test.txt")
        gs.commit("original message")
        gs.amend_commit("amended message")
        commits = list(gs.repo.iter_commits(max_count=1))
        assert commits[0].message.strip() == "amended message"


class TestStageHunk:
    def test_parse_hunks(self, gs):
        with open("hunk_test.txt", "w") as f:
            f.write("linea1\nlinea2\nlinea3\n")
        subprocess.run(["git", "add", "hunk_test.txt"], capture_output=True)
        subprocess.run(["git", "commit", "-m", "base hunk"], capture_output=True)
        with open("hunk_test.txt", "w") as f:
            f.write("linea1\nlinea2_mod\nlinea3\n")
        hunks = gs.parse_diff_hunks("hunk_test.txt")
        assert len(hunks) > 0
        assert isinstance(hunks[0], DiffHunk)

    def test_stage_hunk_invalid_patch(self, gs):
        with open("hunk_err.txt", "w") as f:
            f.write("a\nb\nc\n")
        subprocess.run(["git", "add", "hunk_err.txt"], capture_output=True)
        subprocess.run(["git", "commit", "-m", "base"], capture_output=True)
        with open("hunk_err.txt", "w") as f:
            f.write("x\ny\nz\n")
        hunk = DiffHunk(
            header="@@ -99,3 +99,3 @@",
            lines=["-nonexistent", "-bogus", "-line", "+WRONG"],
            raw="@@ -99,3 +99,3 @@\n-nonexistent\n-bogus\n-line\n+WRONG",
        )
        with pytest.raises(RuntimeError, match="ya no coincide|No se pudo aplicar"):
            gs.stage_hunk("hunk_err.txt", hunk)


class TestWorkingDiff:
    def test_working_diff_clean(self, gs):
        diff = gs.get_working_diff()
        assert diff == "(sin cambios)"

    def test_working_diff_dirty(self, gs):
        with open("f0.txt", "a") as f:
            f.write("mas contenido")
        diff = gs.get_working_diff()
        assert diff != "(sin cambios)"

    def test_staged_diff_clean(self, gs):
        diff = gs.get_staged_diff()
        assert diff == "(sin cambios)"
