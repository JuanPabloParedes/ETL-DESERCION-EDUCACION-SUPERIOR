
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
EXCEL_FILE = (
    ROOT_DIR
    / "data"
    / "bronze"
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

resultados = []

for clave, grupo in df.groupby(claves, dropna=False):
    if len(grupo) < 2:
        continue

    nombre_cambia = (
        grupo["Nombre del Municipio"].nunique(dropna=False) > 1
    )

    columnas_numericas_que_cambian = [
        columna
        for columna in columnas_numericas
        if grupo[columna].nunique(dropna=False) > 1
    ]

    if columnas_numericas_que_cambian:
        categoria = "Diferencias numéricas"
    elif nombre_cambia:
        categoria = "Solo cambia el nombre"
    else:
        categoria = "Filas idénticas"

    resultados.append({
        "AÑO": clave[0],
        "Código delMunicipio": clave[1],
        "cantidad_filas": len(grupo),
        "categoria": categoria,
        "nombre_cambia": nombre_cambia,
        "columnas_numericas_que_cambian": ", ".join(
            columnas_numericas_que_cambian
        ),
    })

resultado = pd.DataFrame(resultados)

print("\n========== DIFERENCIAS ENTRE REGISTROS ==========")
print(f"Claves repetidas analizadas: {len(resultado)}")

print("\nCantidad de claves por categoría:")
print(resultado["categoria"].value_counts().to_string())

print("\nEjemplos con diferencias numéricas:")
diferencias = resultado[
    resultado["categoria"] == "Diferencias numéricas"
]
if diferencias.empty:
    print("No se encontraron diferencias numéricas.")
else:
    print(diferencias.head(15).to_string(index=False))

salida = ROOT_DIR / "logs" / "analisis_diferencias.csv"
salida.parent.mkdir(parents=True, exist_ok=True)
resultado.to_csv(salida, index=False, encoding="utf-8-sig")

print(f"\nDetalle guardado en: {salida}")
print("No se modificó el archivo original.")
