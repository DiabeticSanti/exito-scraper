"""Spider de Scrapy (método 3). Reutiliza el parser del paquete exito_scraper.

Ejecutar:  scrapy runspider scrapy_exito.py -O resultado_scrapy.json
"""

import scrapy

from exito_scraper.parser import URL_PRODUCTO, extraer_datos


class ExitoSpider(scrapy.Spider):
    name = "exito_producto"
    start_urls = [URL_PRODUCTO]
    custom_settings = {
        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        ),
        "DOWNLOAD_TIMEOUT": 30,
        "LOG_LEVEL": "WARNING",
        "ROBOTSTXT_OBEY": True,
    }

    def parse(self, response):
        registro = extraer_datos(response.text, "Scrapy", response.url)
        registro["codigo_respuesta"] = response.status
        yield registro
