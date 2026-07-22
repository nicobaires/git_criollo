from textual.app import ComposeResult
from textual.widgets import ListView, ListItem, Label, Input, Button, TextArea, Static
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.screen import ModalScreen
from git import GitCommandError

from git_criollo.diff_utils import _diff_coloreado
from git_criollo.error_utils import notify_error as _error_base


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
            Label(f"[bold #ff5f5f]¿Borrar Rama?[/]\n¿Seguro que querés eliminar [bold]{self.nombre_rama}[/]?"),
            Horizontal(Button("Sí", variant="error", id="s"), Button("No", variant="primary", id="n"), id="buttons"),
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
            Label(f"[bold #00afd7]¿Mergear?[/]\n¿Mergear [bold]{self.nombre_rama}[/] en la rama actual?"),
            Horizontal(Button("Sí", variant="primary", id="s"), Button("No", variant="default", id="n"), id="buttons"),
            Label("[dim][ESC] Cancelar[/dim]"),
            id="dialog_merge"
        )
    def on_button_pressed(self, event: Button.Pressed) -> None: self.dismiss(True if event.button.id == "s" else False)
    def action_cancel(self) -> None: self.dismiss(False)


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
            Label(f"[bold #ff5f5f]¿Borrar Tag?[/]\n¿Seguro que querés eliminar el tag [bold]{self.nombre_tag}[/]?"),
            Horizontal(Button("Sí", variant="error", id="s"), Button("No", variant="primary", id="n"), id="buttons"),
            Label("[dim][ESC] Cancelar[/dim]"),
            id="dialog_tag_del"
        )
    def on_button_pressed(self, event: Button.Pressed) -> None: self.dismiss(True if event.button.id == "s" else False)
    def action_cancel(self) -> None: self.dismiss(False)


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
            Label("[bold #ffaf00]Comando Git[/]\nIngresá un comando (sin el prefijo 'git '):"),
            Input(placeholder="ej. log --oneline -3"),
            Label("\n[ESC para cancelar]"),
            id="dialog_cmd"
        )
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value.strip(): self.dismiss(event.value.strip())
    def action_quit(self) -> None: self.dismiss("")


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


class VentanaStageHunk(ModalScreen[bool]):
    BINDINGS = [
        ("escape", "quit", "Cancelar"),
        ("q", "quit", "Cancelar"),
        ("y", "stage", "Stage"),
        ("n", "skip", "Skip"),
    ]
    CSS = """
    VentanaStageHunk { align: center middle; background: rgba(0,0,0,0.85); }
    #dialog_hunk { padding: 1; background: #121212; border: heavy #00afff; width: 80%; height: 80%; }
    #hunk_header { height: auto; margin-bottom: 1; }
    #hunk_body { height: 1fr; }
    #hunk_body Static { background: #1a1a1a; padding: 1; }
    #hunk_footer { height: auto; color: #888; margin-top: 1; }
    """
    def __init__(self, path: str, diff_utils_module=None):
        super().__init__()
        self.path = path
        self._hunks: list = []
        self._idx = 0

    @property
    def git(self):
        return self.app.git

    def on_mount(self) -> None:
        self._hunks = self.git.parse_diff_hunks(self.path)
        if not self._hunks:
            self.notify("No hay hunks para stagear.", severity="warning")
            self.dismiss(False)
            return
        self._idx = 0
        self._mostrar_hunk()

    def _mostrar_hunk(self) -> None:
        if self._idx >= len(self._hunks):
            self.notify("No quedan más hunks.", severity="information")
            self.dismiss(True)
            return
        hunk = self._hunks[self._idx]
        header = self.query_one("#hunk_header", Label)
        header.update(f"[bold #00afff]{self.path}[/] — Hunk {self._idx + 1} de {len(self._hunks)}")
        body = self.query_one("#hunk_body", ScrollableContainer)
        body.remove_children()
        body.mount(Static(_diff_coloreado(hunk.raw), markup=True))

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("", id="hunk_header"),
            ScrollableContainer(Static(""), id="hunk_body"),
            Label("[dim][[y]] Stage  [[n]] Skip  [[q]] Cerrar[/dim]", id="hunk_footer"),
            id="dialog_hunk",
        )

    def action_stage(self) -> None:
        if self._idx >= len(self._hunks):
            return
        try:
            self.git.stage_hunk(self.path, self._hunks[self._idx])
            self._hunks = self.git.parse_diff_hunks(self.path)
            self._mostrar_hunk()
        except (GitCommandError, RuntimeError) as e:
            self._notify_error(e)
        except Exception as e:
            self._notify_error(e)

    def action_skip(self) -> None:
        self._idx += 1
        self._mostrar_hunk()

    def _notify_error(self, e: Exception) -> None:
        if isinstance(e, (KeyboardInterrupt, SystemExit)):
            raise
        _error_base(self.notify, e, timeout=10)

    def action_quit(self) -> None:
        self.dismiss(True)


class VentanaRebase(ModalScreen[list[tuple[str, str]] | None]):
    BINDINGS = [
        ("escape", "quit", "Cancelar"),
        ("q", "quit", "Cancelar"),
        ("p", "pick", "Pick"),
        ("r", "reword", "Reword"),
        ("s", "squash", "Squash"),
        ("f", "fixup", "Fixup"),
        ("d", "drop", "Drop"),
        ("enter", "execute", "Ejecutar"),
    ]
    CSS = """
    VentanaRebase { align: center middle; background: rgba(0,0,0,0.85); }
    #dialog_rebase { padding: 1; background: #121212; border: heavy #ffaf00; width: 80%; height: 80%; }
    #rebase_header { height: auto; margin-bottom: 1; }
    #rebase_list { height: 1fr; border: tall #444; }
    #rebase_list:focus { border: tall #ffaf00; }
    #rebase_footer { height: auto; color: #888; margin-top: 1; }
    """
    def __init__(self, commits: list):
        super().__init__()
        self.commits = commits
        self.actions = ["pick"] * len(commits)

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("[bold #ffaf00]Rebase Interactivo[/]\n"
                  "[dim]Seleccioná un commit y presioná p/r/s/f/d para cambiar su acción[/dim]",
                  id="rebase_header"),
            ListView(id="rebase_list"),
            Label("[dim][[p]] Pick  [[r]] Reword  [[s]] Squash  [[f]] Fixup  [[d]] Drop  [Enter] Ejecutar  [[q]] Cerrar[/dim]",
                  id="rebase_footer"),
            id="dialog_rebase",
        )

    def on_mount(self) -> None:
        self._render()

    def _render(self) -> None:
        lista = self.query_one("#rebase_list", ListView)
        lista.clear()
        colors = {"pick": "#00ff00", "reword": "#ffaf00", "squash": "#af5fff",
                  "fixup": "#ff5f5f", "drop": "#888888"}
        for i, c in enumerate(self.commits):
            color = colors.get(self.actions[i], "#ccc")
            texto = f"[{color}]{self.actions[i]:>7}[/] {c.hash} - {c.message}"
            item = ListItem(Label(texto))
            item.idx = i
            lista.append(item)

    def _set_action(self, action: str) -> None:
        lista = self.query_one("#rebase_list", ListView)
        child = lista.highlighted_child
        if child and hasattr(child, "idx"):
            self.actions[child.idx] = action
            self._render()
            lista.index = child.idx

    def action_pick(self) -> None:
        self._set_action("pick")
    def action_reword(self) -> None:
        self._set_action("reword")
    def action_squash(self) -> None:
        self._set_action("squash")
    def action_fixup(self) -> None:
        self._set_action("fixup")
    def action_drop(self) -> None:
        self._set_action("drop")

    def action_execute(self) -> None:
        picks = [a for a in self.actions if a == "pick"]
        if not picks:
            self.notify("Debe haber al menos un commit con 'pick'.", severity="error")
            return
        result = [(c.hash, a) for c, a in zip(self.commits, self.actions)]
        self.dismiss(result)

    def action_quit(self) -> None:
        self.dismiss(None)


class VentanaConflictos(ModalScreen[bool]):
    BINDINGS = [
        ("escape", "quit", "Cerrar"),
        ("q", "quit", "Cerrar"),
        ("o", "ours", "Ours"),
        ("t", "theirs", "Theirs"),
        ("b", "both", "Both"),
    ]
    CSS = """
    VentanaConflictos { align: center middle; background: rgba(0,0,0,0.85); }
    #dialog_conflict { padding: 1; background: #121212; border: heavy #ff5f5f; width: 85%; height: 85%; }
    #conflict_header { height: auto; margin-bottom: 1; }
    #conflict_body { height: 1fr; }
    #conflict_body Static { background: #1a1a1a; padding: 1; }
    #conflict_footer { height: auto; color: #888; margin-top: 1; }
    """
    def __init__(self, archivos: list[str]):
        super().__init__()
        self.archivos = archivos
        self._idx_archivo = 0
        self._regiones: list = []
        self._idx_region = 0

    @property
    def git(self):
        return self.app.git

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("", id="conflict_header"),
            ScrollableContainer(Static(""), id="conflict_body"),
            Label("[dim][[o]] Ours  [[t]] Theirs  [[b]] Both  [[q]] Cerrar[/dim]",
                  id="conflict_footer"),
            id="dialog_conflict",
        )

    def on_mount(self) -> None:
        self._cargar_siguiente_archivo()

    def _cargar_siguiente_archivo(self) -> None:
        while self._idx_archivo < len(self.archivos):
            path = self.archivos[self._idx_archivo]
            self._regiones = self.git.get_conflict_regions(path)
            if self._regiones:
                self._idx_region = 0
                self._mostrar_conflicto(path)
                return
            self._idx_archivo += 1
        self.notify("Todos los conflictos resueltos.", severity="information")
        self.dismiss(True)

    def _mostrar_conflicto(self, path: str) -> None:
        region = self._regiones[self._idx_region]
        header = self.query_one("#conflict_header", Label)
        header.update(
            f"[bold #ff5f5f]{path}[/] — Conflicto {self._idx_region + 1} de {len(self._regiones)}  "
            f"(archivo {self._idx_archivo + 1} de {len(self.archivos)})"
        )
        content = (
            f"[#ff5f5f]<<<<<<< OURS[/]\n"
            f"{region.ours}\n"
            f"[#888888]=======[/]\n"
            f"[#00ff00]{region.theirs}[/]\n"
            f"[#00afff]>>>>>>> THEIRS[/]"
        )
        body = self.query_one("#conflict_body", ScrollableContainer)
        body.remove_children()
        body.mount(Static(content, markup=True))

    def _resolver_y_avanzar(self, choice: str) -> None:
        path = self.archivos[self._idx_archivo]
        region = self._regiones[self._idx_region]
        try:
            self.git.resolve_conflict_region(path, region, choice)
        except (GitCommandError, RuntimeError) as e:
            self._notify_error(e)
            return
        except Exception as e:
            self._notify_error(e)
            return
        self._idx_region += 1
        if self._idx_region >= len(self._regiones):
            try:
                self.git.stage_file(path)
            except (GitCommandError, RuntimeError) as e:
                self._notify_error(e)
            self._idx_archivo += 1
            self._cargar_siguiente_archivo()
        else:
            self._mostrar_conflicto(path)

    def action_ours(self) -> None:
        self._resolver_y_avanzar("ours")
    def action_theirs(self) -> None:
        self._resolver_y_avanzar("theirs")
    def action_both(self) -> None:
        self._resolver_y_avanzar("both")

    def _notify_error(self, e: Exception) -> None:
        if isinstance(e, (KeyboardInterrupt, SystemExit)):
            raise
        _error_base(self.notify, e, timeout=10)

    def action_quit(self) -> None:
        self.dismiss(False)


class VentanaUncommitted(ModalScreen):
    BINDINGS = [
        ("escape", "quit", "Cerrar"),
        ("q", "quit", "Cerrar"),
        ("v", "ver_diff", "Ver Diff"),
        ("a", "stage_all", "Stage All"),
        ("w", "commit_cambios", "Commit"),
        ("p", "stage_hunk", "Stage Hunk"),
        ("i", "agregar_gitignore", "Ignore"),
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
                    Label("[bold]Archivos[/] (Enter: stage/unstage)", id="uc_title"),
                    ListView(id="uc_file_list"),
                    Label("[dim][[a]] Stage All  [[w]] Commit  [[v]] Ver Diff  [[p]] Hunk  [[i]] Ignore  [[q]] Cerrar[/dim]", id="uc_actions"),
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
        self._archivos: list[tuple[str, bool]] = []
        self._ultima_ruta: str | None = None
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

        titulo = self.query_one("#uc_title", Label)
        n = len(self._archivos)
        titulo.update(f"[bold]Archivos ({n})[/] (Enter: stage/unstage)")

        if not self._archivos:
            return

        idx = 0
        if self._ultima_ruta:
            for i, (r, s) in enumerate(self._archivos):
                if r == self._ultima_ruta:
                    idx = i
                    break
        lista.index = idx
        ruta, staged = self._archivos[idx]
        self._ultima_ruta = ruta
        self._actualizar_diff(ruta, staged)

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
            self._ultima_ruta = ruta
            self._actualizar_diff(ruta, staged)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if not item:
            return
        ruta = getattr(item, "archivo_ruta", None)
        if not ruta:
            return
        self._ultima_ruta = ruta
        try:
            staged = getattr(item, "archivo_staged", False)
            if staged:
                self.git.unstage_file(ruta)
            else:
                self.git.stage_file(ruta)
            self._refrescar()
        except (GitCommandError, RuntimeError) as e:
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
        except (GitCommandError, RuntimeError) as e:
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
                except (GitCommandError, RuntimeError) as e:
                    self._notify_error(e)

        self.app.push_screen(VentanaCommit(), guardar)

    def _notify_error(self, e: Exception) -> None:
        if isinstance(e, (KeyboardInterrupt, SystemExit)):
            raise
        _error_base(self.notify, e, timeout=10)

    def action_stage_hunk(self) -> None:
        lista = self.query_one("#uc_file_list", ListView)
        item = lista.highlighted_child
        if not item:
            return
        ruta = getattr(item, "archivo_ruta", None)
        if not ruta:
            return
        staged = getattr(item, "archivo_staged", False)
        if staged:
            self.notify("El archivo ya está staged.", severity="warning")
            return
        info = self.git.get_status()
        if ruta in info.untracked:
            self.notify("No se puede stagear hunks de archivos no trackeados.", severity="warning")
            return
        self.app.push_screen(VentanaStageHunk(ruta), lambda _: self._refrescar())

    def action_agregar_gitignore(self) -> None:
        lista = self.query_one("#uc_file_list", ListView)
        item = lista.highlighted_child
        if not item:
            return
        ruta = getattr(item, "archivo_ruta", None)
        if not ruta:
            return
        info = self.git.get_status()
        if ruta not in info.untracked:
            self.notify("Solo se puede ignorar archivos no trackeados.", severity="warning")
            return
        try:
            self.git.add_to_gitignore(ruta)
            self.notify(f"Ignorado: {ruta}")
            self._refrescar()
        except (GitCommandError, RuntimeError) as e:
            self._notify_error(e)

    def action_quit(self) -> None:
        self.dismiss()
