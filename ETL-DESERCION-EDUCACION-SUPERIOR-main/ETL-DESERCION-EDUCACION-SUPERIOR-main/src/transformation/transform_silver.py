from pathlib import Path
import json
import logging
import pandas as pd

# -----------------------------------------------------------------------------
# RUTAS DEL PROYECTO (Misma convención usada en Bronze)
# -----------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[2]
BRONZE_DIR = ROOT_DIR / "data" / "bronze"
SILVER_DIR = ROOT_DIR / "data" / "silver"
LOG_DIR = ROOT_DIR / "logs"

# Crear carpetas si no existen
LOG_DIR.mkdir(parents=True, exist_ok=True)
SILVER_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "pipeline.log", encoding="utf-8"),
        logging.StreamHandler()
    ],
)

# Estandarización de columnas a snake_case
COLUMNAS_SILVER = {
    "a_o": "anio",
    "c_digo_deldepartamento": "codigo_departamento",
    "nombre_del_departamento": "nombre_departamento",
    "c_digo_delmunicipio": "codigo_municipio",
    "nombre_del_municipio": "nombre_municipio",
    "tecnica_profesional": "tecnica_profesional",
    "tecnologica": "tecnologica",
    "universitaria": "universitaria",
    "especializacion": "especializacion",
    "maestria": "maestria",
    "doctorado": "doctorado",
    "ies_con_oferta": "ies_con_oferta"
}

NIVELES_EDUCATIVOS = [
    "tecnica_profesional",
    "tecnologica",
    "universitaria",
    "especializacion",
    "maestria",
    "doctorado"
]

def transformar_silver():
    """Lee fuentes de Bronze, estandariza, consolida duplicados y genera archivos Silver."""

    logging.info("Iniciando procesamiento de la Capa Silver")

    # 1. Búsqueda de la fuente extraída en Bronze
    api_files = sorted(BRONZE_DIR.glob("matricula_api_*.json"))
    excel_file = BRONZE_DIR / "MEN_ESTADISTICAS_MATRICULA_POR_MUNICIPIOS_ES_20261014.xlsx"

    if api_files:
        fuente_path = api_files[-1]
        logging.info("Cargando datos desde la API Bronze: %s", fuente_path.name)
        with open(fuente_path, "r", encoding="utf-8") as f:
            datos_raw = json.load(f)
        df_raw = pd.DataFrame(datos_raw)
    elif excel_file.exists():
        fuente_path = excel_file
        logging.info("Cargando datos desde el Excel Bronze: %s", fuente_path.name)
        df_raw = pd.read_excel(excel_file)
    else:
        logging.error("No se encontraron archivos en data/bronze/")
        raise FileNotFoundError("No hay datos disponibles en la capa Bronze.")

    filas_iniciales = len(df_raw)

    # 2. Homologación de nombres de columnas
    df = df_raw.rename(columns=COLUMNAS_SILVER)

    mapeo_excel = {
        "AÑO": "anio",
        "Código delDepartamento": "codigo_departamento",
        "Nombre del Departamento": "nombre_departamento",
        "Código delMunicipio": "codigo_municipio",
        "Nombre del Municipio": "nombre_municipio",
        "TECNICA PROFESIONAL": "tecnica_profesional",
        "TECNOLOGICA": "tecnologica",
        "UNIVERSITARIA": "universitaria",
        "ESPECIALIZACION": "especializacion",
        "MAESTRIA": "maestria",
        "DOCTORADO": "doctorado",
        "IES CON OFERTA": "ies_con_oferta"
    }
    df = df.rename(columns=mapeo_excel)

    # 3. Limpieza de tipos de datos y nulos
    cols_numericas = NIVELES_EDUCATIVOS + ["ies_con_oferta"]
    for col in cols_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    df["anio"] = pd.to_numeric(df["anio"], errors="coerce").astype(int)
    
    # Formatear códigos DANE (2 dígitos para departamento, 5 dígitos para municipio)
    df["codigo_departamento"] = df["codigo_departamento"].astype(str).str.strip().str.split('.').str[0].str.zfill(2)
    df["codigo_municipio"] = df["codigo_municipio"].astype(str).str.strip().str.split('.').str[0].str.zfill(5)

    df["nombre_departamento"] = df["nombre_departamento"].astype(str).str.strip().str.upper()
    df["nombre_municipio"] = df["nombre_municipio"].astype(str).str.strip().str.upper()

    # 4. Consolidación de duplicados (Resuelve las 6.780 filas repetidas agrupando por Año y Municipio)
    group_cols = [
        "anio",
        "codigo_departamento",
        "nombre_departamento",
        "codigo_municipio",
        "nombre_municipio"
    ]

    df_wide = df.groupby(group_cols, as_index=False).agg({
        "tecnica_profesional": "sum",
        "tecnologica": "sum",
        "universitaria": "sum",
        "especializacion": "sum",
        "maestria": "sum",
        "doctorado": "sum",
        "ies_con_oferta": "max"
    })

    # Métrica calculada: Matrícula Total por Municipio
    df_wide["total_matricula_municipio"] = df_wide[NIVELES_EDUCATIVOS].sum(axis=1)
    df_wide["total_matricula_municipio"] = df_wide["total_matricula_municipio"].clip(lower=0)

    # 5. Formato Unpivot (Formato Largo para facilitar análisis en Gold)
    df_long = pd.melt(
        df_wide,
        id_vars=group_cols + ["ies_con_oferta", "total_matricula_municipio"],
        value_vars=NIVELES_EDUCATIVOS,
        var_name="nivel_formacion",
        value_name="estudiantes_matriculados"
    )

    # 6. Guardar resultados
    out_wide = SILVER_DIR / "silver_matricula_municipios.csv"
    out_long = SILVER_DIR / "silver_matricula_unpivot.csv"

    df_wide.to_csv(out_wide, index=False, encoding="utf-8")
    df_long.to_csv(out_long, index=False, encoding="utf-8")

    logging.info("Capa Silver procesada exitosamente")

    print("\n================ RESUMEN CAPA SILVER ================")
    print(f"Registros originales leídos:         {filas_iniciales:,}")
    print(f"Registros consolidados (Ancho):      {len(df_wide):,} filas")
    print(f"Registros despivotados (Largo):     {len(df_long):,} filas")
    print(f"Rango de años procesados:            {df_wide['anio'].min()} - {df_wide['anio'].max()}")
    print(f"Departamentos procesados:            {df_wide['nombre_departamento'].nunique()}")
    print(f"Municipios procesados:               {df_wide['nombre_municipio'].nunique()}")
    print(f"Archivo guardado (Formato Ancho):    {out_wide.relative_to(ROOT_DIR)}")
    print(f"Archivo guardado (Formato Largo):    {out_long.relative_to(ROOT_DIR)}")
    print("=====================================================\n")

if __name__ == "__main__":
    transformar_silver()