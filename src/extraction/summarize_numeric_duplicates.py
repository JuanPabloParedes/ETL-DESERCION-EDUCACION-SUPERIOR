
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

resumen = []

for clave, grupo in df.groupby(claves, dropna=False):
    columnas_diferentes = [
        col for col in columnas_numericas
        if grupo[col].nunique(dropna=False) > 1
    ]

    if columnas_diferentes:
        resumen.append({
            "AÑO": clave[0],
            "Código delMunicipio": clave[1],
            "Nombre del Municipio": grupo[
                "Nombre del Municipio"
            ].astype(str).unique().tolist(),
            "Cantidad de filas": len(grupo),
            "Columnas con diferencias": ", ".join(
                columnas_diferentes
            ),
        })

resultado = pd.DataFrame(resumen)

LOG_DIR.mkdir(parents=True, exist_ok=True)

salida = LOG_DIR / "resumen_diferencias_numericas.csv"
resultado.to_csv(salida, index=False, encoding="utf-8-sig")

print("========== RESUMEN DE DIFERENCIAS ==========")
print(f"Claves con diferencias: {len(resultado)}")
print("\nColumnas que más presentan diferencias:")

if not resultado.empty:
    conteo = (
        resultado["Columnas con diferencias"]
        .str.split(", ")
        .explode()
        .value_counts()
    )
    print(conteo.to_string())

    print("\nPrimeras 20 claves:")
    print(resultado.head(20).to_string(index=False))

print(f"\nArchivo guardado en: {salida}")
