from git_criollo.ventanas.input import (
    VentanaNuevaRama,
    VentanaCommit,
    VentanaStashPush,
    VentanaAmend,
    VentanaTag,
    VentanaCherryPick,
    VentanaComando,
)
from git_criollo.ventanas.confirm import (
    VentanaConfirmarBorrado,
    VentanaConfirmarMerge,
    VentanaConfirmarBorradoTag,
    VentanaConfirmarDescarte,
    VentanaConfirmarPush,
    VentanaConfirmarRebase,
    VentanaConfirmarAmend,
    VentanaConfirmarCherryPick,
    VentanaConfirmarStashPop,
    VentanaConfirmarSalir,
)
from git_criollo.ventanas.viewer import (
    VentanaDiff,
    VentanaDetalleCommit,
    VentanaResultado,
)
from git_criollo.ventanas.uncommitted import VentanaUncommitted
from git_criollo.ventanas.interactive import (
    VentanaStageHunk,
    VentanaRebase,
    VentanaConflictos,
)

__all__ = [
    "VentanaNuevaRama",
    "VentanaCommit",
    "VentanaStashPush",
    "VentanaAmend",
    "VentanaTag",
    "VentanaCherryPick",
    "VentanaComando",
    "VentanaConfirmarBorrado",
    "VentanaConfirmarMerge",
    "VentanaConfirmarBorradoTag",
    "VentanaConfirmarDescarte",
    "VentanaConfirmarPush",
    "VentanaConfirmarRebase",
    "VentanaConfirmarAmend",
    "VentanaConfirmarCherryPick",
    "VentanaConfirmarStashPop",
    "VentanaConfirmarSalir",
    "VentanaDiff",
    "VentanaDetalleCommit",
    "VentanaResultado",
    "VentanaUncommitted",
    "VentanaStageHunk",
    "VentanaRebase",
    "VentanaConflictos",
]
