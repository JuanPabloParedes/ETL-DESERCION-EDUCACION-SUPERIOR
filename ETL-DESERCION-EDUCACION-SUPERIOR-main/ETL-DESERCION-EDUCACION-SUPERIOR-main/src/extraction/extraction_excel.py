
from pathlib import Path
from datetime import datetime
import pandas as pd
import logging

# Rutas del proyecto
ROOT_DIR = Path(__file__).resolve().parents[2]
BRONZE_DIR = ROOT_DIR / "data" / "bronze"
LOG_DIR = ROOT_DIR / "logs"

# Archivo Excel original
EXCEL_FILE = BRONZE_DIR / "MEN_ESTADISTICAS_MATRICULA_POR_MUNICIPIOS_ES_20261014.xlsx"

# Configurar registro de ejecución
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "pipeline.log", encoding="utf-8"),
        logging.StreamHandler()
    ],
)

def extraer_excel():
    """Lee el Excel original y registra información básica de la extracción."""

    if not EXCEL_FILE.exists():
        logging.error("No se encontró el archivo Excel: %s", EXCEL_FILE)
        raise FileNotFoundError(f"No se encontró el archivo: {EXCEL_FILE}")

    logging.info("Iniciando extracción del Excel: %s", EXCEL_FILE.name)

    df = pd.read_excel(EXCEL_FILE)

    logging.info("Extracción finalizada correctamente")
    logging.info("Cantidad de filas: %s", len(df))
    logging.info("Cantidad de columnas: %s", len(df.columns))
    logging.info("Columnas encontradas: %s", list(df.columns))

    print("\nResumen de la extracción")
    print("------------------------")
    print(f"Archivo: {EXCEL_FILE.name}")
    print(f"Fecha de extracción: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Filas: {len(df)}")
    print(f"Columnas: {len(df.columns)}")
    print("\nPrimeras cinco filas:")
    print(df.head())

    return df


if __name__ == "__main__":
    extraer_excel()
