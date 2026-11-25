from datetime import datetime, timedelta, timezone
import re

TIPOS_DOCUMENTO = ["CC", "TI", "CE", "PP", "NIT"]
TIPOS_TELEFONO = ["Celular", "Fijo", "Corporativo", "Otro"]
TIPOS_SOLICITUD = ["Peticion", "Queja", "Reclamo", "Sugerencia"]
CANALES_RECEPCION = [
    "Presencial",
    "Correo electrónico",
    "Página web",
    "Teléfono",
    "Redes sociales",
    "Otro",
]
TIPOS_MASCOTA = ["Perro", "Gato", "Otro"]
CAMPUS_VALIDOS = [
    "Campus Medellín - Ciudad Universitaria",
    "Campus Medellín - Ciudadela Robledo",
    "Campus en el Área de la salud",
    "Campus Medellín - Sede de Posgrado",
    "Campus Medellín - Edificio San Ignacio",
    "Campus Medellín - Antigua Escuela de Derecho",
    "Campus Medellín - Edificio Antioquia",
    "Campus Medellín - Casas Patrimoniales",
    "Campus Medellín - Edificio de Extensión",
]
ESTADOS_VALIDOS = ["Registrada", "En proceso", "Solucionada"]


def validar_nombre(nombre: str) -> bool:
    if not nombre or not (3 <= len(nombre.strip()) <= 100):
        return False
    patron = r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ'\- ]+$"
    return bool(re.fullmatch(patron, nombre.strip())) and any(c.isalpha() for c in nombre)


def validar_tipo_documento(tipo_doc: str) -> bool:
    return tipo_doc in TIPOS_DOCUMENTO


def validar_numero_documento(num_doc: str) -> bool:
    if not num_doc or not (3 <= len(num_doc) <= 15):
        return False
    return bool(re.fullmatch(r"[0-9]{3,15}", num_doc))


def validar_tipo_telefono(tipo_tel: str) -> bool:
    return tipo_tel in TIPOS_TELEFONO


def validar_telefono_contacto(tel: str) -> bool:
    return bool(re.fullmatch(r"[0-9]{10}", tel or ""))


def validar_correo(correo: str) -> bool:
    if not correo or len(correo) > 254:
        return False
    local, sep, dominio = correo.strip().partition("@")
    if not sep or not local or len(local) > 64 or local.startswith(".") or local.endswith(".") or ".." in local:
        return False
    if not re.fullmatch(r"[\w.!#$%&'*+/=?^_`{}~\-]+", local):
        return False
    partes = dominio.split(".")
    return (len(partes) >= 2 and bool(re.fullmatch(r"[A-Za-z]{2,63}", partes[-1]))
            and all(re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", x) for x in partes))


def validar_direccion(direccion: str) -> bool:
    if not direccion or direccion.strip() == "N/A":
        return True
    if not (5 <= len(direccion.strip()) <= 200):
        return False
    patron = r"^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ#\-.,/ ]+$"
    return bool(re.fullmatch(patron, direccion.strip()))


def validar_tipo_solicitud(tipo: str) -> bool:
    return tipo in TIPOS_SOLICITUD


def validar_fecha_radicacion(fecha_str: str, formato: str = "%Y-%m-%d %H:%M:%S") -> bool:
    try:
        fecha_dt = datetime.strptime(fecha_str.strip(), formato)
    except (ValueError, AttributeError):
        return False
    return fecha_dt <= ahora_local()


def validar_canal_recepcion(canal: str) -> bool:
    return canal in CANALES_RECEPCION


def validar_asunto(asunto: str) -> bool:
    if not asunto or not asunto.strip():
        return False
    longitud = len(asunto.strip())
    if not (5 <= longitud <= 150):
        return False
    patron = r"^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ.,;:¿?¡!()\- ]+$"
    return bool(re.fullmatch(patron, asunto.strip()))


def validar_descripcion(descripcion: str) -> bool:
    if not descripcion or not descripcion.strip():
        return False
    return 20 <= len(descripcion.strip()) <= 2000 and "\x00" not in descripcion


def validar_tipo_mascota(mascota: str) -> bool:
    return mascota in TIPOS_MASCOTA


def validar_campus(campus: str) -> bool:
    return campus in CAMPUS_VALIDOS


def validar_estado(estado: str) -> bool:
    return estado in ESTADOS_VALIDOS


def validar_transicion_estado(estado_actual: str, estado_nuevo: str) -> bool:
    flujo = {
        "Registrada": ["En proceso"],
        "En proceso": ["Solucionada"],
        "Solucionada": [],
    }
    return estado_nuevo in flujo.get(estado_actual, [])

PERFILES = ["Estudiante", "Docente", "Administrativo", "Ciudadano"]
PLAZO_MAXIMO_DIAS = 30
FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"

def validar_perfil(perfil):
    return perfil in PERFILES

def errores_registro(reg):
    validadores = {"nombre_completo": validar_nombre, "tipo_documento": validar_tipo_documento,
        "numero_documento": validar_numero_documento, "tipo_telefono": validar_tipo_telefono,
        "telefono_contacto": validar_telefono_contacto, "correo_electronico": validar_correo,
        "direccion": validar_direccion, "tipo_solicitud": validar_tipo_solicitud,
        "fecha_radicacion": validar_fecha_radicacion, "canal_recepcion": validar_canal_recepcion,
        "asunto_titulo": validar_asunto, "descripcion_detallada": validar_descripcion,
        "tipo_mascota": validar_tipo_mascota, "campus_relacionado": validar_campus,
        "perfil_solicitante": validar_perfil}
    return [campo for campo, validar in validadores.items() if not validar(reg.get(campo, ""))]


def ahora_local():
    """Fecha y hora de Colombia (UTC-5), sin sufijo en el TXT."""
    return datetime.now(timezone(timedelta(hours=-5))).replace(tzinfo=None)
