# Anwendungstests

Diese Tests pruefen die laufende Anwendung ueber REST und GraphQL. Fuer die
REST-Tests muessen die Anwendung und ihre Dienste erreichbar sein; die Fixtures
pruefen die Readiness und laden die Testdaten neu.

```powershell
uv run pytest tests/integration
uv run pytest tests/integration/rest
uv run pytest tests/integration/graphql
```

Die gemeinsamen Hilfsmodule `common_test.py` und `constants.py` sind ueber den
in `pyproject.toml` konfigurierten Python-Suchpfad auch bei einzeln gestarteten
Testdateien erreichbar. Das TLS-Zertifikat wird relativ zu `constants.py` geladen.

Die isolierten Tests fuer Postgres, Mailpit und Keycloak liegen unter
[`tests/testcontainers`](../testcontainers/README.md). Ein Aufruf von `uv run pytest`
ohne Pfadangabe sammelt beide Testordner ein.
