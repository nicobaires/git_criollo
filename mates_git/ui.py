import os

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Input, Button
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen

from mates_git.git_service import GitService


# --- MODAL: CREAR NUEVA RAMA ---
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


# --- MODAL: CONFIRMAR BORRADO ---
class VentanaConfirmarBorrado(ModalScreen[bool]):
    BINDINGS = [("escape", "cancel", "Cancelar")]
    CSS = """
    VentanaConfirmarBorrado { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_delete { padding: 1 2; background: #262626; border: heavy #ff5f5f; width: 50; height: 10; }
    #buttons { margin-top: 1; height: 3; align: center middle; }
    Button { margin: 0 1; }
    """
    def __init__(self, nombre_rama: str): super().__init__(); self.nombre_rama = nombre_rama
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(f"[bold #ff5f5f]¿Borrar Rama?[/]\n¿Seguro que querés eliminar [bold]{self.nombre_rama}[/]?"),
            Horizontal(Button("Sí", variant="error", id="s"), Button("No", variant="primary", id="n"), id="buttons"),
            id="dialog_delete"
        )
    def on_button_pressed(self, event: Button.Pressed) -> None: self.dismiss(True if event.button.id == "s" else False)
    def action_cancel(self) -> None: self.dismiss(False)


# --- MODAL: ESCRIBIR MENSAJE DE COMMIT ---
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


# --- APLICACIÓN PRINCIPAL ---
class MiLazyGitRamas(App):
    BINDINGS = [
        ("q", "quit", "Salir"),
        ("n", "nueva_rama", "Nueva"),
        ("c", "cambiar_rama", "Checkout"),
        ("d", "eliminar_rama", "Borrar"),
        ("p", "pull_rama", "Pull"),
        ("u", "push_rama", "Push"),
        ("a", "stage_all", "Stage Todo"),
        ("w", "commit_cambios", "Commit"),
    ]

    CSS = """
    Horizontal { width: 100%; height: 100%; }
    .columna { width: 40%; height: 100%; border-right: solid #333; }
    .columna-derecha { width: 60%; height: 100%; }
    .panel { height: 50%; padding: 1; background: #121212; border-bottom: solid #222; }
    ListView { background: #1a1a1a; margin: 1; border: tall #444; height: 65%; }
    ListItem { padding: 0 1; }
    ListItem.--highlight { background: #005f87; }
    Label { margin: 1 0 0 2; }
    #atajos_help { margin: 1 0 1 2; color: #888; height: 25%; }
    #panel_status { overflow-y: auto; height: 1fr; }
    #panel_derecho { overflow-y: auto; height: 1fr; }
    """

    def on_mount(self) -> None:
        try:
            self.git = GitService(os.getcwd())
            self.actualizar_pantalla()
        except Exception:
            self.exit(message="Error: No estás dentro de un repositorio de Git.")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, id="header")
        yield Horizontal(
            Vertical(
                Label("[bold]MIS RAMAS (Local)[/]"),
                ListView(id="lista_ramas"),
                Label(
                    "[bold #00afd7][N][/] Nueva  [bold #00ff00][C][/] Checkout  [bold #ff5f5f][D][/] Borrar\n"
                    "[bold #ffaf00][P][/] Pull   [bold #ffaf00][U][/] Push      [bold #888888][Q][/] Salir\n"
                    "[bold #00ff00][A][/] Stage Todo           [bold #ffaf00][W][/] Commit",
                    id="atajos_help"
                ),
                classes="columna"
            ),
            Vertical(
                Vertical(
                    Label("[bold #00ff00]ESTADO DE ARCHIVOS (git status)[/]"),
                    Label("Buscando cambios...", id="panel_status"),
                    classes="panel"
                ),
                Vertical(
                    Label("[bold #ffaf00]HISTORIAL DE COMMITS[/]"),
                    Label("Cargando historial...", id="panel_derecho"),
                    classes="panel"
                ),
                classes="columna-derecha"
            )
        )
        yield Footer()

    def actualizar_pantalla(self) -> None:
        self.actualizar_ramas()
        self.actualizar_historial()
        self.actualizar_status()

    def actualizar_ramas(self) -> None:
        info = self.git.get_branches()
        lista = self.query_one("#lista_ramas", ListView)
        lista.clear()
        indice_activa = 0
        for orden, nombre in enumerate(info.branches):
            if nombre == info.active:
                texto = f"🌟 [bold #00ff00]{nombre} (Actual)[/]"
                indice_activa = orden
            else:
                texto = f"  {nombre}"
            item = ListItem(Label(texto))
            item.rama_objeto = nombre
            lista.append(item)
        if info.branches:
            lista.index = indice_activa

    def actualizar_historial(self) -> None:
        visor_log = self.query_one("#panel_derecho", Label)
        commits = self.git.get_commits()
        if commits:
            texto_log = "".join(
                f"[#ffaf00]{c.hash}[/#ffaf00] - {c.message} [dim]({c.author})[/dim]\n"
                for c in commits
            )
            visor_log.update(texto_log)
        else:
            visor_log.update("No hay commits.")

    def actualizar_status(self) -> None:
        visor_status = self.query_one("#panel_status", Label)
        info = self.git.get_status()
        texto_status = ""
        if info.is_empty_repo:
            texto_status += "[bold #ffaf00]⚠ ¡Primer commit del repositorio![/]\n\n"
        if info.staged:
            texto_status += "[bold #00ff00]En Stage (Para commit):[/]\n"
            for f in info.staged:
                texto_status += f"  ✔ {f}\n"
        if info.unstaged or info.untracked:
            texto_status += "[bold #ff5f5f]Modificados / No trackeados:[/]\n"
            for f in info.unstaged:
                texto_status += f"  💥 M: {f}\n"
            for f in info.untracked:
                texto_status += f"  ❓ ?: {f}\n"
        visor_status.update(
            texto_status if texto_status else "[#00ff00]✔ Directorio de trabajo limpio[/]"
        )

    def action_nueva_rama(self) -> None:
        def p(n: str | None):
            if n:
                try:
                    self.git.create_branch(n)
                    self.notify(f"Rama '{n}' creada.")
                    self.actualizar_ramas()
                except Exception as e:
                    self.notify(f"Error: {e}", severity="error")
        self.push_screen(VentanaNuevaRama(), p)

    def action_cambiar_rama(self) -> None:
        lista = self.query_one("#lista_ramas", ListView)
        if lista.highlighted_child and (r := getattr(lista.highlighted_child, "rama_objeto", None)):
            try:
                self.git.checkout(r)
                self.notify(f"Checkout: {r}")
                self.actualizar_ramas()
                self.actualizar_status()
            except Exception as e:
                self.notify(f"Error: {e}", severity="error")

    def action_eliminar_rama(self) -> None:
        lista = self.query_one("#lista_ramas", ListView)
        if not lista.highlighted_child:
            return
        r = getattr(lista.highlighted_child, "rama_objeto", None)
        info = self.git.get_branches()
        if r == info.active:
            self.notify("No podés borrar la rama activa.", severity="error")
            return

        def p(b: bool | None):
            if b:
                try:
                    self.git.delete_branch(r)
                    self.notify(f"Borrada: {r}")
                    self.actualizar_ramas()
                except Exception as e:
                    self.notify(f"Error: {e}", severity="error")
        if r:
            self.push_screen(VentanaConfirmarBorrado(r), p)

    def action_pull_rama(self) -> None:
        self.notify("Git pull...")
        try:
            self.git.pull()
            self.notify("¡Pull OK!")
            self.actualizar_historial()
            self.actualizar_status()
        except Exception as e:
            self.notify(f"Falló: {e}", severity="error")

    def action_push_rama(self) -> None:
        self.notify("Git push...")
        try:
            self.git.push(self.git.get_branches().active)
            self.notify("¡Push OK!")
        except Exception as e:
            self.notify(f"Falló: {e}", severity="error")

    def action_stage_all(self) -> None:
        try:
            self.git.stage_all()
            self.notify("Todos los cambios agregados al Stage.")
            self.actualizar_status()
        except Exception as e:
            self.notify(f"Error al agregar: {e}", severity="error")

    def action_commit_cambios(self) -> None:
        info = self.git.get_status()
        if not info.staged and not info.untracked and not info.is_empty_repo:
            self.notify("No hay cambios para confirmar en un commit.", severity="warning")
            return

        def guardar_commit(mensaje: str | None) -> None:
            if mensaje:
                try:
                    self.git.commit(mensaje)
                    self.notify("¡Commit creado con éxito!")
                    self.actualizar_historial()
                    self.actualizar_status()
                except Exception as e:
                    self.notify(f"Error en commit: {e}", severity="error")

        self.push_screen(VentanaCommit(), guardar_commit)
