# GitCriollo

TUI (Terminal User Interface) para Git construida con [Textual](https://textual.textualize.io/) y [GitPython](https://gitpython.readthedocs.io/).

## Instalación

```bash
uv add gitpython textual
```

## Uso

```bash
uv run python -m git_criollo
```

## Atajos

| Tecla | Acción |
|-------|--------|
| `q` | Salir |
| `n` | Crear nueva rama |
| `c` | Checkout (cambiar a rama seleccionada) |
| `d` | Borrar rama seleccionada |
| `m` | Merge rama seleccionada en la actual |
| `p` | Git pull |
| `u` | Git push |
| `f` | Git fetch |
| `a` | Stage all (agregar todos los cambios) |
| `w` | Commit (abre modal para escribir mensaje) |
| `z` | Stash push (con mensaje opcional) |
| `Z` | Stash pop |
| `v` | Ver diff del archivo seleccionado |
| `l` | Cargar más commits en el historial |
| `Enter` | (en panel de archivos) Stage / Unstage archivo |

## Estructura del proyecto

```
git_criollo/
├── __init__.py          # package marker
├── __main__.py          # entry point (python -m git_criollo)
├── git_service.py       # lógica Git (dataclasses + GitService)
└── ui.py                # widgets Textual (modales + App)
```

- `git_service.py` — cero imports de Textual, solo `GitPython` y `dataclasses`. Devuelve objetos planos (`BranchInfo`, `CommitInfo`, `StatusInfo`). Testeable sin terminal.
- `ui.py` — cero imports de `GitPython`. Solo arma widgets y delega en `GitService`.
