"""Migración específica de la entrega original sintética. No usar con datos reales."""
import csv
from pathlib import Path
from archivos import CAMPOS, TIPOS_VALIDOS, DATA_DIR, _guardar_lista_en_archivo
from validaciones import validar_telefono_contacto


def migrar(carpeta=DATA_DIR, confirmar_sinteticos=False):
    if not confirmar_sinteticos:
        raise ValueError('Solo se permite reparar teléfonos de una base sintética verificada.')
    cambios=[]
    for tipo in TIPOS_VALIDOS:
        ruta=Path(carpeta)/f'{tipo}.txt'
        with ruta.open(encoding='utf-8',newline='') as f:
            registros=list(csv.DictReader(f,delimiter='|'))
        for r in registros:
            r.setdefault('fecha_respuesta',''); r.setdefault('perfil_solicitante',''); r.setdefault('fecha_registro','')
            tel=r['telefono_contacto']
            if not validar_telefono_contacto(tel):
                if len(tel)==9 and tel.startswith('3') and tel.isascii() and tel.isdigit():
                    r['telefono_contacto']='30'+tel[1:]
                    cambios.append((tipo,r['id'],'Teléfono sintético: cero añadido después del prefijo 3'))
                else:
                    raise ValueError(f'Teléfono fuera del patrón esperado: {tipo} #{r["id"]}')
        _guardar_lista_en_archivo(ruta,registros)
    return cambios
