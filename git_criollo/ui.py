import os
import re

from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label
from textual.containers import Horizontal, Vertical
from git import GitCommandError

from git_criollo.git_service import GitService
from git_criollo.error_utils import notify_error as _notify_error_base
from git_criollo.ayuda import VentanaAyuda
from git_criollo.ventanas import (
    VentanaNuevaRama,
    VentanaStageHunk,
    VentanaConfirmarBorrado,
    VentanaConfirmarMerge,
    VentanaCommit,
    VentanaStashPush,
    VentanaDiff,
    VentanaAmend,
    VentanaDetalleCommit,
    VentanaTag,
    VentanaConfirmarBorradoTag,
    VentanaCherryPick,
    VentanaComando,
    VentanaResultado,
    VentanaUncommitted,
    VentanaRebase,
    VentanaConflictos,
)


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
        ("f5", "refresh", "Refrescar"),
        ("r", "comando_personalizado", "Cmd"),
        ("p", "stage_hunk", "Stage Hunk"),
        ("R", "rebase", "Rebase"),
        ("M", "resolver_conflictos", "Merge"),
        ("i", "ver_gitignore", ".gitignore"),
        ("I", "agregar_gitignore", "Ignore"),
        ("x", "descartar_cambios", "Descartar"),
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
        except (GitCommandError, RuntimeError) as e:
            self.exit(message=f"Error: No estás dentro de un repositorio de Git. ({e})")
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
                    "[[C]] Cambios  [[p]] Hunk  [[x]] Descartar  [[i]] .gitignore  [[?]] Ayuda[/dim]",
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
        if isinstance(e, (KeyboardInterrupt, SystemExit)):
            raise
        _notify_error_base(self.notify, e, timeout=15)

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
            except (GitCommandError, RuntimeError) as e:
                self._notify_error(e)

        elif lista_id == "lista_unstaged":
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
                except (GitCommandError, RuntimeError) as e:
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
            self.actualizar_pantalla_completa()
        except (GitCommandError, RuntimeError) as e:
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
                except (GitCommandError, RuntimeError) as e:
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
                    self.actualizar_pantalla_completa()
                except (GitCommandError, RuntimeError) as e:
                    self._notify_error(e)
        self.push_screen(VentanaConfirmarMerge(r), p)

    @work(thread=True)
    def action_pull_rama(self) -> None:
        self.notify("Git pull...")
        try:
            self.git.pull()
            self.notify("¡Pull OK!")
            self.actualizar_pantalla_completa()
        except (GitCommandError, RuntimeError) as e:
            self._notify_error(e)

    @work(thread=True)
    def action_push_rama(self) -> None:
        self.notify("Git push...")
        try:
            active_branch = self.git.get_branches().active
            self.git.push(active_branch)
            self.notify("¡Push OK!")
            self.actualizar_pantalla_completa()
        except (GitCommandError, RuntimeError) as e:
            self._notify_error(e)

    @work(thread=True)
    def action_fetch_rama(self) -> None:
        self.notify("Git fetch...")
        try:
            self.git.fetch()
            self.notify("¡Fetch OK!")
            self.actualizar_pantalla_completa()
        except (GitCommandError, RuntimeError) as e:
            self._notify_error(e)

    def action_stage_all(self) -> None:
        try:
            self.git.stage_all()
            self.notify("Todos los cambios agregados al Stage.")
            self.actualizar_status()
        except (GitCommandError, RuntimeError) as e:
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
                    self.actualizar_pantalla_completa()
                except (GitCommandError, RuntimeError) as e:
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
            except (GitCommandError, RuntimeError) as e:
                self._notify_error(e)
        self.push_screen(VentanaStashPush(), p)

    def action_stash_pop(self) -> None:
        try:
            self.git.stash_pop()
            self.notify("Stash recuperado.")
            self.actualizar_status()
        except (GitCommandError, RuntimeError) as e:
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
                m = re.search(r'[a-f0-9]{7,}', linea)
                if m:
                    item.commit_hash = m.group()
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
        except (GitCommandError, RuntimeError) as e:
            self._notify_error(e)

    def _borrar_tag_si_confirmado(self, b: bool | None, tag_name: str) -> None:
        if b:
            try:
                self.git.delete_tag(tag_name)
                self.notify(f"Tag '{tag_name}' borrado.")
                self.actualizar_ramas()
            except (GitCommandError, RuntimeError) as e:
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
                except (GitCommandError, RuntimeError) as e:
                    self._notify_error(e)

        self.push_screen(VentanaAmend(), p)

    def action_crear_tag(self) -> None:
        def p(nombre: str | None):
            if nombre:
                try:
                    self.git.create_tag(nombre)
                    self.notify(f"Tag '{nombre}' creado.")
                    self.actualizar_ramas()
                except (GitCommandError, RuntimeError) as e:
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
                except (GitCommandError, RuntimeError) as e:
                    self._notify_error(e)

        self.push_screen(VentanaCherryPick(), p)

    def action_comando_personalizado(self) -> None:
        def p(cmd: str | None):
            if cmd:
                try:
                    resultado = self.git.run_command(cmd)
                    self.push_screen(VentanaResultado(f"Resultado: git {cmd}", resultado))
                except (GitCommandError, RuntimeError) as e:
                    self._notify_error(e)

        self.push_screen(VentanaComando(), p)

    def action_ver_gitignore(self) -> None:
        try:
            contenido = self.git.get_gitignore_content()
            self.push_screen(VentanaResultado(".gitignore", contenido))
        except (GitCommandError, RuntimeError) as e:
            self._notify_error(e)

    def action_agregar_gitignore(self) -> None:
        focused = self.focused
        if not focused or focused.id != "lista_unstaged":
            self.notify("Seleccioná un archivo no trackeado en el panel de estado.", severity="warning")
            return
        item = focused.highlighted_child
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
            self.actualizar_status()
        except (GitCommandError, RuntimeError) as e:
            self._notify_error(e)

    def action_descartar_cambios(self) -> None:
        focused = self.focused
        if not focused or focused.id not in ("lista_staged", "lista_unstaged"):
            self.notify("Seleccioná un archivo modificado en el panel de estado.", severity="warning")
            return
        item = focused.highlighted_child
        if not item:
            return
        ruta = getattr(item, "archivo_ruta", None)
        if not ruta:
            return
        try:
            self.git.discard_changes(ruta)
            self.notify(f"Cambios descartados: {ruta}")
            self.actualizar_status()
        except (GitCommandError, RuntimeError) as e:
            self._notify_error(e)

    def action_stage_hunk(self) -> None:
        focused = self.focused
        if not focused or focused.id != "lista_unstaged":
            self.notify("Seleccioná un archivo modificado en el panel de estado.", severity="warning")
            return
        item = focused.highlighted_child
        if not item:
            return
        ruta = getattr(item, "archivo_ruta", None)
        if not ruta:
            return
        info = self.git.get_status()
        if ruta in info.untracked:
            self.notify("No se puede stagear hunks de archivos no trackeados.", severity="warning")
            return
        self.push_screen(VentanaStageHunk(ruta), lambda _: self.actualizar_status())

    def action_rebase(self) -> None:
        lista = self.query_one("#lista_commits", ListView)
        child = lista.highlighted_child
        if not child:
            self.notify("Seleccioná un commit en el historial.", severity="warning")
            return
        sha = getattr(child, "commit_hash", None)
        if not sha:
            self.notify("Seleccioná un commit en el historial.", severity="warning")
            return
        commits = self.git.get_commits_for_rebase(sha)
        if len(commits) < 2:
            self.notify("Se necesitan al menos 2 commits para rebase interactivo.", severity="warning")
            return
        def ejecutar(todos):
            if todos:
                try:
                    base_sha = self.git.get_parent_sha(sha)
                    self.git.run_rebase(base_sha, todos)
                    self.notify("Rebase completado.")
                    self.actualizar_pantalla_completa()
                except (GitCommandError, RuntimeError) as e:
                    self._notify_error(e)
        self.push_screen(VentanaRebase(commits), ejecutar)

    def action_resolver_conflictos(self) -> None:
        if not self.git.is_merge_in_progress():
            self.notify("No hay conflictos de merge.", severity="warning")
            return
        archivos = self.git.get_conflicted_files()
        if not archivos:
            self.notify("No hay archivos en conflicto.", severity="warning")
            return
        self.push_screen(VentanaConflictos(archivos), lambda _: self.actualizar_pantalla_completa())

    def action_refresh(self) -> None:
        self.actualizar_pantalla_completa()
        self.notify("Pantalla actualizada.", severity="information", timeout=1)
