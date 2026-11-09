from datetime import datetime, timezone
from pathlib import Path

from exito_scraper import almacen
from exito_scraper.limpieza import ofertas_validas, resumir
from exito_scraper.parser import extraer_datos

FIXTURE = Path(__file__).parent / "fixtures" / "producto_exito.html"


def _datos():
    return extraer_datos(FIXTURE.read_text(encoding="utf-8"), "BeautifulSoup")


def test_descarta_precio_cero():
    validas = ofertas_validas(_datos()["ofertas"])
    assert [o["precio"] for o in validas] == [89899.0, 89900.0]


def test_resumen_usa_precio_minimo_en_stock():
    r = resumir(_datos())
    assert r["precio_referencia"] == 89899.0
    assert r["disponible"] is True
    assert (r["ofertas_validas"], r["ofertas_totales"]) == (2, 3)


def test_resumen_sin_ofertas():
    r = resumir({"nombre": "X", "ofertas": []})
    assert r["precio_referencia"] is None and r["disponible"] is False


def test_resumen_solo_agotado_usa_precio_valido():
    datos = {"ofertas": [{"precio": 50.0, "disponibilidad": "OutOfStock"}]}
    r = resumir(datos)
    assert r["precio_referencia"] == 50.0 and r["disponible"] is False


def test_guardar_crea_encabezado_y_agrega_filas(tmp_path):
    ruta = tmp_path / "datos" / "h.csv"
    fecha = datetime(2026, 11, 9, 12, 0, tzinfo=timezone.utc)
    almacen.guardar(resumir(_datos()), ruta, ahora=fecha)
    almacen.guardar(resumir(_datos()), ruta, ahora=fecha)
    filas = almacen.leer(ruta)
    assert len(filas) == 2
    assert filas[0]["fecha_utc"] == "2026-11-09T12:00:00Z"
    assert filas[0]["precio_referencia"] == "89899.0"
    assert ruta.read_text(encoding="utf-8").count("fecha_utc") == 1


def test_leer_archivo_inexistente(tmp_path):
    assert almacen.leer(tmp_path / "no_existe.csv") == []
