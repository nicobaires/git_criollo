"""Utilidades compartidas para reducir código duplicado."""
from __future__ import annotations

import re
from functools import wraps
from typing import Any, Callable, TypeVar

from textual.widgets import ListView, ListItem, Label
from git import GitCommandError

from git_criollo.error_utils import notify_error as _notify_error_base

F = TypeVar("F", bound=Callable[..., Any])


def git_action(msg_exito: str | None = None, timeout: int = 10) -> Callable[[F], F]:
    """Decorator que envuelve un método en try/except para errores de git.

    El método decorado debe tener `self._notify_error` disponible,
    o tener un atributo `self.notify` (Textual Widget).

    Args:
        msg_exito: Si se provee, muestra este mensaje al finalizar con éxito.
        timeout: Timeout del error notification.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
                if msg_exito:
                    self.notify(msg_exito, severity="information")
                return result
            except (GitCommandError, RuntimeError, Exception) as e:
                if isinstance(e, (KeyboardInterrupt, SystemExit)):
                    raise
                _notify_error_base(self.notify, e, timeout=timeout)
        return wrapper  # type: ignore[return-value]

    return decorator


def get_highlighted_attr(listview: ListView, attr: str) -> Any | None:
    """Obtiene un atributo del item destacado en un ListView.

    Returns:
        El valor del atributo, o None si no hay item o no tiene el atributo.
    """
    child = listview.highlighted_child
    if not child:
        return None
    return getattr(child, attr, None)


def render_commit_list(
    lista: ListView,
    commits: list,
    modo_grafico: bool = False,
) -> int:
    """Renderiza una lista de commits en un ListView.

    Returns:
        Cantidad de commits renderizados.
    """
    lista.clear()
    if modo_grafico:
        for linea in commits:
            item = ListItem(Label(f"[dim]{linea}[/dim]"))
            m = re.search(r'[a-f0-9]{7,}', linea)
            if m:
                item.commit_hash = m.group()
            lista.append(item)
        return len(commits)
    else:
        for c in commits:
            item = ListItem(Label(
                f"[#ffaf00]{c.hash}[/#ffaf00] - {c.message} [dim]({c.author})[/dim]"
            ))
            item.commit_hash = c.hash
            lista.append(item)
        return len(commits)


def render_status_lists(
    staged_list: ListView,
    unstaged_list: ListView,
    staged: list[str],
    unstaged: list[str],
    untracked: list[str],
) -> None:
    """Renderiza las listas de archivos staged, unstaged y untracked."""
    staged_list.clear()
    unstaged_list.clear()

    for f in staged:
        item = ListItem(Label(f"  \u2714 {f}"))
        item.archivo_ruta = f
        item.archivo_staged = True
        staged_list.append(item)

    for f in unstaged:
        item = ListItem(Label(f"  \ud83d\udca5 M: {f}"))
        item.archivo_ruta = f
        item.archivo_staged = False
        unstaged_list.append(item)

    for f in untracked:
        item = ListItem(Label(f"  \u2753 ?: {f}"))
        item.archivo_ruta = f
        item.archivo_staged = False
        unstaged_list.append(item)


def render_status_list_single(
    lista: ListView,
    staged: list[str],
    unstaged: list[str],
    untracked: list[str],
) -> list[tuple[str, bool]]:
    """Renderiza archivos staged/unstaged/untracked en una sola lista.

    Returns:
        Lista de (ruta, esta_staged) para cada archivo.
    """
    lista.clear()
    archivos: list[tuple[str, bool]] = []

    for f in staged:
        archivos.append((f, True))
        item = ListItem(Label(f"  \u2714 {f}"))
        item.archivo_ruta = f
        item.archivo_staged = True
        lista.append(item)

    for f in unstaged:
        archivos.append((f, False))
        item = ListItem(Label(f"  \ud83d\udca5 M: {f}"))
        item.archivo_ruta = f
        item.archivo_staged = False
        lista.append(item)

    for f in untracked:
        archivos.append((f, False))
        item = ListItem(Label(f"  \u2753 ?: {f}"))
        item.archivo_ruta = f
        item.archivo_staged = False
        lista.append(item)

    return archivos
