# GitCriollo

TUI (Terminal User Interface) para Git construida con [Textual](https://textual.textualize.io/) y [GitPython](https://gitpython.readthedocs.io/).

## Instalación

### Como herramienta global (recomendado)

```bash
git clone https://github.com/tu-usuario/git-criollo
cd git-criollo
uv tool install --editable .
```

Después podés ejecutarlo desde cualquier carpeta que sea un repositorio Git:

```bash
gitcriollo
```
### Modo desarrollo

```bash
uv add gitpython textual
```

### Tests

```bash
uv run pytest tests/
```

72 tests que cubren toda la capa de servicio (`git_service.py`), formateo de diffs (`diff_utils.py`) y manejo de errores (`error_utils.py`). Usan repositorios temporales creados con `tmpdir` + `git init`, sin depender de fixtures externos. Ejecutalos con `uv run pytest tests/ -v`.

### Correcciones incluidas

La rama `fix/bugs-lote1` aplica 8 grupos de correcciones sobre el código base:

- **HEAD detached**: muestra SHA corto en vez de asumir `"master"`
- **Cross-platform**: `os.devnull` en vez de `/dev/null` (funciona en Windows)
- **`checkout_remote`**: `rsplit` en vez de `split` para refs anidadas (`origin/feature/x`)
- **pull/push/fetch**: sin fallback silencioso a `origin`, error descriptivo si no hay remote configurado
- **`run_command`**: `shlex.split` + validación anti-inyección + lista de args a `execute()`
- **`stage_hunk`**: manejo específico de `GitCommandError` → `RuntimeError`, cleanup en `finally`
- **Logging**: reemplazados todos los `except Exception: pass` con `logging.warning/exception`
- **Excepciones específicas**: `GitCommandError`, `BadName`, `InvalidGitRepositoryError` en vez de `Exception` genérico
- **Markup Rich escapado**: `]`, `{`, `}` además de `[` en diffs coloreados
- **`KeyboardInterrupt`/`SystemExit`**: no se tragan más (Ctrl+C realmente sale)

## Uso

```bash
uv run python -m git_criollo
```

## Atajos

Presioná `?` dentro de la aplicación para ver la ayuda completa.

| Tecla | Acción | Descripción |
|-------|--------|-------------|
| `q` | Salir | Cerrar GitCriollo |
| `?` | Ayuda | Abrir pantalla de ayuda detallada |
| | **Ramas** | |
| `n` | Nueva rama | Crear una rama local |
| `c` | Checkout | Cambiar a la rama seleccionada |
| `d` | Borrar rama | Eliminar la rama local seleccionada |
| `m` | Merge | Fusionar rama seleccionada en la actual |
| | **Sincronización** | |
| `p` | Pull | Traer cambios del remoto |
| `u` | Push | Subir cambios al remoto |
| `f` | Fetch | Bajar referencias remotas |
| | **Cambios** | |
| `a` | Stage All | Agregar todo al stage |
| `w` | Commit | Crear un commit |
| `e` | Amend | Modificar el mensaje del último commit |
| `v` | Ver Diff | Mostrar diff del archivo seleccionado |
| `H` | Stage Hunk | Stagear hunks individuales del archivo modificado |
| `C` | Cambios sin commit | Pantalla completa con lista de archivos + diff coloreado |
| `Tab` | Ciclo foco | Navegar entre paneles |
| `i` | Ver .gitignore | Mostrar el contenido del .gitignore |
| `I` | Ignorar archivo | Agregar el untracked seleccionado al .gitignore |
| `x` | Descartar cambios | Descartar cambios locales del archivo seleccionado |
| | **Stash** | |
| `z` | Stash Push | Guardar cambios en el stash |
| `Z` | Stash Pop | Recuperar el último stash |
| | **Historial** | |
| `Enter` | Detalle | Ver detalle completo del commit |
| `R` | Rebase interactivo | Abrir rebase con pick/reword/squash/fixup/drop |
| `g` | Toggle Graph | Alternar vista gráfico/lista |
| `l` | +Commits | Cargar más commits |
| | **Tags** | |
| `t` | Crear Tag | Crear un tag ligero |
| `T` | Borrar Tag | Eliminar un tag |
| | **Otros** | |
| `M` | Resolver conflictos | Resolver conflictos de merge (ours/theirs/both) |
| `y` | Cherry-Pick | Aplicar un commit por SHA |
| `r` | Comando | Ejecutar comando git personalizado |
| `F5` | Refrescar | Actualizar manualmente la interfaz |

## Características

- **Ramas**: crear, checkout, borrar (con confirmación), merge, ver ramas locales y remotas con ahead/behind
- **Cambios**: stage/unstage por archivo o global, **interactive staging** (`H`: stagear hunks individuales), diff coloreado con word-diff (verde/rojo para líneas + fondos para palabras +/-, azul para @@), commit, amend, stash push/pop. Pantalla completa con `C`: lista de archivos con contador, diff navegable por flechas, stage/unstage con Enter. Gestión de `.gitignore`: ver (`i`) y agregar untracked (`I`).
- **Historial**: lista paginada de commits con detalle, **rebase interactivo** (`R`: pick/reword/squash/fixup/drop), log gráfico (`git log --graph --oneline --all`), detalle completo con Enter: metadatos (autor/committer/fechas), lista de archivos con ± líneas (scrolleable), diff coloreado con proporciones adaptativas
- **Tags**: crear y borrar tags desde la interfaz
- **Resolución de conflictos**: (`M`) resolver conflictos de merge eligiendo ours/theirs/both por cada región
- **Cherry-pick**: aplicar commits de otras ramas por SHA
- **Comandos personalizados**: ejecutar cualquier comando git y ver el resultado
- **Refresh manual**: presioná `F5` para actualizar la interfaz (sin auto-refresh)
- **Navegación**: Tab para ciclar el foco entre paneles (el borde del panel activo cambia de color), mini-help visible siempre en la columna izquierda, ayuda completa con `?`, pantalla de cambios sin commit con `C`
- **HEAD detached**: se muestra una advertencia visible en el header

## Estructura del proyecto

```
git_criollo/
├── __init__.py              # package marker
├── __main__.py              # entry point (python -m git_criollo)
├── models.py                # dataclasses: BranchInfo, CommitInfo, etc.
├── git_service.py           # lógica Git (GitService) — sin Textual
├── diff_utils.py            # formateo de diff con word-diff coloreado
├── error_utils.py           # función notify_error() compartida
├── styles.py                # CSS de la app principal
├── ayuda.py                 # pantalla de ayuda (VentanaAyuda)
├── ui.py                    # App principal (~300 lines)
├── ui_actions_branches.py   # mixin: branch/tag actions
├── ui_actions_sync.py       # mixin: pull/push/fetch actions
├── ui_actions_changes.py    # mixin: stage/commit/stash/diff actions
├── ui_actions_history.py    # mixin: log/rebase/cherry-pick actions
├── ventanas/
│   ├── __init__.py          # re-exports todas las ventanas
│   ├── input.py             # 7 input dialogs
│   ├── confirm.py           # 3 confirmation dialogs
│   ├── viewer.py            # 3 viewer dialogs
│   ├── interactive.py       # StageHunk, Rebase, Conflictos
│   └── uncommitted.py       # VentanaUncommitted
tests/
├── conftest.py              # fixtures: repo temporal
├── test_diff_utils.py       # _diff_coloreado
├── test_error_utils.py      # notify_error
└── test_git_service.py      # 52 tests: todas las operaciones Git
```

- `models.py` — dataclasses puras (`BranchInfo`, `CommitInfo`, `CommitDetail`, `DiffHunk`, `ConflictRegion`, `StatusInfo`). Sin dependencias.
- `git_service.py` — cero imports de Textual. `GitService` usa modelos de `models.py`. Testeable sin terminal.
- `diff_utils.py` — función `_diff_coloreado()` pura, sin imports de Textual.
- `error_utils.py` — función `notify_error()` compartida entre `ui.py` y `ventanas/`.
- `styles.py` — CSS de la app principal.
- `ui.py` — `GitCriolloApp` hereda de 4 mixins + `App`. Cero imports de `GitPython`.
- `ui_actions_*.py` — mixins de acciones por dominio (ramas, sync, cambios, historial).
- `ventanas/` — 5 archivos con `ModalScreen` agrupados por tipo.
- `ayuda.py` — ventana modal de ayuda con todos los atajos.