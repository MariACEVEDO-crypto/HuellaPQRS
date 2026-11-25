from pathlib import Path
import pandas as pd
from archivos import CAMPOS, DATA_DIR, obtener_todos_los_registros
from reportes import calcular_indicadores, lineas_reporte
from rutas import etiqueta_carpeta


def cargar_todo_pqrs(carpeta=DATA_DIR):
    df = pd.DataFrame(obtener_todos_los_registros(carpeta), columns=CAMPOS)
    for col in ['fecha_radicacion','fecha_maxima_respuesta','fecha_respuesta']:
        df[col+'_dt'] = pd.to_datetime(df[col], errors='coerce', format='%Y-%m-%d %H:%M:%S')
    return df


def exportar_reportes(d, carpeta=DATA_DIR):
    carpeta=Path(carpeta); carpeta.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(d['alertas'], columns=['id','tipo_solicitud','estado_peticion','fecha_maxima_respuesta','dias_restantes','categoria']).to_csv(carpeta/'alertas_vencimiento.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame([{k:r[k] for k in ['id','tipo_solicitud','fecha_radicacion','estado_peticion']} for r in d['antiguas']], columns=['id','tipo_solicitud','fecha_radicacion','estado_peticion']).to_csv(carpeta/'pqrs_antiguas.csv',index=False,encoding='utf-8-sig')
    (carpeta/'resumen_estadistico.txt').write_text('\n'.join(lineas_reporte(d))+'\n', encoding='utf-8')


def ejecutar_analisis_completo(carpeta=DATA_DIR):
    df=cargar_todo_pqrs(carpeta)
    d=calcular_indicadores(df.to_dict('records'), origen=etiqueta_carpeta(carpeta))
    exportar_reportes(d,carpeta)
    print('\n'.join(lineas_reporte(d)))
    return d

if __name__=='__main__': ejecutar_analisis_completo()
