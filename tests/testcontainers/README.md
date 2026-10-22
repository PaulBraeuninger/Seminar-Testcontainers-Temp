# Tests mit Testcontainers

Voraussetzungen: installierte Projektabhaengigkeiten (`uv sync`) und eine laufende
Docker-Engine fuer Linux-Container. Die Fixtures starten und entfernen die
Container automatisch; Host-Ports werden dynamisch vergeben.

```powershell
uv run testcontainers
```

Dieser Projektbefehl fuehrt alle Tests unter `tests/testcontainers` aus und gibt
den Exit-Code von pytest zurueck. Zusaetzliche pytest-Argumente werden durchgereicht:

```powershell
uv run testcontainers -v
uv run testcontainers --collect-only
uv run testcontainers -m keycloak
```

Der direkte pytest-Aufruf ist ebenfalls moeglich:

```powershell
uv run pytest tests/testcontainers/keycloak_test.py
uv run pytest tests/testcontainers
```

## Auswahl mit pytest-Markern

Die Marker `postgres`, `keycloak` und `mailpit` kennzeichnen die benoetigten
Testcontainer. `member` kennzeichnet Tests der Mitgliederverwaltung, `security`
Tests der Authentifizierung und Zugriffsrechte. Marker koennen kombiniert werden:

```powershell
uv run testcontainers -m "postgres and not workflow"
uv run testcontainers -m "keycloak and member"
uv run testcontainers -m security
uv run pytest -m member
```

Die Service-Marker werden nur bei tatsaechlicher Container-Abhaengigkeit gesetzt.
Die Tests fehlerhafter Authorization-Header tragen deshalb nur `security` und
laufen ohne Keycloak-Container. Die Mitgliedsrechte-Tests benoetigen Keycloak,
aber weder PostgreSQL noch Mailpit, weil diese Abhaengigkeiten ersetzt sind.

`workflow` ist fuer kuenftige vollstaendige Geschaeftsablaeufe ueber die API
registriert; aktuell gibt es noch keine solchen Tests. Diese erhalten zusaetzlich
alle benoetigten Service-Marker. Die drei CI-Service-Jobs waehlen ihren jeweiligen
Marker mit `and not workflow`; Tests ohne Container laufen einmal im Keycloak-Job.
Kuenftige Workflow-Tests benoetigen einen eigenen CI-Job.

Alle Marker sind in `pyproject.toml` registriert. `--strict-markers` verhindert,
dass Tippfehler in Markern unbemerkt bleiben.

Die Keycloak-Fixture verwendet das oeffentliche Image
`quay.io/keycloak/keycloak:26.5.5` und importiert
`resources/library-test-realm.json`. Der Realm `library-test` enthaelt den
vertraulichen Client `python-client` und zwei Benutzer: `admin` mit der Client-Rolle
`admin` und `member` mit der Client-Rolle `patient`. Passwort und Client-Secret in
dieser Datei sind ausschliesslich synthetische Testdaten. Fuer den zum Projekt
passenden Login mit Benutzername und Passwort sind Direct Access Grants aktiviert.

`keycloak_test.py` prueft 25 Testfaelle:

- OpenID-Connect-Discovery mit Issuer, Token-Endpunkt und JWKS-Endpunkt.
- Login fuer beide Benutzer mit Access- und Refresh-Token, kryptografischer
  JWT-Pruefung, Benutzerattributen und Client-Rollen.
- Ablehnung eines falschen Passworts und eines unbekannten Benutzers.
- Logout mit anschliessender Introspektion des ungueltigen Refresh-Tokens.
- Verarbeitung gueltiger Bearer-Tokens durch den echten `TokenService`, auch bei
  unterschiedlicher Gross-/Kleinschreibung des Bearer-Schemas.
- Ablehnung fehlender und fehlerhafter Authorization-Header.
- Ablehnung manipulierter Benutzer- und Rollen-Claims bei unveraenderter Signatur.
- Ablehnung abgelaufener, korrekt signierter Tokens. Dafuer wird nur die Uhr der
  JWT-Pruefung ueber das Ablaufdatum und die Zeittoleranz hinaus vorgestellt;
  die Tests muessen nicht auf den Token-Ablauf warten.
- Rollenpruefung durch `RolesRequired`: erlaubte Zugriffe, 403 bei fehlender Rolle
  und alternative Rollen (`ADMIN` oder `PATIENT`).
- Zugriffskontrolle durch `MemberService`: Admins duerfen fremde Mitgliedsdaten
  lesen, Mitglieder ihre eigenen; der Zugriff auf fremde Daten wird abgelehnt.

Die Service-Tests lesen wie die Anwendung die lokale Konfiguration aus
`src/library/config/resources/app.toml`. Der Keycloak-Client wird anschliessend
auf den Testcontainer gesetzt. Die Anwendung und ihre Service-Singletons werden
erst bei Bedarf geladen, damit ein Service-Import keine Verbindung zum regulaeren
Keycloak aufbaut. Fuer die Tests der Mitgliedsrechte sind Repository und
Datenbanksession durch Testdoubles ersetzt; `MemberService`, `TokenService`,
`RolesRequired` und die JWT-Signaturpruefung werden tatsaechlich ausgefuehrt.
Diese Tests pruefen die Sicherheitslogik ohne eine laufende Anwendung oder Datenbank.

Weitere moegliche Tests sind Benutzer anlegen/suchen/aendern/loeschen ueber die
Admin-API, Rollen zuweisen, falsche Client-Secrets ablehnen sowie Token-Widerruf,
deaktivierte Benutzer und Browser-Login mit Authorization Code und PKCE.
Tests der vollstaendigen REST-Verarbeitung einschliesslich Exception-Handlern und
Datenbankzugriff bleiben Aufgabe der REST-Integrationstests.

Referenzen: [Keycloak im Container](https://www.keycloak.org/server/containers)
und [OpenID-Connect-Endpunkte](https://www.keycloak.org/securing-apps/oidc-layers).
