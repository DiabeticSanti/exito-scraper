# exito-scraper

Monitor de precio y disponibilidad del **Mouse Razer Gaming Mouse DeathAdder Essential Right Handed**
publicado en la tienda en línea de Éxito (Colombia).

Proyecto de la asignatura *Programación para Análisis de Datos* (IU Digital de Antioquia).
Continúa la Evidencia de aprendizaje 1 (tres métodos de scraping: BeautifulSoup, Selenium y Scrapy)
y le agrega control de versiones con Git/GitHub y un flujo DevOps con GitHub Actions (CI/CD).

## Estructura

```
src/exito_scraper/   paquete (parser, limpieza, fetch, almacén CSV, reporte HTML, CLI)
scrapy_exito.py      spider de Scrapy (reutiliza el parser del paquete)
tests/               pruebas con pytest (sin red; usan un HTML de ejemplo)
data/historico.csv   historial de mediciones (lo actualiza el workflow programado)
.github/workflows/   ci.yml · cd.yml · scrape.yml
```

## Uso local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .

pytest --cov=exito_scraper          # pruebas
ruff check .                        # análisis estático

python -m exito_scraper --metodo requests --salida data/historico.csv
python -m exito_scraper --html-file tests/fixtures/producto_exito.html   # modo sin red
scrapy runspider scrapy_exito.py -O resultado_scrapy.json
```

## Flujo DevOps

| Workflow | Disparador | Qué hace |
|---|---|---|
| `ci.yml` | push y pull request | Lint con Ruff + pruebas con pytest en Python 3.11 y 3.12 + cobertura |
| `cd.yml` | push a `main` y tags `v*` | Reutiliza `ci.yml`; si pasa, genera el sitio con el último dato y lo despliega en GitHub Pages. Con tag `vX.Y.Z` además construye el paquete y publica un Release |
| `scrape.yml` | diario (cron) y manual | Ejecuta el scraper y guarda una nueva fila en `data/historico.csv` mediante commit |

### Configuración única en GitHub
1. *Settings → Pages → Build and deployment → Source: **GitHub Actions***.
2. *Settings → Actions → General → Workflow permissions: **Read and write***.
3. Proteger `main` (*Settings → Branches*): exigir pull request y el check `CI`.

### Flujo de ramas
`main` (estable, desplegada) ← `develop` (integración) ← `feature/*`, `fix/*`, `docs/*`.
Commits al estilo *Conventional Commits* (`feat:`, `fix:`, `test:`, `ci:`, `docs:`).
Detalles en [CONTRIBUTING.md](CONTRIBUTING.md).

## Limitaciones
- Depende de la estructura JSON-LD del sitio; si Éxito la cambia, las pruebas con HTML de ejemplo seguirán
  pasando pero la ejecución real fallará (para eso existe el workflow programado).
- Los runners de GitHub pueden ser bloqueados por el sitio; en ese caso el paso de scraping falla sin romper el despliegue.
- Uso académico y de baja frecuencia (1 petición diaria); respetar términos de uso y `robots.txt`.
