from textual.app import ComposeResult
from textual.widgets import Label, Static, TextArea
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
    #dialog_detail { padding: 1 2; background: #121212; border: heavy #00afff; width: 90%; height: 90%; }
    #meta_section { height: auto; padding: 0 0 1 0; border-bottom: solid #333; }
    #meta_section Label { margin: 0; }
    #message_label { margin: 0 1; height: auto; }
    #files_container { height: auto; max-height: 8; border-bottom: solid #333; margin: 0; }
    #files_section { margin: 0; padding: 0 1; }
    #detail_container { height: 1fr; }
    #detail_container Static { background: #1a1a1a; padding: 1; }
    """
    def __init__(self, detail: CommitDetail):
        super().__init__()
        self.detail = detail

    def compose(self) -> ComposeResult:
        detail = self.detail
        lines = "".join(
            f"  {escape(path)}  [+{a} -{d}]\n"
            for path, a, d in detail.files
        )
        yield Vertical(
            Label(f"[bold #00afff]Commit: {escape(detail.hash)}[/]"),
            Vertical(
                Label(f"Autor:     {escape(detail.author)}"),
                Label(f"Fecha:     {escape(detail.author_date)}"),
                Label(f"Committer: {escape(detail.committer)}"),
                Label(f"Fecha:     {escape(detail.committer_date)}"),
                id="meta_section",
            ),
            Label(escape(detail.message), id="message_label"),
            Vertical(
                Label(f"[bold]Archivos ({len(detail.files)})[/]"),
                ScrollableContainer(Label(lines, id="files_section"), id="files_container"),
            ),
            ScrollableContainer(Static(_diff_coloreado(detail.diff), markup=True), id="detail_container"),
            Label("[dim][Q / ESC] Cerrar[/dim]"),
            id="dialog_detail"
        )


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
