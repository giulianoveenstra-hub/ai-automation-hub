"""V2.1 measurement definitions. Drawing coordinates are illustrations, never garment cm."""
import copy

PRODUCTS = {'cutoff': 'ARVO ATHLETIC FIT CUTOFF TEE', 'regular': 'ARVO REGULAR FIT T-SHIRT'}
WIDTHS = [('Brustweite',260,'chest'), ('Unterbrustweite',300,'chest'),
          ('Rippenbogenweite',340,'waist'), ('Übergang zur Taille',380,'waist'),
          ('Engste Taillenweite',420,'waist'), ('Hüftweite',465,'waist'), ('Untere Saumweite',510,'hem')]


def definitions(product):
    prefix = 'AT' if product == 'cutoff' else 'RF'
    result = []
    def add(number, name, method, views, axis, region, kind='flat'):
        result.append(dict(code=f'{prefix}{number:02}', name=name, method=method,
                           views=views, axis=axis, region=region, kind=kind))
    add(1,'Körperlänge ab HPS','Flach, ohne Zug. Vom halsseitigen Schulter-/Halsnahtpunkt HPS senkrecht zur unteren Saumkante messen; keine Strecke entlang der Seitennaht.', ['front','back'],'vertical','neck')
    add(2,'Front Neck Drop','Flach, ohne Zug. HPS-Höhe mit einer waagerechten Hilfslinie übertragen. Senkrechte Projektion bis zum tiefsten Punkt der vorderen inneren Halslochkante; nicht entlang der Rundung.', ['front'],'vertical','neck')
    add(3,'Back Neck Drop','Rückseite flach, ohne Zug. Von der waagerecht übertragenen HPS-Höhe senkrecht bis zur tiefsten hinteren inneren Halslochkante messen. Eigenständig, nicht vom Frontmaß ableiten.', ['back'],'vertical','neck')
    add(4,'Schulterstrecke','Flach, gerade vom halsseitigen HPS zum äußeren Schulter-/Armausschnittpunkt derselben Schulter messen; Strecke ist schräg.', ['front','back'],'diagonal','neck')
    for i,(name,y,region) in enumerate(WIDTHS):
        station = f'{prefix}{20+i:02}'
        method = ('Flach und ohne Zug über die gesamte Kleidungsbreite, von linker zu rechter Seitenkante. '
                  'Kein Umfang und keine einzelne Vorder-/Rückenteilbreite. ')
        if i < 6:
            method += f'Messhöhe: {station} unter der waagerechten HPS-Bezugslinie; Höhe je Größe zuerst festlegen und belegen. '
        else:
            method += 'Messhöhe: fertige untere Saumkante, direkt am Abschluss. '
        method += 'Dieselbe Kontrollmessung erscheint in Front/Back; Ansichtswechsel erzeugt keine zweite Messung. Bei abweichenden Schnittteilbreiten ist ein separater Schnittteilplan erforderlich.'
        add(10+i, name+' · Gesamtbreite flach', method, ['front','back'],'horizontal',region)
        if i < 6:
            add(20+i, 'Messhöhe · '+name, 'Senkrechter Abstand von der waagerechten HPS-Bezugslinie zur Station „'+name+'“. Je Größe selbst festlegen, dokumentieren und auf beiden Ansichten identisch verwenden. Keine Höhenwerte aus der Illustration ablesen.', ['front','back'],'vertical',region)
    add(30,'Vertikale Armausschnitttiefe','Flach, ohne Zug. Waagerechte Linie durch den unteren Achsel-/Seitennahteckpunkt legen. Senkrechten Abstand zwischen dieser Linie und HPS-Höhe messen. Side View zeigt nur die Projektion derselben vertikalen Kontrolle.', ['front','side'],'vertical','chest')
    add(31,'Vordere Armausschnittlänge · Nahtlinie','Vorderteil separat flach auslegen, ohne es zu dehnen. Mit flexiblem Maßband der vorderen Armausschnitt-Nahtlinie vom äußeren Schulterpunkt bis zum unteren Achselpunkt folgen. Bei eingefasster Kante zuerst die Naht-/Kantenreferenz mit Hersteller festlegen und belegen. Reproduzierbare Alternative zur Seitenprojektion.', ['front'],'curve','chest')
    add(32,'Hintere Armausschnittlänge · Nahtlinie','Rückenteil separat flach auslegen, ohne es zu dehnen. Flexibles Maßband entlang der hinteren Armausschnitt-Nahtlinie vom äußeren Schulterpunkt bis zum unteren Achselpunkt führen. Kanten-/Nahtreferenz mit Hersteller festlegen; unabhängig vom Vorderteil messen.', ['back'],'curve','chest')
    add(40,'Projektion · Ausladung vorne','KEIN direktes Flachmaß. Standardisierte Seitenaufnahme am dokumentierten Formkörper, Kamera rechtwinklig zur Seitenebene. Vertikale Referenz durch unteren Achsel-/Seitennahteckpunkt; horizontal bis zur vorderen Armausschnittkante auf Höhe '+prefix+'43. Formkörper, Haltung, Kamera und Skalierung dokumentieren. Alternative: '+prefix+'31 als separates Kurvenmaß.', ['side'],'horizontal','chest','projection')
    add(41,'Projektion · Ausladung hinten','KEIN direktes Flachmaß. Gleiche dokumentierte Seitenaufnahme, Referenzlinie und Höhe '+prefix+'43 wie vorne. Horizontal von Referenz bis hinterer Armausschnittkante messen. Unabhängig erfassen; nicht spiegeln. Alternative: '+prefix+'32 als separates Kurvenmaß.', ['side'],'horizontal','chest','projection')
    add(42,'Projektion · gesamte Armausschnittbreite','KEIN direktes Flachmaß. Auf derselben dokumentierten Aufnahme und Höhe '+prefix+'43 horizontal zwischen vorderer und hinterer Armausschnittkante messen. Eigenständig erfassen, keine automatische Summe von '+prefix+'40/41. Für Schnittabnahme Kurvenmaße '+prefix+'31/32 und Tiefe '+prefix+'30 verwenden.', ['side'],'horizontal','chest','projection')
    add(43,'Projektion · Messhöhe unter HPS','KEIN direktes Flachmaß. Senkrechter Abstand von HPS-Höhe zur gemeinsamen horizontalen Projektionsstation. Erst Formkörper, HPS-Übertragung, Fotoebene und Höhe je Größe festlegen. Ohne diese Festlegung sind '+prefix+'40/41/42 nicht vergleichbar.', ['side'],'vertical','chest','projection')
    if product == 'regular':
        add(50,'Ärmellänge ab Schulter','Flach, ohne Zug. Vom äußeren Schulter-/Ärmelansatz entlang der oberen Ärmellinie bis zur fertigen Ärmelkante messen. Nur Regular Fit.', ['front','back'],'diagonal','chest')
        add(51,'Ärmelöffnung flach','Kurzarm flach auslegen, ohne Zug, gerade zwischen den beiden Endpunkten der fertigen Ärmelkante messen. Kein Umfang. Nur Regular Fit.', ['front','back'],'diagonal','chest')
    return result


def points(product):
    return [dict(code=d['code'],name=d['name'],method=d['method'],source='',S=None,M=None,L=None,minus=None,plus=None) for d in definitions(product)]


def label_specs(kind):
    common = dict(width=None,height=None,material='',printing='',source='')
    if kind == 'care':
        return dict(**common, composition='',care='',size='',productInfo='',origin='')
    if kind == 'neck':
        return dict(**common,claim='',placement='Hinterer innerer Halsausschnitt; genaue Position und Abstand offen.',construction='')
    return dict(**common,claim='PERFORMANCE MEETS LIFESTYLE',optionalClaim='BUILT FOR MOVEMENT',hole='',cord='')


def extend_techpack(t, product):
    t = copy.deepcopy(t)
    t.update(variant=PRODUCTS[product],specVersion='2.1',labels={k:label_specs(k) for k in ('care','neck','hang')})
    t['measurements'] += points(product)
    return t
