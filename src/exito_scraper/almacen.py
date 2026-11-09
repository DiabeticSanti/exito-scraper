"""Persistencia del historial de mediciones en un CSV."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

CAMPOS = [
    "fecha_utc", "nombre", "precio_referencia", "disponible", "ofertas_validas",
    "ofertas_totales", "calificacion", "metodo", "url_producto",
]


def guardar(resumen: dict, ruta: str | Path, ahora: datetime | None = None) -> Path:
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    existe = ruta.exists() and ruta.stat().st_size > 0
    fila = {"fecha_utc": (ahora or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")}
    fila.update({k: resumen.get(k) for k in CAMPOS if k != "fecha_utc"})
    with ruta.open("a", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=CAMPOS)
        if not existe:
            escritor.writeheader()
        escritor.writerow(fila)
    return ruta


def leer(ruta: str | Path) -> list[dict]:
    ruta = Path(ruta)
    if not ruta.exists():
        return []
    with ruta.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
