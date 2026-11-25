from validaciones import ahora_local
from datetime import datetime, timedelta
import os
from pathlib import Path
import sys
import time

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from archivos import (
    actualizar_registro,
    cargar_registros,
    exportar_radicado_txt,
    formatear_radicado_ascii,
    guardar_registro,
    obtener_ruta_archivo,
    obtener_todos_los_registros,
)
from graficas import generar_todas_las_graficas
from reportes import calcular_indicadores, lineas_reporte, dias_transcurridos
from rutas import ETIQUETA_BASE
from analizar_pqrs import exportar_reportes
from archivos import consultar_registros
from validaciones import PERFILES, validar_perfil
from getpass import getpass
from usuarios import ARCHIVO_USUARIOS, ControlIntentos, cargar_usuarios
from validaciones import (
    CAMPUS_VALIDOS,
    validar_asunto,
    validar_canal_recepcion,
    validar_correo,
    validar_descripcion,
    validar_direccion,
    validar_fecha_radicacion,
    validar_nombre,
    validar_numero_documento,
    validar_telefono_contacto,
    validar_tipo_documento,
    validar_tipo_mascota,
    validar_tipo_solicitud,
    validar_tipo_telefono,
    validar_transicion_estado,
) 


USUARIO_ACTIVO = None
PLAZO_MAXIMO_DIAS = 30


def limpiar_pantalla():
    if sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")


def mostrar_logo():
    logo = r"""
    ==========================================================================================================
                                    .::----::::::::----::.
                                .:--:..                ..:--:.
                             .:-:.     ..  .:    -:  :.     .:-:.
                           .--.      :=.  :=:.-::: : -.:=:     .--.
                         .:-.   -:   :=::.            .::..==:   .-:.
                        :=.   ::  :---.      .......  .    .. .:   .=:
                       :=.  :=-=.::.      ::-:::::.:-:--.     ---:  .=:
                       =:  :..:--.       .-:=--:..:--::--     .-...  :=
                      --  ...:=.         .-:-..:::::--:-.       .=:   --
                      =.   ::::-.         .-..:::. --:.:-.       -::  .=
                      --  :::::           .=..:::: :--:.-.        -:  --
                      =:  .:+..           .:..::.-:::::::        =-=  :=
                      =.  :::::          :=-.-++.::.=+. ..       ::.  .=
                      =:               ..:=+::=-:#*:#*:*#-            :=
                      --   :--         :+=:.-==::+=:==-===:      .=:  --
                      =.    -=:        .:-:-+*#*=--#%%#:+#-     .-=   .=
                       --   .--:          =++**+++-*#%%*.      .-=.  --
                        =:    :=:     .-:..--:. .. .:-=:.:-.  .::.  :=
                         =:    :==.    .:---.... .....:--:.  .-=-  :=
                          --    ..:=:      ..::-.::::..    :-:-.  --
                           :-.     .=-=-.              .:---:   .-:
                             --.     .:--- =-:.::.: ::-----.  .--
                               .--:       ...::-::- .:..   .:--.
                                  :--:    :-:  ....... :-:--:
                                     .:::--::::::::--:::.

                             SISTEMA DE GESTIÓN PQRS - HUELLAMEPEGA
                           Movimiento Estudiantil Perritos y Gaticos
                                   Universidad de Antioquia
    ==========================================================================================================
    """
    print(logo)
    print(ETIQUETA_BASE)


def login():
    global USUARIO_ACTIVO
    USUARIO_ACTIVO = None
    control = ControlIntentos()
    while True:
        while control.restantes():
            print(f"Bloqueado. Espere {control.restantes()} segundos.", flush=True)
            time.sleep(1)
        limpiar_pantalla()
        mostrar_logo()
        usuario = input("Usuario o correo institucional (0 para salir): ").strip()
        if usuario == "0": return False
        clave = getpass("Contraseña: ")
        datos, mensaje = control.intentar(cargar_usuarios(), usuario, clave)
        if datos:
            USUARIO_ACTIVO = datos['usuario']
            print("Autenticación exitosa.")
            return True
        print(mensaje)


def imprimir_radicado_ascii(reg: dict):
    print(formatear_radicado_ascii(reg))


def registrar_pqrs():
    if not USUARIO_ACTIVO:
        print("\n[ERROR] No hay un usuario autenticado en la sesión.")
        time.sleep(1.5)
        return

    limpiar_pantalla()
    print("==========================================================================================================")
    print("                                      MÓDULO 1: REGISTRAR PQRS                                           ")
    print("==========================================================================================================")

    while True:
        nombre = input("Ingrese Nombre Completo del solicitante: ").strip()
        if validar_nombre(nombre):
            nombre = nombre.strip()
            break
        print("[ERROR] Nombre inválido (3-100 caracteres, solo letras, espacios, tildes, ' o -).")

    while True:
        print("Tipos de Doc: CC, TI, CE, PP, NIT")
        tipo_doc = input("Ingrese Tipo de Documento: ").strip().upper()
        if validar_tipo_documento(tipo_doc):
            break
        print("[ERROR] Tipo de documento no permitido.")

    while True:
        num_doc = input("Ingrese Número de Documento: ").strip()
        if validar_numero_documento(num_doc):
            break
        print("[ERROR] Número de documento inválido (3-15 dígitos numéricos).")

    while True:
        print("Tipos de Teléfono: Celular, Fijo, Corporativo, Otro")
        tipo_tel = input("Ingrese Tipo de Teléfono: ").strip().capitalize()
        if validar_tipo_telefono(tipo_tel):
            break
        print("[ERROR] Tipo de teléfono inválido.")

    while True:
        tel = input("Ingrese Teléfono de Contacto (10 dígitos): ").strip()
        if validar_telefono_contacto(tel):
            break
        print("[ERROR] Teléfono debe contener exactamente 10 dígitos.")

    while True:
        correo = input("Ingrese Correo Electrónico: ").strip()
        if validar_correo(correo):
            break
        print("[ERROR] Formato de correo electrónico inválido.")

    while True:
        direccion = input("Ingrese Dirección (Opcional, Enter para omitir): ").strip()
        if not direccion:
            direccion = "N/A"
            break
        if validar_direccion(direccion):
            break
        print("[ERROR] Dirección debe tener entre 5 y 200 caracteres.")

    while True:
        print("Tipos de Solicitud: Peticion, Queja, Reclamo, Sugerencia")
        tipo_sol = input("Ingrese Tipo de Solicitud: ").strip().capitalize().replace("ó", "o")
        if validar_tipo_solicitud(tipo_sol):
            break
        print("[ERROR] Tipo de solicitud no válido.")

    while True:
        print("Canales: Presencial, Correo electrónico, Página web, Teléfono, Redes sociales, Otro")
        canal = input("Ingrese Canal de Recepción: ").strip()
        if validar_canal_recepcion(canal):
            break
        print("[ERROR] Canal de recepción no válido.")

    while True:
        asunto = input("Ingrese Asunto o Título (5-150 caracteres): ").strip()
        if validar_asunto(asunto):
            asunto = asunto.strip()
            break
        print("[ERROR] Asunto inválido (5-150 caracteres).")

    while True:
        desc = input("Ingrese Descripción detallada (20-2000 caracteres): ").strip()
        if validar_descripcion(desc):
            desc = desc.strip()
            break
        print("[ERROR] Descripción debe contener entre 20 y 2000 caracteres.")

    while True:
        print("Mascota: Perro, Gato, Otro")
        mascota = input("Ingrese Tipo de Mascota: ").strip().capitalize()
        if validar_tipo_mascota(mascota):
            break
        print("[ERROR] Mascota no válida.")

    while True:
        print("\nSeleccione el Campus Relacionado:")
        for idx, c in enumerate(CAMPUS_VALIDOS, 1):
            print(f"{idx}. {c}")
        opc = input("Opción (1-9): ").strip()
        if len(opc) <= 2 and opc.isascii() and opc.isdigit() and 1 <= int(opc) <= len(CAMPUS_VALIDOS):
            campus = CAMPUS_VALIDOS[int(opc) - 1]
            break
        print("[ERROR] Selección de campus inválida.")

    while True:
        perfil = input("Perfil (Estudiante, Docente, Administrativo, Ciudadano): ").strip().capitalize()
        if validar_perfil(perfil): break
        print("Perfil inválido.")
    ahora = ahora_local()
    while True:
        fecha_rad = input("Fecha radicación AAAA-MM-DD HH:MM:SS (Enter = ahora): ").strip() or ahora_local().strftime("%Y-%m-%d %H:%M:%S")
        if validar_fecha_radicacion(fecha_rad): break
        print("Fecha inválida o futura.")

    fecha_max = (ahora + timedelta(days=PLAZO_MAXIMO_DIAS)).strftime("%Y-%m-%d %H:%M:%S")

    registro = {
        "id": "0",
        "nombre_completo": nombre,
        "tipo_documento": tipo_doc,
        "numero_documento": num_doc,
        "tipo_telefono": tipo_tel,
        "telefono_contacto": tel,
        "correo_electronico": correo,
        "direccion": direccion,
        "tipo_solicitud": tipo_sol,
        "fecha_radicacion": fecha_rad,
        "canal_recepcion": canal,
        "asunto_titulo": asunto,
        "descripcion_detallada": desc,
        "tipo_mascota": mascota,
        "campus_relacionado": campus,
        "fecha_maxima_respuesta": fecha_max,
        "estado_peticion": "Registrada",
        "usuario_registro": USUARIO_ACTIVO,
        "perfil_solicitante": perfil,
    }

    guardar_registro(registro)
    ruta_txt = exportar_radicado_txt(registro)

    print("\n[ÉXITO] PQRS Registrada correctamente.")
    print(f"[ARCHIVO TXT] Comprobante exportado en: {ruta_txt}\n")
    imprimir_radicado_ascii(registro)
    input("\nPresione Enter para regresar al menú principal...")


def consultar_pqrs():
    limpiar_pantalla()
    print("==========================================================================================================")
    print("                                      MÓDULO 2: CONSULTAR PQRS                                           ")
    print("==========================================================================================================")
    print("Seleccione Tipo de Solicitud a consultar:")
    print("1. Peticion")
    print("2. Queja")
    print("3. Reclamo")
    print("4. Sugerencia")
    print("5. Consultar Todas")
    opc = input("Opción: ").strip()

    mapa = {"1": "Peticion", "2": "Queja", "3": "Reclamo", "4": "Sugerencia"}
    if opc in mapa:
        ruta = obtener_ruta_archivo(mapa[opc])
        registros = cargar_registros(ruta)
    elif opc == "5":
        registros = obtener_todos_los_registros()
    else:
        print("[ERROR] Opción no válida.")
        time.sleep(1)
        return

    criterio = input("ID (Enter para listar los primeros 20): ").strip()
    if criterio:
        registros = consultar_registros(mapa.get(opc,"Todas"), criterio)
    print(f"Registros encontrados: {len(registros)}")
    for r in registros[:20]:
        imprimir_radicado_ascii(r)
    if len(registros)>20: print("Se muestran 20. Consulte por tipo e ID para ver otro registro.")
    input("Presione Enter para continuar...")


def registrar_cambio_pqrs():
    limpiar_pantalla()
    print("==========================================================================================================")
    print("                                   MÓDULO 3: REGISTRAR CAMBIO EN PQRS                                    ")
    print("==========================================================================================================")
    print("Seleccione Tipo de Solicitud:")
    print("1. Peticion | 2. Queja | 3. Reclamo | 4. Sugerencia")
    opc = input("Opción: ").strip()
    mapa = {"1": "Peticion", "2": "Queja", "3": "Reclamo", "4": "Sugerencia"}
    if opc not in mapa:
        print("[ERROR] Opción inválida.")
        time.sleep(1)
        return

    tipo_sol = mapa[opc]
    ruta = obtener_ruta_archivo(tipo_sol)
    registros = cargar_registros(ruta)

    id_buscar = input("Ingrese el ID del radicado a modificar: ").strip()
    coincidencias = consultar_registros(tipo_sol, id_buscar) if id_buscar else []
    encontrado = coincidencias[0] if coincidencias else None

    if not encontrado:
        print("\n[ERROR] No se encontró ningún registro con ese ID en " + tipo_sol)
        time.sleep(1.5)
        return

    print("\nRegistro encontrado actual:")
    print(f"ID: {encontrado['id']} | Estado Actual: {encontrado['estado_peticion']}")
    print("Flujo permitido de cambio: Registrada -> En proceso -> Solucionada")

    estado_act = encontrado["estado_peticion"]
    if estado_act == "Registrada":
        siguiente = "En proceso"
    elif estado_act == "En proceso":
        siguiente = "Solucionada"
    else:
        print("\n[AVISO] El registro ya se encuentra en estado SOLUCIONADA y no puede cambiar.")
        input("\nPresione Enter para volver...")
        return

    if not validar_transicion_estado(estado_act, siguiente):
        print("\n[ERROR] Transición de estado no permitida.")
        time.sleep(1.5)
        return

    print(f"Siguiente estado permitido: {siguiente}")
    confirmar = input(f"¿Desea cambiar el estado a '{siguiente}'? (S/N): ").strip().upper()
    if confirmar == "S":
        encontrado["estado_peticion"] = siguiente
        if actualizar_registro(encontrado):
            exportar_radicado_txt(encontrado)
            print("\n[ÉXITO] Estado actualizado correctamente y comprobante TXT refrescado.")
            if encontrado.get("fecha_respuesta"):
                print("Fecha real de respuesta:", encontrado["fecha_respuesta"])
                duracion = dias_transcurridos(encontrado['fecha_radicacion'], encontrado['fecha_respuesta'])
                print("Días transcurridos:", f"{duracion:.4f}" if duracion is not None else "No disponible")
        else:
            print("\n[ERROR] No se pudo actualizar el estado.")
    else:
        print("\nCambio cancelado.")

    input("\nPresione Enter para continuar...")


def mostrar_estadisticas():
    limpiar_pantalla()
    print("MÓDULO 4: ESTADÍSTICAS Y KPIS")
    d = calcular_indicadores()
    print("\n".join(lineas_reporte(d)))
    exportar_reportes(d)
    if input("¿Generar gráficas PNG? (S/N): ").strip().upper() == "S":
        for ruta in generar_todas_las_graficas(indicadores=d): print(ruta)
    input("Presione Enter para continuar...")


def menu_principal():
    while True:
        limpiar_pantalla()
        mostrar_logo()
        print(f"Usuario activo: {USUARIO_ACTIVO}")
        print("----------------------------------------------------------------------------------------------------------")
        print("1. Registrar PQRS")
        print("2. Consultar PQRS")
        print("3. Registrar Cambio en PQRS")
        print("4. Estadísticas")
        print("5. Cerrar sesión")
        print("6. Salir")
        print("----------------------------------------------------------------------------------------------------------")
        opc = input("Ingrese una opción (1-6): ").strip()

        try:
            if opc == "1":
                registrar_pqrs()
            elif opc == "2":
                consultar_pqrs()
            elif opc == "3":
                registrar_cambio_pqrs()
            elif opc == "4":
                mostrar_estadisticas()
            elif opc == "5":
                return True
            elif opc == "6":
                print("\n¡Gracias por utilizar el Gestor PQRS HuellaMepega! Hasta luego.")
                return False
            else:
                print("\n[ERROR] Opción no válida.")
                time.sleep(1)
        except (OSError, ValueError) as error:
            print(f"[ERROR] {error}")
            input("Presione Enter para volver al menú...")


def ejecutar_consola() -> None:
    """Ejecuta el flujo clásico en consola cuando se pasa --consola."""
    global USUARIO_ACTIVO
    try:
        while login():
            continuar = menu_principal()
            USUARIO_ACTIVO = None
            if not continuar: break
    except (EOFError, KeyboardInterrupt):
        print("\nSesión finalizada.")
    finally:
        USUARIO_ACTIVO = None


def main() -> None:
    if "--consola" in sys.argv:
        ejecutar_consola()
    else:
        try:
            from app_flet import iniciar_app
        except ModuleNotFoundError as error:
            if error.name != "flet": raise
            print("Flet no está instalado. Ejecute: python -m pip install -r requirements.txt")
            raise SystemExit(1)
        iniciar_app()


if __name__ == "__main__":
    main()