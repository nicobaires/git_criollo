import pytest


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
