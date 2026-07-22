from textual.widgets import ListView
from git import GitCommandError

from git_criollo.ventanas import (
    VentanaNuevaRama, VentanaConfirmarBorrado, VentanaConfirmarMerge,
    VentanaTag, VentanaConfirmarBorradoTag,
)


class MixinBranchActions:
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
            self.notify("No pod\u00e9s borrar una rama remota.", severity="error")
            return
        info = self.git.get_branches()
        if r.startswith("tag:"):
            tag_name = r[4:]
            self.push_screen(VentanaConfirmarBorradoTag(tag_name),
                             lambda b, n=tag_name: self._borrar_tag_si_confirmado(b, n))
            return
        if r == info.active:
            self.notify("No pod\u00e9s borrar la rama activa.", severity="error")
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
            self.notify("Seleccion\u00e1 una rama local.", severity="warning")
            return
        info = self.git.get_branches()
        if r == info.active:
            self.notify("Ya est\u00e1s en esa rama.", severity="warning")
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

    def _borrar_tag_si_confirmado(self, b: bool | None, tag_name: str) -> None:
        if b:
            try:
                self.git.delete_tag(tag_name)
                self.notify(f"Tag '{tag_name}' borrado.")
                self.actualizar_ramas()
            except (GitCommandError, RuntimeError) as e:
                self._notify_error(e)

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
        self.notify(f"Seleccion\u00e1 un tag en la lista de ramas y presion\u00e1 D para borrarlo: {tags}")
