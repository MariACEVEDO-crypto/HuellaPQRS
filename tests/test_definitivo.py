"""Regresiones nuevas: precisión, demo aislada y usuarios del paquete."""
import sys
import unittest
import tempfile
import hashlib
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import json

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ/'src'))
import archivos as a
import reportes as r
import usuarios as u
import preparar_demostracion as demo
import validaciones as v


class RevisionDefinitiva(unittest.TestCase):
    def test_12_precision_y_redondeo_final(self):
        inicio = datetime(2026, 11, 1, 12)
        corte = inicio + timedelta(days=30)
        def caso(segundos):
            return {'estado_peticion':'Solucionada','fecha_radicacion':inicio.strftime(v.FORMATO_FECHA),
                    'fecha_respuesta':(inicio+timedelta(seconds=segundos)).strftime(v.FORMATO_FECHA)}
        casos = [caso(h*3600) for h in (18,42,90,114)]
        d = r.resumen_dias_respuesta(casos,corte)
        self.assertEqual(d['promedio_fraccionario'],2.75)
        self.assertEqual(d['promedio'],3)
        self.assertEqual(d['validos'],4)
        self.assertEqual(r.resumen_dias_respuesta([caso(1)],corte)['promedio_fraccionario'],1/86400)
        self.assertEqual(r.resumen_dias_respuesta([caso(43200)],corte)['promedio'],0)  # empate al par
        self.assertEqual(r.resumen_dias_respuesta([caso(129600)],corte)['promedio'],2)
        self.assertEqual(r.resumen_dias_respuesta([caso(216000)],corte)['promedio'],2)
        self.assertEqual(r.resumen_dias_respuesta([caso(216001)],corte)['promedio'],3)
        self.assertEqual(r.resumen_dias_respuesta([caso(215999)],corte)['promedio'],2)
        d = r.resumen_dias_respuesta([caso(-1),caso(31*86400),dict(caso(0),fecha_respuesta='')],corte)
        self.assertIsNone(d['promedio']); self.assertIsNone(d['promedio_fraccionario']); self.assertEqual(d['validos'],0)
        x=caso(18*3600)
        self.assertEqual(r.dias_transcurridos(x['fecha_radicacion'],x['fecha_respuesta']),.75)
        self.assertIsNone(r.dias_transcurridos(x['fecha_respuesta'],x['fecha_radicacion']))
        self.assertIsNone(r.dias_transcurridos('',x['fecha_respuesta']))

    def test_13_demo_determinista_sin_sobrescribir(self):
        with tempfile.TemporaryDirectory() as tmp:
            carpeta=Path(tmp)/'demo'
            demo.preparar(carpeta)
            datos=a.obtener_todos_los_registros(carpeta)
            self.assertEqual(len(datos),8)
            self.assertEqual(datos,demo.casos_demostracion())
            self.assertTrue(all(not v.errores_registro(x) for x in datos))
            self.assertEqual(r.calcular_indicadores(datos,demo.CORTE_REFERENCIA)['por_perfil'],dict.fromkeys(v.PERFILES,2))
            d=r.calcular_indicadores(datos,demo.CORTE_REFERENCIA)
            self.assertEqual(d['respuesta']['promedio'],3)
            self.assertEqual(d['respuesta']['promedio_fraccionario'],2.75)
            self.assertEqual(d['por_estado_pct']['Solucionada'],50)
            self.assertEqual(d['vencimientos'],{'Vencida':1,'Próxima a vencer':1,'Dentro del plazo':2,'Fecha inválida':0})
            antes={x.name:x.read_bytes() for x in carpeta.iterdir()}
            with self.assertRaises(FileExistsError): demo.preparar(carpeta)
            self.assertEqual(antes,{x.name:x.read_bytes() for x in carpeta.iterdir()})

    def test_14_integridad_base_y_usuarios_reales_del_paquete(self):
        carpeta=RAIZ/'data'
        evidencias=json.loads((RAIZ/'docs/verificacion_datos.json').read_text(encoding='utf-8'))
        datos=[]
        for tipo in a.TIPOS_VALIDOS:
            ruta=carpeta/f'{tipo}.txt'
            self.assertEqual(hashlib.sha256(ruta.read_bytes()).hexdigest(),evidencias[tipo]['sha256_final'])
            registros=a.cargar_registros(ruta)
            self.assertEqual(len(registros),3000)
            self.assertEqual([int(x['id']) for x in registros],list(range(1,3001)))
            datos.extend(registros)
        self.assertEqual(len(datos),12000)
        self.assertTrue(all(v.validar_telefono_contacto(x['telefono_contacto']) for x in datos))
        self.assertTrue(all(not x['fecha_respuesta'] and not x['perfil_solicitante'] for x in datos))
        d=r.calcular_indicadores(datos)
        self.assertEqual(d['respuesta']['solucionados'],4052)
        self.assertIsNone(d['respuesta']['promedio'])
        usuarios=u.cargar_usuarios(carpeta/'Usuarios.txt')
        self.assertEqual(len(usuarios),12)
        activos=usuarios[usuarios['estado']=='Activo']
        self.assertEqual(activos['usuario'].tolist(),['admin_udea'])
        self.assertTrue(set(x['usuario_registro'] for x in datos).issubset(set(usuarios['usuario'])))
        # Credencial pública de ensayo, no es una contraseña personal.
        clave='Kc8mXsGreveoYXJtlni3hA'
        for alias in ('admin_udea','demo.huellamepega@udea.edu.co'):
            self.assertEqual(u.autenticar_usuario(usuarios,alias,clave)['usuario'],'admin_udea')
        self.assertIsNone(u.autenticar_usuario(usuarios,'admin_udea','incorrecta'))
        for alias in usuarios[usuarios['estado']=='Inactivo']['usuario']:
            self.assertIsNone(u.autenticar_usuario(usuarios,alias,clave))
        self.assertIsNone(u.autenticar_usuario(usuarios,demo.USUARIO_DEMO,demo.CLAVE_DEMO))
        cuentas_demo=u.cargar_usuarios(carpeta/'demostracion'/'Usuarios.txt')
        self.assertEqual(cuentas_demo['usuario'].tolist(),[demo.USUARIO_DEMO])
        self.assertEqual(u.autenticar_usuario(cuentas_demo,demo.CORREO_DEMO,demo.CLAVE_DEMO)['usuario'],demo.USUARIO_DEMO)
        self.assertIsNone(u.autenticar_usuario(cuentas_demo,'admin_udea',clave))

    def test_15_rutas_y_demo_del_paquete(self):
        script='''import json, sys; sys.path.insert(0,sys.argv[1]); import archivos as a, usuarios as u, graficas as g, analizar_pqrs as an, reportes as r; d=r.calcular_indicadores(); print(json.dumps(dict(data=str(a.DATA_DIR),usuarios=str(u.ARCHIVO_USUARIOS.parent),radicados=str(a.RADICADOS_DIR.parent),graficas=str(g.GRAFICAS_DIR.parent),analisis=str(an.DATA_DIR),total=d['total'],promedio=d['respuesta']['promedio'],origen=d['origen'])))'''
        for modo,carpeta in [([],RAIZ/'data'),(['--demo'],RAIZ/'data'/'demostracion')]:
            # Un proceso independiente evita efectos de caché de importación.
            salida=subprocess.check_output([sys.executable,'-c',script,str(RAIZ/'src'),*modo],cwd=tempfile.gettempdir(),text=True)
            d=json.loads(salida)
            for campo in ('data','usuarios','radicados','graficas','analisis'):
                self.assertEqual(Path(d[campo]),carpeta)
            registros = a.obtener_todos_los_registros(carpeta)
            esperado = r.calcular_indicadores(registros)
            self.assertEqual(d['total'], len(registros))
            self.assertEqual(d['promedio'], esperado['respuesta']['promedio'])
            self.assertEqual('AISLADA' in d['origen'],bool(modo))
