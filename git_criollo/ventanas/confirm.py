from textual.app import ComposeResult
from textual.widgets import Button, Label
from textual.containers import Horizontal, Vertical
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


class VentanaConfirmarDescarte(ModalScreen[bool]):
    BINDINGS = [("escape", "cancel", "Cancelar")]
    CSS = """
    VentanaConfirmarDescarte { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_discard { padding: 1 2; background: #262626; border: heavy #ff5f5f; width: 56; height: 12; }
    #buttons { margin-top: 1; height: 3; align: center middle; }
    Button { margin: 0 1; }
    """
    def __init__(self, nombre_archivo: str): super().__init__(); self.nombre_archivo = nombre_archivo
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(f"[bold #ff5f5f]\u00bfDescartar cambios?[/]\n\u00bfSeguro que quer\u00e9s descartar los cambios de [bold]{self.nombre_archivo}[/]?\n[dim]Esta acci\u00f3n no se puede deshacer.[/]"),
            Horizontal(Button("S\u00ed, descartar", variant="error", id="s"), Button("No", variant="primary", id="n"), id="buttons"),
            Label("[dim][ESC] Cancelar[/dim]"),
            id="dialog_discard"
        )
    def on_button_pressed(self, event: Button.Pressed) -> None: self.dismiss(True if event.button.id == "s" else False)
    def action_cancel(self) -> None: self.dismiss(False)


class VentanaConfirmarPush(ModalScreen[bool]):
    BINDINGS = [("escape", "cancel", "Cancelar")]
    CSS = """
    VentanaConfirmarPush { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_push { padding: 1 2; background: #262626; border: heavy #00afd7; width: 56; height: 12; }
    #buttons { margin-top: 1; height: 3; align: center middle; }
    Button { margin: 0 1; }
    """
    def __init__(self, branch: str): super().__init__(); self.branch = branch
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(f"[bold #00afd7]\u00bfPush a remoto?[/]\n\u00bfSubir commits de [bold]{self.branch}[/] al remoto?"),
            Horizontal(Button("S\u00ed", variant="primary", id="s"), Button("No", variant="default", id="n"), id="buttons"),
            Label("[dim][ESC] Cancelar[/dim]"),
            id="dialog_push"
        )
    def on_button_pressed(self, event: Button.Pressed) -> None: self.dismiss(True if event.button.id == "s" else False)
    def action_cancel(self) -> None: self.dismiss(False)


class VentanaConfirmarRebase(ModalScreen[bool]):
    BINDINGS = [("escape", "cancel", "Cancelar")]
    CSS = """
    VentanaConfirmarRebase { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_rebase { padding: 1 2; background: #262626; border: heavy #ffaf00; width: 56; height: 12; }
    #buttons { margin-top: 1; height: 3; align: center middle; }
    Button { margin: 0 1; }
    """
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("[bold #ffaf00]\u00bfEjecutar rebase?[/]\n\u00bfSeguro que quer\u00e9s ejecutar el rebase interactivo?\n[dim]Esto reescribe el historial de commits.[/]"),
            Horizontal(Button("S\u00ed", variant="warning", id="s"), Button("No", variant="primary", id="n"), id="buttons"),
            Label("[dim][ESC] Cancelar[/dim]"),
            id="dialog_rebase"
        )
    def on_button_pressed(self, event: Button.Pressed) -> None: self.dismiss(True if event.button.id == "s" else False)
    def action_cancel(self) -> None: self.dismiss(False)


class VentanaConfirmarAmend(ModalScreen[bool]):
    BINDINGS = [("escape", "cancel", "Cancelar")]
    CSS = """
    VentanaConfirmarAmend { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_amend { padding: 1 2; background: #262626; border: heavy #ffaf00; width: 56; height: 12; }
    #buttons { margin-top: 1; height: 3; align: center middle; }
    Button { margin: 0 1; }
    """
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("[bold #ffaf00]\u00bfAmend commit?[/]\n\u00bfSeguro que quer\u00e9s modificar el \u00faltimo commit?\n[dim]Esto reescribe el historial. Si ya lo pusheaste, vas a necesitar force push.[/]"),
            Horizontal(Button("S\u00ed", variant="warning", id="s"), Button("No", variant="primary", id="n"), id="buttons"),
            Label("[dim][ESC] Cancelar[/dim]"),
            id="dialog_amend"
        )
    def on_button_pressed(self, event: Button.Pressed) -> None: self.dismiss(True if event.button.id == "s" else False)
    def action_cancel(self) -> None: self.dismiss(False)


class VentanaConfirmarCherryPick(ModalScreen[bool]):
    BINDINGS = [("escape", "cancel", "Cancelar")]
    CSS = """
    VentanaConfirmarCherryPick { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_cherrypick { padding: 1 2; background: #262626; border: heavy #af5fff; width: 56; height: 12; }
    #buttons { margin-top: 1; height: 3; align: center middle; }
    Button { margin: 0 1; }
    """
    def __init__(self, sha: str): super().__init__(); self.sha = sha
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(f"[bold #af5fff]\u00bfCherry-pick?[/]\n\u00bfAplicar el commit [bold]{self.sha}[/] en la rama actual?"),
            Horizontal(Button("S\u00ed", variant="primary", id="s"), Button("No", variant="default", id="n"), id="buttons"),
            Label("[dim][ESC] Cancelar[/dim]"),
            id="dialog_cherrypick"
        )
    def on_button_pressed(self, event: Button.Pressed) -> None: self.dismiss(True if event.button.id == "s" else False)
    def action_cancel(self) -> None: self.dismiss(False)


class VentanaConfirmarStashPop(ModalScreen[bool]):
    BINDINGS = [("escape", "cancel", "Cancelar")]
    CSS = """
    VentanaConfirmarStashPop { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_stashpop { padding: 1 2; background: #262626; border: heavy #af5fff; width: 56; height: 12; }
    #buttons { margin-top: 1; height: 3; align: center middle; }
    Button { margin: 0 1; }
    """
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("[bold #af5fff]\u00bfStash Pop?[/]\n\u00bfRecuperar y aplicar el \u00faltimo stash?\n[dim]Puede causar conflictos si ten\u00e9s cambios sin commit.[/]"),
            Horizontal(Button("S\u00ed", variant="primary", id="s"), Button("No", variant="default", id="n"), id="buttons"),
            Label("[dim][ESC] Cancelar[/dim]"),
            id="dialog_stashpop"
        )
    def on_button_pressed(self, event: Button.Pressed) -> None: self.dismiss(True if event.button.id == "s" else False)
    def action_cancel(self) -> None: self.dismiss(False)


class VentanaConfirmarSalir(ModalScreen[bool]):
    BINDINGS = [("escape", "cancel", "Cancelar")]
    CSS = """
    VentanaConfirmarSalir { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_quit { padding: 1 2; background: #262626; border: heavy #888; width: 46; height: 11; }
    #buttons { margin-top: 1; height: 3; align: center middle; }
    Button { margin: 0 1; }
    """
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("[bold]\u00bfSalir de GitCriollo?[/]"),
            Horizontal(Button("S\u00ed", variant="error", id="s"), Button("No", variant="primary", id="n"), id="buttons"),
            Label("[dim][ESC] Cancelar[/dim]"),
            id="dialog_quit"
        )
    def on_button_pressed(self, event: Button.Pressed) -> None: self.dismiss(True if event.button.id == "s" else False)
    def action_cancel(self) -> None: self.dismiss(False)
