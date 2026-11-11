"""V2.1 draft PDF: the same geometric source and definitions as the browser."""
from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.graphics.shapes import Drawing, Rect, String
from .model import missing, techpack, migrate
from .drawings import pdf_drawing
from .technical import definitions


def label_drawing(kind, spec):
    """Concept previews; drawn dimensions intentionally do not imply production mm."""
    d=Drawing(430,210)
    green=colors.HexColor('#283b30');pale=colors.HexColor('#eff1e6')
    def text(x,y,value,size=11,color=green):
        d.add(String(x,y,value,fontName='Helvetica-Bold' if value=='ARVO' else 'Helvetica',fontSize=size,fillColor=color,textAnchor='middle'))
    if kind=='care':
        d.add(Rect(125,10,180,190,fillColor=colors.HexColor('#fffef7'),strokeColor=colors.HexColor('#b9c2af')))
        text(215,163,'ARVO',25)
        text(215,130,'COMPOSITION / '+('SIEHE SPEZIFIKATION' if spec['composition'] else 'OFFEN'),8)
        text(215,108,'CARE / '+('SIEHE SPEZIFIKATION' if spec['care'] else 'OFFEN'),8)
        text(215,86,'GRÖSSE / '+(spec['size'] if 0<len(spec['size'])<=12 else 'SIEHE SPEZIFIKATION' if spec['size'] else 'OFFEN'),9)
        text(215,55,'HERKUNFT / '+('SIEHE SPEZIFIKATION' if spec['origin'] else 'OFFEN'),8)
        text(215,28,'ENTWURF',8)
    elif kind=='neck':
        d.add(Rect(70,40,290,130,fillColor=green,strokeColor=green))
        text(215,128,'ARVO',34,pale);text(215,94,'S / M / L',12,pale)
        text(215,65,'CLAIM / '+('SIEHE SPEZIFIKATION' if spec['claim'] else 'OPTIONAL - OFFEN'),8,pale)
    else:
        for x,front in ((80,True),(240,False)):
            d.add(Rect(x,10,130,190,fillColor=green if front else pale,strokeColor=green))
            text(x+65,180,'VORDERSEITE' if front else 'RÜCKSEITE',8,pale if front else green)
            text(x+65,120,'ARVO',26,pale if front else green)
            # Fixed-length brand copy is shown only when it matches the supplied draft.
            value=spec['claim'] if front else spec['optionalClaim']
            for i,line in enumerate(('PERFORMANCE MEETS','LIFESTYLE') if value=='PERFORMANCE MEETS LIFESTYLE' else ('BUILT FOR MOVEMENT',) if value=='BUILT FOR MOVEMENT' else ('TEXT SIEHE SPEZIFIKATION',) if value else ('OFFEN',)):
                text(x+65,80-i*15,line,8,pale if front else green)
    return d


def export_pdf(data, revision, product=None):
    data=migrate(data);product=product or data.get('activeProduct','cutoff')
    if product not in ('cutoff','regular'):
        raise ValueError('Unbekannte Produktvariante')
    t=techpack(data,product);output=BytesIO();styles=getSampleStyleSheet()
    styles['BodyText'].fontSize=9;styles['BodyText'].leading=13
    styles.add(ParagraphStyle('Measurement',parent=styles['BodyText'],fontSize=8.5,leading=11.5))
    def p(value,style='BodyText'):
        text='OFFEN' if value is None or value=='' else str(value)
        return Paragraph(escape(text).replace('\n','<br/>'),styles[style])
    def table(rows,widths,header=True):
        # Keep normal records intact across pages. In-row splitting is only
        # needed for unusually long user notes that exceed a complete page.
        tallest=max((max(cell.wrap(width-10,100000)[1] for cell,width in zip(row,widths))+12 for row in rows),default=0)
        obj=Table(rows,colWidths=widths,repeatRows=1 if header else 0,splitInRow=1 if tallest>650 else 0,hAlign='LEFT')
        commands=[('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#c7cec1')),
                  ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]
        if header:commands.append(('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e6eedf')))
        obj.setStyle(TableStyle(commands));return obj
    story=[p('ARVO / TECH PACK V2.1','Title'),p('01 / Product Overview','Heading1'),p(t['title'],'Heading2'),p(t['variant']),
           p(t['version']+' / Spezifikationsstruktur '+t['specVersion']+' / Revision '+str(revision)),
           p('ENTWURF - KEINE PRODUKTIONSFREIGABE','Heading2'),p(t['context']),p('Quelle: '+t['source']),
           p('S/M/L und Toleranzen bleiben ohne ermittelte Werte OFFEN. Alle Messwerte in cm, Labelformate in mm. Zeichnungen und Vorschauen sind schematisch, nicht maßstäblich. Keine automatische Gradierung oder Gleichsetzung zwischen Produkten.'),
           p('Messbasis','Heading2'),p('Front/Back-Breiten sind die Gesamtbreite des flachliegenden Kleidungsstücks, kein Umfang und keine einzelne Schnittteilbreite. Eine gemeinsame ID ist ein Kontrollmaß, keine automatische Kopie. A-S bleiben im Cutoff-Datensatz unverändert und ohne unbelegte Zeichnungszuordnung.'),
           p('HPS liegt am inneren, halsseitigen Schulter-/Halsnahtpunkt. Stationshöhen werden senkrecht ab waagerechter HPS-Linie gemessen und müssen je Größe festgelegt werden.'),
           p('Seitennähte geschlossen bis zum fertigen unteren Saum. Konkrete Naht-/Kantenverarbeitung mit Hersteller abstimmen.'),
           p('Design / Zeichnungsbelege','Heading2'),p(t['artwork'])]
    for view,title in [('front','02 / Front View'),('back','03 / Back View'),('side','04 / Side View')]:
        details=[('horizontal','Horizontale Gesamtbreiten'),('detail','Vertikale Maße, Schulter & Kurven')] if view!='side' else [(None,'Armausschnitt / technische Projektion')]
        for axis,subtitle in details:
            story.extend([PageBreak(),p(title,'Heading1'),p(subtitle,'Heading2'),
                          p('Schematisch - keine Werte aus der Zeichnung ablesen. IDs entsprechen der Maßtabelle.')])
            if view=='side':story.append(p('Braune Strecken sind KEINE direkten Flachmaße. Gemeinsame Referenzlinie und Projektionshöhe dokumentieren. Vorder-/Hinterkurve und vertikale Tiefe unabhängig kontrollieren.'))
            drawing=pdf_drawing(product,view,axis);drawing.scale(.92,.92);drawing.width=368;drawing.height=570.4
            story.append(drawing)
    story += [PageBreak(),p('05 / Measurement Table','Heading1'),p('S/M/L, Toleranzen und Messdefinitionen - cm')]
    by_code={d['code']:d for d in definitions(product)}
    ordered=[r for r in t['measurements'] if r['code'] in by_code]+[r for r in t['measurements'] if r['code'] not in by_code]
    rows=[[p(v) for v in ('Code / Definition','Messmethode / Beleg','S','M','L','- Tol.','+ Tol.')]]
    for r in ordered:
        rows.append([p(r['code']+' / '+(r['name'] or 'Originaldefinition OFFEN'),'Measurement'),
                     p((r['method'] or 'Keine belegte Zeichnungszuordnung.')+'\nBeleg: '+(r['source'] or 'OFFEN'),'Measurement'),
                     *[p(r[k]) for k in ('S','M','L','minus','plus')]])
    story.append(table(rows,[34*mm,66*mm,*([16*mm]*5)]))
    story += [PageBreak(),p('06 / Fabric & Construction','Heading1'),p('Produktionsstoff','Heading2')]
    fabric_labels=dict(composition='Zusammensetzung',gsm='GSM',stretch='Stretch / Rücksprung',finish='Finish',color='Farbe',source='Beleg / Datum',notes='Hinweise')
    story.append(table([[p(label),p(t['fabric'][key])] for key,label in fabric_labels.items()],[55*mm,125*mm],False))
    story += [p('Referenzstoff, separat','Heading2'),p(t['reference']),p('Verarbeitung / Schnittdetails','Heading2'),
              p('Seitennähte geschlossen bis zum fertigen unteren Saum. Keine automatische Vorgabe von Nahtarten oder technischen Produktionswerten.'),p(t['construction'])]
    label_names={'width':'Breite (mm)','height':'Höhe (mm)','material':'Material','printing':'Druckverfahren','source':'Beleg / Datum','composition':'Materialzusammensetzung','care':'Pflegehinweise','size':'Größe','productInfo':'Produktinformationen','origin':'Herkunft','claim':'Claim','placement':'Platzierung','construction':'Verarbeitung','optionalClaim':'Optionaler Claim (Entwurf)','hole':'Lochposition','cord':'Schnur / Befestigung'}
    for kind,title in [('care','07 / Care Label'),('neck','08 / Neck Label'),('hang','09 / Hang Tag')]:
        spec=t['labels'][kind]
        story += [PageBreak(),p(title,'Heading1'),p('ENTWURF / unbestätigte Angaben bleiben OFFEN; Vorschau nicht maßstäblich.'),label_drawing(kind,spec),Spacer(1,12)]
        story.append(table([[p(label_names[key]),p(value)] for key,value in spec.items()],[55*mm,125*mm],False))
    story += [PageBreak(),p('10 / Offene Angaben und Versionshinweise','Heading1'),p('V2.1: getrennte Varianten, eigene neue AT-/RF-IDs. A-S aus v0.2 werden ohne Originalbeleg weder umbenannt noch neuen Linien zugeordnet. Bestehende Eingaben bleiben erhalten. Schema 2; additive Migration mit Sicherung des Ausgangsstands.'),p('Zeichnungsdefinitionen sind an ihre IDs gebunden. Eine Größenangabe ist keine fachliche Freigabe. Gemeinsame Prüfung von Fit, Stoff, Zeichnungen, Gradierung, Labels und Herstellerangaben bleibt erforderlich.')]
    grouped={}
    for issue in missing(data,product):
        code,_,detail=issue.partition(': ')
        grouped.setdefault(detail,[]).append(code)
    for detail,codes in grouped.items():
        story.append(p(', '.join(codes)+': '+detail))
    for kind,spec in t['labels'].items():
        blank=[label_names[k] for k,v in spec.items() if v in (None,'')]
        if blank:story.append(p(kind.upper()+': '+', '.join(blank)))
    if product=='cutoff':story.append(p('Originaldefinitionen A-S: externe v0.2-Quelle hier weiterhin nicht verfügbar. Keine Gleichsetzung mit den neuen Messpunkten.'))
    def footer(canvas,doc):
        canvas.setFont('Helvetica',8);canvas.drawString(15*mm,10*mm,'ARVO | '+product.upper()+' | V2.1 ENTWURF | Keine Produktionsfreigabe')
        canvas.drawRightString(195*mm,10*mm,str(doc.page))
    SimpleDocTemplate(output,pagesize=(210*mm,297*mm),leftMargin=15*mm,rightMargin=15*mm,topMargin=15*mm,bottomMargin=18*mm,title='ARVO V2.1 Tech Pack - '+product).build(story,onFirstPage=footer,onLaterPages=footer)
    return output.getvalue()
