# ARVO Command Center · Tech Pack V2.1

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

In dieser Sitzung läuft die geprüfte Anwendung auf [Port 8770](http://127.0.0.1:8770), da 8765 bereits von einem anderen lokalen Dienst belegt war. Dafür beim Neustart `--port 8770` anhängen; der Programmstandard bleibt 8765.

Die Datenbank wird beim ersten Start unter `command_center/private/workspace.sqlite3` angelegt. Das Verzeichnis wird von Git ignoriert. Ein anderer Speicherort ist mit `--data-dir /absoluter/privater/pfad` möglich; außerhalb des Repos selbst für Git-Ausschluss sorgen. Nur Programmcode und öffentliche Ausgangssnapshots gehören in dieses öffentliche Repository. Keine privaten Angebote, E-Mails, Zugangsdaten oder echten Arbeitsdaten committen.

## V2.1: Aufbau, Zeichnungen und Messbasis

Die bestehende Oberfläche und ihre Farben/Komponenten bleiben erhalten. Der Tech-Pack-Bereich folgt dieser Reihenfolge: **Product Overview → Technical Drawings → Measurement Table → Fabric & Construction → Branding & Labels**. Aufgaben, Hersteller und Muster werden nicht neu angelegt oder neu organisiert.

- **Cutoff:** eigene Front-/Back-/Side-Ansicht, A–S als erhaltene Originaldatensätze plus 24 neue `AT`-IDs, insgesamt 43 Zeilen. **Regular:** drei eigene Ansichten, 26 unabhängige `RF`-IDs einschließlich Ärmellänge und Ärmelöffnung. Keine automatische Übertragung von Maßen, Stoffen oder Labels zwischen Varianten.
- `AT01`/`RF01`: vertikale Körperlänge ab innerem, halsseitigem HPS. `02` und `03`: getrennte vordere/hintere Halslochtiefe als senkrechte Projektion ab HPS-Höhenniveau, keine Strecke entlang der Rundung. `04`: schräge Schulterstrecke.
- `10–16`: Brust, Unterbrust, Rippenbogen, Taillenübergang, engste Taille, Hüfte und fertiger unterer Saum. **Gesamtbreite des flachliegenden Kleidungsstücks**, weder Umfang noch einzelne Schnittteilbreite. Deshalb dieselbe ID vorne/hinten: eine Kontrolle, keine kopierten Messwerte. Unterschiedliche Vorder-/Rückenschnittteile erfordern einen gesonderten Schnittteilplan; sie sind nicht aus der Gesamtbreite ableitbar.
- `20–25`: eigene, pro Größe noch festzulegende HPS-Messhöhen für die ersten sechs Breitenstationen. Die Saumweite `16` wird direkt an der fertigen unteren Kante gemessen. Stationshöhen nicht aus SVG-Koordinaten ableiten. Fotos/Zustand und Stationsfestlegung dokumentieren.
- `30`: senkrechte Armausschnitttiefe HPS → Achsel-/Seitennahteckpunkt. `31`/`32`: getrennte vordere/hintere Kurvenmaße an der mit dem Hersteller abzustimmenden Naht-/Kantenlinie; reproduzierbare Flachkontrolle ohne Dehnen.
- `40`/`41`: vordere/hintere horizontale Armausschnittausladung in einer **standardisierten Seitenprojektion**. Gemeinsame vertikale Referenz durch unteren Achsel-/Seitennahteckpunkt; Messstation `43` als HPS-Abstand festlegen. Formkörper, Pose, Kameraebene und Skalierung dokumentieren. `42` misst die gesamte projizierte Breite an derselben Station, mit nach außen versetzten Maßpfeilen und Hilfslinien. Keine automatische Addition. Diese vier braunen Maße sind keine direkten Flachmaße; für die Schnittabnahme `30` sowie die getrennten Kurvenmaße `31`/`32` nutzen.
- Geschlossene Seitennaht bis zum durchgehenden unteren Saum; keine Schlitzgeometrie, keine Schlitzmaßlinie und keine neue Schlitzspezifikation im PDF.

**Interaktion:** Filter für alle/horizontale/vertikale Maße, Hals/Schulter, Brust/Armloch, Taille/Hüfte, Saum und ausgewählte ID. Linien (auch per Tab/Enter) und Tabellenzeilen wählen sich gegenseitig aus; „Zur Tabellenzeile“ springt zum Datensatz. Die zugehörige Definition wird unter den Zeichnungen angezeigt. Neue Zeichnungsdefinitionen sind an ihre IDs gebunden und gegen stilles Umdeuten validiert. Quelle/Zustand und Werte bleiben bearbeitbar. A–S sind weiterhin editierbar, werden aber ohne Originalbeleg keiner neuen Geometrie zugewiesen. Insbesondere wurden F–J nicht automatisch neu zugeordnet.

Care Label, Neck Label und Hang Tag besitzen eigene Vorschauen und Felder je Produkt. Die Wortmarke und die angefragten Claims sind Gestaltungsentwürfe; Mischung, Pflege, Herkunft, mm-Abmessungen, Material, Befestigung, Verarbeitung und Druckverfahren bleiben ohne Beleg offen. Keine frei erfundenen Pflegesymbole. S/M/L auf dem Neck-Label zeigen die Größenvarianten des Entwurfs, keine bestätigte Größeneinstufung.

**Technische Quelle:** `technical.py` enthält die verbindlichen neuen IDs/Definitionen. `drawings.py` erzeugt aus derselben primitiven Geometrie sowohl SVG als auch PDF-Vektoren. Pixel-/Zeichnungseinheiten sind niemals cm und treiben keine Werteberechnung an. Die schematischen Silhouetten sind kein maßstäblicher Schnitt und ändern ihre Form nicht automatisch bei einer Zahleneingabe.

## Bedienung

1. **Tech Pack:** Variante wählen, Produktstand und Quellen ergänzen. Erst die tatsächlichen Messhöhen und Messbasis festlegen, dann S/M/L erfassen. Die ursprüngliche v0.2-Datei und ihre Zeichnungen liegen weiterhin nicht vor. A–S samt vorhandenen Definitionen/Werten bleiben erhalten. Neue AT-/RF-Definitionen stammen aus der angefragten V2.1-Erweiterung und sind keine behauptete Rekonstruktion von v0.2.
2. Maße S/M/L in **cm** eintragen. Nicht verfügbare Größen leer lassen. Referenz-/Ziel-/Waschzustand, Datum und Foto-/Dateibeleg je Zeile dokumentieren. Toleranz minus/plus sind **positive Abweichungsbeträge**. `0` ist eine echte Eingabe, leer ist `null`/OFFEN. Keine automatischen Werte oder Gradierung.
3. Produktionsstoff getrennt von UNIQLO-Referenz und LEMUTA-Kandidat pflegen. GSM, Mischung und Belege bleiben leer, bis sie vorliegen. Mehrdeutige oder widersprüchliche Angaben nicht still zusammenführen.
4. **Änderungen speichern** schreibt den gesamten Stand transaktional. Kein Autosave. Nach Neustart bleibt der gespeicherte Stand erhalten. Aufgaben können nach Person/Status gefiltert werden; erledigte Schritte bleiben sichtbar. Neue Aufgaben/Hersteller mit identischem Titel/Namen werden im Editor abgefangen. Keine neuen GitHub-Issues oder externen Nachrichten werden erzeugt. Muster dokumentieren Eingang und Prüfung, ohne Bestellung oder Produktionsfreigabe auszulösen.
5. **PDF exportieren** speichert zunächst offene Eingaben und exportiert die aktuell gewählte, gespeicherte Variante mit Revision, Quellen, OFFEN-Hinweisen und dauerhaftem Entwurfsvermerk. Reihenfolge: Product Overview, Front View (Breiten + Detailseite), Back View (Breiten + Detailseite), Side View, Measurement Table, Fabric & Construction, Care Label, Neck Label, Hang Tag, offene Angaben/Versionshinweise. Die Detailseiten trennen horizontale und vertikale/weitere Maße zur besseren Lesbarkeit; ein UI-Filter lässt im PDF keine Daten weg. Bei Speicherkonflikt wird kein PDF heruntergeladen. Aufgaben, Angebote und Musterjournal werden nicht in das Lieferanten-Tech-Pack aufgenommen. PDF unterstützt die übliche deutsche/lateinische Schrift; beliebige Emojis und nichtlateinische Zeichen sind nicht abgedeckt.
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
- Eigene Modellversion `schemaVersion: 2`, getrennte Datensätze `techpack` (Cutoff) und `regularTechpack`, gespeicherte Auswahl `activeProduct`, feste Größen S/M/L, erhaltene Codes A–S plus eigene AT-/RF-IDs, nullable Zahlen, Quellen/Notizen, stabile IDs, OPEN/WAITING/DONE/DECIDED. Dateipfade sind Textverweise; es gibt keine Datei-Uploads oder externe Bildvorschau und keinen Zugriff auf beliebige Dateien.

## Bestehende Daten und Migration

Beim ersten Start mit einer Schema-1-Datenbank wird der Stand **additiv und transaktional** auf Schema 2 erweitert. Der vollständige ursprüngliche JSON-Text einschließlich Revision wird in der privaten SQLite-Tabelle `migration_backup` gesichert. A–S, Produktfelder, Stoffdaten, Aufgaben, Hersteller und Muster werden unverändert übernommen; nur neue Felder/IDs und ein eigenständiger leerer Regular-Datensatz kommen hinzu. Die Revision steigt einmal; erneuter Start migriert nicht nochmals. Ein alter Browser erhält beim Speichern weiterhin einen Revisionskonflikt.

Schema-1-JSON-Sicherungen bleiben importierbar und werden vor dem Laden serverseitig validiert/erweitert. Schema 2 exportiert beide Varianten samt Labels. Ein Restore ersetzt nach ausdrücklichem Laden und Speichern den gesamten Workspace, führt aber keine automatische Zusammenführung durch. Die interne Migrationssicherung ist kein Ersatz für regelmäßige private JSON-/Datenbankbackups. Zum vollständigen Zurückrollen zunächst den Server stoppen und eine gesicherte ursprüngliche Datenbank mit der alten Programmversion verwenden; die alte Version kann Schema 2 nicht bearbeiten.

## Prüfung des fremden Schema-Repos

Am 11.11.2026 tatsächlich gelesen: [Repository-Inhalt](https://github.com/kobo-labs-open-source/fashion-tech-pack-schema), [README](https://github.com/kobo-labs-open-source/fashion-tech-pack-schema/blob/main/README.md), [LICENSE](https://github.com/kobo-labs-open-source/fashion-tech-pack-schema/blob/main/LICENSE), [Root-Schema](https://github.com/kobo-labs-open-source/fashion-tech-pack-schema/blob/main/schema/tech-pack.schema.json) und [Measurements-Schema](https://github.com/kobo-labs-open-source/fashion-tech-pack-schema/blob/main/schema/measurements.schema.json).

Das Repo bietet JSON Schema 2020-12 und Beispiele, keine fertige Tech-Pack-Anwendung oder PDF-Oberfläche. Die LICENSE ist MIT (Lizenzdatei Blob `078f404bac511225a1438b1663ce3331eba251ad`). Root verlangt style, colorways (mindestens eins), billOfMaterials (mindestens eins), measurements; konkrete Messwerte sind Zahlen, nicht `null`. Das Measurements-Schema beschreibt Größenbindung in Text, erzwingt sie aber nicht durch eine dynamische Referenz. Das Beispiel enthält fremde Produktwerte, die nicht als ARVO-Werte dienen dürfen.

**Entscheidung:** keine Code-/Schema-/Beispielübernahme, keine npm-Abhängigkeit und kein behaupteter Standard-konformer Export. Ein eigenes kleines Entwurfsmodell bildet die offenen Felder, Belege und v0.2-Lücken direkt ab. MIT würde Übernahme mit Erhalt des Copyright-/Lizenzhinweises erlauben; da nichts kopiert wurde, wird das fremde Repo nicht als Abhängigkeit vendort. Die V2.1-Zeichnungsdefinitionen sind eigene, im Auftrag konkretisierte Definitionen; technische Produktionswerte bleiben offen. Eine spätere ausdrückliche Exportkonvertierung kann geprüft werden.

## Tests

```sh
.venv/bin/python -m pip install -r command_center/requirements-dev.txt
.venv/bin/python -m unittest discover -s command_center/tests -v
```

Pypdf ist nur für die Tests erforderlich. Neun Python-Tests prüfen zusätzlich die verlustfreie Schema-1-Migration einschließlich Sicherung/Revision, unabhängige Varianten, vollständige Geometrie-IDs, HPS und neue Hals-/Saum-/Armlochmaße, PDF-Reihenfolge und getrennte Werte. Weiterhin geprüft werden offene Werte, ungültige Zahlen/Datumswerte/IDs, A–S-Erhalt, dauerhaftes Speichern, wiederholte Initialisierung, Konflikte, HTTP-Origin-/CSRF-/Host-Schutz, JSON-Export und PDF-Inhalte einschließlich `0`, langer Texte und Entwurfsvermerk.

Optionaler Browser-Test mit Node.js und Playwright, **nur gegen einen leeren Testdatenordner** (schreibt ausdrücklich fiktive TESTDATEN):

```sh
.venv/bin/python -m command_center.server --data-dir /tmp/arvo-browser-test-v21 --port 8771
# In anderem Terminal:
npm install --no-save --prefix /tmp/arvo-browser playwright
/tmp/arvo-browser/node_modules/.bin/playwright install chromium
ARVO_TEST_URL=http://127.0.0.1:8771 NODE_PATH=/tmp/arvo-browser/node_modules node command_center/tests/browser.cjs
```

Zum Wiederholen einen neuen leeren Testdatenordner wählen. Testausgaben unter `command_center/test-output/` sind ignoriert. Der V2.1-Browsertest prüft sechs Variantenansichten, HPS, Breiten-/Saum-/Armloch-IDs, alle Filter, beide Auswahlrichtungen, unabhängige Werte, Produktwechsel, Speicherung/Reload, Konflikterhalt, JSON-Backup/Restore, Labelvorschau, beide PDF-Downloads und mobile Breite. Er vergleicht außerdem Aufgaben/Hersteller/Muster vor und nach dem Test auf unveränderten Inhalt. Installation und Laufzeit greifen auf keine bezahlte API zu; pip/npm-Downloads benötigen Internet.

## Grenzen und nächster sinnvoller Schritt

Kein fertiges produktionsreifes Tech Pack: Original v0.2 samt belegter A–S-Zuordnung, maßstäbliche/freigegebene Schnittzeichnungen, reale Maße, Stationshöhen, Toleranzen, finale Stoffdaten, Verarbeitung und gemeinsame fachliche Freigabe fehlen. Die neuen schematischen Ansichten ersetzen keine Schnittkonstruktion oder Herstellerprüfung. Projektionen sind ohne dokumentiertes Mess-Setup nicht vergleichbar. Vollständigkeit ist keine Richtigkeitsprüfung. Kein Freigabeknopf, keine Bestellung, kein automatischer Follow-up oder Instagram-Post. Keine automatische Cloud-Bereitstellung. Die gemeinsame Nutzung über zwei reale Rechner/SSH wurde hier nicht getestet; getestet werden parallele Browser auf derselben Instanz. Nächster fachlicher Schritt ist die Übernahme der echten v0.2-Definitionen und Robins realer Messungen.

## Validierungsstand V2.1 · 11.11.2026

Neun Python-Tests und der echte Chromium-Test auf getrennten Testdaten erfolgreich. Desktop-/Mobil-Screenshots und beide PDF-Varianten einschließlich aller Seiten gerendert und visuell geprüft. Keine Testwerte oder privaten Daten werden eingecheckt. Die lokal vorhandene Schema-1-Datenbank enthielt keine definierten A–S-Messpunkte; es gab im PR noch keinen späteren Zeichnungs-/Labelentwurf. Daher ist die Ergänzung im bestehenden ARVO-Stil gehalten, ohne eine nicht verfügbare Vorlage als übernommen auszugeben. Zwei reale Rechner/SSH sowie Safari wurden nicht getestet.
