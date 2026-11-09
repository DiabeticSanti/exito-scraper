"""Línea de comandos: python -m exito_scraper"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import almacen
from .fetch import obtener_html_requests, obtener_html_selenium
from .limpieza import resumir
from .parser import URL_PRODUCTO, extraer_datos


def construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="exito_scraper", description=__doc__)
    p.add_argument("--url", default=URL_PRODUCTO)
    p.add_argument("--metodo", choices=["requests", "selenium"], default="requests")
    p.add_argument("--html-file", help="usar un HTML local en vez de descargar (modo sin red)")
    p.add_argument("--salida", help="CSV de historial donde agregar la medición")
    return p


def main(argv: list[str] | None = None) -> int:
    args = construir_parser().parse_args(argv)
    try:
        if args.html_file:
            html = Path(args.html_file).read_text(encoding="utf-8")
            metodo = "Archivo local"
        elif args.metodo == "selenium":
            html, metodo = obtener_html_selenium(args.url), "Selenium"
        else:
            html, metodo = obtener_html_requests(args.url), "BeautifulSoup"
    except Exception as error:  # noqa: BLE001 - se informa y se devuelve código de error
        print(f"No fue posible obtener la página: {error}", file=sys.stderr)
        return 1

    datos = extraer_datos(html, metodo, args.url)
    if not datos["nombre"] and not datos["ofertas"]:
        print("No se encontraron datos del producto en la página.", file=sys.stderr)
        return 2

    resultado = resumir(datos)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    if args.salida:
        almacen.guardar(resultado, args.salida)
    return 0
