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
uv run testcontainers -k keycloak
```

Der direkte pytest-Aufruf ist ebenfalls moeglich:

```powershell
uv run pytest tests/testcontainers/keycloak_test.py
uv run pytest tests/testcontainers
```

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
