"""Indicadores compartidos por la consola, Flet y los gráficos."""
from validaciones import ahora_local
from datetime import datetime, timedelta
from collections import Counter
from math import ceil
from archivos import obtener_todos_los_registros
from validaciones import FORMATO_FECHA
from rutas import ETIQUETA_BASE


def fecha(valor):
    try:
        return datetime.strptime(valor, FORMATO_FECHA)
    except (ValueError, TypeError):
        return None


def dias_transcurridos(inicio, fin):
    """Duración en días incluyendo la fracción; None si las fechas no son válidas."""
    inicio, fin = fecha(inicio), fecha(fin)
    if inicio is None or fin is None or fin < inicio:
        return None
    return (fin - inicio).total_seconds() / 86400


def resumen_dias_respuesta(registros=None, ahora=None):
    registros = obtener_todos_los_registros() if registros is None else registros
    ahora = ahora or ahora_local()
    segundos = []
    solucionados = 0
    for r in registros:
        if r['estado_peticion'] != 'Solucionada':
            continue
        solucionados += 1
        inicio, fin = fecha(r['fecha_radicacion']), fecha(r.get('fecha_respuesta', ''))
        if inicio and fin and inicio <= fin <= ahora:
            segundos.append((fin - inicio).total_seconds())
    # Se divide una sola vez, sin eliminar las horas/minutos/segundos de cada caso.
    promedio_exacto = sum(segundos) / (len(segundos) * 86400) if segundos else None
    return {'promedio': round(promedio_exacto) if promedio_exacto is not None else None,
            'promedio_fraccionario': promedio_exacto, 'validos': len(segundos),
            'solucionados': solucionados, 'sin_fecha_valida': solucionados-len(segundos)}


def conteo(registros, campo):
    return dict(Counter(r.get(campo, '').strip() or 'No disponible' for r in registros))


def porcentajes(conteos, total):
    return {k: round(v*100/total, 2) if total else 0 for k,v in conteos.items()}


def calcular_indicadores(registros=None, ahora=None, dias_umbral=5, origen=None):
    origen = origen or (ETIQUETA_BASE if registros is None else 'CONJUNTO DE DATOS SUMINISTRADO')
    registros = obtener_todos_los_registros() if registros is None else registros
    ahora = ahora or ahora_local()
    respuesta = resumen_dias_respuesta(registros, ahora)
    activos = [r for r in registros if r['estado_peticion'] in ('Registrada','En proceso')]
    grupos = {'Vencida':0, 'Próxima a vencer':0, 'Dentro del plazo':0, 'Fecha inválida':0}
    alertas = []
    for r in activos:
        limite = fecha(r['fecha_maxima_respuesta'])
        if limite is None:
            categoria = 'Fecha inválida'
        elif limite < ahora:
            categoria = 'Vencida'
        elif limite <= ahora + timedelta(days=dias_umbral):
            categoria = 'Próxima a vencer'
        else:
            categoria = 'Dentro del plazo'
        grupos[categoria] += 1
        if categoria in ('Vencida','Próxima a vencer'):
            segundos = (limite-ahora).total_seconds()
            dias = -ceil(-segundos/86400) if segundos < 0 else ceil(segundos/86400)
            alertas.append({'id':r['id'], 'tipo_solicitud':r['tipo_solicitud'], 'estado_peticion':r['estado_peticion'], 'fecha_maxima_respuesta':r['fecha_maxima_respuesta'], 'dias_restantes':dias, 'categoria':categoria})
    alertas.sort(key=lambda r:r['fecha_maxima_respuesta'])
    fechados = [r for r in activos if fecha(r['fecha_radicacion'])]
    minima = min((r['fecha_radicacion'] for r in fechados), default=None)
    antiguas = [r for r in fechados if r['fecha_radicacion']==minima]
    estado = {k:0 for k in ('Registrada','En proceso','Solucionada')}
    estado.update(conteo(registros,'estado_peticion'))
    canal = conteo(registros,'canal_recepcion')
    mascota = conteo(registros,'tipo_mascota')
    return {'total':len(registros),'activos':len(activos),'respuesta':respuesta,
            'por_tipo':conteo(registros,'tipo_solicitud'),'por_documento':conteo(registros,'tipo_documento'),
            'por_mascota':mascota,'por_mascota_pct':porcentajes(mascota,len(registros)),
            'por_canal':canal,'por_canal_pct':porcentajes(canal,len(registros)),
            'por_campus':conteo(registros,'campus_relacionado'),'por_estado':estado,
            'por_estado_pct':porcentajes(estado,len(registros)),'por_usuario':conteo(registros,'usuario_registro'),
            'por_perfil':conteo(registros,'perfil_solicitante'),'vencimientos':grupos,
            'vencimientos_pct':porcentajes(grupos,len(activos)), 'alertas':alertas,'antiguas':antiguas,
            'corte':ahora.strftime(FORMATO_FECHA),'umbral':dias_umbral,'origen':origen}


def lineas_reporte(d):
    r=d['respuesta']
    lineas=[f"1. Promedio días de respuesta: {r['promedio'] if r['promedio'] is not None else 'No disponible'}",
            f"Promedio antes del redondeo: {r['promedio_fraccionario']:.4f} días" if r['promedio_fraccionario'] is not None else 'Promedio antes del redondeo: No disponible',
            'Criterio: redondeo al entero más cercano al final (empate al par).',
            f"Casos válidos: {r['validos']} de {r['solucionados']} solucionadas.",f"Base seleccionada: {d['origen']}",f"Total: {d['total']} | Activas: {d['activos']} | Corte: {d['corte']}"]
    for titulo,clave,pct in [('Mascotas','por_mascota','por_mascota_pct'),('Canales','por_canal','por_canal_pct'),('Campus','por_campus',None),('Estados','por_estado','por_estado_pct'),('Tipos de PQRS','por_tipo',None),('Documentos de identidad','por_documento',None),('Perfiles','por_perfil',None),('Usuarios registradores','por_usuario',None),('Vencimientos (base: activas)','vencimientos','vencimientos_pct')]:
        lineas.append(titulo+':')
        for k,v in d[clave].items():
            lineas.append(f"  {k}: {v}"+(f" ({d[pct][k]}%)" if pct else ''))
    lineas.append(f"Umbral de alerta: {d['umbral']} días; incluye hoy y excluye solucionadas.")
    lineas.append('PQRS activas más antiguas:')
    for r in d['antiguas'][:10]:
        lineas.append(f"  {r['tipo_solicitud']} #{r['id']} | {r['fecha_radicacion']}")
    if not d['antiguas']: lineas.append('  No disponible')
    lineas.append(f"Alertas: {len(d['alertas'])}; primeras 10 (exportación completa en CSV):")
    for r in d['alertas'][:10]:
        lineas.append(f"  {r['tipo_solicitud']} #{r['id']} | {r['categoria']} | {r['fecha_maxima_respuesta']}")
    return lineas


def promedio_dias_respuesta(): return resumen_dias_respuesta()['promedio']
def distribucion_por_mascota(): return calcular_indicadores()['por_mascota']
def proporcion_por_canal(): return calcular_indicadores()['por_canal_pct']
def distribucion_por_campus(): return calcular_indicadores()['por_campus']
def efectividad_por_estado():
    d=calcular_indicadores(); return {'conteo':d['por_estado'],'porcentajes':d['por_estado_pct']}
