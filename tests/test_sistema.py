"""Pruebas reproducibles, sin modificar data/ del proyecto."""
import sys
import unittest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch
import contextlib
import io
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import archivos as a
import validaciones as v
import usuarios as u
import reportes as r
import graficas as g
import analizar_pqrs as analisis
import generar_datos as generador
import main as cli

CLAVE='Prueba!SoloTemporal2026'


def registro(tipo='Peticion', **cambios):
    dato={'nombre_completo':"Ana María O'Neill", 'tipo_documento':'CC','numero_documento':'0012345',
          'tipo_telefono':'Celular','telefono_contacto':'3001234567','correo_electronico':'ana@example.invalid',
          'direccion':'','tipo_solicitud':tipo,'fecha_radicacion':(v.ahora_local()-timedelta(days=10)).strftime(v.FORMATO_FECHA),
          'canal_recepcion':'Presencial','asunto_titulo':'Solicitud de información',
          'descripcion_detallada':'Descripción extensa de la solicitud | incluye separador y\nsegunda línea.',
          'tipo_mascota':'Perro','campus_relacionado':v.CAMPUS_VALIDOS[0],
          'estado_peticion':'Registrada','usuario_registro':'tester','perfil_solicitante':'Estudiante'}
    dato.update(cambios);return dato


class Sistema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_prueba=u.generar_hash(CLAVE)
        cls.df=pd.DataFrame([{'usuario':'tester','nombre_completo':'Usuario Prueba','correo_institucional':'tester@udea.edu.co','contrasena':cls.hash_prueba,'rol':'Administrador','estado':'Activo'}])

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.carpeta=Path(self.tmp.name)
        u.guardar_usuarios(self.df,self.carpeta/'Usuarios.txt')

    def test_01_validaciones_limites(self):
        casos=[(v.validar_nombre,['Ana','Álvaro O\'Neil','A'*100],['','-- ','A1a','A'*101,'A\nB']),
            (v.validar_tipo_documento,['CC','PP','NIT'],['','XX']),
            (v.validar_numero_documento,['001','1'*15],['12','1'*16,'123a','１２３','²²²']),
            (v.validar_tipo_telefono,['Celular','Fijo','Otro'],['','X']),
            (v.validar_telefono_contacto,['3001234567','0000000000'],['','300123456','1'*11,'１'*10,'3'*9+'a']),
            (v.validar_correo,['a@b.co','a.b+z@sub.example.com'],['','a@@b.co','a@-b.co','a@b..co','a..b@c.co','a@b.c','a@b_.co','a'*65+'@b.co']),
            (v.validar_direccion,['','N/A','Calle 5 #2-10','A'*200],['abc','A'*201,'Calle @@@']),
            (v.validar_tipo_solicitud,v.TIPOS_SOLICITUD,['','X']),
            (v.validar_fecha_radicacion,['2020-02-29 12:00:00',v.ahora_local().strftime(v.FORMATO_FECHA)],['','2026-02-30 00:00:00','2999-01-01 00:00:00','2026/01/01']),
            (v.validar_canal_recepcion,v.CANALES_RECEPCION,['','Fax']),
            (v.validar_asunto,['abcde','a'*150],['','abcd','a'*151,'@@abc']),
            (v.validar_descripcion,['a'*20,'a'*2000,'a'*20+'\n|'],['',' '*30,'a'*19,'a'*2001,'a'*20+'\x00']),
            (v.validar_tipo_mascota,v.TIPOS_MASCOTA,['','Ave']),
            (v.validar_campus,v.CAMPUS_VALIDOS,['','X']),
            (v.validar_perfil,v.PERFILES,['','Otro']),
            (v.validar_estado,v.ESTADOS_VALIDOS,['','X'])]
        for fn,validos,invalidos in casos:
            for valor in validos:
                with self.subTest(campo=fn.__name__,valido=True,valor=valor[:30]): self.assertTrue(fn(valor))
            for valor in invalidos:
                with self.subTest(campo=fn.__name__,valido=False,valor=valor[:30]): self.assertFalse(fn(valor))

    def test_02_autenticacion_y_bloqueo(self):
        df=u.cargar_usuarios(self.carpeta/'Usuarios.txt')
        self.assertEqual(u.autenticar_usuario(df,' TESTER ',CLAVE)['usuario'],'tester')
        self.assertEqual(u.autenticar_usuario(df,'TESTER@UDEA.EDU.CO',CLAVE)['usuario'],'tester')
        self.assertIsNone(u.autenticar_usuario(df,'tester',CLAVE+' '))
        self.assertIsNone(u.autenticar_usuario(df,'',''))
        self.assertNotIn(CLAVE,(self.carpeta/'Usuarios.txt').read_text())
        self.assertNotEqual(u.generar_hash(CLAVE),self.hash_prueba)
        inactivo=df.copy();inactivo.loc[0,'estado']='Inactivo'
        self.assertIsNone(u.autenticar_usuario(inactivo,'tester',CLAVE))
        reloj=[100.0];control=u.ControlIntentos(reloj=lambda:reloj[0])
        for _ in range(3): self.assertIsNone(control.intentar(df,'tester','mal')[0])
        self.assertEqual(control.restantes(),10)
        self.assertIsNone(control.intentar(df,'tester',CLAVE)[0])
        reloj[0]+=9.9;self.assertEqual(control.restantes(),1)
        reloj[0]+=.1;self.assertIsNotNone(control.intentar(df,'tester',CLAVE)[0])
        with self.assertRaises(ValueError):
            plano=df.copy();plano.loc[0,'contrasena']='texto plano';u.guardar_usuarios(plano,self.carpeta/'inseguro.txt')

    def test_03_persistencia_ids_cuatro_tipos(self):
        for tipo in a.TIPOS_VALIDOS:
            primero=a.guardar_registro(registro(tipo),self.carpeta)
            segundo=a.guardar_registro(registro(tipo),self.carpeta)
            self.assertEqual((primero['id'],segundo['id']),('1','2'))
            cargados=a.cargar_registros(a.obtener_ruta_archivo(tipo,self.carpeta))
            self.assertEqual(len(cargados),2)
            self.assertEqual(cargados[0]['descripcion_detallada'],primero['descripcion_detallada'])
            self.assertEqual(cargados[0]['numero_documento'],'0012345')
            self.assertEqual(cargados[0]['estado_peticion'],'Registrada')
            self.assertEqual(cargados[0]['fecha_respuesta'],'')
            self.assertEqual(cargados[0]['direccion'],'N/A')
            self.assertEqual((r.fecha(cargados[0]['fecha_maxima_respuesta'])-r.fecha(cargados[0]['fecha_registro'])).days,30)
        self.assertEqual(len(a.consultar_registros('Todas','000001',self.carpeta)),4)
        self.assertEqual(len(a.consultar_registros('Queja','2',self.carpeta)),1)
        self.assertEqual(a.consultar_registros('Todas','99',self.carpeta),[])
        self.assertEqual(a.consultar_registros('Todas','abc',self.carpeta),[])
        with self.assertRaises(ValueError): a.guardar_registro(registro(telefono_contacto='123'),self.carpeta)
        with self.assertRaises(ValueError): a.guardar_registro(registro(usuario_registro='no_autorizado'),self.carpeta)
        self.assertEqual(len(a.obtener_todos_los_registros(self.carpeta)),8)

    def test_04_transiciones_y_fecha(self):
        reg=a.guardar_registro(registro(),self.carpeta)
        self.assertFalse(a.actualizar_registro(dict(reg,estado_peticion='Solucionada'),self.carpeta))
        reg['estado_peticion']='En proceso';self.assertTrue(a.actualizar_registro(reg,self.carpeta))
        self.assertEqual(reg['fecha_respuesta'],'')
        self.assertFalse(a.actualizar_registro(dict(reg,estado_peticion='Registrada'),self.carpeta))
        reg['estado_peticion']='Solucionada';self.assertTrue(a.actualizar_registro(reg,self.carpeta))
        fecha=reg['fecha_respuesta'];self.assertTrue(fecha)
        self.assertFalse(a.actualizar_registro(reg,self.carpeta))
        self.assertFalse(a.actualizar_registro(dict(reg,estado_peticion='En proceso'),self.carpeta))
        persistido=a.consultar_registros('Peticion','1',self.carpeta)[0]
        self.assertEqual(persistido['fecha_respuesta'],fecha)
        self.assertEqual(r.resumen_dias_respuesta([persistido])['promedio'],10)

    def test_05_radicado_ancho_y_contenido(self):
        asunto='X'*150; correo='a'*64+'@'+'b'*63+'.'+'c'*63+'.'+'d'*50+'.com'
        reg=a.guardar_registro(registro(asunto_titulo=asunto,correo_electronico=correo,direccion='D'*200,nombre_completo='Á'*100),self.carpeta)
        texto=a.formatear_radicado_ascii(reg)
        self.assertTrue(all(len(linea)==120 for linea in texto.splitlines()))
        plano=''.join(linea[2:-2].strip() for linea in texto.splitlines())
        for valor in [asunto,correo,'D'*200,'Á'*100]: self.assertIn(valor,plano)
        self.assertNotIn('segunda línea',texto)
        ruta=a.exportar_radicado_txt(reg,self.carpeta/'radicados')
        self.assertEqual(ruta.read_text(encoding='utf-8'),texto+'\n')

    def test_06_indicadores_casos_limite(self):
        corte=datetime(2026,11,24,12)
        def caso(i,estado,inicio,limite,fin='',perfil=''):
            return registro(id=str(i),estado_peticion=estado,fecha_radicacion=inicio,fecha_maxima_respuesta=limite,fecha_respuesta=fin,perfil_solicitante=perfil)
        f='2026-11-01 12:00:00';l='2026-12-01 12:00:00'
        casos=[caso(1,'Solucionada',f,l,'2026-11-11 12:00:00'),caso(2,'Solucionada',f,l,'2026-11-21 12:00:00'),caso(3,'Solucionada',f,l),caso(4,'Solucionada',f,l,'2026-10-01 12:00:00'),caso(5,'Registrada',f,'2026-11-24 11:59:59'),caso(6,'En proceso',f,'2026-11-29 12:00:00',perfil='Docente'),caso(7,'Registrada',f,'2026-11-29 12:00:01'),caso(8,'En proceso',f,'no fecha'),caso(9,'Registrada',f,'2026-11-24 12:00:00')]
        d=r.calcular_indicadores(casos,corte)
        self.assertEqual(d['respuesta'],{'promedio':15,'promedio_fraccionario':15.0,'validos':2,'solucionados':4,'sin_fecha_valida':2})
        self.assertEqual(d['activos'],5);self.assertEqual(d['vencimientos'],{'Vencida':1,'Próxima a vencer':2,'Dentro del plazo':1,'Fecha inválida':1})
        self.assertEqual(d['vencimientos_pct']['Próxima a vencer'],40)
        self.assertEqual(d['por_estado_pct']['Solucionada'],44.44)
        self.assertEqual(d['por_perfil']['No disponible'],8)
        self.assertEqual(len(d['antiguas']),5)
        self.assertIsNone(r.calcular_indicadores([],corte)['respuesta']['promedio'])
        self.assertEqual(r.calcular_indicadores([],corte)['vencimientos_pct']['Vencida'],0)
        self.assertEqual(r.calcular_indicadores([caso(1,'Solucionada',f,l,'2999-01-01 00:00:00')],corte)['respuesta']['validos'],0)

    def test_07_reportes_graficas_y_consolidacion(self):
        for tipo in a.TIPOS_VALIDOS:a.guardar_registro(registro(tipo),self.carpeta)
        df=analisis.cargar_todo_pqrs(self.carpeta);self.assertEqual(len(df),4)
        d=r.calcular_indicadores(df.to_dict('records'))
        with contextlib.redirect_stdout(io.StringIO()): otro=analisis.ejecutar_analisis_completo(self.carpeta)
        self.assertEqual(d['por_tipo'],otro['por_tipo']);self.assertEqual(d['respuesta'],otro['respuesta'])
        for nombre in ['alertas_vencimiento.csv','pqrs_antiguas.csv','resumen_estadistico.txt']:self.assertTrue((self.carpeta/nombre).is_file())
        rutas=g.generar_todas_las_graficas(self.carpeta/'graficas',indicadores=d)
        self.assertEqual(len(rutas),9)
        self.assertTrue(all(p.read_bytes().startswith(b'\x89PNG') for p in rutas))

    def test_08_generador_no_sobrescribe(self):
        ruta=self.carpeta/'sinteticos.txt';generador.generar_archivo_pqrs('Peticion',ruta,100,55)
        antes=ruta.read_bytes()
        with self.assertRaises(FileExistsError):generador.generar_archivo_pqrs('Peticion',ruta,100,55)
        self.assertEqual(ruta.read_bytes(),antes)
        df=pd.read_csv(ruta,sep='|',dtype=str,keep_default_na=False)
        self.assertTrue(df.telefono_contacto.map(v.validar_telefono_contacto).all())
        self.assertEqual(df.columns.tolist(),a.CAMPOS)

    def test_09_consola_flujo_completo(self):
        # Ejecuta funciones reales de la CLI con entradas controladas; los archivos son temporales.
        datos=['tester','1','Ana Maria','CC','123456','Celular','3001234567','a@example.invalid','','Peticion','Presencial','Prueba de solicitud','Descripción de prueba de más de veinte caracteres','Perro','1','Estudiante','','','2','1','1','','3','1','1','S','','3','1','1','S','','4','N','','5','tester','6']
        entradas=iter(datos)
        salida=io.StringIO()
        with contextlib.ExitStack() as st:
            st.enter_context(patch('builtins.input',side_effect=lambda *args:next(entradas)))
            st.enter_context(patch.object(cli,'getpass',return_value=CLAVE))
            st.enter_context(patch.object(cli,'cargar_usuarios',return_value=self.df))
            st.enter_context(patch.object(cli,'guardar_registro',side_effect=lambda reg:a.guardar_registro(reg,self.carpeta)))
            st.enter_context(patch.object(cli,'obtener_ruta_archivo',side_effect=lambda tipo:a.obtener_ruta_archivo(tipo,self.carpeta)))
            st.enter_context(patch.object(cli,'consultar_registros',side_effect=lambda tipo,id:a.consultar_registros(tipo,id,self.carpeta)))
            st.enter_context(patch.object(cli,'actualizar_registro',side_effect=lambda reg:a.actualizar_registro(reg,self.carpeta)))
            st.enter_context(patch.object(cli,'exportar_radicado_txt',side_effect=lambda reg:a.exportar_radicado_txt(reg,self.carpeta/'radicados')))
            st.enter_context(patch.object(cli,'calcular_indicadores',side_effect=lambda:r.calcular_indicadores(a.obtener_todos_los_registros(self.carpeta))))
            st.enter_context(patch.object(cli,'exportar_reportes',side_effect=lambda d:analisis.exportar_reportes(d,self.carpeta)))
            st.enter_context(contextlib.redirect_stdout(salida))
            cli.ejecutar_consola()
        texto=salida.getvalue();self.assertEqual(texto.count('Autenticación exitosa'),2)
        self.assertIn('Registros encontrados: 1',texto);self.assertIn('Fecha real de respuesta:',texto)
        self.assertIn('Promedio días de respuesta: 0',texto);self.assertIsNone(cli.USUARIO_ACTIVO)
        self.assertEqual(a.consultar_registros('Peticion','1',self.carpeta)[0]['estado_peticion'],'Solucionada')

    def test_11_archivos_antiguos_y_corruptos(self):
        reg=a.guardar_registro(registro(),self.carpeta)
        ruta=a.obtener_ruta_archivo('Peticion',self.carpeta)
        df=pd.read_csv(ruta,sep='|',dtype=str,keep_default_na=False)
        antiguo=df.drop(columns=['fecha_registro','fecha_respuesta','perfil_solicitante'])
        antiguo.loc[0,'tipo_mascota']=' perro '
        antiguo.to_csv(ruta,sep='|',index=False)
        leido=a.cargar_registros(ruta)[0]
        self.assertEqual(leido['tipo_mascota'],'Perro')
        self.assertEqual(leido['fecha_respuesta'],'')
        self.assertEqual(leido['perfil_solicitante'],'')
        duplicados=pd.concat([antiguo,antiguo],ignore_index=True)
        duplicados.to_csv(ruta,sep='|',index=False)
        antes=ruta.read_bytes()
        with self.assertRaises(ValueError):a.guardar_registro(registro(),self.carpeta)
        self.assertEqual(ruta.read_bytes(),antes)
        antiguo.drop(columns=['id']).to_csv(ruta,sep='|',index=False)
        antes=ruta.read_bytes()
        with self.assertRaises(ValueError):a.cargar_registros(ruta)
        self.assertEqual(ruta.read_bytes(),antes)

if __name__=='__main__':unittest.main(verbosity=2)
