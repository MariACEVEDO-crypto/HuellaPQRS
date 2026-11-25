from validaciones import ahora_local
from datetime import datetime, timedelta
from pathlib import Path
import random

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

from archivos import CAMPOS

NOMBRES = [
    "Valentina Andrea Mejía Gómez",
    "Mateo Alejandro Loaiza Ríos",
    "Sofía Isabel Hincapié Toro",
    "Juan Sebastián Correa Zapata",
    "Mariana Lucía Ospina Valencia",
    "David Esteban Monsalve Ruiz",
    "Camila Andrea Vélez Restrepo",
    "Tomás Felipe Cardona Pérez",
    "Sara Valentina Echeverri Gil",
    "Daniel Andrés Montoya Ortiz",
    "Isabella Sofía Cano Bedoya",
    "Samuel David Marín Jaramillo",
    "Laura Camila Zuluaga Henao",
    "Alejandro José Palacio Gaviria",
    "Manuela Alejandra Londoño Arango",
]

TIPOS_DOC = ["CC", "TI", "CE", "PP", "NIT"]
TIPOS_TEL = ["Celular", "Fijo", "Corporativo", "Otro"]
CANALES = [
    "Presencial",
    "Correo electrónico",
    "Página web",
    "Teléfono",
    "Redes sociales",
    "Otro",
]
MASCOTAS = ["Perro", "Gato", "Otro"]
CAMPUS = [
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
ESTADOS = ["Registrada", "En proceso", "Solucionada"]
USUARIOS = [
    "admin_udea",
    "jbedoya_udea",
    "dgiraldo_udea",
    "rquintero_udea",
    "mvelez_udea",
    "jgomez_udea",
    "lrestrepo_udea",
    "cparra_udea",
    "fherrera_udea",
    "apineda_udea",
    "scardenas_udea",
    "mtorres_udea",
]

PLANTILLAS = {
    "Peticion": [
        (
            "Petición de jornada de bienestar animal",
            "Solicito información sobre fechas y requisitos para acceder a servicios básicos de atención para {mascota} en el campus.",
        ),
        (
            "Petición de orientación sobre normas de convivencia",
            "Pido orientación institucional frente a las condiciones de tránsito y permanencia de {mascota} en zonas comunes.",
        ),
    ],
    "Queja": [
        (
            "Queja por demora en atención de reporte",
            "Presento queja porque el reporte asociado a {mascota} no ha recibido seguimiento oportuno dentro del tiempo esperado.",
        ),
        (
            "Queja por falta de señalización en áreas comunes",
            "Manifiesto inconformidad por la escasa señalización y limpieza en espacios donde transita {mascota}.",
        ),
    ],
    "Reclamo": [
        (
            "Reclamo por entrega incompleta de kit",
            "Presento reclamo porque el kit asignado para mi {mascota} en el campus llegó incompleto y sin soporte de entrega.",
        ),
        (
            "Reclamo por solicitud duplicada en el sistema",
            "Se registra un reclamo debido a que mi trámite relacionado con {mascota} aparece duplicado con distinto radicado.",
        ),
        (
            "Reclamo por falta de actualización de caso",
            "Han transcurrido varios días desde el reporte de mi {mascota} sin recibir respuesta ni actualización del estado.",
        ),
    ],
    "Sugerencia": [
        (
            "Sugerencia de puntos de hidratación en campus",
            "Sugiero habilitar puntos fijos de agua limpia y sombra para {mascota} en las zonas verdes del campus.",
        ),
        (
            "Sugerencia de jornadas preventivas periódicas",
            "Propongo programar jornadas informativas y preventivas para {mascota} al inicio de cada semestre académico.",
        ),
        (
            "Sugerencia de canal rápido de atención",
            "Recomiendo disponer de un formulario ágil para reportar novedades de {mascota} de manera oportuna.",
        ),
    ],
}


def generar_archivo_pqrs(
    tipo_solicitud: str, ruta_salida: Path, n_registros: int = 3000, seed: int = 2026
) -> None:
    rng = random.Random(seed)
    base_fecha = datetime(2026, 1, 1, 7, 0, 0)
    ahora = ahora_local()
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)

    with open(ruta_salida, "x", encoding="utf-8") as f:
        f.write("|".join(CAMPOS) + "\n")
        for i in range(1, n_registros + 1):
            nombre = rng.choice(NOMBRES)
            tipo_doc = rng.choice(TIPOS_DOC)
            num_doc = str(rng.randint(100000000, 1999999999))
            tipo_tel = rng.choice(TIPOS_TEL)
            tel = f"3{rng.randint(100000000, 299999999)}"
            base_user = nombre.lower().split()[0] + "." + nombre.lower().split()[-1]
            correo = f"{base_user}{i}@correo.com"
            direccion = (
                f"Carrera {rng.randint(40, 85)} #{rng.randint(1, 99)}-{rng.randint(10, 99)}"
                if i % 5 != 0
                else "N/A"
            )
            canal = rng.choice(CANALES)
            mascota = rng.choice(MASCOTAS)
            campus = rng.choice(CAMPUS)
            asunto, desc_tpl = rng.choice(PLANTILLAS[tipo_solicitud])
            desc = desc_tpl.format(mascota=mascota.lower())

            candidata_rad = base_fecha + timedelta(
                days=rng.randint(0, 320),
                hours=rng.randint(0, 12),
                minutes=rng.randint(0, 59),
                seconds=rng.randint(0, 59),
            )
            f_rad = candidata_rad if candidata_rad <= ahora else ahora - timedelta(hours=1)
            f_max = f_rad + timedelta(days=30)
            estado = rng.choice(ESTADOS)
            usuario = rng.choice(USUARIOS)

            fila = [
                str(i),
                nombre,
                tipo_doc,
                num_doc,
                tipo_tel,
                tel,
                correo,
                direccion,
                tipo_solicitud,
                f_rad.strftime("%Y-%m-%d %H:%M:%S"),
                canal,
                asunto,
                desc,
                mascota,
                campus,
                f_max.strftime("%Y-%m-%d %H:%M:%S"),
                estado,
                usuario,
                "",  # No se dispone de una fecha real de respuesta.
                "",  # Perfil histórico desconocido.
                f_rad.strftime("%Y-%m-%d %H:%M:%S"),  # Registro simulado.
            ]
            f.write("|".join(fila) + "\n")


if __name__ == "__main__":
    DATA_DIR = DATA_DIR / "simulacion"
    if any((DATA_DIR / f"{tipo}.txt").exists() for tipo in PLANTILLAS):
        raise SystemExit("Ya existen datos simulados; no se sobrescribirá ningún archivo.")
    generar_archivo_pqrs("Peticion", DATA_DIR / "Peticion.txt", n_registros=3000, seed=55)
    generar_archivo_pqrs("Queja", DATA_DIR / "Queja.txt", n_registros=3000, seed=77)
    generar_archivo_pqrs("Reclamo", DATA_DIR / "Reclamo.txt", n_registros=3000, seed=101)
    generar_archivo_pqrs("Sugerencia", DATA_DIR / "Sugerencia.txt", n_registros=3000, seed=202)
    print(f"Archivos PQRS generados en: {DATA_DIR}")