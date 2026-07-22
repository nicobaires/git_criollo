import os
import subprocess

import pytest
from git import GitCommandError

from git_criollo.models import ConflictRegion, DiffHunk


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


class TestGetGraphLog:
    def test_returns_lines(self, gs):
        lines = gs.get_graph_log(skip=0, n=5)
        assert len(lines) > 0
        assert all(isinstance(l, str) for l in lines)

    def test_skip_works(self, gs):
        all_lines = gs.get_graph_log(skip=0, n=10)
        skipped = gs.get_graph_log(skip=2, n=10)
        assert len(skipped) <= len(all_lines)
        if len(skipped) > 0 and len(all_lines) > 2:
            assert skipped[0] != all_lines[0]


class TestGetCommits:
    def test_returns_commit_info(self, gs):
        commits = gs.get_commits(skip=0, n=5)
        assert len(commits) > 0
        c = commits[0]
        assert len(c.hash) == 7
        assert c.message
        assert c.author

    def test_skip_limit(self, gs):
        commits = gs.get_commits(skip=0, n=2)
        assert len(commits) <= 2


class TestGetCommitDetail:
    def test_returns_detail(self, gs):
        commits = gs.get_commits(n=1)
        detail = gs.get_commit_detail(commits[0].hash)
        assert detail.hash == commits[0].hash
        assert detail.author
        assert detail.author_date
        assert detail.committer
        assert detail.committer_date
        assert detail.message
        assert isinstance(detail.files, list)


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


class TestPullPushFetch:
    def test_pull_no_remote(self, gs):
        with pytest.raises(RuntimeError, match="No hay remote"):
            gs.pull()

    def test_push_no_remote(self, gs):
        with pytest.raises(RuntimeError, match="No hay remote"):
            gs.push("main")

    def test_fetch_no_remote(self, gs):
        with pytest.raises(RuntimeError, match="No hay remote"):
            gs.fetch()


class TestStash:
    def test_stash_push_and_pop(self, gs):
        with open("stash_test.txt", "w") as f:
            f.write("stash content")
        gs.stage_file("stash_test.txt")
        gs.stash_push("test stash")
        assert "stash_test.txt" not in [item.a_path for item in gs.repo.index.diff(None)]
        gs.stash_pop()
        assert os.path.exists(os.path.join(gs.repo.working_tree_dir, "stash_test.txt"))

    def test_stash_list(self, gs):
        with open("stash_list.txt", "w") as f:
            f.write("test")
        gs.stage_file("stash_list.txt")
        gs.stash_push()
        stashes = gs.stash_list()
        assert len(stashes) > 0


class TestTags:
    def test_create_and_delete(self, gs):
        gs.create_tag("test-tag")
        assert "test-tag" in [t.name for t in gs.repo.tags]
        gs.delete_tag("test-tag")
        assert "test-tag" not in [t.name for t in gs.repo.tags]

    def test_get_tags(self, gs):
        tags = gs.get_tags()
        assert "v1.0" in tags


class TestCherryPick:
    def test_cherry_pick(self, gs):
        gs.create_branch("cherry-source")
        gs.checkout("cherry-source")
        with open("cherry_unique.txt", "w") as f:
            f.write("solo en source")
        subprocess.run(["git", "add", "cherry_unique.txt"], capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "cherry pick me"], capture_output=True
        )
        sha = gs.repo.head.commit.hexsha[:7]
        gs.checkout("main")
        gs.cherry_pick(sha)
        ruta = os.path.join(gs.repo.working_tree_dir, "cherry_unique.txt")
        assert os.path.exists(ruta)
        with open(ruta) as f:
            assert f.read() == "solo en source"


class TestRunCommand:
    def test_valid_command(self, gs):
        result = gs.run_command("log --oneline")
        assert len(result) > 0
        assert "commit" in result or "Error" not in result

    def test_injection_rejected(self, gs):
        result = gs.run_command("; rm -rf /")
        assert "caracteres no permitidos" in result

    def test_shell_metachars_rejected(self, gs):
        for cmd in ["`id`", "$(whoami)", "foo && bar", "foo | bar"]:
            result = gs.run_command(cmd)
            assert "caracteres no permitidos" in result, f"Fallo con: {cmd}"


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
        with pytest.raises(RuntimeError, match="No se pudo aplicar"):
            gs.stage_hunk("hunk_err.txt", hunk)


class TestRebase:
    def test_get_commits_for_rebase(self, gs):
        sha = gs.repo.head.commit.hexsha[:7]
        commits = gs.get_commits_for_rebase(sha)
        assert len(commits) > 0

    def test_get_parent_sha(self, gs):
        sha = list(gs.repo.iter_commits(max_count=2))[-1].hexsha
        parent = gs.get_parent_sha(sha)
        assert parent is None or len(parent) > 0

    def test_run_rebase_with_todos(self, gs):
        base_sha = list(gs.repo.iter_commits(max_count=2))[-1].hexsha
        todos = [(c.hexsha[:7], "pick") for c in gs.repo.iter_commits(max_count=1)]
        try:
            gs.run_rebase(base_sha, todos)
        except GitCommandError as e:
            if "nothing to do" in e.stderr.lower():
                pass
            else:
                raise


class TestConflictResolution:
    def test_get_conflict_regions(self, gs):
        regions = gs.get_conflict_regions("nonexistent.txt")
        assert regions == []

    def test_resolve_conflict_invalid_choice(self, gs):
        region = ConflictRegion(start=0, end=2, ours="a", theirs="b")
        with pytest.raises(ValueError, match="Opción de resolución inválida"):
            gs.resolve_conflict_region("f0.txt", region, "invalida")

    def test_is_merge_in_progress(self, gs):
        assert gs.is_merge_in_progress() is False


class TestGitignore:
    def test_get_content_missing(self, gs):
        content = gs.get_gitignore_content()
        assert "no existe" in content

    def test_get_content_exists(self, gs):
        gitignore = os.path.join(gs.repo.working_tree_dir, ".gitignore")
        with open(gitignore, "w") as f:
            f.write("*.log\n.env\n")
        content = gs.get_gitignore_content()
        assert "*.log" in content

    def test_add_to_gitignore(self, gs):
        gs.add_to_gitignore("*.tmp")
        gitignore = os.path.join(gs.repo.working_tree_dir, ".gitignore")
        with open(gitignore) as f:
            content = f.read()
        assert "*.tmp" in content

    def test_add_duplicate(self, gs):
        gs.add_to_gitignore("*.dup")
        gs.add_to_gitignore("*.dup")
        gitignore = os.path.join(gs.repo.working_tree_dir, ".gitignore")
        with open(gitignore) as f:
            lines = f.read().strip().split("\n")
        assert lines.count("*.dup") == 1


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
