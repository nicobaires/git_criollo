from textual import work
from git import GitCommandError


class MixinSyncActions:
    @work(thread=True)
    def action_pull_rama(self) -> None:
        self.notify("Git pull...")
        try:
            self.git.pull()
            self.notify("\u00a1Pull OK!")
            self.call_from_thread(self.actualizar_pantalla_completa)
        except (GitCommandError, RuntimeError) as e:
            self._notify_error(e)

    @work(thread=True)
    def action_push_rama(self) -> None:
        self.notify("Git push...")
        try:
            active_branch = self.git.get_branches().active
            self.git.push(active_branch)
            self.notify("\u00a1Push OK!")
            self.call_from_thread(self.actualizar_pantalla_completa)
        except (GitCommandError, RuntimeError) as e:
            self._notify_error(e)

    @work(thread=True)
    def action_fetch_rama(self) -> None:
        self.notify("Git fetch...")
        try:
            self.git.fetch()
            self.notify("\u00a1Fetch OK!")
            self.call_from_thread(self.actualizar_pantalla_completa)
        except (GitCommandError, RuntimeError) as e:
            self._notify_error(e)
