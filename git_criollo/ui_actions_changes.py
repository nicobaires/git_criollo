from textual.widgets import ListView
from git import GitCommandError

from git_criollo.ventanas import (
    VentanaCommit, VentanaStashPush, VentanaDiff, VentanaAmend,
    VentanaUncommitted, VentanaStageHunk, VentanaResultado,
    VentanaConfirmarDescarte, VentanaConfirmarAmend, VentanaConfirmarStashPop,
)


class MixinChangeActions:
    def action_uncommitted(self) -> None:
        self.push_screen(VentanaUncommitted())

    def action_stage_all(self) -> None:
        try:
            self.git.stage_all()
            self.notify("Todos los cambios agregados al Stage.")
            self.actualizar_status()
        except (GitCommandError, RuntimeError) as e:
            self._notify_error(e)

    def action_commit_cambios(self) -> None:
        info = self.git.get_status()
        if not info.staged and not info.untracked and not info.is_empty_repo:
            self.notify("No hay cambios para confirmar en un commit.", severity="warning")
            return

        def guardar_commit(mensaje: str | None) -> None:
            if mensaje:
                try:
                    self.git.commit(mensaje)
                    self.notify("\u00a1Commit creado con \u00e9xito!")
                    self.actualizar_pantalla_completa()
                except (GitCommandError, RuntimeError) as e:
                    self._notify_error(e)
        self.push_screen(VentanaCommit(), guardar_commit)

    def action_stash_push(self) -> None:
        def p(val):
            if val is None:
                return
            try:
                self.git.stash_push(val)
                self.notify("Stash guardado.")
                self.actualizar_status()
            except (GitCommandError, RuntimeError) as e:
                self._notify_error(e)
        self.push_screen(VentanaStashPush(), p)

    def action_stash_pop(self) -> None:
        def p(b: bool | None):
            if b:
                try:
                    self.git.stash_pop()
                    self.notify("Stash recuperado.")
                    self.actualizar_status()
                except (GitCommandError, RuntimeError) as e:
                    self._notify_error(e)
        self.push_screen(VentanaConfirmarStashPop(), p)

    def action_ver_diff(self) -> None:
        focused = self.focused
        if not focused or focused.id not in ("lista_staged", "lista_unstaged"):
            self.notify("Seleccion\u00e1 un archivo en el panel de estado.", severity="warning")
            return
        item = focused.highlighted_child
        if not item:
            return
        ruta = getattr(item, "archivo_ruta", None)
        if not ruta:
            return
        staged = focused.id == "lista_staged"
        diff = self.git.get_diff(ruta, staged=staged)
        self.push_screen(VentanaDiff(ruta, diff))

    def action_amend_commit(self) -> None:
        history = self.query_one("#lista_commits", ListView)
        if not history.children:
            self.notify("No hay commits para modificar.", severity="warning")
            return

        def confirmar(b: bool | None):
            if b:
                def p(mensaje: str | None):
                    if mensaje:
                        try:
                            self.git.amend_commit(mensaje)
                            self.notify("Commit modificado (amend).")
                            self.actualizar_pantalla_completa()
                        except (GitCommandError, RuntimeError) as e:
                            self._notify_error(e)
                self.push_screen(VentanaAmend(), p)
        self.push_screen(VentanaConfirmarAmend(), confirmar)

    def action_ver_gitignore(self) -> None:
        try:
            contenido = self.git.get_gitignore_content()
            self.push_screen(VentanaResultado(".gitignore", contenido))
        except (GitCommandError, RuntimeError) as e:
            self._notify_error(e)

    def action_agregar_gitignore(self) -> None:
        focused = self.focused
        if not focused or focused.id != "lista_unstaged":
            self.notify("Seleccion\u00e1 un archivo no trackeado en el panel de estado.", severity="warning")
            return
        item = focused.highlighted_child
        if not item:
            return
        ruta = getattr(item, "archivo_ruta", None)
        if not ruta:
            return
        info = self.git.get_status()
        if ruta not in info.untracked:
            self.notify("Solo se puede ignorar archivos no trackeados.", severity="warning")
            return
        try:
            self.git.add_to_gitignore(ruta)
            self.notify(f"Ignorado: {ruta}")
            self.actualizar_status()
        except (GitCommandError, RuntimeError) as e:
            self._notify_error(e)

    def action_descartar_cambios(self) -> None:
        focused = self.focused
        if not focused or focused.id not in ("lista_staged", "lista_unstaged"):
            self.notify("Seleccion\u00e1 un archivo modificado en el panel de estado.", severity="warning")
            return
        item = focused.highlighted_child
        if not item:
            return
        ruta = getattr(item, "archivo_ruta", None)
        if not ruta:
            return

        def confirmar(b: bool | None):
            if b:
                try:
                    self.git.discard_changes(ruta)
                    self.notify(f"Cambios descartados: {ruta}")
                    self.actualizar_status()
                except (GitCommandError, RuntimeError) as e:
                    self._notify_error(e)
        self.push_screen(VentanaConfirmarDescarte(ruta), confirmar)

    def action_stage_hunk(self) -> None:
        focused = self.focused
        if not focused or focused.id != "lista_unstaged":
            self.notify("Seleccion\u00e1 un archivo modificado en el panel de estado.", severity="warning")
            return
        item = focused.highlighted_child
        if not item:
            return
        ruta = getattr(item, "archivo_ruta", None)
        if not ruta:
            return
        info = self.git.get_status()
        if ruta in info.untracked:
            self.notify("No se puede stagear hunks de archivos no trackeados.", severity="warning")
            return
        self.push_screen(VentanaStageHunk(ruta), lambda _: self.actualizar_status())
