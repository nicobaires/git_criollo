import os
import subprocess

from git_criollo.git_service import GitService


class TestGetBranches:
    def test_active_branch(self, gs):
        info = gs.get_branches()
        assert info.active == "main"
        assert len(info.branches) >= 1

    def test_remotes_list(self, gs):
        info = gs.get_branches()
        assert isinstance(info.remotes, list)

    def test_tags_list(self, gs):
        info = gs.get_branches()
        assert "v1.0" in info.tags

    def test_is_detached_false(self, gs):
        assert gs.get_branches().is_detached is False

    def test_is_detached_true(self, gs_detached):
        assert gs_detached.get_branches().is_detached is True

    def test_detached_shows_sha(self, gs_detached):
        active = gs_detached.get_branches().active
        assert active != "master"
        assert len(active) == 7

    def test_ahead_behind(self, gs):
        info = gs.get_branches()
        assert isinstance(info.ahead, dict)
        assert isinstance(info.behind, dict)


class TestBranches:
    def test_create_and_delete(self, gs):
        gs.create_branch("test-branch")
        assert "test-branch" in [b.name for b in gs.repo.branches]
        gs.delete_branch("test-branch")
        assert "test-branch" not in [b.name for b in gs.repo.branches]

    def test_checkout(self, gs):
        gs.create_branch("nueva")
        gs.checkout("nueva")
        assert gs.repo.active_branch.name == "nueva"

    def test_checkout_remote_rsplit(self, gs):
        subprocess.run(
            ["git", "update-ref", "refs/remotes/origin/feature/x", "HEAD"],
            capture_output=True,
        )
        gs.checkout_remote("origin/feature/x")
        assert gs.repo.active_branch.name == "x"

    def test_merge(self, gs):
        gs.create_branch("merge-target")
        with open("merge_file.txt", "w") as f:
            f.write("merge content")
        subprocess.run(["git", "add", "merge_file.txt"], capture_output=True)
        subprocess.run(["git", "commit", "-m", "merge commit"], capture_output=True)
        gs.checkout("main")
        gs.merge("merge-target")
        assert os.path.exists(os.path.join(gs.repo.working_tree_dir, "merge_file.txt"))
