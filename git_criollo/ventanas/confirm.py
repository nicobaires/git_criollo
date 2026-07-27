from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Button, Label
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen


class VentanaConfirmar(ModalScreen[bool]):
    """Diálogo de confirmación genérico y estilizado."""

    BINDINGS = [
        ("escape", "cancel", "Cancelar"),
        ("left", "focus_no", ""),
        ("right", "focus_si", ""),
    ]

    CSS = """
    VentanaConfirmar {
        align: center middle;
        background: rgba(0,0,0,0.65);
    }
    #dialog_box {
        padding: 1 2 0 2;
        background: $surface;
        border: heavy $accent;
        width: 52;
        height: auto;
    }
    #dialog_title {
        text-align: center;
        width: 100%;
        margin-bottom: 0;
    }
    #dialog_sep {
        text-align: center;
        width: 100%;
        color: $accent;
        margin: 0 0 0 0;
    }
    #dialog_msg {
        width: 100%;
        text-align: center;
        margin: 0 0 0 0;
    }
    #dialog_warning {
        width: 100%;
        text-align: center;
        margin: 0 0 1 0;
    }
    #dialog_buttons {
        height: 3;
        align: center middle;
        margin: 0;
    }
    #dialog_buttons Button {
        margin: 0 1;
    }
    #dialog_hint {
        text-align: center;
        width: 100%;
        margin: 0 0 0 0;
    }
    """

    def __init__(
        self,
        titulo: str,
        mensaje: str,
        warning: str = "",
        color: str = "#888",
        texto_si: str = "Sí",
        variante_si: str = "primary",
    ):
        super().__init__()
        self._titulo = titulo
        self._mensaje = mensaje
        self._warning = warning
        self._color = color
        self._texto_si = texto_si
        self._variante_si = variante_si

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog_box"):
            yield Label(self._titulo, id="dialog_title")
            yield Label("─ ─ ─ ─ ─", id="dialog_sep")
            yield Label(self._mensaje, id="dialog_msg")
            if self._warning:
                yield Label(self._warning, id="dialog_warning")
            with Horizontal(id="dialog_buttons"):
                yield Button(self._texto_si, variant=self._variante_si, id="si")
                yield Button("No", variant="default", id="no")
            yield Label("[dim]ESC para cancelar[/dim]", id="dialog_hint")

    def on_mount(self) -> None:
        self.query_one("#dialog_box").styles.border_color = self._color
        self.query_one("#dialog_sep").styles.color = self._color
        if self._warning:
            self.query_one("#dialog_warning").styles.color = self._color

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "si")

    def action_cancel(self) -> None:
        self.dismiss(False)

    def action_focus_no(self) -> None:
        self.query_one("#no", Button).focus()

    def action_focus_si(self) -> None:
        self.query_one("#si", Button).focus()


def confirmar_borrado_rama(nombre: str) -> VentanaConfirmar:
    return VentanaConfirmar(
        titulo="🗑  ¿Borrar rama?",
        mensaje=f"¿Seguro que querés eliminar [bold]{nombre}[/]?",
        warning="[bold]Esta acción no se puede deshacer.[/]",
        color="#ff5f5f",
        texto_si="Sí, borrar",
        variante_si="error",
    )


def confirmar_merge(nombre: str) -> VentanaConfirmar:
    return VentanaConfirmar(
        titulo="🔀  ¿Mergear?",
        mensaje=f"¿Mergear [bold]{nombre}[/] en la rama actual?",
        color="#00afd7",
        texto_si="Sí, mergear",
        variante_si="primary",
    )


def confirmar_borrado_tag(nombre: str) -> VentanaConfirmar:
    return VentanaConfirmar(
        titulo="🏷  ¿Borrar tag?",
        mensaje=f"¿Seguro que querés eliminar el tag [bold]{nombre}[/]?",
        warning="[bold]Esta acción no se puede deshacer.[/]",
        color="#ff5f5f",
        texto_si="Sí, borrar",
        variante_si="error",
    )


def confirmar_descarte(ruta: str) -> VentanaConfirmar:
    return VentanaConfirmar(
        titulo="🗑  ¿Descartar cambios?",
        mensaje=f"¿Seguro que querés descartar los cambios de [bold]{ruta}[/]?",
        warning="[bold]Esta acción no se puede deshacer.[/]",
        color="#ff5f5f",
        texto_si="Sí, descartar",
        variante_si="error",
    )


def confirmar_push(branch: str) -> VentanaConfirmar:
    return VentanaConfirmar(
        titulo="⬆  ¿Push a remoto?",
        mensaje=f"¿Subir commits de [bold]{branch}[/] al remoto?",
        color="#00afd7",
        texto_si="Sí, push",
        variante_si="primary",
    )


def confirmar_rebase() -> VentanaConfirmar:
    return VentanaConfirmar(
        titulo="⚠  ¿Ejecutar rebase?",
        mensaje="¿Seguro que querés ejecutar el rebase interactivo?",
        warning="[bold]Esto reescribe el historial de commits.[/]",
        color="#ffaf00",
        texto_si="Sí, rebase",
        variante_si="warning",
    )


def confirmar_amend() -> VentanaConfirmar:
    return VentanaConfirmar(
        titulo="✏  ¿Amend commit?",
        mensaje="¿Seguro que querés modificar el último commit?",
        warning="[bold]Esto reescribe el historial. Si ya lo pusheaste, vas a necesitar force push.[/]",
        color="#ffaf00",
        texto_si="Sí, amend",
        variante_si="warning",
    )


def confirmar_cherrypick(sha: str) -> VentanaConfirmar:
    return VentanaConfirmar(
        titulo="🍒  ¿Cherry-pick?",
        mensaje=f"¿Aplicar el commit [bold]{sha}[/] en la rama actual?",
        color="#af5fff",
        texto_si="Sí, cherry-pick",
        variante_si="primary",
    )


def confirmar_stash_pop() -> VentanaConfirmar:
    return VentanaConfirmar(
        titulo="📦  ¿Stash Pop?",
        mensaje="¿Recuperar y aplicar el último stash?",
        warning="Puede causar conflictos si tenés cambios sin commit.",
        color="#af5fff",
        texto_si="Sí, pop",
        variante_si="primary",
    )


def confirmar_salir() -> VentanaConfirmar:
    return VentanaConfirmar(
        titulo="👋  ¿Salir de GitCriollo?",
        mensaje="",
        color="#888",
        texto_si="Sí, salir",
        variante_si="error",
    )
