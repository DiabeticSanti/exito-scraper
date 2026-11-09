# Guía de contribución

## Ramas
- `main`: siempre desplegable. Solo se actualiza por pull request desde `develop` (o `fix/*` urgentes).
- `develop`: integración.
- `feature/<tema>`, `fix/<tema>`, `docs/<tema>`: trabajo diario, salen de `develop`.

## Ciclo
```bash
git switch develop && git pull
git switch -c feature/mi-cambio
pytest && ruff check .
git add -A && git commit -m "feat: descripción corta en imperativo"
git push -u origin feature/mi-cambio
# abrir Pull Request hacia develop; el workflow CI debe quedar en verde
```

## Mensajes de commit
`feat:` nueva funcionalidad · `fix:` corrección · `test:` pruebas · `ci:` workflows · `docs:` documentación · `refactor:` sin cambio funcional.

## Versionado
Versionado semántico. Para publicar: `git tag -a v0.1.0 -m "Primera versión" && git push origin v0.1.0`.
