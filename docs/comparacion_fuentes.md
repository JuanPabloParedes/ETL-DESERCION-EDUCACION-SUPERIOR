
# Comparación de fuentes: Excel y API

## 1. Objetivo

Comparar la información obtenida del archivo Excel y de la API de datos.gov.co para determinar si ambas fuentes aportan registros diferentes o contienen la misma información.

## 2. Fuentes utilizadas

### Archivo Excel
- Archivo: MEN_ESTADISTICAS_MATRICULA_POR_MUNICIPIOS_ES_20261014.xlsx
- Ubicación: data/bronze/
- Formato: XLSX

### API
- URL: https://www.datos.gov.co/api/v3/views/y9ga-zwzy/query.json
- Archivo extraído: matricula_api_20261015_002223.json
- Ubicación: data/bronze/
- Formato: JSON

## 3. Resultados de la extracción

| Característica | Excel | API |
|---|---:|---:|
| Registros | 19.618 | 19.618 |
| Columnas originales | 12 | 16 |
| Campos equivalentes comparados | 12 | 12 |
| Filas repetidas completas | 6.780 | 6.780 |

La API incluye cuatro campos técnicos adicionales respecto al Excel. Para comparar las fuentes, se homologaron los nombres de los 12 campos equivalentes.

## 4. Resultado de la comparación

- Registros coincidentes: 19.618.
- Registros adicionales en Excel: 0.
- Registros adicionales en la API: 0.
- Filas repetidas completas identificadas en Excel: 6.780.
- Filas repetidas completas identificadas en la API: 6.780.

La comparación encontró que ambas fuentes contienen los mismos registros en los 12 campos equivalentes, incluyendo la frecuencia con la que aparece cada registro.

## 5. Decisión propuesta

Se propone conservar ambos archivos originales en Bronze para mantener la trazabilidad y contar con evidencia de las fuentes utilizadas.

Como ambas fuentes contienen los mismos registros, no se recomienda apilarlas como si fueran conjuntos de datos independientes.

Para Silver, se propone trabajar con una sola representación de los datos, después de acordar con el equipo las reglas de calidad y el tratamiento de las filas repetidas.

## 6. Observaciones de calidad

Durante la revisión inicial se observó que los campos "Código delDepartamento" y "Nombre del Departamento" presentan valores iguales en algunos registros, por ejemplo, 11 y 11.

Este comportamiento debe revisarse durante la transformación, sin modificar los archivos originales de Bronze.

Las filas repetidas identificadas deben analizarse antes de eliminarlas, para determinar si corresponden a duplicados no deseados o a registros legítimos.

## 7. Alcance

Esta comparación verifica la coincidencia entre las dos fuentes de matrícula. No demuestra por sí sola la existencia de una variable de deserción ni permite concluir que las filas repetidas sean errores.
