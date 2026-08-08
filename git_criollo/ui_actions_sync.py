from textual import work

from git_criollo.ventanas import confirmar_push


class MixinSyncActions:
    @work(thread=True)
    def action_pull_rama(self) -> None:
        self.call_from_thread(self.notify, "Git pull...")
        try:
            self.git.pull()
            self.call_from_thread(self.notify, "\u00a1Pull OK!")
            self.call_from_thread(self.actualizar_pantalla_completa)
        except (Exception,) as e:
            self.call_from_thread(self._notify_error, e)

    def action_push_rama(self) -> None:
        active_branch = self.git.get_branches().active
        is_detached = self.git.get_branches().is_detached
        if is_detached:
            self.notify("HEAD está suelto (detached). Cambiá a una rama primero.", severity="warning")
            return

        def confirmar(b: bool | None):
            if b:
                self._ejecutar_push(active_branch)
        self.push_screen(confirmar_push(active_branch), confirmar)

    @work(thread=True)
    def _ejecutar_push(self, branch: str) -> None:
        self.call_from_thread(self.notify, "Git push...")
        try:
            self.git.push(branch)
            self.call_from_thread(self.notify, "\u00a1Push OK!")
            self.call_from_thread(self.actualizar_pantalla_completa)
        except (Exception,) as e:
            self.call_from_thread(self._notify_error, e)

    @work(thread=True)
    def action_fetch_rama(self) -> None:
        self.call_from_thread(self.notify, "Git fetch...")
        try:
            self.git.fetch()
            self.call_from_thread(self.notify, "\u00a1Fetch OK!")
            self.call_from_thread(self.actualizar_pantalla_completa)
        except (Exception,) as e:
            self.call_from_thread(self._notify_error, e)
