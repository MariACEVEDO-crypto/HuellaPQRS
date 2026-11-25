"""Crea exclusivamente ocho casos ficticios reproducibles, sin tocar data/*.txt."""
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from archivos import TIPOS_VALIDOS, _guardar_lista_en_archivo
from rutas import DEMO_DIR
from usuarios import generar_hash, guardar_usuarios
from validaciones import CAMPUS_VALIDOS, PERFILES, FORMATO_FECHA, errores_registro

# Cuenta pública del entorno aislado; no es una credencial institucional real.
USUARIO_DEMO = 'demo_operador'
CORREO_DEMO = 'demo.operador@udea.edu.co'
CLAVE_DEMO = 'HuellaDemo!SoloEnsayo26'
CORTE_REFERENCIA = datetime(2026, 11, 24, 12)
DURACIONES_HORAS = (18, 42, 90, 114)


def casos_demostracion():
    nombres = ('Uno', 'Dos', 'Tres', 'Cuatro', 'Cinco', 'Seis', 'Siete', 'Ocho')
    casos = []
    for i, tipo in enumerate(TIPOS_VALIDOS):
        for j in range(2):
            n = 2*i+j
            inicio = CORTE_REFERENCIA - timedelta(days=10+i)
            if j == 1:
                inicio = CORTE_REFERENCIA - timedelta(days=(32, 27, 4, 2)[i])
            fin = inicio + timedelta(hours=DURACIONES_HORAS[i]) if j == 0 else None
            caso = dict(id=str(j+1), nombre_completo='Persona Demo '+nombres[n],
                tipo_documento='CC', numero_documento=str(900001+n), tipo_telefono='Celular',
                telefono_contacto=f'{n+1:010d}', correo_electronico=f'demo{n+1}@example.invalid',
                direccion='N/A', tipo_solicitud=tipo, fecha_radicacion=inicio.strftime(FORMATO_FECHA),
                fecha_registro=inicio.strftime(FORMATO_FECHA), canal_recepcion=('Presencial','Correo electrónico','Página web','Teléfono')[i],
                asunto_titulo='DEMO - Caso ficticio '+nombres[n],
                descripcion_detallada='Caso sintético construido exclusivamente para demostrar los indicadores del proyecto.',
                tipo_mascota=('Perro','Gato','Otro','Perro')[i], campus_relacionado=CAMPUS_VALIDOS[i],
                fecha_maxima_respuesta=(inicio+timedelta(days=30)).strftime(FORMATO_FECHA),
                estado_peticion='Solucionada' if j == 0 else ('En proceso' if i%2 == 0 else 'Registrada'),
                usuario_registro=USUARIO_DEMO, fecha_respuesta=fin.strftime(FORMATO_FECHA) if fin else '',
                perfil_solicitante=PERFILES[i])
            casos.append(caso)
    return casos


def preparar(carpeta=DEMO_DIR):
    carpeta = Path(carpeta)
    # Se rechaza cualquier carpeta que ya exista, incluso si está vacía.
    # Así la regeneración no destruye ensayos ni datos anteriores.
    carpeta.mkdir(parents=True, exist_ok=False)
    casos = casos_demostracion()
    for tipo in TIPOS_VALIDOS:
        _guardar_lista_en_archivo(carpeta / f'{tipo}.txt', [r for r in casos if r['tipo_solicitud']==tipo])
    guardar_usuarios(pd.DataFrame([dict(usuario=USUARIO_DEMO, nombre_completo='Operador Demo',
        correo_institucional=CORREO_DEMO, contrasena=generar_hash(CLAVE_DEMO), rol='Administrador', estado='Activo')]), carpeta/'Usuarios.txt')
    return casos


if __name__ == '__main__':
    try:
        preparar()
        print('Ocho casos sintéticos creados en', DEMO_DIR)
    except FileExistsError:
        raise SystemExit('La carpeta de demostración ya existe. No se sobrescribió ningún archivo.')
