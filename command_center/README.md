# ARVO Command Center MVP

Lokale, gemeinsam nutzbare Arbeitsoberfläche für Giuliano und Robin: Tech Pack zuerst, kompakte Aufgaben und Hersteller-/Mustertracking. Keine KI-API, kein Abo, kein Deployment. Instagram-/Mockup-Bibliothek ist bewusst noch nicht implementiert.

## Installation und Start

Voraussetzungen: Python 3.9+ mit `venv` und `pip`, moderner Browser. Funktioniert ohne Node.js im Betrieb. Geprüft auf diesem Mac mit Python 3.12 und Chromium; kein vollständiger Test aller Apple-Silicon-/Browser-Versionen.

Im Repository-Root, auf dem MVP-Branch:

```sh
git switch codex/arvo-command-center-mvp
python3 -m venv .venv
.venv/bin/python -m pip install -r command_center/requirements.txt
.venv/bin/python -m command_center.server
```

Im Browser [http://127.0.0.1:8765](http://127.0.0.1:8765) öffnen. Beenden mit Ctrl-C. ReportLab ist die einzige direkte Laufzeitabhängigkeit (freie PDF-Bibliothek, BSD-Lizenz; transitive Abhängigkeiten werden durch pip installiert). Ohne ReportLab funktionieren Editor und JSON, der PDF-Endpunkt erklärt die fehlende Installation. Bei belegtem Port `--port 8766` verwenden.

Die Datenbank wird beim ersten Start unter `command_center/private/workspace.sqlite3` angelegt. Das Verzeichnis wird von Git ignoriert. Ein anderer Speicherort ist mit `--data-dir /absoluter/privater/pfad` möglich; außerhalb des Repos selbst für Git-Ausschluss sorgen. Nur Programmcode und öffentliche Ausgangssnapshots gehören in dieses öffentliche Repository. Keine privaten Angebote, E-Mails, Zugangsdaten oder echten Arbeitsdaten committen.

## Bedienung

1. **Tech Pack:** Produktstand, Quellen, Verarbeitung und Zeichnungsverweise ergänzen. A–S aus dem externen v0.2-Kontext bleiben erhalten. Die Originaldatei, Originaldefinitionen und Zeichnungen liegen nicht im Repository und wurden nicht rekonstruiert. Namen/Methoden aus dem Original übernehmen oder bewusst zuordnen. Die Auswahl bietet eigene, ausdrücklich vorgeschlagene Messmethoden; sie bestimmt keine A–S-Zuordnung automatisch. Beispielsweise muss bei der Brustweite die tatsächliche Messhöhe noch im Text festgelegt werden.
2. Maße S/M/L in **cm** eintragen. Nicht verfügbare Größen leer lassen. Referenz-/Ziel-/Waschzustand, Datum und Foto-/Dateibeleg je Zeile dokumentieren. Toleranz minus/plus sind **positive Abweichungsbeträge**. `0` ist eine echte Eingabe, leer ist `null`/OFFEN. Keine automatischen Werte oder Gradierung.
3. Produktionsstoff getrennt von UNIQLO-Referenz und LEMUTA-Kandidat pflegen. GSM, Mischung und Belege bleiben leer, bis sie vorliegen. Mehrdeutige oder widersprüchliche Angaben nicht still zusammenführen.
4. **Änderungen speichern** schreibt den gesamten Stand transaktional. Kein Autosave. Nach Neustart bleibt der gespeicherte Stand erhalten. Aufgaben können nach Person/Status gefiltert werden; erledigte Schritte bleiben sichtbar. Neue Aufgaben/Hersteller mit identischem Titel/Namen werden im Editor abgefangen. Keine neuen GitHub-Issues oder externen Nachrichten werden erzeugt. Muster dokumentieren Eingang und Prüfung, ohne Bestellung oder Produktionsfreigabe auszulösen.
5. **PDF exportieren** speichert zunächst offene Eingaben und exportiert den gespeicherten Tech-Pack-Stand mit Revision, Quellen, OFFEN-Hinweisen und dauerhaftem Entwurfsvermerk. Bei Speicherkonflikt wird kein PDF heruntergeladen. Aufgaben, Angebote und Musterjournal werden nicht in das Lieferanten-Tech-Pack aufgenommen. PDF unterstützt die übliche deutsche/lateinische Schrift; beliebige Emojis und nichtlateinische Zeichen sind nicht abgedeckt.
6. **JSON-Sicherung** lädt den aktuellen Editorstand herunter, einschließlich ungespeicherter Eingaben. **JSON laden** prüft Format/Inhalte serverseitig und lädt sie nach Bestätigung in den Editor; erst Speichern ersetzt die Datenbank. Die Revision der importierten Datei wird nicht als Schreibberechtigung verwendet. Keine automatische Zusammenführung. Lokale Sicherungen privat aufbewahren. Für ein vollständiges Datenbankbackup Server stoppen und die SQLite-Datei kopieren; Wiederherstellung nur bei gestopptem Server.

## Gemeinsam arbeiten, ohne neuen Dienst

Eine **einzige laufende Serverinstanz** ist die gemeinsame Datenquelle. Zwei Browserfenster am selben Mac nutzen denselben Stand. Zwei getrennt gestartete Installationen synchronisieren sich **nicht**.

Für Robins anderen Rechner kann ein bereits eingerichteter und autorisierter SSH-Zugang zum Host genutzt werden:

```sh
ssh -N -L 8766:127.0.0.1:8765 BENUTZER@ARVO-HOST
```

Robin öffnet danach lokal `http://127.0.0.1:8766`. Der Host-Mac und der Server müssen laufen; der SSH-Zugang muss separat eingerichtet sein. Diese Umsetzung aktiviert weder macOS-Fernzugriff noch VPN/Portfreigaben. Keine öffentliche HTTP-Freigabe vornehmen: Der MVP besitzt keinen Login, keine getrennten Benutzerrechte und keine verschlüsselte Datenbank. Er ist auf Loopback gebunden; der SSH-Tunnel übernimmt den authentifizierten Transport. Lokale Programme/Benutzer mit Zugriff auf den Rechner können die App lesen und ändern.

**Parallelzugriff:** Jeder Stand hat eine Revision. Speichert Robin nach Giulianos Änderung einen älteren Stand, erhält er HTTP 409. Seine Eingaben bleiben im Browser. Erst JSON sichern, gespeicherten Stand neu laden und eigene Änderungen manuell abgleichen. Kein stilles Überschreiben. Es gibt kein Live-Polling; vor Änderungen bewusst neu laden. Alle editieren denselben Workspace, die Personenauswahl ist eine Zuständigkeit und keine Anmeldung.

## Quellen und führende Daten

- Ausgangskontext: [ARVO-STATUS](../ARVO-STATUS.md), datierter Nutzerbericht vom 10.11.2026, nicht unabhängig verifiziert. Das Startmodell übernimmt sieben vorhandene Aufgaben einmalig; zwei bleiben DONE. Das Referenzpaket wird nicht erneut als offene Aufgabe angelegt. Wiederholter Serverstart ergänzt keine neuen Aufgaben.
- Herstellerstatus: [bestehender Vergleich](../ocs/supplier-comparison.md), inklusive historischer Widersprüche. Details und historische Preise bleiben dort; keine automatischen Live-Angebote. Im Editor leere Kostenfelder sind unbekannt, nicht kostenfrei.
- Nach Initialisierung ist **die private Datenbank** führend für die Arbeit in der App. Markdown-Dateien bleiben historische Quellsnapshots. Kein automatischer Rückabgleich mit Markdown, GitHub Issues/Projects, AppFlowy, Shopify oder E-Mail. Spätere Snapshot-Änderungen werden nicht unbemerkt über persönliche Änderungen geschrieben.
- Eigene Modellversion `schemaVersion: 1`, feste Größen S/M/L, feste Codes A–S, nullable Zahlen, Quellen/Notizen, stabile IDs, OPEN/WAITING/DONE/DECIDED. Dateipfade sind Textverweise; es gibt keine Upload-/Bildvorschau und keinen Zugriff auf beliebige Dateien.

## Prüfung des fremden Schema-Repos

Am 11.11.2026 tatsächlich gelesen: [Repository-Inhalt](https://github.com/kobo-labs-open-source/fashion-tech-pack-schema), [README](https://github.com/kobo-labs-open-source/fashion-tech-pack-schema/blob/main/README.md), [LICENSE](https://github.com/kobo-labs-open-source/fashion-tech-pack-schema/blob/main/LICENSE), [Root-Schema](https://github.com/kobo-labs-open-source/fashion-tech-pack-schema/blob/main/schema/tech-pack.schema.json) und [Measurements-Schema](https://github.com/kobo-labs-open-source/fashion-tech-pack-schema/blob/main/schema/measurements.schema.json).

Das Repo bietet JSON Schema 2020-12 und Beispiele, keine fertige Tech-Pack-Anwendung oder PDF-Oberfläche. Die LICENSE ist MIT (Lizenzdatei Blob `078f404bac511225a1438b1663ce3331eba251ad`). Root verlangt style, colorways (mindestens eins), billOfMaterials (mindestens eins), measurements; konkrete Messwerte sind Zahlen, nicht `null`. Das Measurements-Schema beschreibt Größenbindung in Text, erzwingt sie aber nicht durch eine dynamische Referenz. Das Beispiel enthält fremde Produktwerte, die nicht als ARVO-Werte dienen dürfen.

**Entscheidung:** keine Code-/Schema-/Beispielübernahme, keine npm-Abhängigkeit und kein behaupteter Standard-konformer Export. Ein eigenes kleines Entwurfsmodell bildet die offenen Felder, Belege und v0.2-Lücken direkt ab. MIT würde Übernahme mit Erhalt des Copyright-/Lizenzhinweises erlauben; da nichts kopiert wurde, wird das fremde Repo nicht als Abhängigkeit vendort. Die Definitionen im Editor sind eigene Vorschläge. Eine spätere ausdrückliche Exportkonvertierung kann geprüft werden.

## Tests

```sh
.venv/bin/python -m pip install -r command_center/requirements-dev.txt
.venv/bin/python -m unittest discover -s command_center/tests -v
```

Pypdf ist nur für die Tests erforderlich. Die Tests prüfen offene Werte, ungültige Zahlen/Datumswerte/IDs, A–S-Erhalt, dauerhaftes Speichern, wiederholte Initialisierung, Konflikte, HTTP-Origin-/CSRF-/Host-Schutz, JSON-Export und PDF-Inhalte einschließlich `0`, langer Texte und Entwurfsvermerk.

Optionaler Browser-Test mit Node.js und Playwright, **nur gegen einen leeren Testdatenordner** (schreibt ausdrücklich fiktive TESTDATEN):

```sh
.venv/bin/python -m command_center.server --data-dir /tmp/arvo-browser-test --port 8765
# In anderem Terminal:
npm install --no-save --prefix /tmp/arvo-browser playwright
/tmp/arvo-browser/node_modules/.bin/playwright install chromium
NODE_PATH=/tmp/arvo-browser/node_modules node command_center/tests/browser.cjs
```

Zum Wiederholen einen neuen leeren Testdatenordner wählen. Testausgaben unter `command_center/test-output/` sind ignoriert. Der Browser-Test prüft Definitionseingabe, Speicherung/Reload, Konflikterhalt, JSON-Sicherung, Aufgabenfilter, Musterpflege, PDF-Download und mobile Breite. Installation und Laufzeit greifen auf keine bezahlte API zu; pip/npm-Downloads benötigen Internet.

## Grenzen und nächster sinnvoller Schritt

Kein fertiges produktionsreifes Tech Pack: Original v0.2, Zeichnungen, Maße, Toleranzen, finale Stoffdaten, Verarbeitung und gemeinsame fachliche Freigabe fehlen. Vollständigkeit ist keine Richtigkeitsprüfung. Kein Freigabeknopf, keine Bestellung, kein automatischer Follow-up oder Instagram-Post. Keine automatische Cloud-Bereitstellung. Die gemeinsame Nutzung über zwei reale Rechner/SSH wurde hier nicht getestet; getestet werden parallele Browser auf derselben Instanz. Nächster fachlicher Schritt ist die Übernahme der echten v0.2-Definitionen und Robins realer Messungen.
