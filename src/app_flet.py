from validaciones import ahora_local
from datetime import datetime, timedelta
from pathlib import Path
import sys
import flet as ft

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
from validaciones import PERFILES
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

PLAZO_MAXIMO_DIAS = 30
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


def _obtener_ruta_usuarios() -> Path:
    # Nunca recurrir a otra base si falta el archivo seleccionado.
    return Path(ARCHIVO_USUARIOS)


def _extraer_usuario_login(resultado_auth, usuario_ingresado: str) -> str:
    if isinstance(resultado_auth, dict):
        return str(
            resultado_auth.get("usuario")
            or resultado_auth.get("nombre_completo")
            or usuario_ingresado
        )
    if resultado_auth is not None and not isinstance(resultado_auth, bool):
        for attr in ("usuario", "nombre_completo", "nombre"):
            valor = getattr(resultado_auth, attr, None)
            if valor:
                return str(valor)
    return usuario_ingresado


def _extraer_nombre_visible(resultado_auth, usuario_ingresado: str) -> str:
    if isinstance(resultado_auth, dict):
        return str(
            resultado_auth.get("nombre_completo")
            or resultado_auth.get("nombre")
            or resultado_auth.get("usuario")
            or usuario_ingresado
        )
    if resultado_auth is not None and not isinstance(resultado_auth, bool):
        for attr in ("nombre_completo", "nombre", "usuario"):
            valor = getattr(resultado_auth, attr, None)
            if valor:
                return str(valor)
    return usuario_ingresado


def main(page: ft.Page):
    page.title = "HuellaMepega PQRS — " + ETIQUETA_BASE
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    usuario_activo = {"codigo": "", "nombre": ""}
    df_usuarios = cargar_usuarios(_obtener_ruta_usuarios())
    control = ControlIntentos()

    titulo = ft.Text(
        "HuellaMepega PQRS",
        size=26,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER,
    )
    subtitulo = ft.Text(
        "Inicia sesión para gestionar solicitudes — " + ETIQUETA_BASE,
        size=13,
        color=ft.Colors.GREY_600,
        text_align=ft.TextAlign.CENTER,
    )

    carpeta_logo = BASE_DIR.parent / "images"
    archivos_logo = []
    if carpeta_logo.exists():
        for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
            archivos_logo.extend(sorted(carpeta_logo.glob(ext)))

    if archivos_logo:
        logo_widget = ft.Image(
            src=archivos_logo[0].name,
            width=140,
            height=140,
            fit=ft.BoxFit.CONTAIN,
            border_radius=70,
        )
    else:
        logo_widget = ft.Icon(ft.Icons.PETS, size=44, color=ft.Colors.TEAL_700)

    campo_usuario = ft.TextField(
        label="Usuario o correo institucional",
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        autofocus=True,
        border_radius=10,
    )

    campo_clave = ft.TextField(
        label="Contraseña",
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True,
        can_reveal_password=True,
        border_radius=10,
    )

    mensaje_estado = ft.Text(
        "",
        size=13,
        color=ft.Colors.RED_700,
        text_align=ft.TextAlign.CENTER,
    )

    def _cabecera_modulo(titulo_modulo: str, on_volver):
        return ft.Row(
            [
                ft.Text(titulo_modulo, size=20, weight=ft.FontWeight.BOLD),
                ft.OutlinedButton(
                    "Volver al menú",
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda _: on_volver(),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    # -------------------------------------------------------------------------
    # MÓDULO 1: REGISTRAR PQRS
    # -------------------------------------------------------------------------
    def mostrar_registrar_pqrs():
        page.controls.clear()

        nombre_inp = ft.TextField(label="Nombre completo del solicitante", border_radius=10)
        tipo_doc_dd = ft.Dropdown(
            label="Tipo de documento",
            options=[ft.DropdownOption(key=x, text=x) for x in TIPOS_DOCUMENTO],
            value="CC",
            border_radius=10,
        )
        num_doc_inp = ft.TextField(label="Número de documento", border_radius=10)
        tipo_tel_dd = ft.Dropdown(
            label="Tipo de teléfono",
            options=[ft.DropdownOption(key=x, text=x) for x in TIPOS_TELEFONO],
            value="Celular",
            border_radius=10,
        )
        tel_inp = ft.TextField(label="Teléfono de contacto (10 dígitos)", border_radius=10)
        correo_inp = ft.TextField(label="Correo electrónico", border_radius=10)
        dir_inp = ft.TextField(label="Dirección (opcional, vacío = N/A)", border_radius=10)
        tipo_sol_dd = ft.Dropdown(
            label="Tipo de solicitud",
            options=[ft.DropdownOption(key=x, text=x) for x in TIPOS_SOLICITUD],
            value="Peticion",
            border_radius=10,
        )
        canal_dd = ft.Dropdown(
            label="Canal de recepción",
            options=[ft.DropdownOption(key=x, text=x) for x in CANALES_RECEPCION],
            value="Presencial",
            border_radius=10,
        )
        asunto_inp = ft.TextField(label="Asunto o título (5-150 caracteres)", border_radius=10)
        desc_inp = ft.TextField(
            label="Descripción detallada (20-2000 caracteres)",
            multiline=True,
            min_lines=3,
            max_lines=5,
            border_radius=10,
        )
        mascota_dd = ft.Dropdown(
            label="Tipo de mascota",
            options=[ft.DropdownOption(key=x, text=x) for x in TIPOS_MASCOTA],
            value="Perro",
            border_radius=10,
        )
        campus_dd = ft.Dropdown(
            label="Campus relacionado",
            options=[ft.DropdownOption(key=x, text=x) for x in CAMPUS_VALIDOS],
            value=CAMPUS_VALIDOS[0] if CAMPUS_VALIDOS else None,
            border_radius=10,
        )

        fecha_inp = ft.TextField(label="Fecha radicación AAAA-MM-DD HH:MM:SS (vacío = ahora)", border_radius=10)
        perfil_dd = ft.Dropdown(label="Perfil del solicitante", options=[ft.DropdownOption(key=x, text=x) for x in PERFILES], border_radius=10)
        feedback = ft.Text("", size=13, color=ft.Colors.RED_700)
        radicado_box = ft.Text(
            "",
            size=12,
            selectable=True,
            font_family="Consolas",
            no_wrap=True,
        )

        def guardar_pqrs_click(e):
            if not usuario_activo["codigo"]: return
            nombre = (nombre_inp.value or "").strip()
            tipo_doc = (tipo_doc_dd.value or "").strip().upper()
            num_doc = (num_doc_inp.value or "").strip()
            tipo_tel = (tipo_tel_dd.value or "").strip()
            tel = (tel_inp.value or "").strip()
            correo = (correo_inp.value or "").strip()
            direccion_raw = (dir_inp.value or "").strip()
            direccion = direccion_raw if direccion_raw else "N/A"
            tipo_sol = (tipo_sol_dd.value or "").strip()
            canal = (canal_dd.value or "").strip()
            asunto = (asunto_inp.value or "").strip()
            desc = (desc_inp.value or "").strip()
            mascota = (mascota_dd.value or "").strip()
            campus = (campus_dd.value or "").strip()

            if not validar_nombre(nombre):
                feedback.value = "Nombre inválido (3-100 caracteres, solo letras y caracteres permitidos)."
                feedback.color = ft.Colors.RED_700
                page.update()
                return
            if not validar_tipo_documento(tipo_doc):
                feedback.value = "Tipo de documento no permitido."
                feedback.color = ft.Colors.RED_700
                page.update()
                return
            if not validar_numero_documento(num_doc):
                feedback.value = "Número de documento inválido (3-15 dígitos numéricos)."
                feedback.color = ft.Colors.RED_700
                page.update()
                return
            if not validar_tipo_telefono(tipo_tel):
                feedback.value = "Tipo de teléfono inválido."
                feedback.color = ft.Colors.RED_700
                page.update()
                return
            if not validar_telefono_contacto(tel):
                feedback.value = "Teléfono de contacto debe contener exactamente 10 dígitos."
                feedback.color = ft.Colors.RED_700
                page.update()
                return
            if not validar_correo(correo):
                feedback.value = "Formato de correo electrónico inválido."
                feedback.color = ft.Colors.RED_700
                page.update()
                return
            if direccion != "N/A" and not validar_direccion(direccion):
                feedback.value = "Dirección debe tener entre 5 y 200 caracteres."
                feedback.color = ft.Colors.RED_700
                page.update()
                return
            if not validar_tipo_solicitud(tipo_sol):
                feedback.value = "Tipo de solicitud no válido."
                feedback.color = ft.Colors.RED_700
                page.update()
                return
            if not validar_canal_recepcion(canal):
                feedback.value = "Canal de recepción no válido."
                feedback.color = ft.Colors.RED_700
                page.update()
                return
            if not validar_asunto(asunto):
                feedback.value = "Asunto inválido (5-150 caracteres)."
                feedback.color = ft.Colors.RED_700
                page.update()
                return
            if not validar_descripcion(desc):
                feedback.value = "Descripción debe tener entre 20 y 2000 caracteres."
                feedback.color = ft.Colors.RED_700
                page.update()
                return
            if not validar_tipo_mascota(mascota):
                feedback.value = "Tipo de mascota no válido."
                feedback.color = ft.Colors.RED_700
                page.update()
                return
            if campus not in CAMPUS_VALIDOS:
                feedback.value = "Selección de campus inválida."
                feedback.color = ft.Colors.RED_700
                page.update()
                return

            ahora = ahora_local()
            fecha_rad = (fecha_inp.value or "").strip() or ahora.strftime("%Y-%m-%d %H:%M:%S")
            if not validar_fecha_radicacion(fecha_rad):
                feedback.value = "La fecha de radicación no puede ser futura."
                feedback.color = ft.Colors.RED_700
                page.update()
                return

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
                "usuario_registro": usuario_activo["codigo"],
                "perfil_solicitante": perfil_dd.value or "",
            }

            try:
                guardar_registro(registro)
                ruta_txt = exportar_radicado_txt(registro)
                radicado_box.value = formatear_radicado_ascii(registro)
                feedback.value = f"PQRS registrada. Comprobante TXT: {ruta_txt}"
                feedback.color = ft.Colors.GREEN_700

                fecha_inp.value = ""
                perfil_dd.value = None
                nombre_inp.value = ""
                num_doc_inp.value = ""
                tel_inp.value = ""
                correo_inp.value = ""
                dir_inp.value = ""
                asunto_inp.value = ""
                desc_inp.value = ""
            except Exception as err:
                feedback.value = f"Error al guardar PQRS: {err}"
                feedback.color = ft.Colors.RED_700

            page.update()

        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        _cabecera_modulo("1. Registrar PQRS", lambda: mostrar_menu_principal(usuario_activo["nombre"])),
                        ft.Divider(),
                        nombre_inp,
                        perfil_dd,
                        fecha_inp,
                        ft.Row([tipo_doc_dd, num_doc_inp], expand=True),
                        ft.Row([tipo_tel_dd, tel_inp], expand=True),
                        correo_inp,
                        dir_inp,
                        ft.Row([tipo_sol_dd, canal_dd], expand=True),
                        asunto_inp,
                        desc_inp,
                        ft.Row([mascota_dd, campus_dd], expand=True),
                        feedback,
                        ft.Button(
                            "Guardar y generar radicado TXT",
                            icon=ft.Icons.SAVE,
                            width=float("inf"),
                            height=44,
                            on_click=guardar_pqrs_click,
                        ),
                        ft.Row([radicado_box], scroll=ft.ScrollMode.AUTO),
                    ],
                    spacing=10,
                ),
                width=680,
                padding=20,
                border_radius=16,
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            )
        )
        page.update()

    # -------------------------------------------------------------------------
    # MÓDULO 2: CONSULTAR PQRS
    # -------------------------------------------------------------------------
    def mostrar_consultar_pqrs():
        page.controls.clear()

        filtro_dd = ft.Dropdown(
            label="Filtrar por tipo de solicitud",
            options=[ft.DropdownOption(key=x, text=x) for x in ["Todas"] + TIPOS_SOLICITUD],
            value="Todas",
            width=260,
            border_radius=10,
        )
        id_filtro = ft.TextField(label="ID (opcional)", width=150)
        resumen_txt = ft.Text("", size=13, weight=ft.FontWeight.BOLD)
        lista_registros = ft.Column(spacing=10)

        def buscar_click(e=None):
            seleccion = filtro_dd.value or "Todas"
            try:
                registros = consultar_registros(seleccion, (id_filtro.value or "").strip())
            except Exception as err:
                resumen_txt.value = f"Error al consultar registros: {err}"
                resumen_txt.color = ft.Colors.RED_700
                lista_registros.controls.clear()
                page.update()
                return

            lista_registros.controls.clear()
            if not registros:
                resumen_txt.value = "No se encontraron registros en el sistema."
                resumen_txt.color = ft.Colors.GREY_700
            else:
                resumen_txt.value = f"Registros encontrados: {len(registros)} (máximo 20 visibles; filtre por ID)"
                resumen_txt.color = ft.Colors.TEAL_700
                for reg in registros[:20]:
                    lista_registros.controls.append(
                        ft.Container(
                                                      content=ft.Row(
                              controls=[
                                  ft.Text(
                                      formatear_radicado_ascii(reg),
                                      size=11,
                                      selectable=True,
                                      font_family="Consolas",
                                      no_wrap=True,
                                  ),
                              ],
                              scroll=ft.ScrollMode.AUTO,
                          ),
                            padding=12,
                            border_radius=10,
                            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                        )
                    )
            page.update()

        filtro_dd.on_select = buscar_click
        id_filtro.on_submit = buscar_click

        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        _cabecera_modulo("2. Consultar PQRS", lambda: mostrar_menu_principal(usuario_activo["nombre"])),
                        ft.Divider(),
                        ft.Row(
                            [
                                filtro_dd,
                                id_filtro,
                                ft.Button("Buscar", icon=ft.Icons.SEARCH, on_click=buscar_click),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        resumen_txt,
                        lista_registros,
                    ],
                    spacing=12,
                ),
                width=740,
                padding=20,
                border_radius=16,
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            )
        )
        buscar_click()

    # -------------------------------------------------------------------------
    # MÓDULO 3: CAMBIAR ESTADO
    # -------------------------------------------------------------------------
    def mostrar_cambiar_estado():
        page.controls.clear()

        tipo_dd = ft.Dropdown(
            label="Tipo de solicitud",
            options=[ft.DropdownOption(key=x, text=x) for x in TIPOS_SOLICITUD],
            value="Peticion",
            border_radius=10,
        )
        id_inp = ft.TextField(label="ID del radicado", border_radius=10)
        info_txt = ft.Text("", size=13)
        siguiente_estado_holder = {"valor": None, "registro": None}

        btn_actualizar = ft.Button(
            "Confirmar cambio de estado",
            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
            disabled=True,
            on_click=lambda e: confirmar_cambio(),
        )

        def buscar_radicado(e):
            siguiente_estado_holder["valor"] = None
            siguiente_estado_holder["registro"] = None
            btn_actualizar.disabled = True

            tipo_sol = (tipo_dd.value or "").strip()
            id_buscar = (id_inp.value or "").strip()
            if not id_buscar.isascii() or not id_buscar.isdigit():
                info_txt.value = "Ingresa el ID del radicado."
                info_txt.color = ft.Colors.RED_700
                page.update()
                return

            try:
                coincidencias = consultar_registros(tipo_sol, id_buscar)
            except (OSError, ValueError) as err:
                info_txt.value = f"Error al consultar: {err}"
                info_txt.color = ft.Colors.RED_700
                page.update()
                return
            encontrado = coincidencias[0] if coincidencias else None

            if not encontrado:
                info_txt.value = f"No se encontró el radicado ID {id_buscar} en {tipo_sol}."
                info_txt.color = ft.Colors.RED_700
                page.update()
                return

            estado_act = encontrado.get("estado_peticion", "")
            if estado_act == "Registrada":
                siguiente = "En proceso"
            elif estado_act == "En proceso":
                siguiente = "Solucionada"
            else:
                info_txt.value = (
                    f"ID {encontrado['id']} | Solicitante: {encontrado.get('nombre_completo', '')} | "
                    f"Estado actual: {estado_act}. Ya está solucionada y no puede cambiar."
                )
                info_txt.color = ft.Colors.AMBER_800
                page.update()
                return

            if not validar_transicion_estado(estado_act, siguiente):
                info_txt.value = f"Transición no permitida: {estado_act} -> {siguiente}."
                info_txt.color = ft.Colors.RED_700
                page.update()
                return

            siguiente_estado_holder["valor"] = siguiente
            siguiente_estado_holder["registro"] = encontrado
            btn_actualizar.disabled = False
            info_txt.value = (
                f"ID {encontrado['id']} | Solicitante: {encontrado.get('nombre_completo', '')} | "
                f"Estado actual: {estado_act} -> Siguiente permitido: {siguiente}"
            )
            info_txt.color = ft.Colors.BLUE_700
            page.update()

        def confirmar_cambio():
            if not usuario_activo["codigo"]: return
            reg = siguiente_estado_holder["registro"]
            nuevo_estado = siguiente_estado_holder["valor"]
            if not reg or not nuevo_estado:
                return

            try:
                reg["estado_peticion"] = nuevo_estado
                if not actualizar_registro(reg):
                    raise ValueError("No se pudo actualizar el estado.")
                exportar_radicado_txt(reg)
                btn_actualizar.disabled = True
                siguiente_estado_holder["valor"] = None
                siguiente_estado_holder["registro"] = None
                info_txt.value = f"Estado actualizado a '{nuevo_estado}' y comprobante TXT refrescado."
                if reg.get("fecha_respuesta"):
                    duracion = dias_transcurridos(reg['fecha_radicacion'], reg['fecha_respuesta'])
                    dias_texto = f"{duracion:.4f}" if duracion is not None else "No disponible"
                    info_txt.value += f" Fecha real: {reg['fecha_respuesta']} | Días: {dias_texto}"
                info_txt.color = ft.Colors.GREEN_700
            except Exception as err:
                info_txt.value = f"Error al actualizar estado: {err}"
                info_txt.color = ft.Colors.RED_700

            page.update()

        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        _cabecera_modulo("3. Cambiar Estado de PQRS", lambda: mostrar_menu_principal(usuario_activo["nombre"])),
                        ft.Divider(),
                        ft.Text("Flujo permitido: Registrada -> En proceso -> Solucionada", size=12, color=ft.Colors.GREY_700),
                        tipo_dd,
                        id_inp,
                        ft.Row(
                            [
                                ft.Button("Buscar radicado", icon=ft.Icons.SEARCH, on_click=buscar_radicado),
                                btn_actualizar,
                            ],
                            spacing=10,
                        ),
                        info_txt,
                    ],
                    spacing=12,
                ),
                width=640,
                padding=20,
                border_radius=16,
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            )
        )
        page.update()

    # -------------------------------------------------------------------------
    # MÓDULO 4: ESTADÍSTICAS Y GRÁFICAS
    # -------------------------------------------------------------------------
    def mostrar_estadisticas():
        page.controls.clear()

        d = calcular_indicadores()
        exportar_reportes(d)
        estado_graficas = ft.Text("", size=13)
        lista_archivos_graficas = ft.Column(spacing=4)

        def generar_graficas_click(e):
            lista_archivos_graficas.controls.clear()
            try:
                archivos = generar_todas_las_graficas(mostrar=False, indicadores=d)
                estado_graficas.value = f"Gráficas generadas ({len(archivos)} archivos):"
                estado_graficas.color = ft.Colors.GREEN_700
                for ruta in archivos:
                    lista_archivos_graficas.controls.append(ft.Text(f"• {ruta}", size=12, selectable=True))
            except Exception as err:
                estado_graficas.value = f"Error al generar gráficas: {err}"
                estado_graficas.color = ft.Colors.RED_700
            page.update()

        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        _cabecera_modulo("4. Estadísticas y Gráficas", lambda: mostrar_menu_principal(usuario_activo["nombre"])),
                        ft.Divider(),
                        *[ft.Text(linea, size=13, selectable=True) for linea in lineas_reporte(d)],
                        ft.Divider(),
                        ft.Button(
                            "Generar todas las gráficas (PNG)",
                            icon=ft.Icons.IMAGE,
                            on_click=generar_graficas_click,
                        ),
                        estado_graficas,
                        lista_archivos_graficas,
                    ],
                    spacing=8,
                ),
                width=700,
                padding=20,
                border_radius=16,
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            )
        )
        page.update()

    # -------------------------------------------------------------------------
    # MENÚ PRINCIPAL Y LOGIN
    # -------------------------------------------------------------------------
    def mostrar_menu_principal(usuario_actual: str):
        page.controls.clear()
        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            f"Bienvenido, {usuario_actual}",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "Selecciona una opción — " + ETIQUETA_BASE,
                            size=13,
                            color=ft.Colors.GREY_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Button(
                            "1. Registrar PQRS",
                            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                            width=300,
                            height=42,
                            on_click=lambda _: mostrar_registrar_pqrs(),
                        ),
                        ft.Button(
                            "2. Consultar PQRS",
                            icon=ft.Icons.SEARCH,
                            width=300,
                            height=42,
                            on_click=lambda _: mostrar_consultar_pqrs(),
                        ),
                        ft.Button(
                            "3. Cambiar Estado",
                            icon=ft.Icons.SYNC_ALT,
                            width=300,
                            height=42,
                            on_click=lambda _: mostrar_cambiar_estado(),
                        ),
                        ft.Button(
                            "4. Estadísticas y Gráficas",
                            icon=ft.Icons.BAR_CHART,
                            width=300,
                            height=42,
                            on_click=lambda _: mostrar_estadisticas(),
                        ),
                        ft.TextButton(
                            "Cerrar sesión",
                            icon=ft.Icons.LOGOUT,
                            on_click=lambda _: mostrar_login(),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                ),
                width=440,
                padding=24,
                border_radius=16,
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            )
        )
        page.update()

    def al_iniciar_sesion(e):
        nonlocal df_usuarios

        usuario = (campo_usuario.value or "").strip()
        clave = campo_clave.value or ""

        df_usuarios = cargar_usuarios(_obtener_ruta_usuarios())
        datos_usuario, mensaje = control.intentar(df_usuarios, usuario, clave)
        campo_clave.value = ""
        if not datos_usuario:
            mensaje_estado.value = mensaje
            mensaje_estado.color = ft.Colors.RED_700
            page.update()
            return

        mensaje_estado.value = ""
        usuario_activo["codigo"] = _extraer_usuario_login(datos_usuario, usuario)
        usuario_activo["nombre"] = _extraer_nombre_visible(datos_usuario, usuario)
        mostrar_menu_principal(usuario_activo["nombre"])

    campo_clave.on_submit = al_iniciar_sesion

    boton_ingresar = ft.Button(
        content=ft.Text("Ingresar", size=15),
        icon=ft.Icons.LOGIN,
        width=float("inf"),
        height=45,
        on_click=al_iniciar_sesion,
    )

    tarjeta_login = ft.Container(
        content=ft.Column(
            [
                logo_widget,
                titulo,
                subtitulo,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                campo_usuario,
                campo_clave,
                mensaje_estado,
                boton_ingresar,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        ),
        width=420,
        padding=24,
        border_radius=16,
        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
    )

    def mostrar_login():
        usuario_activo["codigo"] = ""
        usuario_activo["nombre"] = ""
        page.controls.clear()
        campo_usuario.value = ""
        campo_clave.value = ""
        mensaje_estado.value = ""
        page.add(tarjeta_login)
        page.update()

    mostrar_login()


def iniciar_app() -> None:
    ft.run(main, assets_dir=str(BASE_DIR.parent / "images"))


if __name__ == "__main__":
    iniciar_app()