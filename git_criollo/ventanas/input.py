from textual.app import ComposeResult
from textual.widgets import Input, Label
from textual.containers import Vertical
from textual.screen import ModalScreen


class VentanaInput(ModalScreen[str]):
    """Diálogo de input genérico y estilizado."""

    BINDINGS = [("escape", "quit", "Cancelar")]

    CSS = """
    VentanaInput { align: center middle; background: rgba(0,0,0,0.6); }
    #input_box { padding: 1 2; background: $surface; border: heavy $accent; width: 56; height: 11; }
    #input_box Input { margin-top: 1; }
    #input_hint { margin-top: 0; }
    """

    def __init__(
        self,
        titulo: str,
        descripcion: str,
        placeholder: str = "",
        color: str = "#888",
        width: int = 56,
    ):
        super().__init__()
        self._titulo = titulo
        self._descripcion = descripcion
        self._placeholder = placeholder
        self._color = color
        self._width = width

    def compose(self) -> ComposeResult:
        with Vertical(id="input_box"):
            yield Label(f"[bold {self._color}]{self._titulo}[/]\n{self._descripcion}")
            yield Input(placeholder=self._placeholder)
            yield Label("\n[dim]ESC para cancelar[/dim]", id="input_hint")

    def on_mount(self) -> None:
        self.query_one("#input_box").styles.border_color = self._color
        self.query_one("#input_box").styles.width = self._width

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value.strip():
            self.dismiss(event.value.strip())

    def action_quit(self) -> None:
        self.dismiss("")


def VentanaNuevaRama() -> VentanaInput:
    return VentanaInput(
        titulo="Crear Nueva Rama",
        descripcion="Nombre de la rama:",
        placeholder="ej. mejora-interfaz",
        color="#00afd7",
        width=50,
    )


def VentanaCommit() -> VentanaInput:
    return VentanaInput(
        titulo="Confirmar Commit",
        descripcion="Escribe el mensaje del commit y presiona Enter:",
        placeholder="ej. fix: corrige error en ventana modal",
        color="#ffaf00",
        width=60,
    )


def VentanaStashPush() -> VentanaInput:
    return VentanaInput(
        titulo="Stash Push",
        descripcion="Mensaje (opcional, Enter para stash sin mensaje):",
        placeholder="mensaje opcional",
        color="#af5fff",
        width=60,
    )


def VentanaAmend() -> VentanaInput:
    return VentanaInput(
        titulo="Amend Commit",
        descripcion="Nuevo mensaje del commit:",
        placeholder="ej. fix: corrige error en ventana modal",
        color="#ffaf00",
        width=60,
    )


def VentanaTag() -> VentanaInput:
    return VentanaInput(
        titulo="Crear Tag",
        descripcion="Nombre del tag:",
        placeholder="ej. v1.0.0",
        color="#00afd7",
        width=50,
    )


def VentanaCherryPick() -> VentanaInput:
    return VentanaInput(
        titulo="Cherry-Pick",
        descripcion="SHA del commit a aplicar:",
        placeholder="ej. a1b2c3d",
        color="#af5fff",
        width=60,
    )


def VentanaComando() -> VentanaInput:
    return VentanaInput(
        titulo="Comando Git",
        descripcion="Ingresá un comando (sin el prefijo 'git '):",
        placeholder="ej. log --oneline -3",
        color="#ffaf00",
        width=60,
    )
