from pathlib import Path
import numpy as np
import hashlib
import hmac
import secrets
from getpass import getpass
from time import monotonic
from validaciones import validar_correo, validar_nombre
import pandas as pd

from rutas import BASE_DIR, DATA_DIR
ARCHIVO_USUARIOS = DATA_DIR / "Usuarios.txt"

COLUMNAS_USUARIOS = [
    "usuario",
    "nombre_completo",
    "correo_institucional",
    "contrasena",
    "rol",
    "estado",
]

ROLES_VALIDOS = ["Administrador", "Supervisor", "Operador"]
ESTADOS_USUARIO = ["Activo", "Inactivo"]


def normalizar_usuarios(df: pd.DataFrame) -> pd.DataFrame:
    for col in COLUMNAS_USUARIOS:
        if col not in df.columns:
            df[col] = pd.NA

    df = df[COLUMNAS_USUARIOS].copy()

    for col in COLUMNAS_USUARIOS:
        df[col] = df[col].astype("string").str.strip()
        df[col] = df[col].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})

    df["usuario"] = df["usuario"].str.lower()
    df["nombre_completo"] = df["nombre_completo"].fillna("Usuario sin nombre")
    df["correo_institucional"] = df["correo_institucional"].fillna("").str.lower()
    df["contrasena"] = df["contrasena"].fillna("")
    df["rol"] = df["rol"].fillna("Operador")
    df["estado"] = df["estado"].fillna("Inactivo").str.capitalize()

    df = (
        df.dropna(subset=["usuario"])
        .drop_duplicates(subset=["usuario"], keep="first")
        .reset_index(drop=True)
    )
    return df


def cargar_usuarios(ruta: Path = ARCHIVO_USUARIOS) -> pd.DataFrame:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    if not ruta.exists() or ruta.stat().st_size == 0:
        return normalizar_usuarios(pd.DataFrame(columns=COLUMNAS_USUARIOS))

    try:
        df = pd.read_csv(ruta, sep="|", dtype=str, engine="python")
        return normalizar_usuarios(df)
    except Exception as exc:
        print(f"Error al leer '{ruta}': {exc}. Se iniciará vacío.")
        return normalizar_usuarios(pd.DataFrame(columns=COLUMNAS_USUARIOS))


def guardar_usuarios(df: pd.DataFrame, ruta: Path = ARCHIVO_USUARIOS) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df_norm = normalizar_usuarios(df)
    if not df_norm["contrasena"].str.startswith("pbkdf2_sha256$").all():
        raise ValueError("No se permite almacenar contraseñas en texto plano.")
    temporal = ruta.with_suffix(".tmp")
    df_norm.to_csv(temporal, sep="|", index=False, encoding="utf-8")
    temporal.replace(ruta)


def autenticar_usuario(
    df_usuarios: pd.DataFrame, usuario: str, contrasena: str
) -> dict | None:
    if df_usuarios.empty or not usuario.strip() or not contrasena:
        return None

    u_clean = usuario.strip().lower()
    c_clean = contrasena

    coincidencia = df_usuarios[
        ((df_usuarios["usuario"] == u_clean) | (df_usuarios["correo_institucional"] == u_clean))
        & (df_usuarios["estado"].str.capitalize() == "Activo")
    ]

    if coincidencia.empty:
        return None

    if len(coincidencia) != 1:
        return None
    fila = coincidencia.iloc[0]
    if not verificar_hash(c_clean, str(fila["contrasena"])):
        return None
    return {
        "usuario": str(fila["usuario"]),
        "nombre_completo": str(fila["nombre_completo"]),
        "correo_institucional": str(fila["correo_institucional"]),
        "rol": str(fila["rol"]),
        "estado": str(fila["estado"]),
    }


def resumen_usuarios_numpy_pandas(df_usuarios: pd.DataFrame) -> None:
    if df_usuarios.empty:
        print("No hay usuarios registrados.")
        return

    roles = df_usuarios["rol"].to_numpy()
    estados = df_usuarios["estado"].to_numpy()

    print("\n--- RESUMEN DE USUARIOS ---")
    print(f"Total usuarios: {len(df_usuarios)}")
    print(
        f"Activos: {np.sum(estados == 'Activo')} | Inactivos: {np.sum(estados == 'Inactivo')}"
    )

    valores_rol, conteos_rol = np.unique(roles, return_counts=True)
    for r, c in zip(valores_rol, conteos_rol):
        print(f"  - {r}: {c}")

    cruce = pd.crosstab(
        df_usuarios["rol"], df_usuarios["estado"], margins=True, margins_name="Total"
    )
    print("\n" + cruce.to_string())


def crear_usuario(df_usuarios: pd.DataFrame) -> pd.DataFrame:
    print("\n--- CREAR USUARIO ---")
    usuario = input("Nombre de usuario (ej. jdoe_udea): ").strip().lower()
    if not usuario:
        print("El usuario es obligatorio.")
        return df_usuarios

    if (df_usuarios["usuario"] == usuario).any():
        print("Ese nombre de usuario ya existe.")
        return df_usuarios

    nombre = input("Nombre completo: ").strip()
    correo = input("Correo institucional: ").strip().lower()
    contrasena = getpass("Contraseña (mínimo 12 caracteres): ")
    if not validar_nombre(nombre) or not validar_correo(correo) or not correo.lower().endswith("@udea.edu.co") or len(contrasena) < 12 or (df_usuarios["correo_institucional"] == correo.lower()).any():
        print("Datos inválidos o correo duplicado.")
        return df_usuarios
    contrasena = generar_hash(contrasena)

    rol_in = (
        input(f"Rol ({'/'.join(ROLES_VALIDOS)}) [Operador]: ").strip().capitalize()
    )
    rol = rol_in if rol_in in ROLES_VALIDOS else "Operador"

    nuevo = pd.DataFrame(
        [
            {
                "usuario": usuario,
                "nombre_completo": nombre,
                "correo_institucional": correo,
                "contrasena": contrasena,
                "rol": rol,
                "estado": "Activo",
            }
        ]
    )

    df_actualizado = normalizar_usuarios(
        pd.concat([df_usuarios, nuevo], ignore_index=True)
    )
    guardar_usuarios(df_actualizado)
    print(f"Usuario '{usuario}' creado y guardado en data/Usuarios.txt.")
    return df_actualizado


def cambiar_estado_usuario(df_usuarios: pd.DataFrame) -> pd.DataFrame:
    if df_usuarios.empty:
        print("No hay usuarios.")
        return df_usuarios

    usuario = input("\nUsuario a modificar (ej. mvelez_udea): ").strip().lower()
    mask = df_usuarios["usuario"] == usuario
    if not mask.any():
        print("Usuario no encontrado.")
        return df_usuarios

    nuevo_estado = (
        input(f"Nuevo estado ({'/'.join(ESTADOS_USUARIO)}): ").strip().capitalize()
    )
    if nuevo_estado not in ESTADOS_USUARIO:
        print("Estado no válido.")
        return df_usuarios

    df_usuarios.loc[mask, "estado"] = nuevo_estado
    df_actualizado = normalizar_usuarios(df_usuarios)
    guardar_usuarios(df_actualizado)
    print(f"Estado de '{usuario}' actualizado a {nuevo_estado}.")
    return df_actualizado


def generar_hash(clave):
    sal = secrets.token_hex(16)
    resultado = hashlib.pbkdf2_hmac("sha256", clave.encode(), bytes.fromhex(sal), 600000).hex()
    return f"pbkdf2_sha256$600000${sal}${resultado}"

def verificar_hash(clave, almacenado):
    try:
        metodo, iteraciones, sal, esperado = almacenado.split("$")
        if metodo != "pbkdf2_sha256" or iteraciones != "600000":
            return False
        calculado = hashlib.pbkdf2_hmac("sha256", clave.encode(), bytes.fromhex(sal), int(iteraciones)).hex()
        return hmac.compare_digest(calculado, esperado)
    except (ValueError, TypeError):
        return False

class ControlIntentos:
    # Reloj monotónico: no depende de cambios en la hora del computador.
    def __init__(self, segundos=10, reloj=monotonic):
        self.segundos = segundos
        self.reloj = reloj
        self.fallos = 0
        self.hasta = 0

    def restantes(self):
        from math import ceil
        return max(0, ceil(self.hasta - self.reloj()))

    def intentar(self, usuarios, usuario, clave):
        if self.restantes():
            return None, f"Bloqueado. Espere {self.restantes()} segundos."
        resultado = autenticar_usuario(usuarios, usuario, clave)
        if resultado:
            self.fallos = 0
            return resultado, ""
        self.fallos += 1
        if self.fallos >= 3:
            self.hasta = self.reloj() + self.segundos
            self.fallos = 0
            return None, f"Bloqueado durante {self.segundos} segundos."
        return None, f"Credenciales inválidas. Intentos restantes: {3-self.fallos}."
