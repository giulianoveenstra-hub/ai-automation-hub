"""Draft-only PDF export. No inference, grading or production approval."""
from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from .model import missing


def export_pdf(data, revision):
    output = BytesIO()
    styles = getSampleStyleSheet()
    styles['BodyText'].fontSize = 9
    styles['BodyText'].leading = 13
    styles['BodyText'].alignment = TA_LEFT
    def p(value, style='BodyText'):
        text = 'OFFEN' if value is None or value == '' else str(value)
        return Paragraph(escape(text).replace('\n', '<br/>'), styles[style])
    t = data['techpack']
    story = [p('ARVO / TECH PACK', 'Title'), p(t['title'], 'Heading1'),
             p(t['version'] + ' / Revision ' + str(revision)),
             p('ENTWURF - KEINE PRODUKTIONSFREIGABE', 'Heading2'),
             p('Export enthält ausschließlich gespeicherte Eingaben. OFFEN bedeutet unbekannt; keine automatische Größengradierung. Alle Maße und Toleranzen in cm.'),
             p('Kontext', 'Heading2'), p(t['context']), p('Quelle: ' + t['source']),
             p('Maßtabelle / S - M - L', 'Heading2')]
    rows = [[p(x) for x in ('Code / Maßpunkt', 'Messmethode / Beleg', 'S', 'M', 'L', '- Tol.', '+ Tol.')]]
    for r in t['measurements']:
        rows.append([p(r['code'] + ' / ' + (r['name'] or 'Definition OFFEN')),
                     p((r['method'] or 'Methode OFFEN') + '\nBeleg: ' + (r['source'] or 'OFFEN')),
                     *[p(r[k]) for k in ('S','M','L','minus','plus')]])
    table = Table(rows, colWidths=[34*mm, 66*mm, *([16*mm]*5)], repeatRows=1, splitInRow=1, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e6eedf')),
        ('VALIGN',(0,0),(-1,-1),'TOP'), ('GRID',(0,0),(-1,-1),.3,colors.HexColor('#c7cec1')),
        ('LEFTPADDING',(0,0),(-1,-1),5), ('RIGHTPADDING',(0,0),(-1,-1),5),
        ('TOPPADDING',(0,0),(-1,-1),6), ('BOTTOMPADDING',(0,0),(-1,-1),6),
    ]))
    story += [table, Spacer(1,5*mm), p('Produktionsstoff (nicht Referenzstoff)', 'Heading2')]
    labels = dict(composition='Zusammensetzung',gsm='GSM',stretch='Stretch / Rücksprung',finish='Finish',color='Farbe',source='Beleg / Datum',notes='Hinweise')
    for key, label in labels.items():
        story += [p(label, 'Heading3'), p(t['fabric'][key])]
    story += [p('Referenz, separat', 'Heading2'), p(t['reference']),
              p('Verarbeitung / Nähte / Labels / Pflege', 'Heading2'),p(t['construction']),
              p('Design / Zeichnungen / Platzierung', 'Heading2'),p(t['artwork']),
              p('Offene Angaben', 'Heading2')]
    for issue in missing(data):
        story.append(p('- ' + issue))
    if not missing(data):
        story.append(p('Pflichtfelder befüllt. Fachliche Prüfung, Musterprüfung und gemeinsame Freigabe weiterhin erforderlich.'))
    def footer(canvas, doc):
        canvas.setFont('Helvetica', 8)
        canvas.drawString(15*mm, 10*mm, 'ARVO | ENTWURF | Keine Produktionsfreigabe')
        canvas.drawRightString(195*mm, 10*mm, str(doc.page))
    SimpleDocTemplate(output, pagesize=(210*mm,297*mm), leftMargin=15*mm, rightMargin=15*mm,
                      topMargin=15*mm,bottomMargin=18*mm, title='ARVO Tech Pack - Entwurf').build(story,onFirstPage=footer,onLaterPages=footer)
    return output.getvalue()
