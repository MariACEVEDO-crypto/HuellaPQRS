from validaciones import ahora_local
from datetime import datetime, timedelta
from textwrap import wrap
from threading import RLock
from functools import wraps
from pathlib import Path
import pandas as pd
from validaciones import (validar_transicion_estado, errores_registro, FORMATO_FECHA, PLAZO_MAXIMO_DIAS,
    TIPOS_DOCUMENTO, TIPOS_TELEFONO, CANALES_RECEPCION, TIPOS_MASCOTA, CAMPUS_VALIDOS, ESTADOS_VALIDOS, PERFILES)

# Protege las escrituras dentro de una misma instancia del programa.
_candado = RLock()
def escritura_segura(funcion):
    @wraps(funcion)
    def ejecutar(*args, **kwargs):
        with _candado:
            return funcion(*args, **kwargs)
    return ejecutar

from rutas import BASE_DIR, DATA_DIR, MODO_DEMO
RADICADOS_DIR = DATA_DIR / "radicados"

CAMPOS = [
    "id",
    "nombre_completo",
    "tipo_documento",
    "numero_documento",
    "tipo_telefono",
    "telefono_contacto",
    "correo_electronico",
    "direccion",
    "tipo_solicitud",
    "fecha_radicacion",
    "canal_recepcion",
    "asunto_titulo",
    "descripcion_detallada",
    "tipo_mascota",
    "campus_relacionado",
    "fecha_maxima_respuesta",
    "estado_peticion",
    "usuario_registro",
    "fecha_respuesta",
    "perfil_solicitante",
    "fecha_registro",
]

TIPOS_VALIDOS = ["Peticion", "Queja", "Reclamo", "Sugerencia"]


def obtener_ruta_archivo(tipo_solicitud: str, carpeta: Path = DATA_DIR) -> Path:
    tipo_limpio = tipo_solicitud.strip().capitalize()
    if tipo_limpio not in TIPOS_VALIDOS:
        raise ValueError(f"Tipo de solicitud no válido: {tipo_solicitud}")
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta / f"{tipo_limpio}.txt"


def cargar_registros(ruta: Path) -> list[dict]:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    if not ruta.exists() or ruta.stat().st_size == 0:
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("|".join(CAMPOS) + "\n")
        return []

    df = pd.read_csv(ruta, sep="|", dtype=str, engine="python", keep_default_na=False)
    # Los archivos antiguos pueden carecer de las tres columnas nuevas, no de las originales.
    columnas_antiguas = set(CAMPOS) - {"fecha_respuesta", "perfil_solicitante", "fecha_registro"}
    if not columnas_antiguas.issubset(df.columns) or set(df.columns) - set(CAMPOS) or not isinstance(df.index, pd.RangeIndex):
        raise ValueError(f"Estructura inesperada de {ruta.name}; revise el archivo sin sobrescribirlo.")
    for col in CAMPOS:
        if col not in df.columns:
            df[col] = ""
    df = df[CAMPOS].fillna("")
    for col in CAMPOS:
        df[col] = df[col].str.strip()
    # Estandarizar únicamente categorías conocidas. No inferir datos faltantes.
    categorias = {"tipo_documento": TIPOS_DOCUMENTO, "tipo_telefono": TIPOS_TELEFONO,
        "tipo_solicitud": TIPOS_VALIDOS, "canal_recepcion": CANALES_RECEPCION,
        "tipo_mascota": TIPOS_MASCOTA, "campus_relacionado": CAMPUS_VALIDOS,
        "estado_peticion": ESTADOS_VALIDOS, "perfil_solicitante": PERFILES}
    for campo, valores in categorias.items():
        equivalencias = {valor.casefold(): valor for valor in valores}
        if campo == "tipo_solicitud": equivalencias["petición"] = "Peticion"
        df[campo] = df[campo].map(lambda valor: equivalencias.get(valor.casefold(), valor))
    ids = df["id"].tolist()
    if any(not x.isascii() or not x.isdigit() or len(x)>15 or int(x)<1 for x in ids):
        raise ValueError(f"IDs inválidos en {ruta.name}; no se modificó el archivo.")
    if sorted(map(int, ids)) != list(range(1, len(ids)+1)):
        raise ValueError(f"IDs duplicados o discontinuos en {ruta.name}; no se modificó el archivo.")
    if ruta.stem in TIPOS_VALIDOS and not (df["tipo_solicitud"] == ruta.stem).all():
        raise ValueError(f"Tipo de solicitud incompatible con {ruta.name}.")
    return df.to_dict(orient="records")


def _guardar_lista_en_archivo(ruta: Path, registros: list[dict]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(registros, columns=CAMPOS).fillna("")
    temporal = ruta.with_suffix(".tmp")
    df.to_csv(temporal, sep="|", index=False, encoding="utf-8")
    temporal.replace(ruta)


@escritura_segura
def guardar_registro(registro: dict, carpeta: Path = DATA_DIR) -> dict:
    errores = errores_registro(registro)
    if errores:
        raise ValueError("Campos inválidos: " + ", ".join(errores))
    from usuarios import cargar_usuarios
    usuarios = cargar_usuarios(carpeta / "Usuarios.txt")
    if not ((usuarios["usuario"] == registro.get("usuario_registro")) & (usuarios["estado"] == "Activo")).any():
        raise ValueError("Usuario registrador no autorizado")
    registro["estado_peticion"] = "Registrada"
    fecha_registro = ahora_local()
    registro["fecha_registro"] = fecha_registro.strftime(FORMATO_FECHA)
    registro["fecha_maxima_respuesta"] = (fecha_registro + timedelta(days=PLAZO_MAXIMO_DIAS)).strftime(FORMATO_FECHA)
    tipo_sol = registro["tipo_solicitud"]
    ruta = obtener_ruta_archivo(tipo_sol, carpeta)
    registros = cargar_registros(ruta)

    ids_existentes = []
    for r in registros:
        try:
            ids_existentes.append(int(str(r.get("id", "0")).strip()))
        except ValueError:
            pass

    nuevo_id = (max(ids_existentes) + 1) if ids_existentes else 1
    registro["id"] = str(nuevo_id)
    registro["tipo_solicitud"] = tipo_sol

    direccion_limpia = str(registro.get("direccion", "")).strip()
    registro["direccion"] = direccion_limpia if direccion_limpia else "N/A"

    registro["fecha_respuesta"] = ""
    registros.append(registro)
    _guardar_lista_en_archivo(ruta, registros)
    return registro


@escritura_segura
def actualizar_registro(registro_actualizado: dict, carpeta: Path = DATA_DIR) -> bool:
    tipo_sol = registro_actualizado.get("tipo_solicitud", "Peticion").strip().capitalize()
    ruta = obtener_ruta_archivo(tipo_sol, carpeta)
    registros = cargar_registros(ruta)

    id_buscado = str(registro_actualizado.get("id", "")).strip()
    for idx, reg in enumerate(registros):
        if str(reg.get("id", "")).strip() == id_buscado:
            estado_actual = reg["estado_peticion"]
            estado_nuevo = registro_actualizado.get("estado_peticion", estado_actual)
            if not validar_transicion_estado(estado_actual, estado_nuevo):
                return False

            actualizado = reg.copy()
            actualizado["estado_peticion"] = estado_nuevo
            # La fecha de respuesta se asigna solo al cerrar la solicitud.
            actualizado["fecha_respuesta"] = reg.get("fecha_respuesta", "")
            if estado_actual == "En proceso" and estado_nuevo == "Solucionada":
                actualizado["fecha_respuesta"] = ahora_local().strftime("%Y-%m-%d %H:%M:%S")
            registros[idx] = actualizado
            _guardar_lista_en_archivo(ruta, registros)
            registro_actualizado.update(actualizado)
            return True
    return False


def obtener_todos_los_registros(carpeta: Path = DATA_DIR) -> list[dict]:
    todos = []
    for tipo in TIPOS_VALIDOS:
        ruta = obtener_ruta_archivo(tipo, carpeta)
        todos.extend(cargar_registros(ruta))
    return todos


def formatear_radicado_ascii(reg: dict) -> str:
    anc = 120
    borde = "+" + "-" * (anc - 2) + "+"

    def fmt_linea(texto: str) -> str:
        partes = wrap(texto, width=anc-4, break_long_words=True, break_on_hyphens=False) or [""]
        return "\n".join("| " + parte.ljust(anc-4) + " |" for parte in partes)

    def fmt_centrado(texto: str) -> str:
        contenido = texto[: anc - 4]
        return "| " + contenido.center(anc - 4) + " |"

    direccion_val = str(reg.get("direccion", "")).strip() or "N/A"
    id_formateado = str(reg.get("id", "0")).zfill(6)

    lineas = [
        borde,
        fmt_centrado("UNIVERSIDAD DE ANTIOQUIA - MEPEGA"),
        fmt_centrado("COMPROBANTE DE DEMOSTRACIÓN SINTÉTICA" if MODO_DEMO else "COMPROBANTE OFICIAL DE RADICACIÓN DE PQRS"),
        borde,
        fmt_linea(
            f"RADICADO ID: {id_formateado} | FECHA RADICACIÓN: {reg.get('fecha_radicacion', 'N/A')}"
        ),
        fmt_linea(
            f"ESTADO: {reg.get('estado_peticion', 'Registrada')} | FECHA MÁXIMA RESPUESTA: {reg.get('fecha_maxima_respuesta', 'N/A')}"
        ),
        fmt_linea(f"FECHA DE REGISTRO: {reg.get('fecha_registro') or 'N/A'}"),
        fmt_linea(f"FECHA REAL DE RESPUESTA: {reg.get('fecha_respuesta') or 'N/A'}"),
        borde,
        fmt_centrado("DATOS DEL SOLICITANTE"),
        fmt_linea(f"Nombre Completo   : {reg.get('nombre_completo', 'N/A')}"),
        fmt_linea(
            f"Documento         : {reg.get('tipo_documento', 'N/A')} {reg.get('numero_documento', 'N/A')}"
        ),
        fmt_linea(
            f"Teléfono Contacto : {reg.get('telefono_contacto', 'N/A')} ({reg.get('tipo_telefono', 'N/A')})"
        ),
        fmt_linea(f"Correo Electrónico: {reg.get('correo_electronico', 'N/A')}"),
        fmt_linea(f"Dirección         : {direccion_val}"),
        fmt_linea(f"Perfil solicitante: {reg.get('perfil_solicitante') or 'No disponible'}"),
        borde,
        fmt_centrado("CLASIFICACIÓN Y UBICACIÓN"),
        fmt_linea(
            f"Tipo Solicitud    : {reg.get('tipo_solicitud', 'N/A')} | Canal Recepción: {reg.get('canal_recepcion', 'N/A')}"
        ),
        fmt_linea(
            f"Tipo de Mascota   : {reg.get('tipo_mascota', 'N/A')} | Campus UdeA: {reg.get('campus_relacionado', 'N/A')}"
        ),
        borde,
        fmt_centrado("RESUMEN DE LA SOLICITUD"),
        fmt_linea(f"Asunto / Título   : {reg.get('asunto_titulo', 'N/A')}"),
        fmt_linea(f"Registrado Por    : {reg.get('usuario_registro', 'N/A')}"),
        borde,
    ]
    return "\n".join(lineas)


def exportar_radicado_txt(reg: dict, carpeta_salida: Path = RADICADOS_DIR) -> Path:
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    tipo_limpio = str(reg.get("tipo_solicitud", "PQRS")).strip().capitalize()
    id_limpio = str(reg.get("id", "0")).strip().zfill(6)
    ruta_txt = carpeta_salida / f"radicado_{tipo_limpio}_{id_limpio}.txt"
    contenido = formatear_radicado_ascii(reg)
    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write(contenido + "\n")
    return ruta_txt

def consultar_registros(tipo="Todas", id_buscar="", carpeta=DATA_DIR):
    registros = obtener_todos_los_registros(carpeta) if tipo == "Todas" else cargar_registros(obtener_ruta_archivo(tipo, carpeta))
    criterio = id_buscar.strip()
    if criterio:
        if len(criterio) > 15 or not criterio.isascii() or not criterio.isdigit():
            return []
        return [r for r in registros if r["id"] == str(int(criterio))]
    return registros
