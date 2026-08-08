from textual.app import ComposeResult
from textual.widgets import ListView, ListItem, Label, Static
from textual.containers import Vertical, ScrollableContainer
from textual.screen import ModalScreen
from git import GitCommandError

from git_criollo.diff_utils import _diff_coloreado
from git_criollo.error_utils import notify_error as _error_base


def _notify_screen_error(notify_method, e: Exception) -> None:
    """Error handler para ModalScreens que no heredan de la app principal."""
    if isinstance(e, (KeyboardInterrupt, SystemExit)):
        raise
    _error_base(notify_method, e, timeout=10)


class VentanaStageHunk(ModalScreen[bool]):
    BINDINGS = [
        ("escape", "quit", "Cancelar"),
        ("q", "quit", "Cancelar"),
        ("y", "stage", "Stage"),
        ("n", "skip", "Skip"),
        ("p", "previous", "Anterior"),
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
        header.update(
            f"[bold #00afff]{self.path}[/] — Hunk {self._idx + 1} de {len(self._hunks)}"
        )
        body = self.query_one("#hunk_body", ScrollableContainer)
        body.remove_children()
        body.mount(Static(_diff_coloreado(hunk.raw), markup=True))

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("", id="hunk_header"),
            ScrollableContainer(Static(""), id="hunk_body"),
            Label(
                "[dim][[y]] Stage  [[n]] Skip  [[p]] Anterior  [[q]] Cerrar[/dim]",
                id="hunk_footer",
            ),
            id="dialog_hunk",
        )

    def action_stage(self) -> None:
        if self._idx >= len(self._hunks):
            return
        try:
            self.git.stage_hunk(self.path, self._hunks[self._idx])
            self.notify(f"Hunk {self._idx + 1} stageado.", timeout=1.5)
            # Re-parsear: los offsets cambian después de stagear
            self._hunks = self.git.parse_diff_hunks(self.path)
            # Mantener el mismo índice (ahora apunta al siguiente hunk real)
            self._mostrar_hunk()
        except (GitCommandError, RuntimeError) as e:
            self._notify_error(e)
        except Exception as e:
            self._notify_error(e)

    def action_skip(self) -> None:
        self._idx += 1
        self._mostrar_hunk()

    def action_previous(self) -> None:
        if self._idx > 0:
            self._idx -= 1
            self._mostrar_hunk()
        else:
            self.notify("Ya estás en el primer hunk.", severity="information", timeout=1.5)

    def _notify_error(self, e: Exception) -> None:
        _notify_screen_error(self.notify, e)

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
                  "[dim]Seleccion\u00e1 un commit y presion\u00e1 p/r/s/f/d para cambiar su acci\u00f3n[/dim]",
                  id="rebase_header"),
            ListView(id="rebase_list"),
            Label("[dim][[p]] Pick  [[r]] Reword  [[s]] Squash  [[f]] Fixup  [[d]] Drop  [Enter] Ejecutar  [[q]] Cerrar[/dim]",
                  id="rebase_footer"),
            id="dialog_rebase",
        )

    def on_mount(self) -> None:
        self.call_after_refresh(self._render_rebase)

    def _render_rebase(self) -> None:
        lista = self.query_one("#rebase_list", ListView)
        if lista.children:
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
            self._render_rebase()
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
        self._resueltas = 0

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
                self._resueltas = 0
                self._mostrar_conflicto(path)
                return
            self._idx_archivo += 1
        self.notify("Todos los conflictos resueltos.", severity="information")
        self.dismiss(True)

    def _mostrar_conflicto(self, path: str) -> None:
        region = self._regiones[self._idx_region]
        header = self.query_one("#conflict_header", Label)
        header.update(
            f"[bold #ff5f5f]{path}[/] \u2014 Conflicto {self._resueltas + 1} \u2014 {len(self._regiones)} restantes  "
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
        self._resueltas += 1
        self._regiones = self.git.get_conflict_regions(path)
        if self._regiones:
            self._idx_region = 0
            self._mostrar_conflicto(path)
        else:
            try:
                self.git.stage_file(path)
            except (GitCommandError, RuntimeError) as e:
                self._notify_error(e)
            self._idx_archivo += 1
            self._cargar_siguiente_archivo()

    def action_ours(self) -> None:
        self._resolver_y_avanzar("ours")
    def action_theirs(self) -> None:
        self._resolver_y_avanzar("theirs")
    def action_both(self) -> None:
        self._resolver_y_avanzar("both")

    def _notify_error(self, e: Exception) -> None:
        _notify_screen_error(self.notify, e)

    def action_quit(self) -> None:
        self.dismiss(False)
