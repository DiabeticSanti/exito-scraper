"""Extracción de datos de producto a partir de HTML con JSON-LD.

Es la misma estrategia de la Evidencia 1, pero aislada en funciones puras
(reciben texto HTML, devuelven datos) para poder probarlas sin red.
"""

from __future__ import annotations

import json
import re
from typing import Any

from bs4 import BeautifulSoup

URL_PRODUCTO = (
    "https://www.exito.com/"
    "mouse-razer-gaming-mouse-deathadder-essential-right-handed-103634469-mp/p"
)


def buscar_producto(objeto: Any) -> dict | None:
    """Busca recursivamente el objeto JSON-LD de tipo Product (listas y @graph incluidos)."""
    if isinstance(objeto, list):
        for elemento in objeto:
            encontrado = buscar_producto(elemento)
            if encontrado:
                return encontrado
    elif isinstance(objeto, dict):
        tipo = objeto.get("@type", [])
        if isinstance(tipo, str):
            tipo = [tipo]
        if "Product" in tipo:
            return objeto
        if "@graph" in objeto:
            return buscar_producto(objeto["@graph"])
    return None


def a_numero(valor: Any) -> float | None:
    """Convierte un precio (número o texto como '89.900' o '$ 89.900,00') a float."""
    if valor is None or isinstance(valor, bool):
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).strip()
    if "$" in texto or re.search(r"\d\.\d{3}", texto):
        # formato colombiano: punto de miles, coma decimal
        texto = texto.split(",")[0]
        digitos = re.sub(r"[^\d]", "", texto)
        return float(digitos) if digitos else None
    try:
        return float(texto)
    except ValueError:
        return None


def _estado(url_disponibilidad: str | None) -> str | None:
    if not url_disponibilidad:
        return None
    return str(url_disponibilidad).rstrip("/").split("/")[-1]


def extraer_ofertas(producto: dict | None) -> list[dict]:
    """Devuelve una lista de {'precio': float|None, 'disponibilidad': str|None} (una por oferta)."""
    if not producto:
        return []
    ofertas = producto.get("offers", [])
    if isinstance(ofertas, dict):
        interno = ofertas.get("offers")
        ofertas = interno if isinstance(interno, list) else [ofertas]
    resultado = []
    for oferta in ofertas:
        if not isinstance(oferta, dict):
            continue
        precio = oferta.get("price")
        if precio is None:
            especificacion = oferta.get("priceSpecification", {})
            if isinstance(especificacion, dict):
                precio = especificacion.get("price")
        resultado.append(
            {
                "precio": a_numero(precio),
                "disponibilidad": _estado(oferta.get("availability")),
            }
        )
    return resultado


def _nombre(soup: BeautifulSoup, producto: dict | None) -> str | None:
    nombre = producto.get("name") if producto else None
    if not nombre:
        h1 = soup.select_one("h1")
        nombre = h1.get_text(" ", strip=True) if h1 else None
    if not nombre:
        meta = soup.select_one('meta[property="og:title"]')
        nombre = meta.get("content") if meta else None
    return nombre


def _precios_visibles(soup: BeautifulSoup) -> list[dict]:
    """Respaldo: busca en el HTML elementos de precio cuando el JSON-LD no trae ninguno."""
    encontrados: list[dict] = []
    for etiqueta in soup.select('[class*="price"], [data-testid*="price"]'):
        texto = etiqueta.get_text(" ", strip=True)
        if texto and "$" in texto:
            precio = a_numero(texto)
            if precio is not None and all(o["precio"] != precio for o in encontrados):
                encontrados.append({"precio": precio, "disponibilidad": None})
    return encontrados


def extraer_datos(html: str, metodo: str, url: str = URL_PRODUCTO) -> dict:
    """Extrae nombre, ofertas y calificación de la ficha de un producto.

    El registro conserva los campos de la Evidencia 1 (precio y disponibilidad como texto
    separado por ' | ') y agrega la lista estructurada ``ofertas``.
    """
    soup = BeautifulSoup(html, "html.parser")
    producto = None
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            producto = buscar_producto(json.loads(script.string or script.get_text()))
        except (json.JSONDecodeError, TypeError):
            continue
        if producto:
            break

    ofertas = extraer_ofertas(producto)
    if not any(o["precio"] is not None for o in ofertas):
        ofertas = ofertas or _precios_visibles(soup)

    precios: list[str] = []
    estados: list[str] = []
    for o in ofertas:
        if o["precio"] is not None:
            texto = str(int(o["precio"])) if float(o["precio"]).is_integer() else str(o["precio"])
            if texto not in precios:
                precios.append(texto)
        if o["disponibilidad"] and o["disponibilidad"] not in estados:
            estados.append(o["disponibilidad"])

    calificacion = None
    if producto:
        valoracion = producto.get("aggregateRating", {})
        if isinstance(valoracion, dict):
            calificacion = valoracion.get("ratingValue")

    return {
        "nombre": _nombre(soup, producto),
        "precio": " | ".join(precios) or None,
        "disponibilidad": " | ".join(estados) or None,
        "calificacion": calificacion,
        "url_producto": url,
        "metodo": metodo,
        "ofertas": ofertas,
    }
