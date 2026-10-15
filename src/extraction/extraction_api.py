
from pathlib import Path
from datetime import datetime
import json
import logging
import requests

# Rutas del proyecto
ROOT_DIR = Path(__file__).resolve().parents[2]
BRONZE_DIR = ROOT_DIR / "data" / "bronze"
LOG_DIR = ROOT_DIR / "logs"

# API de datos.gov.co
API_URL = "https://www.datos.gov.co/api/v3/views/y9ga-zwzy/query.json"

# Crear carpeta de registros si no existe
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "pipeline.log", encoding="utf-8"),
        logging.StreamHandler()
    ],
)

def extraer_api():
    """Consulta la API y guarda la respuesta original en Bronze."""

    BRONZE_DIR.mkdir(parents=True, exist_ok=True)

    logging.info("Iniciando extracción desde la API")
    logging.info("URL consultada: %s", API_URL)

    try:
        respuesta = requests.get(API_URL, timeout=60)
        respuesta.raise_for_status()
        datos = respuesta.json()

        # Guardar la respuesta original sin transformar sus registros
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_salida = BRONZE_DIR / f"matricula_api_{fecha}.json"

        with open(archivo_salida, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=2)

        if isinstance(datos, list):
            cantidad = len(datos)
        elif isinstance(datos, dict):
            cantidad = len(datos.get("data", [])) if isinstance(datos.get("data"), list) else 1
        else:
            cantidad = 0

        logging.info("Extracción de API finalizada")
        logging.info("Archivo guardado: %s", archivo_salida.name)
        logging.info("Tipo de respuesta: %s", type(datos).__name__)
        logging.info("Cantidad de elementos principales: %s", cantidad)

        print("\nResumen de la extracción de API")
        print("--------------------------------")
        print(f"Archivo guardado: {archivo_salida.name}")
        print(f"Tipo de respuesta: {type(datos).__name__}")
        print(f"Cantidad de elementos principales: {cantidad}")

        return datos

    except requests.RequestException as error:
        logging.error("Error al consultar la API: %s", error)
        raise
    except ValueError as error:
        logging.error("La respuesta no contiene JSON válido: %s", error)
        raise


if __name__ == "__main__":
    extraer_api()
