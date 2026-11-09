from pathlib import Path

import pytest

from exito_scraper.parser import a_numero, buscar_producto, extraer_datos

FIXTURE = Path(__file__).parent / "fixtures" / "producto_exito.html"


@pytest.fixture
def html() -> str:
    return FIXTURE.read_text(encoding="utf-8")


def test_extrae_nombre(html):
    datos = extraer_datos(html, "BeautifulSoup")
    assert datos["nombre"] == "Mouse Razer Gaming Mouse Deathadder Essential Right Handed"


def test_extrae_precios_y_disponibilidad_como_en_evidencia_1(html):
    datos = extraer_datos(html, "BeautifulSoup")
    assert datos["precio"] == "89899 | 89900 | 0"
    assert datos["disponibilidad"] == "InStock | OutOfStock"


def test_calificacion_ausente_es_none(html):
    assert extraer_datos(html, "BeautifulSoup")["calificacion"] is None


def test_conserva_ofertas_estructuradas(html):
    ofertas = extraer_datos(html, "BeautifulSoup")["ofertas"]
    assert len(ofertas) == 3
    assert ofertas[2] == {"precio": 0.0, "disponibilidad": "OutOfStock"}


def test_registra_metodo_y_url(html):
    datos = extraer_datos(html, "Selenium", url="https://ejemplo.test/p")
    assert datos["metodo"] == "Selenium"
    assert datos["url_producto"] == "https://ejemplo.test/p"


def test_producto_dentro_de_graph():
    objeto = {"@graph": [{"@type": "WebSite"}, {"@type": ["Product"], "name": "X"}]}
    assert buscar_producto(objeto)["name"] == "X"


def test_respaldo_h1_y_precio_visible_cuando_no_hay_json_ld():
    html = (
        '<html><body><h1>Teclado</h1>'
        '<span class="product-price">$ 120.500</span></body></html>'
    )
    datos = extraer_datos(html, "BeautifulSoup")
    assert datos["nombre"] == "Teclado"
    assert datos["precio"] == "120500"
    assert datos["disponibilidad"] is None


def test_json_ld_invalido_no_rompe():
    html = '<script type="application/ld+json">{no es json</script><h1>Algo</h1>'
    datos = extraer_datos(html, "BeautifulSoup")
    assert datos["nombre"] == "Algo"
    assert datos["ofertas"] == []


def test_calificacion_presente():
    html = (
        '<script type="application/ld+json">{"@type":"Product","name":"P",'
        '"aggregateRating":{"ratingValue":4.5},"offers":{"price":"100","availability":'
        '"https://schema.org/InStock"}}</script>'
    )
    datos = extraer_datos(html, "BeautifulSoup")
    assert datos["calificacion"] == 4.5
    assert datos["precio"] == "100"


@pytest.mark.parametrize(
    "entrada, esperado",
    [(89900, 89900.0), ("89899", 89899.0), ("$ 89.900", 89900.0), ("$ 89.900,00", 89900.0),
     (None, None), ("abc", None), (True, None)],
)
def test_a_numero(entrada, esperado):
    assert a_numero(entrada) == esperado
