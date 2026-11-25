# Manual de usuario — HuellaMepega

## 1. Información general

- **Proyecto:** HuellaMepega — Gestor de PQRS.
- Universidad de Antioquia.
- **Asignatura:** Algoritmia y Programación.
- **Semestre:** 2026-2.

## 2. Introducción

HuellaMepega es una aplicación académica desarrollada en Python para gestionar peticiones, quejas, reclamos y sugerencias relacionadas con la atención y el bienestar de las mascotas.

El sistema permite registrar solicitudes, consultar información, actualizar estados, generar comprobantes de radicación y obtener indicadores estadísticos.

Dispone de dos modalidades de ejecución:

- Interfaz gráfica desarrollada con Flet.
- Interfaz de línea de comandos (CLI).

Ambas modalidades utilizan los mismos módulos de procesamiento, validación y almacenamiento.

## 3. Requisitos del sistema

Para ejecutar HuellaMepega se requiere:

- Python 3.12 o 3.13.
- Visual Studio Code o una terminal de comandos.
- Bibliotecas especificadas en requirements.txt.
- Acceso de lectura y escritura a las carpetas del proyecto.

La interfaz gráfica y la consola fueron comprobadas en Windows con Python 3.12.

No se requiere un servidor externo ni un sistema gestor de bases de datos.

## 4. Instalación

1. Extraer completamente el archivo comprimido del proyecto.
2. Abrir Visual Studio Code.
3. Seleccionar Archivo → Abrir carpeta.
4. Seleccionar la carpeta HuellaMepega.
5. Abrir una nueva terminal.
6. Instalar las dependencias mediante el siguiente comando:

```bash
python -m pip install -r requirements.txt
```

Se recomienda utilizar un entorno virtual independiente para evitar conflictos con las bibliotecas de otros proyectos.

## 5. Estructura del proyecto

| Carpeta o archivo | Contenido |
|---|---|
| src/ | Código fuente del sistema. |
| data/ | Archivos de PQRS, usuarios, reportes y gráficas. |
| data/demostracion/ | Base sintética independiente para pruebas. |
| docs/ | Manual de usuario, documentación técnica e informe de pruebas. |
| images/ | Logo e identidad visual. |
| tests/ | Pruebas automatizadas. |
| README.md | Información general e instrucciones de ejecución. |
| requirements.txt | Dependencias necesarias. |
| LICENSE | Licencia del proyecto. |
| .gitignore | Exclusión de archivos temporales. |

No es necesario modificar las rutas del código ni editar directamente los archivos de almacenamiento.

## 6. Ejecución del programa

### 6.1. Interfaz gráfica

Ejecutar desde la carpeta principal:

```bash
python src/main.py
```

Se abrirá la ventana de HuellaMepega con el formulario de inicio de sesión.

### 6.2. Interfaz de consola

Ejecutar:

```bash
python src/main.py --consola
```

El programa mostrará el formulario de autenticación directamente en la terminal.

### 6.3. Modo de demostración

Para realizar pruebas sin modificar los 12.000 registros históricos, utilizar alguno de los siguientes comandos.

Interfaz gráfica:

```bash
python src/main.py --demo
```

Interfaz de consola:

```bash
python src/main.py --consola --demo
```

El sistema identificará este modo mediante el mensaje DEMOSTRACIÓN SINTÉTICA AISLADA.

## 7. Inicio de sesión

### 7.1. Base histórica sintética

Las credenciales de acceso académico se encuentran en el archivo README.md.

El usuario de esta base es:

`admin_udea`

También se permite utilizar el alias de correo institucional simulado correspondiente.

### 7.2. Base de demostración

El usuario de demostración es:

`demo_operador`

La contraseña pública de ensayo y el alias correspondiente se encuentran en README.md.

Las credenciales de la base histórica no permiten acceder a la base de demostración y viceversa.

### 7.3. Procedimiento de autenticación

1. Ingresar el nombre de usuario o correo institucional simulado.
2. Ingresar la contraseña.
3. Presionar Ingresar o Enter, según la interfaz.
4. Esperar la validación de las credenciales.

Si las credenciales son correctas y el usuario está activo, se mostrará el menú principal.

### 7.4. Bloqueo temporal

Después de tres intentos fallidos, el sistema activa un bloqueo temporal de diez segundos.

Durante este periodo no se admiten nuevos intentos válidos de autenticación en la instancia bloqueada.

Una vez finalizado el bloqueo, el usuario puede intentar ingresar nuevamente.

Las contraseñas se almacenan mediante mecanismos de hash y no como texto plano dentro del archivo de usuarios.

Las cuentas disponibles tienen fines exclusivamente académicos.

## 8. Menú principal

El sistema cuenta con los siguientes módulos:

| Opción | Funcionalidad |
|---|---|
| 1 | Registrar PQRS. |
| 2 | Consultar PQRS. |
| 3 | Cambiar estado de una PQRS. |
| 4 | Estadísticas y gráficas. |
| 5 | Cerrar sesión en consola. |
| 6 | Salir del programa en consola. |

En la interfaz gráfica, el cierre de sesión se realiza mediante el botón correspondiente. Para finalizar el programa se puede cerrar la ventana.

## 9. Registrar una PQRS

### 9.1. Procedimiento

1. Iniciar sesión.
2. Seleccionar Registrar PQRS.
3. Completar los datos del solicitante.
4. Seleccionar las características de la solicitud.
5. Escribir el asunto y la descripción.
6. Guardar el registro.
7. Consultar el comprobante de radicación generado.

### 9.2. Información solicitada

| Campo | Requisito |
|---|---|
| Nombre completo | Entre 3 y 100 caracteres, con al menos una letra. |
| Tipo de documento | CC, TI, CE, PP o NIT. |
| Número de documento | Entre 3 y 15 dígitos. |
| Tipo de teléfono | Celular, Fijo, Corporativo u Otro. |
| Número telefónico | Exactamente 10 dígitos. |
| Correo electrónico | Formato válido y máximo 254 caracteres. |
| Dirección | Opcional; entre 5 y 200 caracteres cuando se proporciona. |
| Perfil | Estudiante, Docente, Administrativo o Ciudadano. |
| Tipo de solicitud | Petición, Queja, Reclamo o Sugerencia. |
| Canal de recepción | Seleccionar una de las opciones disponibles. |
| Tipo de mascota | Perro, Gato u Otro. |
| Campus | Seleccionar una de las opciones disponibles. |
| Asunto | Entre 5 y 150 caracteres. |
| Descripción | Entre 20 y 2.000 caracteres. |
| Fecha de radicación | Fecha válida, no futura. |

La fecha de radicación puede dejarse vacía para utilizar automáticamente la fecha y hora actuales. Si se ingresa manualmente, debe utilizarse el formato:

```text
AAAA-MM-DD HH:MM:SS
```

### 9.3. Información generada automáticamente

El sistema asigna:

- Identificador consecutivo.
- Fecha de registro.
- Fecha máxima de respuesta.
- Estado inicial Registrada.
- Usuario responsable del registro.

El plazo máximo configurado es de 30 días calendario a partir de la fecha de registro.

Cada tipo de solicitud dispone de una secuencia independiente de identificadores.

## 10. Comprobante de radicación

Después de guardar una solicitud, el programa genera un comprobante TXT con la información principal de la PQRS.

El radicado incluye el identificador, fechas, estado, datos del solicitante, clasificación, asunto y usuario registrador.

La descripción detallada se almacena en la base de datos, pero no se incluye en el comprobante.

Cada línea del archivo TXT contiene exactamente 120 caracteres.

Los comprobantes se almacenan en:

| Modo | Ubicación |
|---|---|
| Histórico | data/radicados/ |
| Demostración | data/demostracion/radicados/ |

En la interfaz gráfica se utiliza una fuente monoespaciada y desplazamiento horizontal para facilitar la lectura de las líneas completas.

Si el borde derecho no se visualiza completamente, utilizar el desplazamiento horizontal o abrir directamente el archivo TXT.

## 11. Consultar una PQRS

Para consultar una solicitud:

1. Seleccionar Consultar PQRS.
2. Elegir el tipo de solicitud.
3. Ingresar el identificador.
4. Presionar Buscar.
5. Revisar el comprobante mostrado.

También se pueden consultar todas las categorías.

El identificador puede repetirse entre diferentes tipos de PQRS, por lo que la identificación completa de una solicitud corresponde al tipo y su número.

Cuando se realiza una búsqueda sin identificador, el sistema muestra como máximo 20 comprobantes e informa la cantidad total de coincidencias.

La consulta no modifica los registros almacenados.

## 12. Cambiar el estado de una PQRS

Las solicitudes siguen el siguiente flujo:

```text
Registrada → En proceso → Solucionada
```

Para actualizar una solicitud:

1. Seleccionar Cambiar Estado.
2. Elegir el tipo de PQRS.
3. Ingresar el identificador.
4. Presionar Buscar radicado.
5. Revisar el estado actual y el siguiente permitido.
6. Confirmar el cambio.

No se permiten saltos entre estados, retrocesos ni reaperturas de solicitudes solucionadas.

Cuando una solicitud pasa a Solucionada, se registra automáticamente la fecha y hora real de respuesta.

El sistema también calcula el tiempo transcurrido desde la radicación y actualiza el comprobante TXT.

## 13. Estadísticas e indicadores

Para consultar los resultados, seleccionar Estadísticas y Gráficas en Flet o la opción 4 en consola.

El sistema presenta los siguientes indicadores:

- Promedio real de días de respuesta.
- Promedio antes del redondeo.
- Cantidad de casos con fechas válidas.
- Total de solicitudes.
- Solicitudes activas.
- Distribución por mascotas.
- Distribución por canales.
- Distribución por campus.
- Distribución por estado.
- Cantidad por tipo de PQRS.
- Distribución por documentos de identidad.
- Perfil del solicitante.
- Cantidad de registros por usuario.
- Solicitudes vencidas.
- Solicitudes próximas a vencer.
- Solicitudes activas más antiguas.

### 13.1. Promedio de días de respuesta

El promedio se calcula utilizando las solicitudes solucionadas que contienen fechas válidas de radicación y respuesta.

El redondeo se aplica únicamente al resultado final.

Cuando no existe información suficiente, el indicador se presenta como No disponible.

En la base histórica inicial, las fechas reales de respuesta y los perfiles desconocidos permanecen vacíos. El sistema no asigna información ficticia a estos campos.

### 13.2. Vencimientos

Las solicitudes activas se clasifican como:

- Vencidas.
- Próximas a vencer.
- Dentro del plazo.
- Con fecha inválida.

El umbral de alerta configurado es de cinco días.

Los porcentajes de vencimiento se calculan sobre las solicitudes activas, excluyendo las solucionadas.

### 13.3. Generación de gráficas

En la interfaz gráfica, presionar Generar todas las gráficas (PNG).

En consola, responder S cuando el sistema pregunte si se desean generar las gráficas.

Los nueve archivos generados corresponden a:

1. Distribución por mascotas.
2. Canales de recepción.
3. Campus.
4. Estados.
5. Tipos de PQRS.
6. Documentos de identidad.
7. Perfiles.
8. Usuarios registradores.
9. Vencimientos.

Las gráficas se almacenan en:

- `data/graficas/` para la base histórica.
- `data/demostracion/graficas/` para la demostración.

Los archivos PNG pueden abrirse directamente desde Visual Studio Code o el Explorador de archivos.

## 14. Base histórica y base de demostración

### 14.1. Base histórica sintética

El proyecto incluye 12.000 registros sintéticos.

| Tipo de solicitud | Cantidad |
|---|---:|
| Petición | 3.000 |
| Queja | 3.000 |
| Reclamo | 3.000 |
| Sugerencia | 3.000 |
| **Total** | **12.000** |

Estos registros permiten comprobar el procesamiento de volúmenes de información y la generación de estadísticas.

No corresponden a solicitudes veterinarias reales.

### 14.2. Base de demostración

La base independiente fue diseñada inicialmente con ocho casos sintéticos, cuatro de ellos solucionados.

Durante las pruebas funcionales realizadas el 25 de noviembre de 2026 se registró y solucionó una petición adicional.

Los resultados obtenidos fueron:

| Indicador | Resultado |
|---|---:|
| Total de solicitudes | 9 |
| Registradas | 2 |
| En proceso | 2 |
| Solucionadas | 5 |
| Activas | 4 |
| Promedio antes del redondeo | 2,2007 días |
| Promedio redondeado | 2 días |
| Porcentaje de resolución | 55,56 % |

Estos resultados pueden cambiar cuando se registren nuevas solicitudes o se actualicen estados.

Las operaciones realizadas en la base de demostración no modifican los registros históricos.

## 15. Cerrar sesión y salir

### Interfaz gráfica

- Presionar Cerrar sesión para regresar al formulario de autenticación.
- Cerrar la ventana para finalizar el programa.

### Consola

- Seleccionar la opción 5 para cerrar sesión.
- Seleccionar la opción 6 para finalizar el programa.
- En la pantalla de autenticación, utilizar la opción de salida indicada por el sistema.

## 16. Comandos complementarios

### Generar reportes de la base histórica

```bash
python src/analizar_pqrs.py
```

### Generar gráficas de la base histórica

```bash
python src/graficas.py
```

### Generar reportes de demostración

```bash
python src/analizar_pqrs.py --demo
```

### Generar gráficas de demostración

```bash
python src/graficas.py --demo
```

### Ejecutar las pruebas automatizadas

```bash
python -m unittest discover -s tests -v
```

La ejecución final del 25 de noviembre de 2026 superó las 15 pruebas automatizadas, sin fallos ni errores.

## 17. Recomendaciones de uso

- No modificar manualmente los identificadores de las solicitudes.
- No editar directamente las contraseñas almacenadas.
- No eliminar los archivos de datos necesarios.
- Conservar una copia de seguridad del proyecto.
- Utilizar el modo de demostración para practicar.
- Evitar ejecutar varias instancias sobre la misma carpeta de datos.
- No almacenar datos personales reales.
- No utilizar las credenciales académicas en sistemas de producción.

El archivo generar_datos.py está destinado a generar datos sintéticos adicionales en una carpeta independiente. No es necesario ejecutarlo para utilizar el proyecto entregado.

## 18. Preguntas frecuentes

### ¿Qué hago si el programa no abre?

Verificar que Python esté instalado y ejecutar nuevamente:

```bash
python -m pip install -r requirements.txt
```

Comprobar que la terminal esté ubicada en la carpeta principal del proyecto.

### ¿Qué hago si Flet no abre?

Revisar la instalación de las dependencias gráficas y la versión de Python.

Como alternativa, utilizar la interfaz de consola:

```bash
python src/main.py --consola
```

### ¿Por qué aparece No disponible en el promedio histórico?

Porque los registros históricos originales no contienen fechas reales de respuesta.

El cálculo puede comprobarse utilizando la base de demostración.

### ¿Por qué aparecen perfiles sin información?

Los registros históricos carecen de ese dato. Los registros nuevos requieren seleccionar un perfil válido.

### ¿Por qué dos solicitudes pueden tener el mismo identificador?

Porque cada categoría de PQRS utiliza un archivo y una secuencia de identificadores independientes.

### ¿Por qué cambian las estadísticas de vencimiento?

Porque se calculan utilizando la fecha y hora de corte actual.

### ¿Qué ocurre si ingreso una contraseña incorrecta tres veces?

El sistema activa un bloqueo temporal de diez segundos.

### ¿Dónde se guardan las gráficas?

En la carpeta graficas de la base seleccionada.

### ¿Puedo modificar solicitudes sin afectar la base histórica?

Sí. Debe iniciar el sistema utilizando el argumento `--demo`.

### ¿Puedo utilizar el programa con información real?

El sistema está diseñado para fines académicos y utiliza datos sintéticos. No ha sido evaluado como una aplicación de producción.

## 19. Documentación complementaria

- [Documentación técnica](documentacion_tecnica.md)
- [Informe de pruebas](informe_pruebas.md)
- [README del proyecto](../README.md)
- [Licencia](../LICENSE)

## 20. Licencia

HuellaMepega se publica bajo la licencia Creative Commons Atribución-NoComercial-CompartirIgual 4.0 Internacional (CC BY-NC-SA 4.0).

El proyecto tiene fines académicos y educativos.

---

**HuellaMepega — Algoritmia y Programación — Universidad de Antioquia, 2026-2.**