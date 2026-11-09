from pathlib import Path

import pytest

pytest.importorskip("scrapy")

from scrapy.http import HtmlResponse  # noqa: E402
from scrapy_exito import ExitoSpider  # noqa: E402

FIXTURE = Path(__file__).parent / "fixtures" / "producto_exito.html"


def test_spider_produce_mismo_resultado_que_los_otros_metodos():
    cuerpo = FIXTURE.read_bytes()
    respuesta = HtmlResponse(url="https://ejemplo.test/p", body=cuerpo, encoding="utf-8")
    registros = list(ExitoSpider().parse(respuesta))
    assert len(registros) == 1
    r = registros[0]
    assert r["metodo"] == "Scrapy" and r["codigo_respuesta"] == 200
    assert r["precio"] == "89899 | 89900 | 0"
    assert r["disponibilidad"] == "InStock | OutOfStock"
