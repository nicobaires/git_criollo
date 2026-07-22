from textual.app import ComposeResult
from textual.widgets import Input, Label, Vertical
from textual.screen import ModalScreen


class VentanaNuevaRama(ModalScreen[str]):
    BINDINGS = [("escape", "quit", "Cancelar")]
    CSS = """
    VentanaNuevaRama { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_create { padding: 1 2; background: #262626; border: heavy #00afd7; width: 50; height: 11; }
    Input { margin-top: 1; }
    """
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("[bold #00afd7]Crear Nueva Rama[/]\nNombre de la rama:"),
            Input(placeholder="ej. mejora-interfaz"),
            Label("\n[ESC para cancelar]"),
            id="dialog_create"
        )
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value.strip(): self.dismiss(event.value.strip())
    def action_quit(self) -> None: self.dismiss("")


class VentanaCommit(ModalScreen[str]):
    BINDINGS = [("escape", "quit", "Cancelar")]
    CSS = """
    VentanaCommit { align: center middle; background: rgba(0, 0, 0, 0.6); }
    #dialog_commit { padding: 1 2; background: #262626; border: heavy #ffaf00; width: 60; height: 11; }
    Input { margin-top: 1; }
    """
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("[bold #ffaf00]Confirmar Commit[/]\nEscribe el mensaje del commit y presiona Enter:"),
            Input(placeholder="ej. fix: corrige error en ventana modal"),
            Label("\n[Presiona ESC para cancelar]"),
            id="dialog_commit"
        )
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value.strip(): self.dismiss(event.value.strip())
    def action_quit(self) -> None: self.dismiss("")


class VentanaStashPush(ModalScreen):
    BINDINGS = [("escape", "quit", "Cancelar")]
    CSS = """
    VentanaStashPush { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_stash { padding: 1 2; background: #262626; border: heavy #af5fff; width: 60; height: 11; }
    Input { margin-top: 1; }
    """
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("[bold #af5fff]Stash Push[/]\nMensaje (opcional, Enter para stash sin mensaje):"),
            Input(placeholder="mensaje opcional"),
            Label("\n[ESC para cancelar]"),
            id="dialog_stash"
        )
    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value.strip())
    def action_quit(self) -> None: self.dismiss(None)


class VentanaAmend(ModalScreen[str]):
    BINDINGS = [("escape", "quit", "Cancelar")]
    CSS = """
    VentanaAmend { align: center middle; background: rgba(0, 0, 0, 0.6); }
    #dialog_amend { padding: 1 2; background: #262626; border: heavy #ffaf00; width: 60; height: 11; }
    Input { margin-top: 1; }
    """
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("[bold #ffaf00]Amend Commit[/]\nNuevo mensaje del commit:"),
            Input(placeholder="ej. fix: corrige error en ventana modal"),
            Label("\n[Presiona ESC para cancelar]"),
            id="dialog_amend"
        )
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value.strip(): self.dismiss(event.value.strip())
    def action_quit(self) -> None: self.dismiss("")


class VentanaTag(ModalScreen[str]):
    BINDINGS = [("escape", "quit", "Cancelar")]
    CSS = """
    VentanaTag { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_tag { padding: 1 2; background: #262626; border: heavy #00afd7; width: 50; height: 11; }
    Input { margin-top: 1; }
    """
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("[bold #00afd7]Crear Tag[/]\nNombre del tag:"),
            Input(placeholder="ej. v1.0.0"),
            Label("\n[ESC para cancelar]"),
            id="dialog_tag"
        )
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value.strip(): self.dismiss(event.value.strip())
    def action_quit(self) -> None: self.dismiss("")


class VentanaCherryPick(ModalScreen[str]):
    BINDINGS = [("escape", "quit", "Cancelar")]
    CSS = """
    VentanaCherryPick { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_cherry { padding: 1 2; background: #262626; border: heavy #af5fff; width: 60; height: 11; }
    Input { margin-top: 1; }
    """
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("[bold #af5fff]Cherry-Pick[/]\nSHA del commit a aplicar:"),
            Input(placeholder="ej. a1b2c3d"),
            Label("\n[ESC para cancelar]"),
            id="dialog_cherry"
        )
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value.strip(): self.dismiss(event.value.strip())
    def action_quit(self) -> None: self.dismiss("")


class VentanaComando(ModalScreen[str]):
    BINDINGS = [("escape", "quit", "Cancelar")]
    CSS = """
    VentanaComando { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_cmd { padding: 1 2; background: #262626; border: heavy #ffaf00; width: 60; height: 11; }
    Input { margin-top: 1; }
    """
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("[bold #ffaf00]Comando Git[/]\nIngres\u00e1 un comando (sin el prefijo 'git '):"),
            Input(placeholder="ej. log --oneline -3"),
            Label("\n[ESC para cancelar]"),
            id="dialog_cmd"
        )
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value.strip(): self.dismiss(event.value.strip())
    def action_quit(self) -> None: self.dismiss("")
