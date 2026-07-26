from textual.widgets import ListView

from git_criollo.helpers import git_action
from git_criollo.ventanas import (
    VentanaDetalleCommit, VentanaCherryPick, VentanaRebase, VentanaConflictos,
    confirmar_cherrypick, confirmar_rebase,
)


class MixinHistoryActions:
    def action_toggle_grafico(self) -> None:
        self._modo_grafico = not self._modo_grafico
        self.actualizar_historial()
        modo = "gr\u00e1fico" if self._modo_grafico else "detalle"
        self.notify(f"Modo historial: {modo}")

    def action_mas_commits(self) -> None:
        lista = self.query_one("#lista_commits", ListView)
        n = 20
        if self._modo_grafico:
            lineas = self.git.get_graph_log(skip=self._commit_offset, n=n)
            from git_criollo.helpers import render_commit_list
            render_commit_list(lista, lineas, modo_grafico=True)
            if lineas:
                self._commit_offset += len(lineas)
            else:
                self.notify("No hay m\u00e1s commits.")
        else:
            commits = self.git.get_commits(skip=self._commit_offset, n=n)
            from git_criollo.helpers import render_commit_list
            render_commit_list(lista, commits, modo_grafico=False)
            if commits:
                self._commit_offset += len(commits)
            else:
                self.notify("No hay m\u00e1s commits.")

    @git_action()
    def _mostrar_detalle_commit(self, sha: str) -> None:
        detail = self.git.get_commit_detail(sha)
        self.push_screen(VentanaDetalleCommit(detail))

    def action_cherry_pick(self) -> None:
        def p(sha: str | None):
            if sha:
                def confirmar(b: bool | None):
                    if b:
                        try:
                            self.git.cherry_pick(sha)
                            self.notify(f"Cherry-pick de {sha} aplicado.")
                            self.actualizar_pantalla_completa()
                        except (Exception,) as e:
                            self._notify_error(e)
                self.push_screen(confirmar_cherrypick(sha), confirmar)
        self.push_screen(VentanaCherryPick(), p)

    def action_rebase(self) -> None:
        lista = self.query_one("#lista_commits", ListView)
        child = lista.highlighted_child
        if not child:
            self.notify("Seleccion\u00e1 un commit en el historial.", severity="warning")
            return
        sha = getattr(child, "commit_hash", None)
        if not sha:
            self.notify("Seleccion\u00e1 un commit en el historial.", severity="warning")
            return
        commits = self.git.get_commits_for_rebase(sha)
        if len(commits) < 2:
            self.notify("Se necesitan al menos 2 commits para rebase interactivo.", severity="warning")
            return

        def ejecutar(todos):
            if todos:
                def confirmar(b: bool | None):
                    if b:
                        try:
                            base_sha = self.git.get_parent_sha(sha)
                            self.git.run_rebase(base_sha, todos)
                            self.notify("Rebase completado.")
                            self.actualizar_pantalla_completa()
                        except (Exception,) as e:
                            self._notify_error(e)
                self.push_screen(confirmar_rebase(), confirmar)
        self.push_screen(VentanaRebase(commits), ejecutar)

    def action_resolver_conflictos(self) -> None:
        if not self.git.is_merge_in_progress():
            self.notify("No hay conflictos de merge.", severity="warning")
            return
        archivos = self.git.get_conflicted_files()
        if not archivos:
            self.notify("No hay archivos en conflicto.", severity="warning")
            return
        self.push_screen(VentanaConflictos(archivos), lambda _: self.actualizar_pantalla_completa())
