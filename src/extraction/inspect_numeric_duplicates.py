
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
BRONZE_DIR = ROOT_DIR / "data" / "bronze"
LOG_DIR = ROOT_DIR / "logs"

EXCEL_FILE = (
    BRONZE_DIR
    / "MEN_ESTADISTICAS_MATRICULA_POR_MUNICIPIOS_ES_20261014.xlsx"
)

df = pd.read_excel(EXCEL_FILE)

claves = ["AÑO", "Código delMunicipio"]

columnas_numericas = [
    "TECNICA PROFESIONAL",
    "TECNOLOGICA",
    "UNIVERSITARIA",
    "ESPECIALIZACION",
    "MAESTRIA",
    "DOCTORADO",
    "IES CON OFERTA",
]

# Identificar claves con valores numéricos diferentes.
claves_con_diferencias = []

for clave, grupo in df.groupby(claves, dropna=False):
    if len(grupo) < 2:
        continue

    columnas_diferentes = [
        columna
        for columna in columnas_numericas
        if grupo[columna].nunique(dropna=False) > 1
    ]

    if columnas_diferentes:
        claves_con_diferencias.append(clave)

# Recuperar todos los registros de esas claves.
muestra = df.merge(
    pd.DataFrame(
        claves_con_diferencias,
        columns=claves,
    ),
    on=claves,
    how="inner",
)

muestra = muestra.sort_values(claves)

print("\n========== INSPECCIÓN DE DIFERENCIAS NUMÉRICAS ==========")
print(f"Claves con diferencias numéricas: {len(claves_con_diferencias)}")
print(f"Filas involucradas: {len(muestra)}")

print("\nPrimeros 30 registros completos:")
print(muestra.head(30).to_string(index=False))

LOG_DIR.mkdir(parents=True, exist_ok=True)

salida = LOG_DIR / "registros_con_diferencias_numericas.csv"
muestra.to_csv(salida, index=False, encoding="utf-8-sig")

print(f"\nRegistros guardados para inspección: {salida}")
print("El archivo original no fue modificado.")
