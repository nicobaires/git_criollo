# GitCriollo

TUI (Terminal User Interface) para Git construida con [Textual](https://textual.textualize.io/) y [GitPython](https://gitpython.readthedocs.io/).

**Funcional, simple, rápido y en español.**

## Instalación

### Como herramienta global (recomendado)

```bash
git clone https://github.com/nicobaires/git_criollo
cd git_criollo
uv tool install --editable .
```

Después podés ejecutarlo desde cualquier carpeta. Si no hay un repositorio Git, te ofrece inicializar uno, clonar por URL o salir:

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

72 tests que cubren toda la capa de servicio (`git_service.py`), formateo de diffs (`diff_utils.py`) y manejo de errores (`error_utils.py`). Usan repositorios temporales creados con `tmpdir`.

### Correcciones incluidas

- **HEAD detached**: muestra SHA corto en vez de asumir `"master"`
- **Cross-platform**: `os.devnull` en vez de `/dev/null` (funciona en Windows)
- **`checkout_remote`**: `rsplit` en vez de `split` para refs anidadas (`origin/feature/x`)
- **pull/push/fetch**: sin fallback silencioso a `origin`, error descriptivo si no hay remote configurado
- **`run_command`**: `shlex.split` + validación anti-inyección + lista de args a `execute()`
- **`stage_hunk`**: localización robusta de hunks via `raw_diff.find(hunk.raw)`, cleanup en `finally`
- **Logging**: reemplazados todos los `except Exception: pass` con `logging.warning/exception`
- **Excepciones específicas**: `GitCommandError`, `BadName`, `InvalidGitRepositoryError` en vez de `Exception` genérico
- **Markup Textual**: `textual.markup.escape` para diffs (backslashes, corchetes, llaves correctamente escapados)
- **`KeyboardInterrupt`/`SystemExit`**: no se tragan más (Ctrl+C realmente sale)
- **Thread-safety**: `call_from_thread` para notificaciones en pull/push/fetch (evita crashes)
- **Resolución de conflictos**: re-parseo de regiones tras cada resolución (evita offsets stale)
- **Push en detached HEAD**: aviso antes de intentar push sin rama activa
- **NameError en handlers**: corregido `is_merge_in_progress` y `get_conflict_regions`

## Uso

```bash
uv run python -m git_criollo
```

Si el directorio actual no es un repositorio Git, la app pregunta por consola antes de iniciar:

```
No hay un repositorio Git en este directorio.
[i] Inicializar git init
[c] Clonar repositorio (URL)
[q] Salir
```

- `i` — inicializa `git init` (pedís el nombre del directorio; Enter = directorio actual)
- `c` — clona un repositorio por URL
- `q` — sale sin iniciar

Recién después de inicializar/clonar (o si ya había un repo) arranca la interfaz.

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
- **Cambios**: stage/unstage por archivo o global, **interactive staging** (`H`: stagear hunks individuales), diff coloreado con word-diff (verde/rojo para líneas + fondos para palabras +/-)
- **Historial**: lista paginada de commits con detalle interactivo (columna archivos + diff por archivo), **rebase interactivo** (`R`: pick/reword/squash/fixup/drop, con confirmación), log gráfico
- **Tags**: crear y borrar tags desde la interfaz
- **Resolución de conflictos**: (`M`) resolver conflictos de merge eligiendo ours/theirs/both por cada región
- **Cherry-pick**: aplicar commits de otras ramas por SHA (con confirmación)
- **Comandos personalizados**: ejecutar cualquier comando git y ver el resultado
- **Sincronización**: pull, push (con confirmación), fetch
- **Refresh manual**: presioná `F5` para actualizar la interfaz (sin auto-refresh)
- **Confirmaciones**: acciones destructivas (borrar rama, descartar cambios, push, amend, rebase, cherry-pick, stash pop, salir) piden confirmación antes de ejecutar
- **Navegación**: Tab para ciclar el foco entre paneles (el borde del panel activo cambia de color), mini-help visible siempre en la columna izquierda, ayuda completa con `?`
- **HEAD detached**: se muestra una advertencia visible en el header

## Estructura del proyecto

```
git_criollo/
├── __init__.py              # package marker
├── __main__.py              # entry point: verifica repo / menú init-clone-quit (python -m git_criollo)
├── models.py                # dataclasses: BranchInfo, CommitInfo, etc.
├── git_service.py           # lógica Git (GitService) — sin Textual
├── diff_utils.py            # formateo de diff con word-diff coloreado
├── error_utils.py           # función notify_error() compartida
├── helpers.py               # utilidades: render_commit_list(), etc.
├── styles.py                # CSS de la app principal
├── ayuda.py                 # pantalla de ayuda (VentanaAyuda)
├── ui.py                    # App principal (~300 lines)
├── ui_actions_branches.py   # mixin: branch/tag actions
├── ui_actions_sync.py       # mixin: pull/push/fetch actions
├── ui_actions_changes.py    # mixin: stage/commit/stash/diff actions
├── ui_actions_history.py    # mixin: log/rebase/cherry-pick actions
├── ventanas/
│   ├── __init__.py          # re-exports todas las ventanas
│   ├── input.py             # diálogos input
│   ├── confirm.py           # diálogos confirmación
│   ├── viewer.py            # diálogos visualización
│   ├── interactive.py       # StageHunk, Rebase, Conflictos
│   └── uncommitted.py       # VentanaUncommitted
tests/
├── conftest.py              # fixtures: repo temporal
├── test_diff_utils.py       # tests formateo diff
├── test_error_utils.py      # tests error handling
└── test_git_service.py      # tests completos de operaciones Git
```

- `models.py` — dataclasses puras sin dependencias
- `git_service.py` — lógica Git sin imports de Textual (testeable)
- `diff_utils.py` — funciones puras para formateo de diff
- `error_utils.py` — utilidades compartidas
- `ui.py` — App principal (4 mixins + App base)
- `ui_actions_*.py` — mixins organizados por dominio
- `ventanas/` — componentes ModalScreen agrupados por tipo
- `ayuda.py` — pantalla de ayuda con atajos

## Licencia

MIT License. Ver [LICENSE](LICENSE) para detalles.
