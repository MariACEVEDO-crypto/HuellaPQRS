"""Prueba de eventos y lógica de Flet sin cliente gráfico. No verifica el SDK real."""
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch
from unittest import TestCase
from contextlib import ExitStack
from tempfile import TemporaryDirectory
import importlib
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import archivos as a
import reportes as r
import usuarios as u
import analizar_pqrs as analisis

class Valores:
    def __getattr__(self,nombre): return nombre
    def all(self,*args): return args

class Control:
    def __init__(self,*args,**kwargs):
        self.args=args;self.value=args[0] if args and isinstance(args[0],str) else ''
        self.controls=args[0] if args and isinstance(args[0],list) else []
        self.content=None;self.label='';self.disabled=False
        self.__dict__.update(kwargs)

class Pagina:
    def __init__(self):self.controls=[]
    def add(self,*controles):self.controls.extend(controles)
    def update(self):pass

class FletSimulado(ModuleType):
    def __getattr__(self,nombre):
        if nombre in ['Icons','Colors','MainAxisAlignment','CrossAxisAlignment','ScrollMode','FontWeight','TextAlign','BoxFit','Border']:return Valores()
        if nombre=='dropdown':return SimpleNamespace(Option=Control)
        if nombre=='Page':return Pagina
        return Control

def buscar(raiz, etiqueta):
    for c in recorrer(raiz):
        if getattr(c,'label',None)==etiqueta or getattr(c,'value',None)==etiqueta:
            return c
        contenido=getattr(c,'content',None)
        if isinstance(contenido,Control) and contenido.value==etiqueta:return c
    raise AssertionError('No se encontró el control '+etiqueta)

def recorrer(raiz):
    for c in getattr(raiz,'controls',[]):
        yield c;yield from recorrer(c)
    contenido=getattr(raiz,'content',None)
    if isinstance(contenido,Control):yield contenido;yield from recorrer(contenido)

class EventosFlet(TestCase):
    def test_flujo_y_bloqueo_simulados(self):
        clave='ClaveSimulada!2026'; reloj=[100.0]
        df=pd.DataFrame([{'usuario':'tester','nombre_completo':'Usuario Prueba','correo_institucional':'tester@udea.edu.co','contrasena':u.generar_hash(clave),'rol':'Administrador','estado':'Activo'}])
        with TemporaryDirectory() as tmp, ExitStack() as st:
            carpeta=Path(tmp);u.guardar_usuarios(df,carpeta/'Usuarios.txt')
            st.enter_context(patch.dict(sys.modules,{'flet':FletSimulado('flet')}))
            app=importlib.import_module('app_flet')
            self.addCleanup(sys.modules.pop,'app_flet',None)
            st.enter_context(patch.object(app,'cargar_usuarios',return_value=df))
            st.enter_context(patch.object(app,'ControlIntentos',side_effect=lambda:u.ControlIntentos(reloj=lambda:reloj[0])))
            st.enter_context(patch.object(app,'guardar_registro',side_effect=lambda reg:a.guardar_registro(reg,carpeta)))
            st.enter_context(patch.object(app,'consultar_registros',side_effect=lambda tipo,id:a.consultar_registros(tipo,id,carpeta)))
            st.enter_context(patch.object(app,'obtener_ruta_archivo',side_effect=lambda tipo:a.obtener_ruta_archivo(tipo,carpeta)))
            st.enter_context(patch.object(app,'actualizar_registro',side_effect=lambda reg:a.actualizar_registro(reg,carpeta)))
            st.enter_context(patch.object(app,'exportar_radicado_txt',side_effect=lambda reg:a.exportar_radicado_txt(reg,carpeta/'radicados')))
            st.enter_context(patch.object(app,'calcular_indicadores',side_effect=lambda:r.calcular_indicadores(a.obtener_todos_los_registros(carpeta))))
            st.enter_context(patch.object(app,'exportar_reportes',side_effect=lambda d:analisis.exportar_reportes(d,carpeta)))
            page=Pagina();app.main(page)
            def login(password):
                buscar(page,'Usuario o correo institucional').value='tester@udea.edu.co'
                buscar(page,'Contraseña').value=password
                buscar(page,'Ingresar').on_click(None)
            for _ in range(3):login('mal')
            self.assertTrue(any('Bloqueado' in str(c.value) for c in recorrer(page)))
            login(clave);self.assertTrue(any('Bloqueado' in str(c.value) for c in recorrer(page)))
            reloj[0]+=10;login(clave)
            buscar(page,'1. Registrar PQRS').on_click(None)
            datos={'Nombre completo del solicitante':'Ana Maria','Número de documento':'00123','Teléfono de contacto (10 dígitos)':'3001234567','Correo electrónico':'a@example.invalid','Asunto o título (5-150 caracteres)':'Prueba de solicitud','Descripción detallada (20-2000 caracteres)':'Descripción de prueba válida y suficientemente larga.','Perfil del solicitante':'Estudiante'}
            for campo,valor in datos.items():buscar(page,campo).value=valor
            buscar(page,'Guardar y generar radicado TXT').on_click(None)
            self.assertEqual(len(a.consultar_registros('Peticion','1',carpeta)),1)
            buscar(page,'Volver al menú').on_click(None)
            buscar(page,'2. Consultar PQRS').on_click(None)
            buscar(page,'ID (opcional)').value='000001';buscar(page,'Buscar').on_click(None)
            self.assertTrue(any('Registros encontrados: 1' in str(c.value) for c in recorrer(page)))
            buscar(page,'Volver al menú').on_click(None)
            buscar(page,'3. Cambiar Estado').on_click(None)
            for _ in range(2):
                buscar(page,'ID del radicado').value='1';buscar(page,'Buscar radicado').on_click(None)
                buscar(page,'Confirmar cambio de estado').on_click(None)
            self.assertEqual(a.consultar_registros('Peticion','1',carpeta)[0]['estado_peticion'],'Solucionada')
            buscar(page,'Volver al menú').on_click(None)
            buscar(page,'4. Estadísticas y Gráficas').on_click(None)
            self.assertTrue(any('Promedio días de respuesta: 0' in str(c.value) for c in recorrer(page)))
            buscar(page,'Volver al menú').on_click(None)
            buscar(page,'Cerrar sesión').on_click(None)
            self.assertEqual(buscar(page,'Contraseña').value,'')
