from textual.app import ComposeResult
from textual.widgets import Label, Static, TextArea
from textual.containers import Vertical, ScrollableContainer
from textual.screen import ModalScreen

from git_criollo.diff_utils import _diff_coloreado


class VentanaDiff(ModalScreen):
    BINDINGS = [("escape", "quit", "Cerrar"), ("q", "quit", "Cerrar")]
    CSS = """
    VentanaDiff { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_diff { padding: 1 2; background: #121212; border: heavy #00afff; width: 80%; height: 80%; }
    #diff_container { height: 1fr; }
    Static { background: #1a1a1a; padding: 1; }
    """
    def __init__(self, path: str, diff: str): super().__init__(); self.path = path; self.diff = diff
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(f"[bold #00afff]Diff: {self.path}[/]"),
            ScrollableContainer(Static(_diff_coloreado(self.diff), markup=True), id="diff_container"),
            Label("[dim][Q / ESC] Cerrar[/dim]"),
            id="dialog_diff"
        )
    def action_quit(self) -> None: self.dismiss()


class VentanaDetalleCommit(ModalScreen):
    BINDINGS = [("escape", "quit", "Cerrar"), ("q", "quit", "Cerrar")]
    CSS = """
    VentanaDetalleCommit { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_detail { padding: 1 2; background: #121212; border: heavy #00afff; width: 80%; height: 80%; }
    #detail_container { height: 1fr; }
    #meta_label { padding: 0 1; height: auto; }
    Static { background: #1a1a1a; padding: 1; }
    """
    def __init__(self, sha: str, meta: str, diff: str): super().__init__(); self.sha = sha; self.meta = meta; self.diff = diff
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(f"[bold #00afff]Commit: {self.sha}[/]"),
            Label(self.meta, id="meta_label"),
            ScrollableContainer(Static(_diff_coloreado(self.diff), markup=True), id="detail_container"),
            Label("[dim][Q / ESC] Cerrar[/dim]"),
            id="dialog_detail"
        )
    def action_quit(self) -> None: self.dismiss()


class VentanaResultado(ModalScreen):
    BINDINGS = [("escape", "quit", "Cerrar"), ("q", "quit", "Cerrar")]
    CSS = """
    VentanaResultado { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_result { padding: 1 2; background: #121212; border: heavy #ffaf00; width: 80%; height: 80%; }
    TextArea { background: #1a1a1a; border: tall #333; }
    """
    def __init__(self, titulo: str, texto: str): super().__init__(); self.titulo = titulo; self.texto = texto
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(f"[bold #ffaf00]{self.titulo}[/]"),
            TextArea(self.texto, read_only=True, show_line_numbers=True),
            Label("[dim][Q / ESC] Cerrar[/dim]"),
            id="dialog_result"
        )
    def action_quit(self) -> None: self.dismiss()
