"""One geometric source for browser SVG and PDF vectors; never calibrated measurements."""
from html import escape
from .technical import definitions, WIDTHS

INK = '#283a31'
DIM = '#657d67'
PROJECTION = '#987b51'


def scene(product, view, filter_axis=None):
    """Primitive coordinates use SVG's top-left origin; IDs match technical catalog."""
    nodes = []
    def node(kind, **kw):
        nodes.append(dict(kind=kind, **kw))
    def path(commands, **kw):
        node('path',commands=commands,**kw)
    def line(x1,y1,x2,y2,**kw):
        node('line',x1=x1,y1=y1,x2=x2,y2=y2,**kw)
    def text(x,y,value,**kw):
        node('text',x=x,y=y,text=value,**kw)
    neck = 153 if view=='front' else 116
    station_x = [113,115,122,131,134,130,125] if product=='cutoff' else [115,115,116,117,117,116,116]
    if view != 'side':
        if product == 'cutoff':
            outline=[('M',154,100),('L',118,112),('C',134,193,120,238,113,260),('L',125,510),('L',275,510),('L',287,260),('C',280,238,266,193,282,112),('L',246,100),('C',239,neck,161,neck,154,100),('Z',)]
        else:
            outline=[('M',154,100),('L',118,112),('L',66,194),('L',100,220),('L',119,192),('L',115,260),('L',116,510),('L',284,510),('L',285,260),('L',281,192),('L',300,220),('L',334,194),('L',282,112),('L',246,100),('C',239,neck,161,neck,154,100),('Z',)]
        left_body=[]
        right_body=[]
        for i in range(1,len(WIDTHS)):
            y0,y1=WIDTHS[i-1][1],WIDTHS[i][1]
            x0,x1=station_x[i-1],station_x[i]
            left_body.append(('C',x0,y0+(y1-y0)/3,x1,y1-(y1-y0)/3,x1,y1))
        for i in range(len(WIDTHS)-1,0,-1):
            y0,y1=WIDTHS[i][1],WIDTHS[i-1][1]
            x0,x1=400-station_x[i],400-station_x[i-1]
            right_body.append(('C',x0,y0+(y1-y0)/3,x1,y1-(y1-y0)/3,x1,y1))
        # Swap only the body section, keeping neck, shoulder and sleeve geometry.
        a=next(i for i,c in enumerate(outline) if c[-2:]==(station_x[0],260))
        b=next(i for i,c in enumerate(outline) if c[0]=='L' and c[1:]==(400-station_x[0],260))
        outline=outline[:a+1]+left_body+[('L',400-station_x[-1],510)]+right_body+outline[b+1:]
        path(outline,stroke=INK,fill='#f6f7f2',width=1.8)
        # Closed hem, no side notch or opening; inset stitch line.
        line(126 if product=='cutoff' else 117,502,274 if product=='cutoff' else 283,502,stroke='#a3afa0',dash=True)
        path([('M',154,100),('C',153,neck+12,247,neck+12,246,100)],stroke='#a3afa0')
        line(200,160,200,492,stroke='#c2cabe',dash=True)
        hps=(154,100)
        node('circle',x=154,y=100,r=3.5,fill=INK)
        line(154,100,126,72,stroke=INK)
        text(102,64,'HPS',size=12,anchor='middle',fill=INK)
        text(200,558,'GESAMTBREITE FLACH / KEIN UMFANG',size=10,anchor='middle')
    else:
        # A shaped side projection on a form, not the silhouette of a flat piece.
        path([('M',184,100),('L',158,118),('C',143,150,148,185,151,230),('C',157,278,173,309,200,320),('C',228,302,245,268,249,230),('C',255,180,249,139,226,116),('L',211,103)],stroke=INK,fill='#f6f7f2',width=1.8)
        path([('M',158,118),('C',135,235,148,406,143,510),('L',253,510),('C',248,406,266,235,226,116)],stroke=INK,width=1.8)
        line(144,502,252,502,stroke='#a3afa0',dash=True)
        line(200,112,200,524,stroke=PROJECTION,dash=True)
        line(184,100,290,100,stroke='#a3afa0',dash=True)
        node('circle',x=184,y=100,r=3.5,fill=INK)
        node('circle',x=200,y=320,r=3,fill=INK)
        line(184,100,154,72,stroke=INK)
        text(145,64,'HPS',size=12,anchor='middle')
        text(90,535,'VORNE',size=11,anchor='middle')
        text(308,535,'HINTEN',size=11,anchor='middle')
        text(200,556,'SEITENPROJEKTION / KEIN FLACHMASS',size=10,anchor='middle',fill=PROJECTION)
        text(200,577,'Referenz: Vertikale durch Achsel-/Seitennahteckpunkt',size=9,anchor='middle')
        if product=='regular':
            path([('M',158,118),('L',123,195),('L',170,232),('L',226,116)],stroke='#a3afa0',dash=True)
            text(200,595,'Ärmel für Armlochkontrolle schematisch transparent',size=9,anchor='middle')

    prefix='AT' if product=='cutoff' else 'RF'
    catalog={d['code']:d for d in definitions(product)}
    def dim(number, start, end, label, extensions=(), curve=None):
        code=f'{prefix}{number:02}'
        d=catalog[code]
        if view not in d['views'] or (filter_axis and (d['axis']=='horizontal' if filter_axis=='detail' else d['axis']!=filter_axis)):
            return
        common=dict(point=code,axis=d['axis'],region=d['region'],projection=d['kind']=='projection')
        color=PROJECTION if common['projection'] else DIM
        for a,b in extensions:
            line(*a,*b,stroke='#a3afa0',dash=True,**common)
        if curve:
            path(curve,stroke=color,width=2.5,dash=True,**common)
        else:
            line(*start,*end,stroke=color,width=1.15,**common)
            # Separate arrowheads, not calibrated marker lengths.
            from math import atan2,cos,sin
            angle=atan2(end[1]-start[1],end[0]-start[0])
            for pt,theta in ((start,angle),(end,angle+3.141592653589793)):
                for offset in (-.5,.5):
                    line(pt[0],pt[1],pt[0]+6*cos(theta+offset),pt[1]+6*sin(theta+offset),stroke=color,**common)
        for pt in (start,end):
            node('circle',x=pt[0],y=pt[1],r=2,fill=color,**common)
        x,y=label
        # Small opaque text backing keeps contour crossings legible.
        text(x,y,code,size=11,anchor='middle',fill=color,**common)

    if view!='side':
        dim(1,(333,100),(333,510),(352,310),[((154,100),(333,100)),((275,510),(333,510))])
        drop=139.75 if view=='front' else 112
        # Neck curve's actual cubic minimum is 3/4 of the control depth.
        dim(2 if view=='front' else 3,(200,100),(200,drop),(219,88),[((154,100),(246,100))])
        dim(4,(154,100),(118,112),(132,90))
        dim(30,(88,100),(88,260),(88,186),[((154,100),(88,100)),((113,260),(88,260))])
        for i,(_,y,_) in enumerate(WIDTHS):
            left=station_x[i]
            right=400-left
            dim(10+i,(left,y),(right,y),(307,y+4),[((right,y),(289,y))])
            if i<6:
                x=25+i*8
                dim(20+i,(x,100),(x,y),(x,y-9),[((154,100),(x,100)),((left,y),(x,y))])
        arc=[('M',118,112),('C',134,193,120,238,113,260)] if product=='cutoff' else [('M',118,112),('C',139,154,130,216,115,260)]
        dim(31 if view=='front' else 32,(118,112),(113 if product=='cutoff' else 115,260),(148,218),curve=arc)
        if product=='regular':
            path(arc,stroke='#a3afa0',dash=True)
            dim(50,(282,112),(334,194),(347,146))
            dim(51,(334,194),(300,220),(345,225))
    else:
        dim(30,(300,100),(300,320),(324,303),[((200,320),(300,320))])
        # All three horizontal distances refer to the SAME station y=230.
        dim(40,(151,230),(200,230),(102,216),[((151,230),(100,230))])
        dim(41,(200,230),(249,230),(299,248),[((249,230),(298,248))])
        dim(42,(151,367),(249,367),(200,390),[((151,230),(151,367)),((249,230),(249,367))])
        dim(43,(78,100),(78,230),(55,169),[((184,100),(78,100)),((151,230),(78,230))])
    return nodes


def svg(product, view):
    nodes=scene(product,view)
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 620" role="img" aria-label="{escape(product)} {escape(view)} technische Messzeichnung">',
         '<title>ARVO - schematische technische Ansicht, nicht maßstäblich</title>']
    active=None
    for n in nodes:
        point=n.get('point')
        if point!=active:
            if active:out.append('</g>')
            if point:
                d=next(d for d in definitions(product) if d['code']==point)
                out.append(f'<g class="measurement-line" data-point-id="{point}" data-axis="{n["axis"]}" data-region="{n["region"]}" tabindex="0" role="button" aria-label="{point}: {escape(d["name"])}"><title>{escape(d["name"])}</title>')
            active=point
        style=f' stroke="{n.get("stroke","none")}" fill="{n.get("fill","none")}" stroke-width="{n.get("width",1)}"'
        if n.get('dash'):style+=' stroke-dasharray="4 3"'
        if n['kind']=='path':
            commands=' '.join(c[0]+' '+' '.join(str(v) for v in c[1:]) for c in n['commands'])
            out.append(f'<path d="{commands}"{style}/>')
        elif n['kind']=='line':
            out.append(f'<line x1="{n["x1"]}" y1="{n["y1"]}" x2="{n["x2"]}" y2="{n["y2"]}"{style}/>')
        elif n['kind']=='circle':
            out.append(f'<circle cx="{n["x"]}" cy="{n["y"]}" r="{n["r"]}"{style}/>')
        else:
            out.append(f'<text x="{n["x"]}" y="{n["y"]}" font-family="Arial, sans-serif" font-size="{n.get("size",11)}" text-anchor="{n.get("anchor","start")}" fill="{n.get("fill",INK)}">{escape(n["text"])}</text>')
    if active:out.append('</g>')
    return ''.join(out)+'</svg>'


def pdf_drawing(product, view, axis=None):
    from reportlab.graphics.shapes import Drawing, Line, Path, Circle, String
    from reportlab.lib.colors import HexColor
    drawing=Drawing(400,620)
    for n in scene(product,view,axis):
        stroke=HexColor(n.get('stroke',INK));fill=HexColor(n['fill']) if n.get('fill') else None
        options=dict(strokeColor=stroke,strokeWidth=n.get('width',1))
        if n.get('dash'):options['strokeDashArray']=[4,3]
        if n['kind']=='line':shape=Line(n['x1'],620-n['y1'],n['x2'],620-n['y2'],**options)
        elif n['kind']=='circle':shape=Circle(n['x'],620-n['y'],n['r'],fillColor=fill,**options)
        elif n['kind']=='path':
            shape=Path(fillColor=fill,**options)
            for c in n['commands']:
                if c[0]=='M':shape.moveTo(c[1],620-c[2])
                elif c[0]=='L':shape.lineTo(c[1],620-c[2])
                elif c[0]=='C':shape.curveTo(c[1],620-c[2],c[3],620-c[4],c[5],620-c[6])
                elif c[0]=='Z':shape.closePath()
        else:shape=String(n['x'],620-n['y'],n['text'],fontName='Helvetica',fontSize=n.get('size',11),textAnchor=n.get('anchor','start'),fillColor=HexColor(n.get('fill',INK)))
        drawing.add(shape)
    return drawing
