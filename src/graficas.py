from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from archivos import DATA_DIR
from reportes import calcular_indicadores

GRAFICAS_DIR=DATA_DIR/'graficas'


def generar_todas_las_graficas(carpeta_salida=GRAFICAS_DIR, mostrar=False, indicadores=None):
    d=indicadores if indicadores is not None else calcular_indicadores()
    carpeta_salida=Path(carpeta_salida); carpeta_salida.mkdir(parents=True,exist_ok=True)
    rutas=[]
    for nombre,clave,titulo,unidad in [
        ('mascota','por_mascota','Solicitudes por mascota','Cantidad'),
        ('canal','por_canal_pct','Proporción por canal','Porcentaje (%)'),
        ('campus','por_campus','Solicitudes por campus','Cantidad'),
        ('estado','por_estado_pct','Distribución por estado','Porcentaje (%)'),
        ('tipo','por_tipo','Tipos de PQRS','Cantidad'),
        ('documento','por_documento','Documentos de identidad','Cantidad'),
        ('perfil','por_perfil','Perfil del solicitante','Cantidad'),
        ('usuario','por_usuario','Carga operativa por usuario','Cantidad'),
        ('vencimiento','vencimientos_pct','Plazos de PQRS activas','Porcentaje (%)')]:
        datos=d[clave]
        fig,ax=plt.subplots(figsize=(10, max(4,0.4*len(datos)+2)))
        ax.barh(list(datos),list(datos.values()),color='#21867a')
        ax.set_title(titulo); ax.set_xlabel(unidad)
        ax.grid(axis='x',alpha=.2)
        if not datos or clave=='por_perfil' and set(datos)=={'No disponible'}:
            ax.set_title(titulo+' — sin datos de perfil' if clave=='por_perfil' else titulo+' — sin registros')
        fig.text(.01,.01,d['origen']+' / corte: '+d['corte'],fontsize=8)
        fig.tight_layout(rect=(0,.04,1,1))
        ruta=carpeta_salida/f'pqrs_por_{nombre}.png'; fig.savefig(ruta,dpi=150); plt.close(fig); rutas.append(ruta)
    return rutas

if __name__=='__main__':
    for ruta in generar_todas_las_graficas(): print(ruta)
