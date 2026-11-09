"""Uso: python -m exito_scraper.sitio [csv_historial] [carpeta_salida]"""

import sys

from .reporte import generar_sitio

if __name__ == "__main__":
    argumentos = sys.argv[1:]
    csv_historial = argumentos[0] if len(argumentos) > 0 else "data/historico.csv"
    carpeta = argumentos[1] if len(argumentos) > 1 else "site"
    print(generar_sitio(csv_historial, carpeta))
