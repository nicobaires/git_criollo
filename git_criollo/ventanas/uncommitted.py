from textual.app import ComposeResult
from textual.widgets import ListView, ListItem, Label, Static
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.screen import ModalScreen
from git import GitCommandError

from git_criollo.diff_utils import _diff_coloreado
from git_criollo.error_utils import notify_error as _error_base
from git_criollo.ventanas.viewer import VentanaDiff
from git_criollo.ventanas.input import VentanaCommit
from git_criollo.ventanas.interactive import VentanaStageHunk


class VentanaUncommitted(ModalScreen):
    BINDINGS = [
        ("escape", "quit", "Cerrar"),
        ("q", "quit", "Cerrar"),
        ("v", "ver_diff", "Ver Diff"),
        ("a", "stage_all", "Stage All"),
        ("w", "commit_cambios", "Commit"),
        ("H", "stage_hunk", "Stage Hunk"),
        ("x", "descartar_cambios", "Descartar"),
        ("i", "agregar_gitignore", "Ignore"),
    ]
    CSS = """
    VentanaUncommitted { align: center middle; background: rgba(0,0,0,0.85); }
    #dialog_uc { padding: 1; background: #121212; border: heavy #00afff; width: 90%; height: 90%; }
    #uc_body { height: 1fr; }
    #uc_files { width: 30%; height: 100%; border-right: solid #333; }
    #uc_file_list { height: 1fr; margin: 1; border: tall #444; }
    #uc_file_list:focus { border: tall #00afff; }
    #uc_file_list_scroll { height: 1fr; }
    #uc_actions { margin: 1 0 0 2; color: #888; height: auto; }
    #uc_diff_panel { width: 70%; height: 100%; }
    #uc_diff_container { height: 1fr; }
    #uc_diff_container Static { background: #1a1a1a; padding: 1; }
    #uc_diff_header { margin: 0 0 0 2; height: auto; }
    """
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("[bold #00afff]\u2500\u2500 CAMBIOS SIN COMMIT \u2500\u2500[/]"),
            Horizontal(
                Vertical(
                    Label("[bold]Archivos[/] (Enter: stage/unstage)", id="uc_title"),
                    ListView(id="uc_file_list"),
                    Label("[dim][[a]] Stage All  [[w]] Commit  [[v]] Ver Diff  [[H]] Hunk  [[x]] Descartar  [[i]] Ignore  [[q]] Cerrar[/dim]", id="uc_actions"),
                    id="uc_files",
                ),
                Vertical(
                    Label("[bold]Diff[/]", id="uc_diff_header"),
                    ScrollableContainer(Static("Seleccion\u00e1 un archivo", markup=True), id="uc_diff_container"),
                    id="uc_diff_panel",
                ),
                id="uc_body",
            ),
            id="dialog_uc",
        )

    def on_mount(self) -> None:
        self._archivos: list[tuple[str, bool]] = []
        self._ultima_ruta: str | None = None
        self._refrescar()

    @property
    def git(self):
        return self.app.git

    def _refrescar(self) -> None:
        info = self.git.get_status()
        lista = self.query_one("#uc_file_list", ListView)
        lista.clear()
        self._archivos = []

        for f in info.staged:
            self._archivos.append((f, True))
            item = ListItem(Label(f"  \u2714 {f}"))
            item.archivo_ruta = f
            item.archivo_staged = True
            lista.append(item)
        for f in info.unstaged:
            self._archivos.append((f, False))
            item = ListItem(Label(f"  \ud83d\udca5 M: {f}"))
            item.archivo_ruta = f
            item.archivo_staged = False
            lista.append(item)
        for f in info.untracked:
            self._archivos.append((f, False))
            item = ListItem(Label(f"  \u2753 ?: {f}"))
            item.archivo_ruta = f
            item.archivo_staged = False
            lista.append(item)

        titulo = self.query_one("#uc_title", Label)
        n = len(self._archivos)
        titulo.update(f"[bold]Archivos ({n})[/] (Enter: stage/unstage)")

        if not self._archivos:
            return

        idx = 0
        if self._ultima_ruta:
            for i, (r, s) in enumerate(self._archivos):
                if r == self._ultima_ruta:
                    idx = i
                    break
        lista.index = idx
        ruta, staged = self._archivos[idx]
        self._ultima_ruta = ruta
        self._actualizar_diff(ruta, staged)

    def _actualizar_diff(self, ruta: str, staged: bool) -> None:
        container = self.query_one("#uc_diff_container", ScrollableContainer)
        if staged:
            raw = self.git.get_diff(ruta, staged=True)
        else:
            raw = self.git.get_diff(ruta, staged=False)
        header = self.query_one("#uc_diff_header", Label)
        header.update(f"[bold]{'[Staged] ' if staged else ''}{ruta}[/]")
        container.remove_children()
        container.mount(Static(_diff_coloreado(raw), markup=True))

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        item = event.item
        if not item:
            return
        ruta = getattr(item, "archivo_ruta", None)
        staged = getattr(item, "archivo_staged", False)
        if ruta:
            self._ultima_ruta = ruta
            self._actualizar_diff(ruta, staged)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if not item:
            return
        ruta = getattr(item, "archivo_ruta", None)
        if not ruta:
            return
        self._ultima_ruta = ruta
        try:
            staged = getattr(item, "archivo_staged", False)
            if staged:
                self.git.unstage_file(ruta)
            else:
                self.git.stage_file(ruta)
            self._refrescar()
        except (GitCommandError, RuntimeError) as e:
            self._notify_error(e)

    def action_ver_diff(self) -> None:
        lista = self.query_one("#uc_file_list", ListView)
        item = lista.highlighted_child
        if not item:
            self.notify("Seleccion\u00e1 un archivo.", severity="warning")
            return
        ruta = getattr(item, "archivo_ruta", None)
        if not ruta:
            return
        staged = getattr(item, "archivo_staged", False)
        diff = self.git.get_diff(ruta, staged=staged)
        self.app.push_screen(VentanaDiff(ruta, diff))

    def action_stage_all(self) -> None:
        try:
            self.git.stage_all()
            self._refrescar()
        except (GitCommandError, RuntimeError) as e:
            self._notify_error(e)

    def action_commit_cambios(self) -> None:
        info = self.git.get_status()
        if not info.staged and not info.untracked and not info.is_empty_repo:
            self.notify("No hay cambios para confirmar.", severity="warning")
            return

        def guardar(mensaje: str | None) -> None:
            if mensaje:
                try:
                    self.git.commit(mensaje)
                    self._refrescar()
                except (GitCommandError, RuntimeError) as e:
                    self._notify_error(e)

        self.app.push_screen(VentanaCommit(), guardar)

    def _notify_error(self, e: Exception) -> None:
        if isinstance(e, (KeyboardInterrupt, SystemExit)):
            raise
        _error_base(self.notify, e, timeout=10)

    def action_stage_hunk(self) -> None:
        lista = self.query_one("#uc_file_list", ListView)
        item = lista.highlighted_child
        if not item:
            return
        ruta = getattr(item, "archivo_ruta", None)
        if not ruta:
            return
        staged = getattr(item, "archivo_staged", False)
        if staged:
            self.notify("El archivo ya est\u00e1 staged.", severity="warning")
            return
        info = self.git.get_status()
        if ruta in info.untracked:
            self.notify("No se puede stagear hunks de archivos no trackeados.", severity="warning")
            return
        self.app.push_screen(VentanaStageHunk(ruta), lambda _: self._refrescar())

    def action_descartar_cambios(self) -> None:
        lista = self.query_one("#uc_file_list", ListView)
        item = lista.highlighted_child
        if not item:
            return
        ruta = getattr(item, "archivo_ruta", None)
        if not ruta:
            return
        try:
            self.git.discard_changes(ruta)
            self.notify(f"Cambios descartados: {ruta}")
            self._refrescar()
        except (GitCommandError, RuntimeError) as e:
            self._notify_error(e)

    def action_agregar_gitignore(self) -> None:
        lista = self.query_one("#uc_file_list", ListView)
        item = lista.highlighted_child
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
            self._refrescar()
        except (GitCommandError, RuntimeError) as e:
            self._notify_error(e)

    def action_quit(self) -> None:
        self.dismiss()
