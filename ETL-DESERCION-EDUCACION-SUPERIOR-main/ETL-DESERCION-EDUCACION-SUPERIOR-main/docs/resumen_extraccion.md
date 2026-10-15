
# Resumen de extracción - Proyecto ETL

## Responsable
Juan Pablo Paredes Gomez

## Objetivo
Extraer los datos originales de matrícula por municipios desde un archivo Excel y una API de datos.gov.co, conservando los archivos sin transformaciones en la capa Bronze.

## Fuente 1: Excel
- Archivo: MEN_ESTADISTICAS_MATRICULA_POR_MUNICIPIOS_ES_20261014.xlsx
- Registros leídos: 19.618
- Columnas: 12
- Resultado: extracción exitosa.

## Fuente 2: API
- URL: https://www.datos.gov.co/api/v3/views/y9ga-zwzy/query.json
- Archivo generado: matricula_api_20261015_002223.json
- Registros recibidos: 19.618
- Campos originales: 16
- Resultado: extracción exitosa.

## Scripts desarrollados
- `src/extraction/extraction_excel.py`: lectura del Excel y registro del resultado de extracción.
- `src/extraction/extraction_api.py`: consulta de la API y almacenamiento de la respuesta JSON.
- `src/extraction/compare_sources.py`: comparación de los 12 campos equivalentes y análisis de filas repetidas.

## Resultado de la comparación
Las fuentes contienen los mismos 19.618 registros en los 12 campos equivalentes. No se encontraron registros adicionales exclusivos de ninguna fuente.

Se identificaron 6.780 filas repetidas completas en cada fuente. Este resultado debe ser revisado durante la fase de calidad de datos.

## Ubicación de los datos originales
Los archivos se conservan localmente en `data/bronze/`. No se modifican durante la extracción.

## Observación
El conjunto de datos corresponde a matrícula y oferta educativa por municipio. Se debe verificar si el proyecto requiere una fuente complementaria con indicadores explícitos de deserción estudiantil.
