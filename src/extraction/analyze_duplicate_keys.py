
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
BRONZE_DIR = ROOT_DIR / "data" / "bronze"

EXCEL_FILE = (
    BRONZE_DIR
    / "MEN_ESTADISTICAS_MATRICULA_POR_MUNICIPIOS_ES_20261014.xlsx"
)

df = pd.read_excel(EXCEL_FILE)

claves = ["AÑO", "Código delMunicipio"]

# Filas cuya combinación año-municipio aparece más de una vez
repetidas = df[
    df.duplicated(subset=claves, keep=False)
].copy()

print("\n========== ANÁLISIS DE CLAVES REPETIDAS ==========")
print(f"Filas con año-municipio repetido: {len(repetidas)}")

# Contar cuántas versiones diferentes existen para cada clave
variantes = (
    repetidas.groupby(claves, dropna=False)
    .apply(lambda grupo: len(grupo.drop_duplicates()), include_groups=False)
    .reset_index(name="variantes_distintas")
)

print(
    "Claves con varias versiones de fila:",
    int((variantes["variantes_distintas"] > 1).sum())
)

print("\nDistribución de versiones por clave:")
print(variantes["variantes_distintas"].value_counts().sort_index())

# Identificar las columnas que cambian dentro de las claves repetidas
columnas_datos = [col for col in df.columns if col not in claves]

cambios = []

for clave, grupo in repetidas.groupby(claves, dropna=False):
    columnas_diferentes = [
        columna
        for columna in columnas_datos
        if grupo[columna].nunique(dropna=False) > 1
    ]

    if columnas_diferentes:
        cambios.append({
            "AÑO": clave[0],
            "Código delMunicipio": clave[1],
            "cantidad_filas": len(grupo),
            "columnas_que_cambian": ", ".join(columnas_diferentes),
        })

cambios_df = pd.DataFrame(cambios)

print("\n========== CAMPOS QUE CAMBIAN ==========")

if cambios_df.empty:
    print("No se encontraron diferencias entre las filas de cada clave.")
else:
    print("Claves con diferencias en sus datos:", len(cambios_df))
    print("\nEjemplos:")
    print(cambios_df.head(15).to_string(index=False))

    salida = ROOT_DIR / "logs" / "analisis_claves_repetidas.csv"
    salida.parent.mkdir(parents=True, exist_ok=True)
    cambios_df.to_csv(salida, index=False, encoding="utf-8-sig")
    print(f"\nDetalle guardado en: {salida}")

print("\nNo se eliminaron ni modificaron registros originales.")
