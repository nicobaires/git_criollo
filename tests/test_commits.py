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
