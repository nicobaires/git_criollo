import os

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Input, Button, TextArea, Static
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.screen import ModalScreen
from git import GitCommandError

from git_criollo.git_service import GitService
from git_criollo.ayuda import VentanaAyuda


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


# --- MODAL: CONFIRMAR MERGE ---
class VentanaConfirmarMerge(ModalScreen[bool]):
    BINDINGS = [("escape", "cancel", "Cancelar")]
    CSS = """
    VentanaConfirmarMerge { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_merge { padding: 1 2; background: #262626; border: heavy #00afd7; width: 56; height: 10; }
    #buttons { margin-top: 1; height: 3; align: center middle; }
    Button { margin: 0 1; }
    """
    def __init__(self, nombre_rama: str): super().__init__(); self.nombre_rama = nombre_rama
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(f"[bold #00afd7]¿Mergear?[/]\n¿Mergear [bold]{self.nombre_rama}[/] en la rama actual?"),
            Horizontal(Button("Sí", variant="primary", id="s"), Button("No", variant="default", id="n"), id="buttons"),
            id="dialog_merge"
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


# --- MODAL: STASH PUSH ---
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


# --- MODAL: VER DIFF ---

def _diff_coloreado(diff: str) -> str:
    lines = []
    for line in diff.split("\n"):
        safe = line.replace("[", "\\[")
        if line.startswith("diff --git") or line.startswith("index") or line.startswith("---") or line.startswith("+++"):
            lines.append(f"[#888888]{safe}[/]")
        elif line.startswith("@@"):
            lines.append(f"[#00afff]{safe}[/]")
        elif line.startswith("+"):
            lines.append(f"[#00ff00]{safe}[/]")
        elif line.startswith("-"):
            lines.append(f"[#ff5f5f]{safe}[/]")
        else:
            lines.append(safe)
    return "\n".join(lines)


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


# --- MODAL: AMEND COMMIT ---
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


# --- MODAL: DETALLE DE COMMIT ---
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


# --- MODAL: CREAR TAG ---
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


# --- MODAL: CONFIRMAR BORRADO TAG ---
class VentanaConfirmarBorradoTag(ModalScreen[bool]):
    BINDINGS = [("escape", "cancel", "Cancelar")]
    CSS = """
    VentanaConfirmarBorradoTag { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_tag_del { padding: 1 2; background: #262626; border: heavy #ff5f5f; width: 50; height: 10; }
    #buttons { margin-top: 1; height: 3; align: center middle; }
    Button { margin: 0 1; }
    """
    def __init__(self, nombre_tag: str): super().__init__(); self.nombre_tag = nombre_tag
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(f"[bold #ff5f5f]¿Borrar Tag?[/]\n¿Seguro que querés eliminar el tag [bold]{self.nombre_tag}[/]?"),
            Horizontal(Button("Sí", variant="error", id="s"), Button("No", variant="primary", id="n"), id="buttons"),
            id="dialog_tag_del"
        )
    def on_button_pressed(self, event: Button.Pressed) -> None: self.dismiss(True if event.button.id == "s" else False)
    def action_cancel(self) -> None: self.dismiss(False)


# --- MODAL: CHERRY-PICK ---
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


# --- MODAL: COMANDO PERSONALIZADO ---
class VentanaComando(ModalScreen[str]):
    BINDINGS = [("escape", "quit", "Cancelar")]
    CSS = """
    VentanaComando { align: center middle; background: rgba(0,0,0,0.6); }
    #dialog_cmd { padding: 1 2; background: #262626; border: heavy #ffaf00; width: 60; height: 11; }
    Input { margin-top: 1; }
    """
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("[bold #ffaf00]Comando Git[/]\nIngresá un comando (sin el prefijo 'git '):"),
            Input(placeholder="ej. log --oneline -3"),
            Label("\n[ESC para cancelar]"),
            id="dialog_cmd"
        )
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value.strip(): self.dismiss(event.value.strip())
    def action_quit(self) -> None: self.dismiss("")


# --- MODAL: RESULTADO DE COMANDO ---
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


# --- MODAL: CAMBIOS SIN COMMIT ---
class VentanaUncommitted(ModalScreen):
    BINDINGS = [
        ("escape", "quit", "Cerrar"),
        ("q", "quit", "Cerrar"),
        ("v", "ver_diff", "Ver Diff"),
        ("a", "stage_all", "Stage All"),
        ("w", "commit_cambios", "Commit"),
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
            Label("[bold #00afff]── CAMBIOS SIN COMMIT ──[/]"),
            Horizontal(
                Vertical(
                    Label("[bold]Archivos[/] (Enter: stage/unstage)"),
                    ListView(id="uc_file_list"),
                    Label("[dim][A] Stage All  [W] Commit  [V] Ver Diff  [Q] Cerrar[/dim]", id="uc_actions"),
                    id="uc_files",
                ),
                Vertical(
                    Label("[bold]Diff[/]", id="uc_diff_header"),
                    ScrollableContainer(Static("Seleccioná un archivo", markup=True), id="uc_diff_container"),
                    id="uc_diff_panel",
                ),
                id="uc_body",
            ),
            id="dialog_uc",
        )

    def on_mount(self) -> None:
        self._archivos: list[tuple[str, bool]] = []  # (ruta, is_staged)
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
            item = ListItem(Label(f"  ✔ {f}"))
            item.archivo_ruta = f
            item.archivo_staged = True
            lista.append(item)
        for f in info.unstaged:
            self._archivos.append((f, False))
            item = ListItem(Label(f"  💥 M: {f}"))
            item.archivo_ruta = f
            item.archivo_staged = False
            lista.append(item)
        for f in info.untracked:
            self._archivos.append((f, False))
            item = ListItem(Label(f"  ❓ ?: {f}"))
            item.archivo_ruta = f
            item.archivo_staged = False
            lista.append(item)

        if self._archivos:
            lista.index = 0
            self._actualizar_diff(self._archivos[0][0], self._archivos[0][1])

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
            self._actualizar_diff(ruta, staged)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if not item:
            return
        ruta = getattr(item, "archivo_ruta", None)
        if not ruta:
            return
        staged = getattr(item, "archivo_staged", False)
        try:
            if staged:
                self.git.unstage_file(ruta)
            else:
                self.git.stage_file(ruta)
            self._refrescar()
        except Exception as e:
            self._notify_error(e)

    def action_ver_diff(self) -> None:
        lista = self.query_one("#uc_file_list", ListView)
        item = lista.highlighted_child
        if not item:
            self.notify("Seleccioná un archivo.", severity="warning")
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
        except Exception as e:
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
                except Exception as e:
                    self._notify_error(e)

        self.app.push_screen(VentanaCommit(), guardar)

    def _notify_error(self, e: Exception) -> None:
        if isinstance(e, GitCommandError):
            msg = e.stderr.strip() if e.stderr else str(e)
        else:
            msg = str(e)
        self.notify(f"Error: {msg}", severity="error")

    def action_quit(self) -> None:
        self.dismiss()


# --- APLICACIÓN PRINCIPAL ---
class GitCriolloApp(App):
    BINDINGS = [
        ("q", "quit", "Salir"),
        ("n", "nueva_rama", "Nueva"),
        ("c", "cambiar_rama", "Checkout"),
        ("d", "eliminar_rama", "Borrar"),
        ("m", "merge_rama", "Merge"),
        ("p", "pull_rama", "Pull"),
        ("u", "push_rama", "Push"),
        ("f", "fetch_rama", "Fetch"),
        ("a", "stage_all", "Stage Todo"),
        ("w", "commit_cambios", "Commit"),
        ("z", "stash_push", "Stash Push"),
        ("Z", "stash_pop", "Stash Pop"),
        ("v", "ver_diff", "Ver Diff"),
        ("l", "mas_commits", "+Commits"),
        ("g", "toggle_grafico", "Log Graph"),
        ("e", "amend_commit", "Amend"),
        ("t", "crear_tag", "Tag+"),
        ("T", "eliminar_tag", "Tag-"),
        ("y", "cherry_pick", "Cherry"),
        ("r", "comando_personalizado", "Cmd"),
        ("?", "ayuda", "Ayuda"),
        ("C", "uncommitted", "Cambios"),
    ]

    CSS = """
    Horizontal { width: 100%; height: 100%; }
    .columna { width: 25%; height: 100%; border-right: solid #333; }
    .columna-derecha { width: 75%; height: 100%; }
    .panel { padding: 1; background: #121212; border-bottom: solid #222; }
    .panel-status { height: auto; }
    .panel-history { height: 1fr; }
    ListView { background: #1a1a1a; margin: 1; border: tall #444; }
    ListView:focus { border: tall #00afff; }
    #lista_ramas { height: 1fr; }
    #lista_ramas:focus { border: tall #00afd7; }
    #lista_staged { height: auto; max-height: 8; margin: 0 0 0 1; border: solid #333; }
    #lista_unstaged { height: auto; max-height: 8; margin: 0 0 0 1; border: solid #333; }
    #lista_commits { height: 1fr; margin: 1; border: solid #333; }
    #lista_commits:focus { border: tall #ffaf00; }
    ListItem { padding: 0 1; }
    ListItem.--highlight { background: #005f87; }
    Label { margin: 1 0 0 2; }
    .label-subtitle { margin: 0 0 0 2; text-style: bold; }
    #atajos_help { margin: 1 0 1 2; color: #888; height: auto; }
    #info_rama { margin: 0 0 0 2; color: #aaa; height: auto; }
    """

    def on_mount(self) -> None:
        try:
            self.git = GitService(os.getcwd())
            self._commit_offset = 0
            self._modo_grafico = False
            self.actualizar_pantalla_completa()
            self.set_interval(5, self.actualizar_status)
        except Exception:
            self.exit(message="Error: No estás dentro de un repositorio de Git.")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, id="header")
        yield Horizontal(
            Vertical(
                Label("[bold]MIS RAMAS[/]"),
                ListView(id="lista_ramas"),
                Label("", id="info_rama"),
                Label(
                    "[dim]Presioná [bold]?[/bold] para ayuda completa[/dim]",
                    id="atajos_help"
                ),
                classes="columna"
            ),
            Vertical(
                Vertical(
                    Label("[bold #00ff00]ESTADO DE ARCHIVOS[/]", classes="label-subtitle"),
                    Label("[bold #00ff00]Staged:[/]"),
                    ListView(id="lista_staged"),
                    Label("[bold #ff5f5f]Modificados / No trackeados:[/]"),
                    ListView(id="lista_unstaged"),
                    classes="panel panel-status"
                ),
                Vertical(
                    Label("[bold #ffaf00]HISTORIAL DE COMMITS[/]", classes="label-subtitle"),
                    ListView(id="lista_commits"),
                    classes="panel panel-history"
                ),
                classes="columna-derecha"
            )
        )
        yield Footer()

    def actualizar_pantalla_completa(self) -> None:
        """Método centralizado para refrescar toda la UI"""
        try:
            self.actualizar_ramas()
            self.actualizar_historial()
            self.actualizar_status()
            self.actualizar_header()
        except Exception as e:
            self.notify(f"Error al actualizar pantalla: {e}", severity="error")

    def actualizar_header(self) -> None:
        try:
            info = self.git.get_branches()
            a = info.ahead.get(info.active, 0)
            b = info.behind.get(info.active, 0)
            sufijo = f" [+{a} -{b}]" if a or b else ""
            self.sub_title = f"{info.active}{sufijo}"
        except Exception:
            self.sub_title = ""

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
            a = info.ahead.get(nombre, 0)
            b = info.behind.get(nombre, 0)
            if a or b:
                texto += f" [dim][+{a} -{b}][/dim]"
            item = ListItem(Label(texto))
            item.rama_objeto = nombre
            item.es_remota = False
            lista.append(item)

        if info.remotes:
            sep = ListItem(Label("[dim]── Remotas ──[/dim]"))
            sep.disabled = True
            lista.append(sep)
            for rm in info.remotes:
                item = ListItem(Label(f"  [dim]{rm}[/dim]"))
                item.rama_objeto = rm
                item.es_remota = True
                lista.append(item)

        if info.tags:
            sep = ListItem(Label("[dim]── Tags ──[/dim]"))
            sep.disabled = True
            lista.append(sep)
            for tg in info.tags:
                item = ListItem(Label(f"  [#ffaf00]●[/#ffaf00] {tg}"))
                item.rama_objeto = f"tag:{tg}"
                item.es_remota = False
                lista.append(item)

        if info.branches:
            lista.index = indice_activa

        info_label = self.query_one("#info_rama", Label)
        status = self.git.get_status()
        a = info.ahead.get(info.active, 0)
        b = info.behind.get(info.active, 0)
        partes = [f"[bold]{info.active}[/]"]
        if a or b:
            partes.append(f"[dim][+{a} -{b}][/dim]")
        dirty = bool(status.unstaged or status.untracked)
        icono = "[#ff5f5f]● sucio[/]" if dirty else "[#00ff00]● limpio[/]"
        partes.append(icono)
        info_label.update("  ".join(partes))

    def actualizar_historial(self) -> None:
        self._commit_offset = 0
        lista = self.query_one("#lista_commits", ListView)
        lista.clear()
        if self._modo_grafico:
            lineas = self.git.get_graph_log(skip=0, n=20)
            for linea in lineas:
                item = ListItem(Label(f"[dim]{linea}[/dim]"))
                lista.append(item)
            self._commit_offset = len(lineas)
        else:
            commits = self.git.get_commits(skip=0, n=20)
            for c in commits:
                item = ListItem(Label(
                    f"[#ffaf00]{c.hash}[/#ffaf00] - {c.message} [dim]({c.author})[/dim]"
                ))
                item.commit_hash = c.hash
                lista.append(item)
            self._commit_offset = len(commits)

    def actualizar_status(self) -> None:
        info = self.git.get_status()

        staged_list = self.query_one("#lista_staged", ListView)
        staged_list.clear()
        for f in info.staged:
            item = ListItem(Label(f"  ✔ {f}"))
            item.archivo_ruta = f
            item.archivo_staged = True
            staged_list.append(item)

        unstaged_list = self.query_one("#lista_unstaged", ListView)
        unstaged_list.clear()
        for f in info.unstaged:
            item = ListItem(Label(f"  💥 M: {f}"))
            item.archivo_ruta = f
            item.archivo_staged = False
            unstaged_list.append(item)
        for f in info.untracked:
            item = ListItem(Label(f"  ❓ ?: {f}"))
            item.archivo_ruta = f
            item.archivo_staged = False
            unstaged_list.append(item)

    # --- EVENTOS ---

    def key_tab(self) -> None:
        order = ["lista_ramas", "lista_staged", "lista_unstaged", "lista_commits"]
        focused = self.focused
        if focused and focused.id in order:
            idx = (order.index(focused.id) + 1) % len(order)
        else:
            idx = 0
        self.query_one(f"#{order[idx]}", ListView).focus()

    def _notify_error(self, e: Exception) -> None:
        if isinstance(e, GitCommandError):
            msg = e.stderr.strip() if e.stderr else str(e)
        else:
            msg = str(e)
        self.notify(f"Error: {msg}", severity="error")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        lista_id = event.list_view.id
        item = event.item
        if not item:
            return
        ruta = getattr(item, "archivo_ruta", None)
        if not ruta:
            return

        if lista_id == "lista_staged":
            try:
                self.git.unstage_file(ruta)
                self.notify(f"Unstage: {ruta}")
                self.actualizar_status()
            except Exception as e:
                self._notify_error(e)

        elif lista_id == "lista_unstaged":
            try:
                self.git.stage_file(ruta)
                self.notify(f"Stage: {ruta}")
                self.actualizar_status()
            except Exception as e:
                self._notify_error(e)

        elif lista_id == "lista_commits":
            sha = getattr(item, "commit_hash", None)
            if sha:
                self._mostrar_detalle_commit(sha)

        elif lista_id == "lista_ramas":
            r = getattr(item, "rama_objeto", None)
            if r and r.startswith("tag:"):
                tag_name = r[4:]
                self.push_screen(VentanaConfirmarBorradoTag(tag_name),
                                 lambda b, n=tag_name: self._borrar_tag_si_confirmado(b, n))

    # --- ACCIONES ---

    def action_ayuda(self) -> None:
        self.push_screen(VentanaAyuda())

    def action_uncommitted(self) -> None:
        self.push_screen(VentanaUncommitted())

    def action_nueva_rama(self) -> None:
        def p(n: str | None):
            if n:
                try:
                    self.git.create_branch(n)
                    self.notify(f"Rama '{n}' creada.")
                    self.actualizar_ramas()
                except Exception as e:
                    self._notify_error(e)
        self.push_screen(VentanaNuevaRama(), p)

    def action_cambiar_rama(self) -> None:
        lista = self.query_one("#lista_ramas", ListView)
        child = lista.highlighted_child
        if not child:
            return
        r = getattr(child, "rama_objeto", None)
        if not r:
            return
        es_remota = getattr(child, "es_remota", False)
        try:
            if es_remota:
                self.git.checkout_remote(r)
                self.notify(f"Checkout: {r}")
            else:
                self.git.checkout(r)
                self.notify(f"Checkout: {r}")
            # self.actualizar_ramas()
            # self.actualizar_status()
            self.actualizar_pantalla_completa()
        except Exception as e:
            self._notify_error(e)

    def action_eliminar_rama(self) -> None:
        lista = self.query_one("#lista_ramas", ListView)
        child = lista.highlighted_child
        if not child:
            return
        r = getattr(child, "rama_objeto", None)
        if not r or getattr(child, "es_remota", False):
            self.notify("No podés borrar una rama remota.", severity="error")
            return
        info = self.git.get_branches()
        if r.startswith("tag:"):
            tag_name = r[4:]
            self.push_screen(VentanaConfirmarBorradoTag(tag_name),
                             lambda b, n=tag_name: self._borrar_tag_si_confirmado(b, n))
            return
        if r == info.active:
            self.notify("No podés borrar la rama activa.", severity="error")
            return

        def p(b: bool | None):
            if b:
                try:
                    self.git.delete_branch(r)
                    self.notify(f"Borrada: {r}")
                    self.actualizar_pantalla_completa()
                except Exception as e:
                    self._notify_error(e)
        if r:
            self.push_screen(VentanaConfirmarBorrado(r), p)

    def action_merge_rama(self) -> None:
        lista = self.query_one("#lista_ramas", ListView)
        child = lista.highlighted_child
        if not child:
            return
        r = getattr(child, "rama_objeto", None)
        if not r or getattr(child, "es_remota", False):
            self.notify("Seleccioná una rama local.", severity="warning")
            return
        info = self.git.get_branches()
        if r == info.active:
            self.notify("Ya estás en esa rama.", severity="warning")
            return

        def p(b: bool | None):
            if b:
                try:
                    self.git.merge(r)
                    self.notify(f"Merged {r} en {info.active}")
                    # self.actualizar_historial()
                    # self.actualizar_status()
                    self.actualizar_pantalla_completa()
                except Exception as e:
                    self._notify_error(e)
        self.push_screen(VentanaConfirmarMerge(r), p)

    def action_pull_rama(self) -> None:
        self.notify("Git pull...")
        try:
            self.git.pull()
            self.notify("¡Pull OK!")
            # self.actualizar_historial()
            # self.actualizar_status()
            self.actualizar_pantalla_completa()
        except Exception as e:
            self._notify_error(e)

    # def action_push_rama(self) -> None:
    #     self.notify("Git push...")
    #     try:
    #         self.git.push(self.git.get_branches().active)
    #         self.notify("¡Push OK!")
    #     except Exception as e:
    #         self.notify(f"Falló: {e}", severity="error")

    def action_push_rama(self) -> None:
        self.notify("Git push...")
        try:
            active_branch = self.git.get_branches().active
            self.git.push(active_branch)
            self.notify("¡Push OK!")
            self.actualizar_pantalla_completa()   # ← Esto es lo importante
        except Exception as e:
            self._notify_error(e)

    def action_fetch_rama(self) -> None:
        self.notify("Git fetch...")
        try:
            self.git.fetch()
            self.notify("¡Fetch OK!")
            # self.actualizar_historial()
            # self.actualizar_ramas()
            self.actualizar_pantalla_completa()
        except Exception as e:
            self._notify_error(e)

    def action_stage_all(self) -> None:
        try:
            self.git.stage_all()
            self.notify("Todos los cambios agregados al Stage.")
            self.actualizar_status()
        except Exception as e:
            self._notify_error(e)

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
                    # self.actualizar_historial()
                    # self.actualizar_status()
                    self.actualizar_pantalla_completa()
                except Exception as e:
                    self._notify_error(e)

        self.push_screen(VentanaCommit(), guardar_commit)

    def action_stash_push(self) -> None:
        def p(val):
            if val is None:
                return
            try:
                self.git.stash_push(val)
                self.notify("Stash guardado.")
                self.actualizar_status()
            except Exception as e:
                self._notify_error(e)
        self.push_screen(VentanaStashPush(), p)

    def action_stash_pop(self) -> None:
        try:
            self.git.stash_pop()
            self.notify("Stash recuperado.")
            self.actualizar_status()
        except Exception as e:
            self._notify_error(e)

    def action_ver_diff(self) -> None:
        focused = self.focused
        if not focused or focused.id not in ("lista_staged", "lista_unstaged"):
            self.notify("Seleccioná un archivo en el panel de estado.", severity="warning")
            return
        item = focused.highlighted_child
        if not item:
            return
        ruta = getattr(item, "archivo_ruta", None)
        if not ruta:
            return
        staged = focused.id == "lista_staged"
        diff = self.git.get_diff(ruta, staged=staged)
        self.push_screen(VentanaDiff(ruta, diff))

    def action_toggle_grafico(self) -> None:
        self._modo_grafico = not self._modo_grafico
        self.actualizar_historial()
        modo = "gráfico" if self._modo_grafico else "detalle"
        self.notify(f"Modo historial: {modo}")

    def action_mas_commits(self) -> None:
        lista = self.query_one("#lista_commits", ListView)
        n = 20
        if self._modo_grafico:
            lineas = self.git.get_graph_log(skip=self._commit_offset, n=n)
            for linea in lineas:
                item = ListItem(Label(f"[dim]{linea}[/dim]"))
                lista.append(item)
            if lineas:
                self._commit_offset += len(lineas)
            else:
                self.notify("No hay más commits.")
        else:
            commits = self.git.get_commits(skip=self._commit_offset, n=n)
            for c in commits:
                item = ListItem(Label(
                    f"[#ffaf00]{c.hash}[/#ffaf00] - {c.message} [dim]({c.author})[/dim]"
                ))
                item.commit_hash = c.hash
                lista.append(item)
            if commits:
                self._commit_offset += len(commits)
            else:
                self.notify("No hay más commits.")

    def _mostrar_detalle_commit(self, sha: str) -> None:
        try:
            detail = self.git.get_commit_detail(sha)
            meta = f"[bold]Autor:[/] {detail.author}    [bold]Fecha:[/] {detail.date}\n\n{detail.message}"
            self.push_screen(VentanaDetalleCommit(sha, meta, detail.diff))
        except Exception as e:
            self._notify_error(e)

    def _borrar_tag_si_confirmado(self, b: bool | None, tag_name: str) -> None:
        if b:
            try:
                self.git.delete_tag(tag_name)
                self.notify(f"Tag '{tag_name}' borrado.")
                self.actualizar_ramas()
            except Exception as e:
                self._notify_error(e)

    def action_amend_commit(self) -> None:
        history = self.query_one("#lista_commits", ListView)
        if not history.children:
            self.notify("No hay commits para modificar.", severity="warning")
            return

        def p(mensaje: str | None):
            if mensaje:
                try:
                    self.git.amend_commit(mensaje)
                    self.notify("Commit modificado (amend).")
                    self.actualizar_pantalla_completa()
                except Exception as e:
                    self._notify_error(e)

        self.push_screen(VentanaAmend(), p)

    def action_crear_tag(self) -> None:
        def p(nombre: str | None):
            if nombre:
                try:
                    self.git.create_tag(nombre)
                    self.notify(f"Tag '{nombre}' creado.")
                    self.actualizar_ramas()
                except Exception as e:
                    self._notify_error(e)

        self.push_screen(VentanaTag(), p)

    def action_eliminar_tag(self) -> None:
        info = self.git.get_branches()
        if not info.tags:
            self.notify("No hay tags para borrar.", severity="warning")
            return
        tags = ", ".join(info.tags)
        self.notify(f"Seleccioná un tag en la lista de ramas y presioná [bold]D[/bold] para borrarlo: {tags}")

    def action_cherry_pick(self) -> None:
        def p(sha: str | None):
            if sha:
                try:
                    self.git.cherry_pick(sha)
                    self.notify(f"Cherry-pick de {sha} aplicado.")
                    self.actualizar_pantalla_completa()
                except Exception as e:
                    self._notify_error(e)

        self.push_screen(VentanaCherryPick(), p)

    def action_comando_personalizado(self) -> None:
        def p(cmd: str | None):
            if cmd:
                try:
                    resultado = self.git.run_command(cmd)
                    self.push_screen(VentanaResultado(f"Resultado: git {cmd}", resultado))
                except Exception as e:
                    self._notify_error(e)

        self.push_screen(VentanaComando(), p)
