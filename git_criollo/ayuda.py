from textual.app import ComposeResult
from textual.widgets import Label
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal


SECCIONES = [
    ("RAMAS", [
        ("n", "Nueva rama:", "Crear una rama local a partir del commit actual."),
        ("c", "Checkout:", "Cambiar a la rama seleccionada. Si es remota crea una local con tracking."),
        ("d", "Borrar rama:", "Eliminar la rama local seleccionada (pide confirmación)."),
        ("m", "Merge:", "Fusionar la rama seleccionada en la actual (pide confirmación)."),
    ]),
    ("SINCRONIZACIÓN", [
        ("p", "Pull:", "Traer cambios del remoto (git pull)."),
        ("u", "Push:", "Subir commits locales al remoto (git push)."),
        ("f", "Fetch:", "Bajar referencias remotas sin merge (git fetch)."),
    ]),
    ("CAMBIOS", [
        ("a", "Stage All:", "Agregar todos los archivos al stage (git add -A)."),
        ("w", "Commit:", "Abrir modal para escribir mensaje y confirmar (git commit)."),
        ("e", "Amend:", "Modificar el mensaje del último commit (git commit --amend)."),
        ("v", "Ver Diff:", "Mostrar el diff del archivo seleccionado en el panel de estado."),
        ("H", "Stage Hunk:", "Stagear hunks individuales del archivo modificado. Flechas o `p`/`n` para navegar hunks."),
        ("C", "Cambios sin commit:", "Abrir pantalla completa con lista de archivos y diff coloreado. Enter stage/unstage, flechas cambian el diff."),
        ("Tab", "Ciclo foco:", "Navegar entre Ramas → Staged → Unstaged → Historial."),
        ("i", "Ver .gitignore:", "Abrir el archivo .gitignore en un modal de lectura."),
        ("I", "Ignorar archivo:", "Agregar el archivo no trackeado seleccionado al .gitignore."),
        ("x", "Descartar cambios:", "Descartar cambios locales del archivo seleccionado (git checkout --)."),
    ]),
    ("CONFLICTOS", [
        ("M", "Resolver conflictos:", "Abrir resolución de conflictos de merge (ours/theirs/both)."),
    ]),
    ("STASH", [
        ("z", "Stash Push:", "Guardar cambios actuales en el stash (mensaje opcional)."),
        ("Z", "Stash Pop:", "Recuperar y aplicar el último stash guardado."),
    ]),
    ("HISTORIAL", [
        ("Enter", "Detalle:", "Ver autor, fecha, mensaje y diff del commit seleccionado."),
        ("R", "Rebase interactivo:", "Abrir rebase interactivo con pick/reword/squash/fixup/drop."),
        ("g", "Toggle Graph:", "Alternar entre lista de commits y log gráfico."),
        ("l", " +Commits:", "Cargar 20 commits más en el historial."),
    ]),
    ("TAGS", [
        ("t", "Crear Tag:", "Crear un tag ligero con el nombre que se ingrese."),
        ("T", "Borrar Tag:", "Eliminar el tag seleccionado en la lista (pide confirmación)."),
    ]),
    ("OTROS", [
        ("y", "Cherry-Pick:", "Aplicar un commit de otra rama por su SHA."),
        ("r", "Comando:", "Ejecutar cualquier comando git personalizado (sin prefijo 'git ')."),
        ("F5", "Refrescar:", "Actualizar manualmente toda la interfaz."),
        ("?", "Ayuda:", "Mostrar esta pantalla de ayuda completa."),
        ("q", "Salir:", "Cerrar GitCriollo."),
    ]),
]


class VentanaAyuda(ModalScreen):
    BINDINGS = [("escape", "quit", "Cerrar"), ("q", "quit", "Cerrar"), ("?", "quit", "Cerrar")]

    CSS = """
    VentanaAyuda { align: center middle; background: rgba(0,0,0,0.85); }
    #dialog_ayuda { padding: 1 3; background: #1a1a1a; border: heavy #ffaf00; width: 85%; height: 85%; }
    #scroll { overflow-y: auto; height: 1fr; margin-bottom: 1; }
    .seccion-titulo { color: #ffaf00; text-style: bold; margin-top: 1; border-bottom: dashed #333; }
    .fila { height: auto; padding: 0 0; margin-left: 2; }
    .tecla { color: #00afff; text-style: bold; width: 10; }
    .accion { color: #ffaf00; text-style: bold; width: 16; }
    .descrip { color: #ccc; width: 1fr; }
    #footer { color: #888; text-align: center; }
    """

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("[bold #ffaf00]─── GITCRIOLLO — AYUDA COMPLETA ───[/]\n"),
            Vertical(id="scroll"),
            Label("[dim]Presioná [bold]Q[/bold], [bold]ESC[/bold] o [bold]?[/bold] para cerrar[/dim]", id="footer"),
            id="dialog_ayuda"
        )

    async def on_mount(self) -> None:
        scroll = self.query_one("#scroll", Vertical)
        items = []
        for titulo, atajos in SECCIONES:
            items.append(Label(f"\n[bold #ffaf00]• {titulo}[/]", classes="seccion-titulo"))
            for tecla, accion, descrip in atajos:
                items.append(Horizontal(
                    Label(f"[[{tecla}]]", classes="tecla"),
                    Label(f"{accion}", classes="accion"),
                    Label(f"{descrip}", classes="descrip"),
                    classes="fila",
                ))
        # Usamos mount_all de forma asíncrona para garantizar un layout limpio
        await scroll.mount_all(items)

    def action_quit(self) -> None:
        self.dismiss()


