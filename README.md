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
| `p` | Stage Hunk | Stagear hunks individuales del archivo modificado |
| `C` | Cambios sin commit | Pantalla completa con lista de archivos + diff coloreado |
| `Tab` | Ciclo foco | Navegar entre paneles |
| `i` | Ver .gitignore | Mostrar el contenido del .gitignore |
| `I` | Ignorar archivo | Agregar el untracked seleccionado al .gitignore |
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
- **Cambios**: stage/unstage por archivo o global, **interactive staging** (`p`: stagear hunks individuales), diff coloreado con word-diff (verde/rojo para líneas + fondos para palabras +/-, azul para @@), commit, amend, stash push/pop. Pantalla completa con `C`: lista de archivos con contador, diff navegable por flechas, stage/unstage con Enter. Gestión de `.gitignore`: ver (`i`) y agregar untracked (`I`).
- **Historial**: lista paginada de commits con detalle, **rebase interactivo** (`R`: pick/reword/squash/fixup/drop), log gráfico (`git log --graph --oneline --all`), detalle completo con diff coloreado al presionar Enter
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
├── __init__.py          # package marker
├── __main__.py          # entry point (python -m git_criollo)
├── ayuda.py             # pantalla de ayuda (VentanaAyuda)
├── diff_utils.py        # formateo de diff con word-diff coloreado
├── error_utils.py       # función notify_error() compartida
├── git_service.py       # lógica Git (dataclasses + GitService)
├── ui.py                # App principal (GitCriolloApp)
└── ventanas.py          # todos los ModalScreen
```

- `git_service.py` — cero imports de Textual, solo `GitPython` y `dataclasses`. Devuelve objetos planos (`BranchInfo`, `CommitInfo`, `CommitDetail`, `StatusInfo`, `DiffHunk`, `ConflictRegion`). Testeable sin terminal.
- `diff_utils.py` — función `_diff_coloreado()` pura, sin imports de Textual.
- `error_utils.py` — función `notify_error()` compartida entre `ui.py` y `ventanas.py`.
- `ventanas.py` — todos los `ModalScreen` (input, confirmación, diff, detalle, stage hunk, rebase, conflictos, cambios sin commit, etc.). Usa Textual pero no `GitPython`.
- `ui.py` — cero imports de `GitPython`. Solo `GitCriolloApp` que delega en `GitService` y monta las ventanas de `ventanas.py`.
- `ayuda.py` — define la ventana modal de ayuda con todos los atajos y descripciones.
