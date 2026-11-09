"""Limpieza: descarta ofertas con precio 0 y resume el estado del producto.

En la Evidencia 1 se observó un precio 0 junto con un estado OutOfStock. Aquí se aplica la
regla de limpieza propuesta: una oferta es válida solo si su precio es mayor que cero.
"""

from __future__ import annotations


def ofertas_validas(ofertas: list[dict]) -> list[dict]:
    return [o for o in ofertas if o.get("precio") is not None and o["precio"] > 0]


def resumir(datos: dict) -> dict:
    """Reduce el registro crudo a una fila analizable."""
    todas = datos.get("ofertas", [])
    validas = ofertas_validas(todas)
    en_stock = [o for o in validas if o.get("disponibilidad") == "InStock"]
    candidatas = en_stock or validas
    return {
        "nombre": datos.get("nombre"),
        "precio_referencia": min(o["precio"] for o in candidatas) if candidatas else None,
        "disponible": bool(en_stock),
        "ofertas_validas": len(validas),
        "ofertas_totales": len(todas),
        "calificacion": datos.get("calificacion"),
        "metodo": datos.get("metodo"),
        "url_producto": datos.get("url_producto"),
    }
