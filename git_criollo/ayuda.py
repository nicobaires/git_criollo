from textual.app import ComposeResult
from textual.widgets import Label
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal


SECCIONES = [
    ("RAMAS", [
        ("N", "Presioná N →", "Nueva rama: crear una rama local a partir del commit actual."),
        ("C", "Presioná C →", "Checkout: cambiar a la rama seleccionada. Si es remota crea una local con tracking."),
        ("D", "Presioná D →", "Borrar rama: eliminar la rama local seleccionada (pide confirmación)."),
        ("M", "Presioná M →", "Merge: fusionar la rama seleccionada en la actual (pide confirmación)."),
    ]),
    ("SINCRONIZACIÓN", [
        ("P", "Presioná P →", "Pull: traer cambios del remoto (git pull)."),
        ("U", "Presioná U →", "Push: subir commits locales al remoto (git push)."),
        ("F", "Presioná F →", "Fetch: bajar referencias remotas sin merge (git fetch)."),
    ]),
    ("CAMBIOS", [
        ("A", "Presioná A →", "Stage All: agregar todos los archivos al stage (git add -A)."),
        ("W", "Presioná W →", "Commit: abrir modal para escribir mensaje y confirmar (git commit)."),
        ("E", "Presioná E →", "Amend: modificar el mensaje del último commit (git commit --amend)."),
        ("V", "Presioná V →", "Ver Diff: mostrar el diff del archivo seleccionado en el panel de estado."),
        ("Tab", "Presioná Tab →", "Ciclo foco: navegar entre Ramas → Staged → Unstaged → Historial."),
    ]),
    ("STASH", [
        ("z", "Presioná z →", "Stash Push: guardar cambios actuales en el stash (mensaje opcional)."),
        ("Z", "Presioná Z →", "Stash Pop: recuperar y aplicar el último stash guardado."),
    ]),
    ("HISTORIAL", [
        ("Enter", "Presioná Enter →", "Detalle: ver autor, fecha, mensaje y diff del commit seleccionado."),
        ("G", "Presioná G →", "Toggle Graph: alternar entre lista de commits y log gráfico."),
        ("L", "Presioná L →", "+Commits: cargar 20 commits más en el historial."),
    ]),
    ("TAGS", [
        ("t", "Presioná t →", "Crear Tag: crear un tag ligero con el nombre que se ingrese."),
        ("T", "Presioná T →", "Borrar Tag: eliminar el tag seleccionado en la lista (pide confirmación)."),
    ]),
    ("OTROS", [
        ("Y", "Presioná Y →", "Cherry-Pick: aplicar un commit de otra rama por su SHA."),
        ("R", "Presioná R →", "Comando: ejecutar cualquier comando git personalizado (sin prefijo 'git ')."),
        ("?", "Presioná ? →", "Ayuda: mostrar esta pantalla de ayuda completa."),
        ("Q", "Presioná Q →", "Salir: cerrar GitCriollo."),
    ]),
]


class VentanaAyuda(ModalScreen):
    BINDINGS = [("escape", "quit", "Cerrar"), ("q", "quit", "Cerrar"), ("?", "quit", "Cerrar")]

    CSS = """
    VentanaAyuda { align: center middle; background: rgba(0,0,0,0.85); }
    #dialog_ayuda { padding: 1 3; background: #1a1a1a; border: heavy #ffaf00; width: 90%; height: 90%; }
    #scroll { overflow-y: auto; height: 1fr; }
    .seccion { margin-top: 1; }
    .seccion-titulo { color: #ffaf00; text-style: bold; margin-bottom: 1; }
    .fila { height: 3; margin-left: 2; }
    .tecla { color: #00afff; text-style: bold; width: 8; }
    .accion { color: #ffaf00; width: 18; }
    .descrip { color: #ccc; }
    .footer { margin-top: 1; color: #888; }
    """

    def compose(self) -> ComposeResult:
        children = [
            Label("[bold #ffaf00]─── GITCRIOLLO — AYUDA COMPLETA ───[/]", id="titulo"),
            Vertical(id="scroll"),
            Label("[dim]Presioná [bold]Q[/bold], [bold]ESC[/bold] o [bold]?[/bold] para cerrar[/dim]", id="footer"),
        ]
        yield Vertical(*children, id="dialog_ayuda")

    def on_mount(self) -> None:
        scroll = self.query_one("#scroll", Vertical)
        items = []
        for titulo, atajos in SECCIONES:
            items.append(Label(f"\n{ titulo }", classes="seccion-titulo"))
            for tecla, accion, descrip in atajos:
                items.append(Horizontal(
                    Label(f"[bold #00afff][{ tecla }][/]", classes="tecla"),
                    Label(f"{ accion }", classes="accion"),
                    Label(f"{ descrip }", classes="descrip"),
                    classes="fila",
                ))
        scroll.mount(*items)

    def action_quit(self) -> None:
        self.dismiss()
