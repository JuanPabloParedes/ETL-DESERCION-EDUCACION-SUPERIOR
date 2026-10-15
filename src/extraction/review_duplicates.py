
from pathlib import Path
import logging
import pandas as pd

# Rutas del proyecto
ROOT_DIR = Path(__file__).resolve().parents[2]
BRONZE_DIR = ROOT_DIR / "data" / "bronze"
LOG_DIR = ROOT_DIR / "logs"

EXCEL_FILE = (
    BRONZE_DIR
    / "MEN_ESTADISTICAS_MATRICULA_POR_MUNICIPIOS_ES_20261014.xlsx"
)

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


def revisar_duplicados():
    if not EXCEL_FILE.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {EXCEL_FILE}"
        )

    df = pd.read_excel(EXCEL_FILE)

    logging.info("Iniciando diagnóstico de duplicados")
    logging.info("Registros originales: %s", len(df))

    # 1. Filas completamente idénticas
    duplicados_exactos = df.duplicated(keep=False)
    cantidad_filas_en_grupos_exactos = int(duplicados_exactos.sum())
    repeticiones_sobrantes = int(df.duplicated().sum())

    print("\n========== DIAGNÓSTICO DE DUPLICADOS ==========")
    print(f"Total de registros: {len(df)}")
    print(
        "Filas pertenecientes a grupos de duplicados exactos:",
        cantidad_filas_en_grupos_exactos,
    )
    print(
        "Repeticiones sobrantes si se conservara una fila por grupo:",
        repeticiones_sobrantes,
    )

    if duplicados_exactos.any():
        print("\nEjemplos de filas completamente repetidas:")
        print(
            df.loc[duplicados_exactos]
            .sort_values(list(df.columns))
            .head(10)
            .to_string(index=False)
        )

    # 2. Repeticiones de la combinación año + municipio
    claves = ["AÑO", "Código delMunicipio"]

    if all(columna in df.columns for columna in claves):
        cantidad_por_clave = (
            df.groupby(claves, dropna=False)
            .size()
            .reset_index(name="cantidad_registros")
        )

        claves_repetidas = cantidad_por_clave[
            cantidad_por_clave["cantidad_registros"] > 1
        ]

        print("\n========== CLAVES REPETIDAS ==========")
        print(
            "Combinaciones año-municipio con más de un registro:",
            len(claves_repetidas),
        )

        if not claves_repetidas.empty:
            print("\nEjemplos de combinaciones repetidas:")
            print(
                claves_repetidas
                .sort_values("cantidad_registros", ascending=False)
                .head(10)
                .to_string(index=False)
            )

            # Examinar si los registros de esas claves difieren
            muestra_claves = claves_repetidas[claves].head(10)

            muestra = df.merge(
                muestra_claves,
                on=claves,
                how="inner",
            )

            print("\nDetalle de las primeras claves repetidas:")
            print(muestra.head(20).to_string(index=False))

    # 3. Guardar evidencia del diagnóstico
    salida = LOG_DIR / "diagnostico_duplicados.txt"

    with open(salida, "w", encoding="utf-8") as archivo:
        archivo.write("DIAGNÓSTICO DE DUPLICADOS\n")
        archivo.write(f"Total de registros: {len(df)}\n")
        archivo.write(
            "Filas en grupos de duplicados exactos: "
            f"{cantidad_filas_en_grupos_exactos}\n"
        )
        archivo.write(
            "Repeticiones sobrantes: "
            f"{repeticiones_sobrantes}\n"
        )

        if all(columna in df.columns for columna in claves):
            archivo.write(
                "Combinaciones año-municipio repetidas: "
                f"{len(claves_repetidas)}\n"
            )

    logging.info("Diagnóstico guardado en %s", salida)
    print(f"\nDiagnóstico guardado en: {salida}")
    print("No se eliminaron ni modificaron registros originales.")


if __name__ == "__main__":
    revisar_duplicados()
