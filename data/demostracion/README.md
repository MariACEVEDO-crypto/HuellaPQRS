# DEMOSTRACIÓN SINTÉTICA AISLADA — NO ES LA BASE HISTÓRICA

Ocho casos ficticios construidos para comprobar el cálculo de tiempo de atención y los perfiles. No representan personas ni actividad real. No se combinan con los 12.000 registros de `data/*.txt`. Los cuatro TXT, Usuarios.txt, radicados, CSV, TXT y gráficas de esta carpeta son independientes. Use `python src/main.py --consola --demo` desde la raíz; para Flet, `python src/main.py --demo` (renderizado pendiente de verificar). Se muestra la etiqueta de modo en el menú y los reportes. Las credenciales son solo de ensayo: consulte el README principal.

## Valores esperados iniciales

| Tipo | ID | Duración de solución | Perfil |
|---|---:|---:|---|
| Peticion | 1 | 18 horas = 0,75 días | Estudiante |
| Queja | 1 | 42 horas = 1,75 días | Docente |
| Reclamo | 1 | 90 horas = 3,75 días | Administrativo |
| Sugerencia | 1 | 114 horas = 4,75 días | Ciudadano |

Promedio sin truncamiento = 264 horas / 4 / 24 = 2,75 días. Indicador entero: 3 días (redondeo al entero más cercano; empate al par). Antes se habría promediado 0, 1, 3 y 4: 2 días. Cobertura: 4 de 4 solucionadas. Hay 2 casos de cada uno de los cuatro perfiles (25 % cada uno), 4 activos y 4 solucionados (50 %). Al corte de referencia 2026-11-24 12:00:00 hora Colombia: 1 activa vencida, 1 próxima a vencer, 2 dentro del plazo. Los vencimientos cambian con el reloj real y al actualizar estados.

Para la demostración en vivo: consulte Reclamo #2 (En proceso), cambie a Solucionada y revise la fecha real y duración. Después se tendrán 5 casos con fecha de respuesta válida. El promedio cambiará según la hora de ejecución. Ensaye en una copia para conservar estos resultados iniciales. El generador `src/preparar_demostracion.py` documenta el origen de estos casos y se niega a sobrescribir una carpeta existente.
