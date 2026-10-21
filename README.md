# SWE-Python
This is the repo for the python task of the lecture "Software Engineering"

## Testcontainers-Tests

Mit laufender Docker-Engine alle Tests fuer Postgres, Mailpit und Keycloak ausfuehren:

```powershell
uv run testcontainers
```

Weitere pytest-Optionen koennen angehaengt werden, z.B. `uv run testcontainers -v`.
Details stehen in [tests/testcontainers/README.md](tests/testcontainers/README.md).
