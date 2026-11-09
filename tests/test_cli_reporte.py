import json
from pathlib import Path

import requests

from exito_scraper import almacen, cli, fetch
from exito_scraper.limpieza import resumir
from exito_scraper.parser import extraer_datos
from exito_scraper.reporte import generar_sitio

FIXTURE = Path(__file__).parent / "fixtures" / "producto_exito.html"


def test_cli_modo_archivo_imprime_resumen(capsys, tmp_path):
    salida = tmp_path / "h.csv"
    codigo = cli.main(["--html-file", str(FIXTURE), "--salida", str(salida)])
    assert codigo == 0
    impreso = json.loads(capsys.readouterr().out)
    assert impreso["precio_referencia"] == 89899.0
    assert len(almacen.leer(salida)) == 1


def test_cli_error_de_red_devuelve_1(monkeypatch, capsys):
    def falla(url, timeout=25):
        raise requests.ConnectionError("sin red")

    monkeypatch.setattr(cli, "obtener_html_requests", falla)
    assert cli.main([]) == 1
    assert "No fue posible" in capsys.readouterr().err


def test_cli_pagina_sin_producto_devuelve_2(monkeypatch):
    monkeypatch.setattr(cli, "obtener_html_requests", lambda url: "<html></html>")
    assert cli.main([]) == 2


def test_fetch_requests_envia_user_agent(monkeypatch):
    capturado = {}

    class Resp:
        text = "<html>ok</html>"

        def raise_for_status(self):
            pass

    def falso_get(url, headers, timeout):
        capturado.update(headers=headers, timeout=timeout)
        return Resp()

    monkeypatch.setattr(fetch.requests, "get", falso_get)
    assert fetch.obtener_html_requests("https://x.test") == "<html>ok</html>"
    assert "Mozilla" in capturado["headers"]["User-Agent"] and capturado["timeout"] == 25


def test_generar_sitio_con_datos(tmp_path):
    csv_ = tmp_path / "h.csv"
    r = resumir(extraer_datos(FIXTURE.read_text(encoding="utf-8"), "BeautifulSoup"))
    almacen.guardar(r, csv_)
    index = generar_sitio(csv_, tmp_path / "site")
    contenido = index.read_text(encoding="utf-8")
    assert "Disponible" in contenido and "89899.0" in contenido


def test_generar_sitio_sin_datos(tmp_path):
    index = generar_sitio(tmp_path / "vacio.csv", tmp_path / "site")
    assert "Aún no hay mediciones" in index.read_text(encoding="utf-8")


def test_generar_sitio_escapa_html(tmp_path):
    csv_ = tmp_path / "h.csv"
    almacen.guardar({"nombre": "x", "metodo": "<script>alert(1)</script>",
                     "disponible": True, "precio_referencia": 1}, csv_)
    contenido = generar_sitio(csv_, tmp_path / "s").read_text(encoding="utf-8")
    assert "<script>alert(1)" not in contenido
