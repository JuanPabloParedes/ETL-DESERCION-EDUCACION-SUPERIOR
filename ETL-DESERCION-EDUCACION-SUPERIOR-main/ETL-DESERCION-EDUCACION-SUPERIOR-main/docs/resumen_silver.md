# Resumen de Transformación - Capa Silver

## Responsable
Juan Jose Grueso

## Objetivo
Limpiar, estandarizar y consolidar la información de matrícula por municipio proveniente de la capa Bronze, resolviendo las filas duplicadas y generando los datasets depurados en formato ancho y largo (*unpivot*).

## Reglas de Calidad Aplicadas

1. **Estandarización de Nombres:**
   - Columnas homogenizadas a `snake_case` (`anio`, `codigo_departamento`, `nombre_departamento`, `codigo_municipio`, `nombre_municipio`, etc.).
2. **Formateo DANE:**
   - Códigos ajustados con ceros a la izquierda (2 dígitos departamento, 5 dígitos municipio).
3. **Resolución de Duplicados:**
   - Agrupación por `anio` y `codigo_municipio` sumando la matrícula de cada nivel educativo para consolidar las filas desagregadas sin eliminar información.
4. **Tratamiento de Nulos:**
   - Conversión de valores nulos a `0` en campos numéricos y cálculo de `total_matricula_municipio`.

## Archivos Creados en `data/silver/`
- `silver_matricula_municipios.csv`: Formato ancho consolidado por municipio/año.
- `silver_matricula_unpivot.csv`: Formato largo despivotado por nivel de formación.