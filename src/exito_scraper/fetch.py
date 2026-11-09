"""Descarga del HTML con Requests (estático) o Selenium (renderizado)."""

from __future__ import annotations

import time

import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    )
}


def obtener_html_requests(url: str, timeout: int = 25) -> str:
    respuesta = requests.get(url, headers=HEADERS, timeout=timeout)
    respuesta.raise_for_status()
    return respuesta.text


def obtener_html_selenium(url: str, espera: int = 5) -> str:  # pragma: no cover (requiere Chrome)
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait

    opciones = Options()
    for arg in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage",
                "--window-size=1365,900"):
        opciones.add_argument(arg)
    driver = webdriver.Chrome(options=opciones)
    try:
        driver.get(url)
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(espera)
        return driver.page_source
    finally:
        driver.quit()
