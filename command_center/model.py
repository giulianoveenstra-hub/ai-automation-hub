"""Versioned draft model. Unknown numeric values are None, never zero defaults."""
import copy
import math
import string

STATUSES = ('OPEN', 'WAITING', 'DONE', 'DECIDED')
OWNERS = ('Robin', 'Giuliano', 'Gemeinsam')
SOURCE = 'ARVO-STATUS.md · Snapshot 2026-11-10 · Nutzerbericht, nicht unabhängig geprüft'
# Suggestions only: v0.2's original A-S mapping is not available in this repository.
METHODS = {
    'Brustweite (1/2)': 'Flach, ohne Zug, waagerecht zwischen den Seitennähten auf der gemeinsam festzulegenden Höhe messen. Höhe im Maßpunkt dokumentieren.',
    'Körperlänge ab HPS': 'Vom höchsten Schulterpunkt am Halsansatz parallel zur vorderen Mitte bis zur Saumkante messen; flach und ohne Zug.',
    'Saumweite (1/2)': 'Flach, ohne Zug, gerade von linker zu rechter Saumkante messen.',
    'Schulterbreite': 'Auf der Rückseite flach, gerade zwischen den äußeren Schulterpunkten messen. Endpunkte am Foto markieren.',
    'Halslochweite': 'Flach, ohne Zug, gerade zwischen den inneren Halslochkanten messen.',
    'Halslochtiefe vorne': 'Senkrecht von der Verbindungslinie der höchsten Schulterpunkte zur tiefsten vorderen Halslochkante messen.',
    'Armausschnitttiefe': 'Senkrecht vom höchsten Schulterpunkt bis zur waagerechten Linie durch den unteren Armausschnitt messen.',
}

def seed():
    tasks = [
        ('measure-reference', 'UNIQLO-Referenzen messen: verfügbare S/M/L, Methode und Fotos festhalten', 'Robin', 'OPEN'),
        ('agree-design', 'Frontlogo, Rückenprint, Silhouette, Grading und Toleranzen abstimmen', 'Gemeinsam', 'OPEN'),
        ('instagram-plan', 'Instagram-Profil und Pre-Launch-Content planen', 'Giuliano', 'OPEN'),
        ('evaluate-samples', 'Reale Swatches/Muster auf Stoff, Fit und Waschverhalten prüfen', 'Gemeinsam', 'OPEN'),
        ('compare-quotes', 'Vergleichbare schriftliche Angebote, Gesamtkosten und Schnittrechte klären', 'Gemeinsam', 'OPEN'),
        ('references-sent', 'Referenzpaket an die vier antwortenden Hersteller versendet', 'Gemeinsam', 'DONE'),
        ('lemuta-call', 'LEMUTA-Gespräch vom 10.11.2026 geführt', 'Gemeinsam', 'DONE'),
    ]
    suppliers = [
        ('lemuta', 'LEMUTA', 'WAITING', 'Stoffswatches erwartet; 50% Baumwolle / 50% Polyester, 150 GSM nur besprochener Kandidat, nicht ARVO-Spezifikation.'),
        ('makealabel', 'MakeaLabel', 'WAITING', 'Referenzpaket gesendet, weitere Antwort laut Snapshot ausstehend. Vor Nachfrage Posteingang prüfen.'),
        ('top', 'T.O.P Studios', 'WAITING', 'Referenzpaket gesendet, weitere Antwort laut Snapshot ausstehend. Vor Nachfrage Posteingang prüfen.'),
        ('sot', 'Sportswear of Tomorrow', 'WAITING', 'Referenzpaket gesendet; widersprüchliche Stoff-/GSM-Angaben im Lieferantenvergleich prüfen.'),
        ('52ger', '52GER', 'OPEN', 'Antwortstatus ungeprüft; Posteingang prüfen.'),
        ('dowe', 'DOWE Sportswear', 'OPEN', 'Antwortstatus ungeprüft; Posteingang prüfen.'),
        ('highkraft', 'HighKraft EU', 'OPEN', 'Antwortstatus ungeprüft; Posteingang prüfen.'),
    ]
    return dict(schemaVersion=1, techpack=dict(
        title='ARVO · Sleeveless Cut-off Tee', version='v0.2 · Arbeitsfortführung', unit='cm',
        context='Breite Schulterabdeckung, enger Rundhals, moderat tailliert, keine Kompression. A–S aus v0.2 erhalten; ursprüngliche Definitionen und Zeichnungen fehlen hier. Keine finale Produktionsfreigabe.',
        source=SOURCE, construction='', artwork='',
        measurements=[dict(code=c, name='', method='', source='', S=None, M=None, L=None,
                           minus=None, plus=None) for c in string.ascii_uppercase[:19]],
        fabric=dict(composition='', gsm=None, stretch='', finish='', color='', source='', notes=''),
        reference='UNIQLO-Referenz laut Labelbericht: 53% Baumwolle / 47% Polyester, davon 30 Prozentpunkte recyceltes Polyester; GSM unbekannt. Kein ARVO-Produktionsstoff. LEMUTA-Kandidat separat im Herstellertracking.'),
        tasks=[dict(id=i, title=t, owner=o, status=s, due='', notes='', source=SOURCE) for i,t,o,s in tasks],
        suppliers=[dict(id=i, name=n, status=s, notes=note, source='ocs/supplier-comparison.md · Snapshot 2026-11-10 · ungeprüft',
                        composition='', gsm=None, moq=None, sampleCost=None, currency='EUR', leadTime='', questions='') for i,n,s,note in suppliers],
        samples=[dict(id='lemuta-swatches', supplier='lemuta', title='Stoffswatches', status='WAITING',
                      requested='', received='', review='', source=SOURCE)],
    )

def validate(data):
    """Strict shape, finite numbers, stable IDs, bounded payloads; draft blanks allowed."""
    template = seed()
    def walk(value, spec, path):
        if isinstance(spec, dict):
            if not isinstance(value, dict) or set(value) != set(spec):
                raise ValueError(path + ': unbekannte oder fehlende Felder')
            for key in spec:
                walk(value[key], spec[key], path + '.' + key)
        elif isinstance(spec, list):
            if not isinstance(value, list) or len(value) > 200:
                raise ValueError(path + ': ungültige Liste')
            for item in value:
                walk(item, spec[0], path)
        elif spec is None:
            if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1000000):
                raise ValueError(path + ': Zahl muss endlich und nicht negativ sein')
        elif isinstance(spec, int):
            if type(value) is not int or value != spec:
                raise ValueError(path + ': unbekannte Modellversion')
        elif not isinstance(value, str) or len(value) > 4000 or any(ord(c) < 32 and c not in '\n\r\t' for c in value):
            raise ValueError(path + ': ungültiger Text')
    walk(data, template, 'workspace')
    if data['techpack']['unit'] != 'cm':
        raise ValueError('Maßeinheit muss cm bleiben')
    points = data['techpack']['measurements']
    if [p['code'] for p in points] != list(string.ascii_uppercase[:19]):
        raise ValueError('A–S müssen in ursprünglicher Reihenfolge erhalten bleiben')
    for group in ('tasks', 'suppliers', 'samples'):
        ids = [r['id'] for r in data[group]]
        if any(not i for i in ids) or len(set(ids)) != len(ids):
            raise ValueError('Leere oder doppelte IDs in ' + group)
        for row in data[group]:
            if row['status'] not in STATUSES:
                raise ValueError('Unbekannter Status')
            if group == 'tasks' and row['owner'] not in OWNERS:
                raise ValueError('Unbekannte Zuständigkeit')
            for key in ('due', 'requested', 'received'):
                if row.get(key):
                    from datetime import date
                    try:
                        if date.fromisoformat(row[key]).isoformat() != row[key]:
                            raise ValueError()
                    except ValueError:
                        raise ValueError('Datum muss YYYY-MM-DD sein')
    supplier_ids = {s['id'] for s in data['suppliers']}
    if any(s['supplier'] not in supplier_ids for s in data['samples']):
        raise ValueError('Muster muss einem vorhandenen Hersteller zugeordnet sein')
    return copy.deepcopy(data)

def missing(data):
    t = data['techpack']
    issues = []
    for p in t['measurements']:
        fields = [k for k in ('name','method','source') if not p[k].strip()]
        fields += [k for k in ('S','M','L','minus','plus') if p[k] is None]
        if fields:
            labels = {'name':'Definition','method':'Messmethode','source':'Beleg','minus':'Toleranz minus','plus':'Toleranz plus'}
            issues.append(p['code'] + ': ' + ', '.join(labels.get(k,k) for k in fields))
    for key in ('composition','gsm','source'):
        if t['fabric'][key] in ('', None):
            issues.append('Produktionsstoff: ' + {'composition':'Zusammensetzung','gsm':'GSM','source':'Beleg'}[key])
    for key in ('construction', 'artwork'):
        if not t[key].strip():
            issues.append({'construction':'Verarbeitung','artwork':'Design / Zeichnungen'}[key] + ': offen')
    return issues
