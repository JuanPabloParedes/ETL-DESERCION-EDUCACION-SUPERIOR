
from pathlib import Path
from collections import Counter
import json
import logging
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
BRONZE_DIR = ROOT_DIR / "data" / "bronze"
LOG_DIR = ROOT_DIR / "logs"

EXCEL_FILE = (
    BRONZE_DIR
    / "MEN_ESTADISTICAS_MATRICULA_POR_MUNICIPIOS_ES_20261014.xlsx"
)

API_FILES = sorted(BRONZE_DIR.glob("matricula_api_*.json"))

LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            LOG_DIR / "pipeline.log", encoding="utf-8"
        ),
        logging.StreamHandler(),
    ],
)

# Equivalencias entre los nombres de la API y los del Excel.
API_COLUMNAS = {
    "a_o": "AÑO",
    "c_digo_deldepartamento": "Código delDepartamento",
    "nombre_del_departamento": "Nombre del Departamento",
    "c_digo_delmunicipio": "Código delMunicipio",
    "nombre_del_municipio": "Nombre del Municipio",
    "tecnica_profesional": "TECNICA PROFESIONAL",
    "tecnologica": "TECNOLOGICA",
    "universitaria": "UNIVERSITARIA",
    "especializacion": "ESPECIALIZACION",
    "maestria": "MAESTRIA",
    "doctorado": "DOCTORADO",
    "ies_con_oferta": "IES CON OFERTA",
}

COLUMNAS = [
    "AÑO",
    "Código delDepartamento",
    "Nombre del Departamento",
    "Código delMunicipio",
    "Nombre del Municipio",
    "TECNICA PROFESIONAL",
    "TECNOLOGICA",
    "UNIVERSITARIA",
    "ESPECIALIZACION",
    "MAESTRIA",
    "DOCTORADO",
    "IES CON OFERTA",
]


def normalizar_valor(valor):
    """Normaliza valores para compararlos sin alterar los archivos."""

    if pd.isna(valor):
        return "<NULO>"

    # Trata números enteros y decimales equivalentes como iguales.
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        numero = float(valor)
        if numero.is_integer():
            return str(int(numero))
        return str(numero)

    texto = str(valor).strip()

    # Normaliza también valores numéricos que llegan como texto.
    try:
        numero = float(texto)
        if numero.is_integer():
            return str(int(numero))
        return str(numero)
    except (ValueError, OverflowError):
        return texto.casefold()


def convertir_a_registros(df):
    """Convierte las filas en tuplas comparables."""

    preparado = df[COLUMNAS].copy()

    for columna in COLUMNAS:
        preparado[columna] = preparado[columna].map(normalizar_valor)

    return Counter(
        tuple(fila)
        for fila in preparado.itertuples(index=False, name=None)
    )


def comparar_fuentes():
    if not EXCEL_FILE.exists():
        raise FileNotFoundError(f"No se encontró el Excel: {EXCEL_FILE}")

    if not API_FILES:
        raise FileNotFoundError(
            f"No se encontraron archivos JSON en {BRONZE_DIR}"
        )

    api_file = API_FILES[-1]

    logging.info("Excel: %s", EXCEL_FILE.name)
    logging.info("API: %s", api_file.name)

    df_excel = pd.read_excel(EXCEL_FILE)

    with open(api_file, "r", encoding="utf-8") as archivo:
        datos_api = json.load(archivo)

    if not isinstance(datos_api, list):
        raise ValueError("La respuesta de la API no es una lista.")

    df_api = pd.DataFrame(datos_api)

    # Excluir los metadatos de la API y renombrar sus 12 campos.
    df_api = df_api.rename(columns=API_COLUMNAS)

    faltantes_excel = [c for c in COLUMNAS if c not in df_excel.columns]
    faltantes_api = [c for c in COLUMNAS if c not in df_api.columns]

    print("\n========== COMPARACIÓN DE FUENTES ==========")
    print(f"Excel: {EXCEL_FILE.name}")
    print(f"API: {api_file.name}")

    print("\n1. DIMENSIONES")
    print(f"Excel: {len(df_excel)} filas, {len(df_excel.columns)} columnas")
    print(f"API: {len(df_api)} filas, {len(df_api.columns)} columnas")

    if faltantes_excel or faltantes_api:
        print("\nNo se puede comparar: faltan columnas.")
        print("Faltantes en Excel:", faltantes_excel)
        print("Faltantes en API:", faltantes_api)
        return

    print("\n2. COLUMNAS COMPARADAS")
    print(f"Se compararán {len(COLUMNAS)} campos equivalentes.")

    registros_excel = convertir_a_registros(df_excel)
    registros_api = convertir_a_registros(df_api)

    # Cuenta coincidencias respetando cuántas veces aparece cada fila.
    coincidentes = sum(
        min(cantidad, registros_api.get(registro, 0))
        for registro, cantidad in registros_excel.items()
    )

    solo_excel = sum(
        max(0, cantidad - registros_api.get(registro, 0))
        for registro, cantidad in registros_excel.items()
    )

    solo_api = sum(
        max(0, cantidad - registros_excel.get(registro, 0))
        for registro, cantidad in registros_api.items()
    )

    duplicados_excel = len(df_excel) - len(registros_excel)
    duplicados_api = len(df_api) - len(registros_api)

    print("\n3. DUPLICADOS DENTRO DE CADA FUENTE")
    print(f"Excel: {duplicados_excel}")
    print(f"API: {duplicados_api}")

    print("\n4. COMPARACIÓN DE REGISTROS COMPLETOS")
    print(f"Registros coincidentes: {coincidentes}")
    print(f"Registros adicionales en Excel: {solo_excel}")
    print(f"Registros adicionales en API: {solo_api}")

    if solo_excel == 0 and solo_api == 0:
        print("\nRESULTADO: las fuentes contienen los mismos registros.")
    else:
        print("\nRESULTADO: hay diferencias que deben investigarse.")

    logging.info(
        "Comparación terminada: coincidentes=%s, solo_excel=%s, solo_api=%s",
        coincidentes,
        solo_excel,
        solo_api,
    )


if __name__ == "__main__":
    comparar_fuentes()
