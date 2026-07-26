from textual.app import ComposeResult
from textual.widgets import Label, Static, ListView, ListItem, TextArea
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.screen import ModalScreen
from textual.markup import escape

from git_criollo.diff_utils import _diff_coloreado
from git_criollo.models import CommitDetail


class BaseModalScreen(ModalScreen):
    """Clase base para modales de solo lectura con bindings y CSS comunes."""
    BINDINGS = [
        ("escape", "quit", "Cerrar"),
        ("q", "quit", "Cerrar"),
    ]

    CSS = """
    BaseModalScreen { align: center middle; background: rgba(0,0,0,0.6); }
    """

    def action_quit(self) -> None:
        self.dismiss()


class VentanaDiff(BaseModalScreen):
    CSS = """
    VentanaDiff { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_diff { padding: 1 2; background: #121212; border: heavy #00afff; width: 80%; height: 80%; }
    #diff_container { height: 1fr; }
    #diff_container Static { background: #1a1a1a; padding: 1; }
    """
    def __init__(self, path: str, diff: str):
        super().__init__()
        self.path = path
        self.diff = diff

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(f"[bold #00afff]Diff: {escape(self.path)}[/]"),
            ScrollableContainer(Static(_diff_coloreado(self.diff), markup=True), id="diff_container"),
            Label("[dim][Q / ESC] Cerrar[/dim]"),
            id="dialog_diff"
        )


class VentanaDetalleCommit(BaseModalScreen):
    CSS = """
    VentanaDetalleCommit { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_detail { padding: 1; background: #121212; border: heavy #00afff; width: 90%; height: 90%; }
    #left_panel { width: 35%; height: 100%; border-right: solid #333; padding: 1; }
    #meta_section { height: auto; max-height: 50%; overflow-y: auto; border-bottom: solid #333; padding: 0 0 1 0; }
    #meta_section Label { margin: 0; }
    #files_header { height: auto; margin-top: 1; }
    #file_list { height: 1fr; border: tall #444; margin-top: 1; }
    #file_list:focus { border: tall #00afff; }
    #right_panel { width: 65%; height: 100%; padding: 0 1; }
    #message_label { height: auto; color: #ffaf00; padding: 1 0; border-bottom: solid #333; }
    #diff_header { height: auto; color: #00afff; margin-bottom: 1; }
    #diff_container { height: 1fr; }
    #diff_container Static { background: #1a1a1a; padding: 1; }
    """
    def __init__(self, detail: CommitDetail):
        super().__init__()
        self.detail = detail

    def compose(self) -> ComposeResult:
        detail = self.detail
        yield Vertical(
            Horizontal(
                Vertical(
                    Label(f"[bold #00afff]Commit: {escape(detail.hash)}[/]"
                          + (f"  [dim]({', '.join(detail.branches)})[/]" if detail.branches else "")),
                    Vertical(
                        Label(f"[bold #87d7ff]{escape(detail.committer)}[/]"),
                        Label(f"[bold #87d7ff]{escape(detail.committer_date)}"),
                        id="meta_section",
                    ),
                    Label(f"[bold]Archivos ({len(detail.files)})[/]", id="files_header"),
                    ListView(id="file_list"),
                    id="left_panel",
                ),
                Vertical(
                    Label(escape(detail.message), id="message_label"),
                    Label("Seleccioná un archivo", id="diff_header"),
                    ScrollableContainer(Static(""), id="diff_container"),
                    id="right_panel",
                ),
                id="body",
            ),
            Label("[dim][Q / ESC] Cerrar[/dim]"),
            id="dialog_detail"
        )

    def on_mount(self) -> None:
        lista = self.query_one("#file_list", ListView)
        for path, a, d in self.detail.files:
            item = ListItem(Label(f"  {escape(path)}  [green]+{a}[/] [red]-{d}[/]"))
            item.file_path = path
            lista.append(item)
        if self.detail.files:
            lista.index = 0
            self._actualizar_diff(self.detail.files[0][0])

    def _actualizar_diff(self, path: str) -> None:
        diff = self.app.git.get_commit_file_diff(self.detail.hash, path)
        header = self.query_one("#diff_header", Label)
        header.update(f"[bold #00afff]Diff: {escape(path)}[/]")
        container = self.query_one("#diff_container", ScrollableContainer)
        container.remove_children()
        lineas = diff.split("\n")
        start = 0
        for i, linea in enumerate(lineas):
            if linea.startswith("diff --git"):
                start = i
                break
        container.mount(Static(_diff_coloreado("\n".join(lineas[start:])), markup=True))

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        item = event.item
        if not item:
            return
        path = getattr(item, "file_path", None)
        if path:
            self._actualizar_diff(path)


class VentanaResultado(BaseModalScreen):
    CSS = """
    VentanaResultado { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_result { padding: 1 2; background: #121212; border: heavy #ffaf00; width: 80%; height: 80%; }
    TextArea { background: #1a1a1a; border: tall #333; }
    """
    def __init__(self, titulo: str, texto: str):
        super().__init__()
        self.titulo = titulo
        self.texto = texto

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(f"[bold #ffaf00]{escape(self.titulo)}[/]"),
            TextArea(self.texto, read_only=True, show_line_numbers=True),
            Label("[dim][Q / ESC] Cerrar[/dim]"),
            id="dialog_result"
        )
