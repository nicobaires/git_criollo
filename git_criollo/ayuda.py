from textual.app import ComposeResult
from textual.widgets import Label
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal


SECCIONES = [
    ("RAMAS", [
        ("N", "Nueva rama:", "Crear una rama local a partir del commit actual."),
        ("C", "Checkout:", "Cambiar a la rama seleccionada. Si es remota crea una local con tracking."),
        ("D", "Borrar rama:", "Eliminar la rama local seleccionada (pide confirmación)."),
        ("M", "Merge:", "Fusionar la rama seleccionada en la actual (pide confirmación)."),
    ]),
    ("SINCRONIZACIÓN", [
        ("P", "Pull:", "Traer cambios del remoto (git pull)."),
        ("U", "Push:", "Subir commits locales al remoto (git push)."),
        ("F", "Fetch:", "Bajar referencias remotas sin merge (git fetch)."),
    ]),
    ("CAMBIOS", [
        ("A", "Stage All:", "Agregar todos los archivos al stage (git add -A)."),
        ("W", "Commit:", "Abrir modal para escribir mensaje y confirmar (git commit)."),
        ("E", "Amend:", "Modificar el mensaje del último commit (git commit --amend)."),
        ("V", "Ver Diff:", "Mostrar el diff del archivo seleccionado en el panel de estado."),
        ("C", "Cambios sin commit:", "Abrir pantalla completa con lista de archivos y diff coloreado. Enter stage/unstage, flechas cambian el diff."),
        ("Tab", "Ciclo foco:", "Navegar entre Ramas → Staged → Unstaged → Historial."),
    ]),
    ("STASH", [
        ("z", "Stash Push:", "Guardar cambios actuales en el stash (mensaje opcional)."),
        ("Z", "Stash Pop:", "Recuperar y aplicar el último stash guardado."),
    ]),
    ("HISTORIAL", [
        ("Enter", "Detalle:", "Ver autor, fecha, mensaje y diff del commit seleccionado."),
        ("G", "Toggle Graph:", "Alternar entre lista de commits y log gráfico."),
        ("L", " +Commits:", "Cargar 20 commits más en el historial."),
    ]),
    ("TAGS", [
        ("t", "Crear Tag:", "Crear un tag ligero con el nombre que se ingrese."),
        ("T", "Borrar Tag:", "Eliminar el tag seleccionado en la lista (pide confirmación)."),
    ]),
    ("OTROS", [
        ("Y", "Cherry-Pick:", "Aplicar un commit de otra rama por su SHA."),
        ("R", "Comando:", "Ejecutar cualquier comando git personalizado (sin prefijo 'git ')."),
        ("?", "Ayuda:", "Mostrar esta pantalla de ayuda completa."),
        ("Q", "Salir:", "Cerrar GitCriollo."),
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
                    Label(f"[{tecla}]", classes="tecla"),
                    Label(f"{accion}", classes="accion"),
                    Label(f"{descrip}", classes="descrip"),
                    classes="fila",
                ))
        # Usamos mount_all de forma asíncrona para garantizar un layout limpio
        await scroll.mount_all(items)

    def action_quit(self) -> None:
        self.dismiss()