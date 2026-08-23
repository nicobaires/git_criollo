from git import GitCommandError


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
