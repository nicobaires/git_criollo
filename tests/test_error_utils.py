from git import GitCommandError

from git_criollo.error_utils import notify_error


class FakeNotify:
    def __init__(self):
        self.calls = []

    def __call__(self, message, **kwargs):
        self.calls.append((message, kwargs.get("timeout", 10)))


class TestNotifyError:
    def test_git_command_error_includes_stderr(self):
        notify = FakeNotify()
        e = GitCommandError("git status", 128, stderr="fatal: not a git repository")
        notify_error(notify, e)
        assert len(notify.calls) == 1
        message, timeout = notify.calls[0]
        assert "fatal: not a git repository" in message or "not a git repository" in message

    def test_runtime_error_passthrough(self):
        notify = FakeNotify()
        e = RuntimeError("algo sali\u00f3 mal")
        notify_error(notify, e)
        assert len(notify.calls) == 1
        assert "algo sali\u00f3 mal" in notify.calls[0][0]

    def test_value_error_passthrough(self):
        notify = FakeNotify()
        e = ValueError("valor inv\u00e1lido")
        notify_error(notify, e)
        assert len(notify.calls) == 1
        assert "valor inv\u00e1lido" in notify.calls[0][0]

    def test_generic_exception_wraps(self):
        notify = FakeNotify()
        e = KeyError("foo")
        notify_error(notify, e)
        assert len(notify.calls) == 1
        assert "foo" in notify.calls[0][0]

    def test_merge_conflict_detection(self):
        notify = FakeNotify()
        e = GitCommandError(
            "git merge",
            1,
            stderr="Automatic merge failed; fix conflicts and then commit the result.",
        )
        notify_error(notify, e)
        assert len(notify.calls) == 1
        assert "conflict" in notify.calls[0][0].lower() or "conflicto" in notify.calls[0][0].lower()
