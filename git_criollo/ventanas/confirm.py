from textual.app import ComposeResult
from textual.widgets import Button, Label, Horizontal
from textual.containers import Vertical
from textual.screen import ModalScreen


class VentanaConfirmarBorrado(ModalScreen[bool]):
    BINDINGS = [("escape", "cancel", "Cancelar")]
    CSS = """
    VentanaConfirmarBorrado { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_delete { padding: 1 2; background: #262626; border: heavy #ff5f5f; width: 50; height: 12; }
    #buttons { margin-top: 1; height: 3; align: center middle; }
    Button { margin: 0 1; }
    """
    def __init__(self, nombre_rama: str): super().__init__(); self.nombre_rama = nombre_rama
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(f"[bold #ff5f5f]\u00bfBorrar Rama?[/]\n\u00bfSeguro que quer\u00e9s eliminar [bold]{self.nombre_rama}[/]?"),
            Horizontal(Button("S\u00ed", variant="error", id="s"), Button("No", variant="primary", id="n"), id="buttons"),
            Label("[dim][ESC] Cancelar[/dim]"),
            id="dialog_delete"
        )
    def on_button_pressed(self, event: Button.Pressed) -> None: self.dismiss(True if event.button.id == "s" else False)
    def action_cancel(self) -> None: self.dismiss(False)


class VentanaConfirmarMerge(ModalScreen[bool]):
    BINDINGS = [("escape", "cancel", "Cancelar")]
    CSS = """
    VentanaConfirmarMerge { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_merge { padding: 1 2; background: #262626; border: heavy #00afd7; width: 56; height: 12; }
    #buttons { margin-top: 1; height: 3; align: center middle; }
    Button { margin: 0 1; }
    """
    def __init__(self, nombre_rama: str): super().__init__(); self.nombre_rama = nombre_rama
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(f"[bold #00afd7]\u00bfMergear?[/]\n\u00bfMergear [bold]{self.nombre_rama}[/] en la rama actual?"),
            Horizontal(Button("S\u00ed", variant="primary", id="s"), Button("No", variant="default", id="n"), id="buttons"),
            Label("[dim][ESC] Cancelar[/dim]"),
            id="dialog_merge"
        )
    def on_button_pressed(self, event: Button.Pressed) -> None: self.dismiss(True if event.button.id == "s" else False)
    def action_cancel(self) -> None: self.dismiss(False)


class VentanaConfirmarBorradoTag(ModalScreen[bool]):
    BINDINGS = [("escape", "cancel", "Cancelar")]
    CSS = """
    VentanaConfirmarBorradoTag { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_tag_del { padding: 1 2; background: #262626; border: heavy #ff5f5f; width: 50; height: 12; }
    #buttons { margin-top: 1; height: 3; align: center middle; }
    Button { margin: 0 1; }
    """
    def __init__(self, nombre_tag: str): super().__init__(); self.nombre_tag = nombre_tag
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(f"[bold #ff5f5f]\u00bfBorrar Tag?[/]\n\u00bfSeguro que quer\u00e9s eliminar el tag [bold]{self.nombre_tag}[/]?"),
            Horizontal(Button("S\u00ed", variant="error", id="s"), Button("No", variant="primary", id="n"), id="buttons"),
            Label("[dim][ESC] Cancelar[/dim]"),
            id="dialog_tag_del"
        )
    def on_button_pressed(self, event: Button.Pressed) -> None: self.dismiss(True if event.button.id == "s" else False)
    def action_cancel(self) -> None: self.dismiss(False)
