from git import GitCommandError


def notify_error(notify_method, e: Exception, timeout: int = 10) -> None:
    if isinstance(e, GitCommandError):
        msg = (e.stderr or str(e)).strip()
        if "merge" in msg.lower() and "conflict" in msg.lower():
            msg = "⚠️ Conflictos de merge. Resolvelos y hacé commit.\n" + msg
    else:
        msg = str(e)
    notify_method(f"Error: {msg}", severity="error", timeout=timeout)
