"""Genera el sitio estático (index.html) que despliega el workflow de CD."""

from __future__ import annotations

from html import escape
from pathlib import Path

from .almacen import leer

PLANTILLA = """<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Monitor Éxito · Razer DeathAdder Essential</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:860px;margin:2rem auto;
padding:0 1rem;line-height:1.5}}
table{{border-collapse:collapse;width:100%;display:block;overflow-x:auto}}
th,td{{border:1px solid #8884;padding:.4rem .6rem;text-align:left;
white-space:nowrap}}
.estado{{font-size:1.4rem;font-weight:600}}
</style></head><body>
<h1>Monitor de precio · Razer DeathAdder Essential</h1>
{resumen}
<h2>Historial</h2>
{tabla}
<p><small>Generado automáticamente por GitHub Actions.
Proyecto académico, IU Digital de Antioquia.</small></p>
</body></html>
"""


def _resumen(ultima: dict | None) -> str:
    if not ultima:
        return "<p>Aún no hay mediciones registradas.</p>"
    disponible = "Disponible" if ultima["disponible"] == "True" else "Sin inventario"
    precio = ultima["precio_referencia"] or "sin precio válido"
    return (
        f'<p class="estado">{escape(disponible)} · COP {escape(precio)}</p>'
        f"<p>Última medición: {escape(ultima['fecha_utc'])} ({escape(ultima['metodo'])}).</p>"
    )


def generar_sitio(csv_historial: str | Path, carpeta_salida: str | Path) -> Path:
    filas = leer(csv_historial)
    encabezados = ["fecha_utc", "precio_referencia", "disponible", "ofertas_validas", "metodo"]
    cabecera = "".join(f"<th>{escape(h)}</th>" for h in encabezados)
    cuerpo = "".join(
        "<tr>" + "".join(f"<td>{escape(str(f[h]))}</td>" for h in encabezados) + "</tr>"
        for f in reversed(filas)
    )
    tabla = f"<table><thead><tr>{cabecera}</tr></thead><tbody>{cuerpo}</tbody></table>"
    salida = Path(carpeta_salida)
    salida.mkdir(parents=True, exist_ok=True)
    destino = salida / "index.html"
    destino.write_text(
        PLANTILLA.format(resumen=_resumen(filas[-1] if filas else None), tabla=tabla),
        encoding="utf-8",
    )
    return destino
