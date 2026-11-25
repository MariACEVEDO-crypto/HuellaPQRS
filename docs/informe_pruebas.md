# Informe de pruebas — HuellaMepega

## 1. Información general

| Concepto | Información |
|---|---|
| Proyecto | HuellaMepega — Gestor de PQRS |
     Universidad de Antioquia 
| Asignatura | Algoritmia y Programación |
| Semestre | 2026-2 |
| Fecha de verificación final | 25 de noviembre de 2026 |

## 2. Objetivo

Verificar el funcionamiento, la integridad de los datos, la consistencia de los indicadores estadísticos y el cumplimiento de los requisitos técnicos del sistema HuellaMepega.

Las pruebas permiten identificar errores, comprobar las correcciones realizadas y verificar las principales funcionalidades mediante casos automatizados y comprobaciones manuales.

## 3. Entorno de pruebas

Las comprobaciones finales se realizaron en el siguiente entorno:

| Componente | Característica |
|---|---|
| Sistema operativo | Windows |
| Lenguaje | Python 3.12 |
| Entorno de desarrollo | Visual Studio Code |
| Interfaz gráfica | Flet 0.80.5 |
| Procesamiento de datos | Pandas y NumPy |
| Visualización | Matplotlib |
| Pruebas automatizadas | Unittest |
| Almacenamiento | Archivos planos TXT |
| Datos de prueba | Registros sintéticos |

Previamente, también se realizaron pruebas de consola y procesamiento de datos en Linux con Python 3.13.

## 4. Metodología

La verificación del sistema comprende cuatro componentes:

1. Pruebas automatizadas de las funciones del programa.
2. Pruebas funcionales en la interfaz gráfica.
3. Pruebas funcionales mediante consola.
4. Comprobaciones de integridad y consistencia de los datos.

Las pruebas automatizadas de las operaciones de negocio utilizan archivos temporales para evitar modificaciones sobre la base histórica.

Las comprobaciones manuales que requieren registrar solicitudes o modificar estados se realizan mediante una base sintética de demostración independiente.

## 5. Pruebas automatizadas

Para ejecutar la suite de pruebas, se utiliza el siguiente comando desde la carpeta principal del proyecto:

```bash
python -m unittest discover -s tests -v
```

### 5.1. Casos de prueba

| ID | Funcionalidad evaluada | Resultado |
|---|---|---|
| P01 | Validaciones de campos, formatos, longitudes y casos límite. | Superada |
| P02 | Autenticación, usuarios activos, protección de contraseñas y bloqueo temporal. | Superada |
| P03 | Persistencia de registros e identificadores independientes por tipo de PQRS. | Superada |
| P04 | Transiciones de estado y registro automático de la fecha de respuesta. | Superada |
| P05 | Generación del radicado, contenido y ancho de 120 caracteres por línea. | Superada |
| P06 | Indicadores estadísticos, vencimientos, fechas inválidas y bases vacías. | Superada |
| P07 | Consolidación de datos, exportación de reportes y generación de gráficas. | Superada |
| P08 | Generación de datos sintéticos sin sobrescribir archivos existentes. | Superada |
| P09 | Flujo completo de las funcionalidades de consola. | Superada |
| P10 | Simulación automatizada de los eventos de la interfaz Flet. | Superada |
| P11 | Compatibilidad con archivos históricos y detección de estructuras incorrectas. | Superada |
| P12 | Precisión del promedio de respuesta y redondeo final. | Superada |
| P13 | Generación reproducible de la base de demostración y protección contra sobrescritura. | Superada |
| P14 | Integridad de la base histórica y verificación de usuarios autorizados. | Superada |
| P15 | Selección de rutas y separación entre la base histórica y la base de demostración. | Superada |

### 5.2. Resultado final

La ejecución final del 25 de noviembre de 2026 presentó los siguientes resultados:

| Indicador | Resultado |
|---|---:|
| Pruebas ejecutadas | 15 |
| Pruebas superadas | 15 |
| Pruebas fallidas | 0 |
| Errores de ejecución | 0 |
| Porcentaje de pruebas superadas | 100 % |
| Tiempo de ejecución | 19,893 segundos |

Salida final de la terminal:

```text
Ran 15 tests in 19.893s

OK
```

El porcentaje indicado corresponde a las pruebas ejecutadas y no representa una medición de cobertura total del código fuente.

## 6. Pruebas funcionales de la interfaz gráfica

La aplicación gráfica se ejecutó mediante:

```bash
python src/main.py
```

También se verificó el modo de demostración independiente mediante:

```bash
python src/main.py --demo
```

| ID | Operación | Resultado observado |
|---|---|---|
| GUI-01 | Apertura de la aplicación gráfica. | Satisfactorio |
| GUI-02 | Visualización del logo y formulario de autenticación. | Satisfactorio |
| GUI-03 | Inicio de sesión en la base histórica. | Satisfactorio |
| GUI-04 | Consulta de una PQRS por tipo e identificador. | Satisfactorio |
| GUI-05 | Visualización de las estadísticas históricas. | Satisfactorio |
| GUI-06 | Generación de nueve archivos gráficos PNG. | Satisfactorio |
| GUI-07 | Inicio de sesión en la base de demostración. | Satisfactorio |
| GUI-08 | Registro de una nueva petición. | Satisfactorio |
| GUI-09 | Generación automática del identificador y comprobante. | Satisfactorio |
| GUI-10 | Transición de Registrada a En proceso. | Satisfactorio |
| GUI-11 | Transición de En proceso a Solucionada. | Satisfactorio |
| GUI-12 | Registro automático de la fecha real de respuesta. | Satisfactorio |
| GUI-13 | Actualización de los indicadores estadísticos. | Satisfactorio |
| GUI-14 | Activación del bloqueo después de tres intentos fallidos. | Satisfactorio |
| GUI-15 | Cierre de sesión. | Satisfactorio |
| GUI-16 | Corrección de los saltos de línea del radicado consultado. | Satisfactorio |

Las comprobaciones manuales se realizaron mediante la interfaz gráfica real, complementando las pruebas automatizadas de eventos simulados.

## 7. Pruebas funcionales de consola

La versión de consola se ejecutó mediante:

```bash
python src/main.py --consola --demo
```

Se comprobó el acceso del usuario de demostración, la visualización del menú principal, la consulta de indicadores estadísticos y la salida del programa.

Adicionalmente, la suite automatizada verifica el flujo completo de registro, consulta, actualización de solicitudes y cierre de sesión mediante las funciones de consola.

Los resultados estadísticos obtenidos en la consola coincidieron con los presentados por la interfaz gráfica.

## 8. Verificación de la base histórica

La base histórica contiene 12.000 registros sintéticos distribuidos en cuatro archivos independientes.

| Tipo de solicitud | Cantidad |
|---|---:|
| Petición | 3.000 |
| Queja | 3.000 |
| Reclamo | 3.000 |
| Sugerencia | 3.000 |
| **Total** | **12.000** |

Las comprobaciones de integridad verifican:

- Conservación de los registros históricos.
- Identificadores consecutivos e independientes.
- Ausencia de identificadores duplicados dentro de cada categoría.
- Corrección de los 3.718 números telefónicos sintéticos que incumplían la longitud requerida.
- Conservación de los campos originales restantes.
- Ausencia de fechas históricas de respuesta y perfiles inventados.

Los resultados de integridad y las referencias SHA-256 se encuentran en el archivo [verificacion_datos.json](verificacion_datos.json).

## 9. Resultados estadísticos de la base histórica

Durante la ejecución del 25 de noviembre de 2026 se obtuvieron los siguientes indicadores:

| Estado | Cantidad | Porcentaje |
|---|---:|---:|
| Registrada | 4.019 | 33,49 % |
| En proceso | 3.929 | 32,74 % |
| Solucionada | 4.052 | 33,77 % |
| **Total** | **12.000** | **100 %** |

Las solicitudes activas corresponden a 7.948 registros.

El promedio histórico de días de respuesta se presenta como No disponible, debido a que los registros solucionados originales no contienen fechas reales de respuesta.

Esta condición corresponde a una limitación de la información histórica y no a un error de cálculo.

## 10. Prueba de registro y actualización de una PQRS

Se utilizó la base de demostración para registrar una petición adicional con datos ficticios.

| Campo | Resultado |
|---|---|
| Tipo de solicitud | Petición |
| Identificador generado | 000003 |
| Estado inicial | Registrada |
| Fecha de radicación | 25/11/2026 14:46:44 |
| Fecha máxima de respuesta | 25/12/2026 14:46:44 |
| Perfil del solicitante | Estudiante |
| Usuario registrador | demo_operador |

Posteriormente, la solicitud pasó al estado En proceso y finalmente al estado Solucionada.

El sistema registró automáticamente la fecha real de respuesta:

```text
2026-11-25 14:52:02
```

El tiempo transcurrido fue de 5 minutos y 18 segundos, equivalente aproximadamente a 0,0037 días.

Esta prueba permitió verificar el registro de fechas, la persistencia del estado y la actualización automática de los indicadores.

## 11. Resultados de la base de demostración

La base de demostración contiene inicialmente ocho registros sintéticos. Durante las comprobaciones se agregó y solucionó una solicitud adicional.

Los resultados obtenidos fueron:

| Indicador | Resultado |
|---|---:|
| Total de PQRS | 9 |
| Solicitudes registradas | 2 |
| Solicitudes en proceso | 2 |
| Solicitudes solucionadas | 5 |
| Solicitudes activas | 4 |
| Porcentaje de resolución | 55,56 % |
| Promedio de respuesta antes del redondeo | 2,2007 días |
| Promedio de respuesta redondeado | 2 días |
| Casos válidos para el promedio | 5 de 5 |
| Solicitudes vencidas | 1 |
| Solicitudes próximas a vencer | 1 |
| Solicitudes dentro del plazo | 2 |

### Distribución por perfil

| Perfil | Cantidad |
|---|---:|
| Estudiante | 3 |
| Docente | 2 |
| Administrativo | 2 |
| Ciudadano | 2 |
| **Total** | **9** |

Los resultados corresponden exclusivamente a casos sintéticos y no representan solicitudes veterinarias reales.

## 12. Verificación del radicado TXT

Se comprobó el archivo:

```text
data/demostracion/radicados/radicado_Peticion_000003.txt
```

Para verificar la longitud de sus líneas se utilizó el siguiente comando en PowerShell:

```powershell
Get-Content ".\data\demostracion\radicados\radicado_Peticion_000003.txt" -Encoding UTF8 | ForEach-Object { $_.Length } | Group-Object | Select-Object Name,Count
```

Resultado obtenido:

```text
Name Count
---- -----
120     25
```

El comprobante evaluado contiene 25 líneas de exactamente 120 caracteres cada una.

La comprobación confirma el cumplimiento del requisito de ancho para este radicado. Las pruebas automatizadas complementan esta verificación mediante casos con campos de diferentes longitudes.

## 13. Verificación de gráficas

La interfaz gráfica reportó la generación satisfactoria de los siguientes nueve archivos:

| Archivo | Indicador |
|---|---|
| pqrs_por_mascota.png | Distribución por mascotas |
| pqrs_por_canal.png | Canales de recepción |
| pqrs_por_campus.png | Distribución por campus |
| pqrs_por_estado.png | Estados de las solicitudes |
| pqrs_por_tipo.png | Tipos de PQRS |
| pqrs_por_documento.png | Documentos de identidad |
| pqrs_por_perfil.png | Perfiles de solicitantes |
| pqrs_por_usuario.png | Solicitudes registradas por usuario |
| pqrs_por_vencimiento.png | Clasificación de vencimientos |

Los archivos se almacenan en la carpeta de gráficas correspondiente a la base seleccionada.

La generación de archivos fue comprobada. La revisión visual individual de todas las gráficas constituye una comprobación complementaria.

## 14. Correcciones y pruebas de regresión

Durante las comprobaciones finales se realizaron los siguientes ajustes:

| Situación identificada | Corrección aplicada |
|---|---|
| División automática de las líneas del radicado en Flet. | Incorporación de texto sin ajuste automático de línea y desplazamiento horizontal. |
| Error de indentación durante la modificación del código. | Corrección de la sangría y comprobación mediante py_compile. |
| Archivo de verificación requerido por una prueba fuera de su ubicación original. | Restauración de verificacion_datos.json en docs. |
| Prueba de rutas que esperaba ocho registros de demostración. | Actualización para comprobar la base seleccionada sin depender de una cantidad fija de registros de ensayo. |

La prueba independiente que verifica la generación reproducible de los ocho casos iniciales se conserva.

Después de realizar las modificaciones se ejecutaron nuevamente las 15 pruebas automatizadas, obteniendo un resultado satisfactorio.

## 15. Limitaciones de las pruebas

- No se realizó una auditoría de seguridad para entornos de producción.
- No se realizaron pruebas de escritura concurrente desde múltiples procesos.
- No se verificó integralmente la compatibilidad con macOS.
- Las pruebas no representan una garantía absoluta de ausencia de errores.
- Los datos históricos desconocidos limitan algunos indicadores estadísticos.
- La visibilidad de los bordes laterales del radicado puede depender del ancho disponible en la interfaz gráfica.
- Se comprobó la activación del bloqueo temporal en Flet; queda como comprobación complementaria verificar explícitamente el desbloqueo posterior.
- No se ha realizado una verificación de la versión final publicada en GitHub.

## 16. Conclusiones

Las 15 pruebas automatizadas finalizaron satisfactoriamente, sin fallos ni errores de ejecución.

Las comprobaciones funcionales realizadas en Windows permitieron verificar las principales operaciones de la interfaz gráfica y de la consola.

Se comprobó la consistencia de los indicadores estadísticos, el registro de fechas reales de respuesta, la separación de las bases de datos y el cumplimiento del ancho exigido para el radicado evaluado.

Los resultados respaldan el funcionamiento de las funcionalidades principales del sistema dentro del alcance académico y de los escenarios de prueba ejecutados.

## 17. Documentación complementaria

- [Documentación técnica](documentacion_tecnica.md)
- [Manual de usuario](manual_de_usuario.md)
- [Verificación de datos](verificacion_datos.json)
- [README del proyecto](../README.md)

---

**HuellaMepega — Algoritmia y Programación — Universidad de Antioquia, 2026-2.**