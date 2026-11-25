"""Selecciona una única carpeta de datos por proceso, sin mezclar las bases."""
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
HISTORICO_DIR = BASE_DIR / 'data'
DEMO_DIR = HISTORICO_DIR / 'demostracion'
MODO_DEMO = '--demo' in sys.argv
DATA_DIR = DEMO_DIR if MODO_DEMO else HISTORICO_DIR
ETIQUETA_BASE = 'DEMOSTRACIÓN SINTÉTICA AISLADA' if MODO_DEMO else 'BASE HISTÓRICA SINTÉTICA ORIGINAL'


def etiqueta_carpeta(carpeta):
    carpeta = Path(carpeta).resolve()
    if carpeta == DEMO_DIR.resolve():
        return 'DEMOSTRACIÓN SINTÉTICA AISLADA'
    if carpeta == HISTORICO_DIR.resolve():
        return 'BASE HISTÓRICA SINTÉTICA ORIGINAL'
    return 'CONJUNTO DE DATOS SUMINISTRADO'
