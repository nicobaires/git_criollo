from textual.app import ComposeResult
from textual.widgets import Label
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal


SECCIONES = [
    ("RAMAS", [
        ("N", "Nueva rama", "Crear una nueva rama local. Te pide el nombre y la crea a partir del commit actual."),
        ("C", "Checkout", "Cambiar a la rama seleccionada en la lista. Si es remota, crea una local con el mismo nombre y hace seguimiento."),
        ("D", "Borrar rama", "Eliminar la rama seleccionada. No permite borrar la rama activa ni ramas remotas. Pide confirmación."),
        ("M", "Merge", "Mergear la rama seleccionada en la rama actual. Pide confirmación antes de ejecutar."),
    ]),
    ("SINCRONIZACIÓN", [
        ("P", "Pull", "Traer los últimos cambios del remoto (git pull) y actualiza la interfaz."),
        ("U", "Push", "Subir los commits locales al remoto (git push) y refresca la información de ahead/behind."),
        ("F", "Fetch", "Bajar las referencias del remoto sin hacer merge (git fetch). Útil para ver ramas nuevas sin mezclar."),
    ]),
    ("CAMBIOS", [
        ("A", "Stage All", "Agregar todos los archivos modificados y no trackeados al stage (git add -A)."),
        ("W", "Commit", "Abrir un modal para escribir el mensaje del commit y confirmarlo (git commit)."),
        ("E", "Amend", "Modificar el mensaje del último commit. Equivale a git commit --amend -m 'mensaje'."),
        ("V", "Ver Diff", "Mostrar el diff del archivo seleccionado en el panel de estado (staged o unstaged)."),
        ("Tab", "Ciclo foco", "Navegar entre los paneles: Ramas → Staged → Unstaged → Historial → Ramas ..."),
    ]),
    ("STASH", [
        ("z", "Stash Push", "Guardar los cambios actuales en el stash. Podés agregar un mensaje opcional."),
        ("Z", "Stash Pop", "Recuperar el último stash guardado y aplicarlo sobre los archivos actuales."),
    ]),
    ("HISTORIAL", [
        ("Enter", "Detalle", "Ver el detalle completo del commit seleccionado: autor, fecha, mensaje y diff estadístico."),
        ("G", "Toggle Graph", "Alternar entre la vista de lista de commits y el log gráfico con --graph --oneline --all."),
        ("L", "+Commits", "Cargar 20 commits más en el historial. Funciona tanto en modo lista como en modo gráfico."),
    ]),
    ("TAGS", [
        ("t", "Crear Tag", "Crear un tag ligero con el nombre que se ingrese (git tag <nombre>)."),
        ("T", "Borrar Tag", "Eliminar un tag. Seleccioná el tag en la lista y presioná T, o Enter sobre él y confirmá."),
    ]),
    ("OTROS", [
        ("Y", "Cherry-Pick", "Aplicar un commit de otra rama a la rama actual. Ingresá el SHA del commit (git cherry-pick)."),
        ("R", "Comando", "Ejecutar cualquier comando git personalizado. No escribas el prefijo 'git '. El resultado se muestra en una ventana."),
        ("?", "Ayuda", "Mostrar esta pantalla de ayuda completa con la descripción de todos los atajos."),
        ("Q", "Salir", "Cerrar GitCriollo."),
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
    .tecla { color: #00afff; text-style: bold; width: 10; }
    .accion { color: #00ff00; width: 20; }
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
