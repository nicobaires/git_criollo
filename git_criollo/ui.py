import os
import re

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label
from textual.containers import Horizontal, Vertical
from git import GitCommandError

from git_criollo.git_service import GitService
from git_criollo.error_utils import notify_error as _notify_error_base
from git_criollo.ayuda import VentanaAyuda
from git_criollo.styles import CSS
from git_criollo.ventanas import VentanaComando, VentanaResultado, VentanaConfirmarBorradoTag
from git_criollo.ui_actions_branches import MixinBranchActions
from git_criollo.ui_actions_sync import MixinSyncActions
from git_criollo.ui_actions_changes import MixinChangeActions
from git_criollo.ui_actions_history import MixinHistoryActions


class GitCriolloApp(
    MixinBranchActions, MixinSyncActions,
    MixinChangeActions, MixinHistoryActions,
    App,
):
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
        ("f5", "refresh", "Refrescar"),
        ("r", "comando_personalizado", "Cmd"),
        ("H", "stage_hunk", "Stage Hunk"),
        ("R", "rebase", "Rebase"),
        ("M", "resolver_conflictos", "Merge"),
        ("i", "ver_gitignore", ".gitignore"),
        ("I", "agregar_gitignore", "Ignore"),
        ("x", "descartar_cambios", "Descartar"),
        ("?", "ayuda", "Ayuda"),
        ("C", "uncommitted", "Cambios"),
    ]

    CSS = CSS

    def on_mount(self) -> None:
        try:
            self.git = GitService(os.getcwd())
            self._commit_offset = 0
            self._modo_grafico = False
            self.actualizar_pantalla_completa()
        except (GitCommandError, RuntimeError) as e:
            self.exit(message=f"Error: No est\u00e1s dentro de un repositorio de Git. ({e})")
        except Exception as e:
            self.exit(message=f"Error inesperado al iniciar: {e}")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, id="header")
        yield Horizontal(
            Vertical(
                Label("[bold]MIS RAMAS[/]"),
                ListView(id="lista_ramas"),
                Label("", id="info_rama"),
                Label(
                    "[dim][[n]] Rama  [[c]] Checkout  [[d]] Borrar  [[m]] Merge  "
                    "[[C]] Cambios  [[H]] Hunk  [[x]] Descartar  [[i]] .gitignore  [[?]] Ayuda[/dim]",
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
        try:
            self.actualizar_ramas()
            self.actualizar_historial()
            self.actualizar_status()
            self.actualizar_header()
        except (GitCommandError, RuntimeError) as e:
            self.notify(f"Error de Git: {e}", severity="error")
        except Exception as e:
            self.notify(f"Error inesperado al actualizar pantalla: {e}", severity="error")

    def actualizar_header(self) -> None:
        try:
            info = self.git.get_branches()
            if info.is_detached:
                self.sub_title = "[bold #ff5f5f]HEAD suelto (detached)[/]"
                return
            a = info.ahead.get(info.active, 0)
            b = info.behind.get(info.active, 0)
            sufijo = f" [+{a} -{b}]" if a or b else ""
            self.sub_title = f"{info.active}{sufijo}"
        except (GitCommandError, RuntimeError) as e:
            self.sub_title = f"[error] {e}"
        except Exception as e:
            self.sub_title = ""

    def actualizar_ramas(self) -> None:
        info = self.git.get_branches()
        lista = self.query_one("#lista_ramas", ListView)
        lista.clear()
        indice_activa = 0

        for orden, nombre in enumerate(info.branches):
            if nombre == info.active:
                texto = f"\u2b50 [bold #00ff00]{nombre} (Actual)[/]"
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
            sep = ListItem(Label("[dim]\u2500\u2500 Remotas \u2500\u2500[/dim]"))
            sep.disabled = True
            lista.append(sep)
            for rm in info.remotes:
                item = ListItem(Label(f"  [dim]{rm}[/dim]"))
                item.rama_objeto = rm
                item.es_remota = True
                lista.append(item)

        if info.tags:
            sep = ListItem(Label("[dim]\u2500\u2500 Tags \u2500\u2500[/dim]"))
            sep.disabled = True
            lista.append(sep)
            for tg in info.tags:
                item = ListItem(Label(f"  [#ffaf00]\u25cf[/#ffaf00] {tg}"))
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
        icono = "[#ff5f5f]\u25cf sucio[/]" if dirty else "[#00ff00]\u25cf limpio[/]"
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
                m = re.search(r'[a-f0-9]{7,}', linea)
                if m:
                    item.commit_hash = m.group()
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
            item = ListItem(Label(f"  \u2714 {f}"))
            item.archivo_ruta = f
            item.archivo_staged = True
            staged_list.append(item)

        unstaged_list = self.query_one("#lista_unstaged", ListView)
        unstaged_list.clear()
        for f in info.unstaged:
            item = ListItem(Label(f"  \ud83d\udca5 M: {f}"))
            item.archivo_ruta = f
            item.archivo_staged = False
            unstaged_list.append(item)
        for f in info.untracked:
            item = ListItem(Label(f"  \u2753 ?: {f}"))
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
        if isinstance(e, (KeyboardInterrupt, SystemExit)):
            raise
        _notify_error_base(self.notify, e, timeout=15)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        lista_id = event.list_view.id
        item = event.item
        if not item:
            return

        if lista_id == "lista_staged":
            ruta = getattr(item, "archivo_ruta", None)
            if not ruta:
                return
            try:
                self.git.unstage_file(ruta)
                self.notify(f"Unstage: {ruta}")
                self.actualizar_status()
            except (GitCommandError, RuntimeError) as e:
                self._notify_error(e)

        elif lista_id == "lista_unstaged":
            ruta = getattr(item, "archivo_ruta", None)
            if not ruta:
                return
            try:
                self.git.stage_file(ruta)
                self.notify(f"Stage: {ruta}")
                self.actualizar_status()
            except (GitCommandError, RuntimeError) as e:
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

    # --- ACCIONES QUE QUEDAN EN UI ---

    def action_ayuda(self) -> None:
        self.push_screen(VentanaAyuda())

    def action_comando_personalizado(self) -> None:
        def p(cmd: str | None):
            if cmd:
                try:
                    resultado = self.git.run_command(cmd)
                    self.push_screen(VentanaResultado(f"Resultado: git {cmd}", resultado))
                except (GitCommandError, RuntimeError) as e:
                    self._notify_error(e)
        self.push_screen(VentanaComando(), p)

    def action_refresh(self) -> None:
        self.actualizar_pantalla_completa()
        self.notify("Pantalla actualizada.", severity="information", timeout=1)
