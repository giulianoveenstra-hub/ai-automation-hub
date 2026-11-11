'use strict';
let workspace, revision, csrf, methods, catalog, dirty = false, busy = false;
const statuses = ['OPEN','WAITING','DONE','DECIDED'];
const owners = ['Robin','Giuliano','Gemeinsam'];
const $ = s => document.querySelector(s);
const el = (tag, text, cls) => { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; if (cls) n.className = cls; return n; };
function message(text='') { $('#message').textContent = text; }
function changed() { dirty = true; $('#save-state').textContent = 'Ungespeicherte Änderungen'; updateMissing(); }
function field(parent, label, obj, key, {number=false, area=false, choices=null, type='text'}={}) {
  const wrap = el('label',label), input = el(choices ? 'select' : area ? 'textarea' : 'input');
  if (choices) choices.forEach(v => { const o=el('option',typeof v==='string'?v:v.label);o.value=typeof v==='string'?v:v.value;input.append(o); });
  else if (!area) { input.type = number ? 'number' : type; if (number) { input.min='0';input.step='any';input.max='1000000'; } }
  input.value = obj[key] ?? ''; input.dataset.key=key;
  input.addEventListener('input',()=>{ obj[key] = number ? (input.value === '' ? null : Number(input.value)) : input.value; changed(); });
  wrap.append(input);parent.append(wrap);return input;
}
function updateMissing() {
  if (!workspace) return;
  const missing=[], t=currentTech();
  for (const p of t.measurements) {
    const blank=['name','method','source','S','M','L','minus','plus'].filter(k=>p[k]===null||p[k]==='');
    if (blank.length) missing.push(p.code+': '+blank.join(', '));
  }
  for (const k of ['composition','gsm','source']) if(t.fabric[k]===null||t.fabric[k]==='')missing.push('Produktionsstoff: '+k);
  for (const k of ['construction','artwork']) if(!t[k])missing.push(k+': offen');
  $('#missing-count').textContent = `(${missing.length} offene Zeilen/Felder)`;
  $('#missing').replaceChildren(...missing.map(x=>el('li',x)));
}
function currentTech() { return workspace.activeProduct === 'regular' ? workspace.regularTechpack : workspace.techpack; }
function currentCatalog() { return catalog[workspace.activeProduct]; }
let selectedPoint = '', drawingGeneration = 0;
function renderTech() {
  const t=currentTech(), parent=$('#tech-fields');parent.replaceChildren();
  $('#product-select').value=workspace.activeProduct;
  field(parent,'Produkt',t,'title');field(parent,'Version / Arbeitsstand',t,'version');field(parent,'Kontextquelle / Datum',t,'source');
  field(parent,'Silhouette / Kontext',t,'context',{area:true});field(parent,'Design / Zeichnungen / Dateiverweise',t,'artwork',{area:true});
  const tbody=$('#measurements tbody');tbody.replaceChildren();
  const defined=new Map(currentCatalog().map(d=>[d.code,d]));
  // Existing records retain their storage order; meaningful new geometry is shown first.
  const ordered=[...t.measurements.filter(p=>defined.has(p.code)),...t.measurements.filter(p=>!defined.has(p.code))];
  for (const p of ordered) {
    const d=defined.get(p.code),tr=el('tr');tr.dataset.pointId=p.code;tr.id='row-'+p.code;
    const code=el('td'),button=el('button',p.code,'point-code');button.type='button';button.setAttribute('aria-label',p.code+' auswählen');button.onclick=()=>selectPoint(p.code);code.append(button);tr.append(code);
    const def=el('td');
    if(d) {def.append(el('strong',p.name));if(d.kind==='projection')def.append(el('span','PROJEKTION · KEIN FLACHMASS','projection-badge'));}
    else field(def,p.code+' Definition',p,'name');
    const details=el('details');details.append(el('summary',d?'Messdefinition':'Messdefinition bearbeiten'));
    if(d)details.append(el('p',p.method));else field(details,p.code+' Messmethode',p,'method',{area:true});
    def.append(details);tr.append(def);
    for(const key of ['S','M','L','minus','plus']) {const cell=el('td');field(cell,p.code+' '+key,p,key,{number:true});tr.append(cell);}
    const source=el('td');field(source,p.code+' Quelle / Zustand',p,'source',{area:true});tr.append(source);
    tr.addEventListener('click',()=>selectPoint(p.code));tbody.append(tr);
  }
  const fabric=$('#fabric-fields');fabric.replaceChildren();
  for (const [key,label] of Object.entries({composition:'Zusammensetzung',gsm:'Flächengewicht (GSM)',stretch:'Stretch / Rücksprung',finish:'Finish / Verarbeitung',color:'Farbe / Farbcode',source:'Beleg / Datum',notes:'Stoffhinweise / Evidenzstatus'})) field(fabric,label,t.fabric,key,{number:key==='gsm',area:key==='notes'});
  const construction=$('#construction-fields');construction.replaceChildren();field(construction,'Verarbeitung / Nähte / Labels / Pflege',t,'construction',{area:true});
  const ref=$('#reference');ref.replaceChildren();field(ref,'Referenzstoff (separat, kein Produktionsstandard)',t,'reference',{area:true});
  const picker=$('#point-select');picker.replaceChildren(el('option','Messpunkt auswählen'));picker.firstChild.value='';
  for(const p of ordered){const option=el('option',p.code+' / '+(p.name||'Originaldefinition offen'));option.value=p.code;picker.append(option);}
  if(!t.measurements.some(p=>p.code===selectedPoint))selectedPoint='';
  picker.value=selectedPoint;renderDrawings();renderLabels();updateMissing();
}
async function renderDrawings() {
  const generation=++drawingGeneration, product=workspace.activeProduct,grid=$('#drawing-grid');grid.replaceChildren();
  try {
    for(const [view,title] of [['front','Front View'],['back','Back View'],['side','Side View']]) {
      const r=await fetch('/api/drawing?product='+product+'&view='+view);if(!r.ok)throw new Error('Zeichnung konnte nicht geladen werden');
      const text=await r.text();if(generation!==drawingGeneration)return;
      const card=el('article',undefined,'drawing-card');card.dataset.view=view;card.append(el('h4',title));
      const svg=new DOMParser().parseFromString(text,'image/svg+xml').documentElement;
      if(svg.localName!=='svg')throw new Error('Ungültige Zeichnung');card.append(document.importNode(svg,true));
      card.append(el('p',view==='side'?'Projektion: vorne/hinten getrennt erfassen. Braun = kein direktes Flachmaß.':'HPS = halsseitiger Schulterpunkt. Gemeinsame Breiten-ID = eine Gesamtbreitenkontrolle.','drawing-note'));
      for(const g of card.querySelectorAll('[data-point-id]')){
        const select=()=>{selectPoint(g.dataset.pointId);$('#row-'+g.dataset.pointId)?.scrollIntoView({behavior:'smooth',block:'center'});};
        g.addEventListener('click',select);g.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();select();}});
      }
      grid.append(card);
    }
    applyDrawingFilter();selectPoint(selectedPoint);
  } catch(e){if(generation===drawingGeneration)message(e.message);}
}
function selectPoint(code) {
  selectedPoint=code;$('#point-select').value=code;
  for(const row of document.querySelectorAll('#measurements tbody tr'))row.classList.toggle('selected',row.dataset.pointId===code);
  for(const group of document.querySelectorAll('#drawing-grid [data-point-id]'))group.classList.toggle('selected',group.dataset.pointId===code);
  const p=currentTech().measurements.find(p=>p.code===code),d=currentCatalog().find(d=>d.code===code),info=$('#point-info');info.replaceChildren();
  if(p){info.append(el('strong',p.code+' / '+(p.name||'Originaldefinition offen')));info.append(el('p',p.method||'Keine belegte Zuordnung zu einer Zeichnung. A–S bleiben unverändert; Originaldefinition ergänzen.'));if(d?.kind==='projection')info.append(el('p','Projektionsmaß: keine direkte flache Schnittkontrolle. Alternative Kurvenmaße und Tiefe separat dokumentieren.','projection-note'));}
  else info.append(el('p','Messpunkt in Zeichnung oder Tabelle auswählen. Maße und Toleranzen bleiben bis zur Ermittlung offen.'));
  applyDrawingFilter();
}
function applyDrawingFilter() {
  const filter=$('#drawing-filter').value;
  for(const g of document.querySelectorAll('#drawing-grid [data-point-id]')){
    const show=filter==='all'||(filter==='selected'?g.dataset.pointId===selectedPoint:g.dataset.axis===filter||g.dataset.region===filter);
    g.classList.toggle('filtered-out',!show);g.setAttribute('aria-hidden',String(!show));g.setAttribute('tabindex',show?'0':'-1');
  }
}
function renderLabels() {
  const grid=$('#labels-grid');grid.replaceChildren();
  const labels=currentTech().labels;
  const titles={care:'Care Label',neck:'Neck Label',hang:'Hang Tag'};
  const specs={width:'Breite (mm)',height:'Höhe (mm)',material:'Material',printing:'Druckverfahren',source:'Beleg / Datum',composition:'Materialzusammensetzung',care:'Pflegehinweise (unbestätigt = offen)',size:'Größe',productInfo:'Produktinformationen',origin:'Herkunft (nur mit Beleg)',claim:'Claim',placement:'Platzierung',construction:'Verarbeitungsart',optionalClaim:'Optionaler Claim (Entwurf)',hole:'Lochposition',cord:'Schnur / Befestigung'};
  for(const kind of ['care','neck','hang']) {
    const card=el('article',undefined,'label-card');card.append(el('h4',titles[kind]));
    const preview=el('div',undefined,'label-preview '+kind);preview.id='preview-'+kind;card.append(preview);
    const fields=el('div',undefined,'label-fields');
    for(const key of Object.keys(labels[kind])) {const input=field(fields,titles[kind]+' / '+specs[key],labels[kind],key,{number:['width','height'].includes(key),area:['care','productInfo','source'].includes(key)});input.addEventListener('input',()=>updateLabelPreview(kind));}
    card.append(fields);grid.append(card);updateLabelPreview(kind);
  }
}
function updateLabelPreview(kind) {
  const spec=currentTech().labels[kind],preview=$('#preview-'+kind);preview.replaceChildren();
  const line=(value,cls)=>el('div',value||'OFFEN',cls);
  if(kind==='care') {
    const paper=el('div',undefined,'care-paper');paper.append(line('ARVO','label-wordmark'),line(spec.composition),line(spec.care),line('GRÖSSE / '+(spec.size||'OFFEN')),line(spec.productInfo),line('HERKUNFT / '+(spec.origin||'OFFEN')));preview.append(paper);
  }else if(kind==='neck') {
    const patch=el('div',undefined,'neck-patch');patch.append(line('ARVO','label-wordmark'),line('S / M / L','size-options'),line(spec.claim||'CLAIM OPTIONAL / OFFEN'));preview.append(patch);
  }else {
    for(const face of ['VORDERSEITE','RÜCKSEITE']){const tag=el('div',undefined,'hang-face');tag.append(line(face,'face-caption'),line('ARVO','label-wordmark'));tag.append(line(face==='VORDERSEITE'?spec.claim:spec.optionalClaim));preview.append(tag);}
  }
  preview.append(line('ENTWURF · FORMAT '+(spec.width??'OFFEN')+' × '+(spec.height??'OFFEN')+' mm','label-format'));
}
$('#product-select').onchange=e=>{workspace.activeProduct=e.target.value;selectedPoint='';changed();renderTech();};
$('#drawing-filter').onchange=applyDrawingFilter;
$('#point-select').onchange=e=>selectPoint(e.target.value);
$('#go-row').onclick=()=>{if(selectedPoint)$('#row-'+selectedPoint)?.scrollIntoView({behavior:'smooth',block:'center'});};

function renderTasks() {
  const list=$('#task-list');list.replaceChildren();
  const rows=workspace.tasks.filter(t=>(!$('#owner-filter').value||t.owner===$('#owner-filter').value)&&(!$('#status-filter').value||t.status===$('#status-filter').value));
  if(!rows.length)list.append(el('p','Keine Aufgaben für diesen Filter.','muted'));
  for(const t of rows){const card=el('article',undefined,'card'),grid=el('div',undefined,'grid');
    field(grid,'Aufgabe',t,'title');field(grid,'Zuständigkeit',t,'owner',{choices:owners});field(grid,'Status',t,'status',{choices:statuses});field(grid,'Fällig (optional)',t,'due',{type:'date'});
    field(grid,'Notizen',t,'notes',{area:true});field(grid,'Quelle / Datum',t,'source',{area:true});card.append(grid);list.append(card);
  }
}
function renderSuppliers() {
  const list=$('#supplier-list');list.replaceChildren();
  for(const s of workspace.suppliers){const card=el('details',undefined,'card');card.append(el('summary',s.name+' / '+s.status));const grid=el('div',undefined,'grid');
    field(grid,'Hersteller',s,'name');field(grid,'Status',s,'status',{choices:statuses});field(grid,'MOQ (Umfang in Notizen klären)',s,'moq',{number:true});field(grid,'Musterkosten (Steuer/Umfang in Notizen)',s,'sampleCost',{number:true});
    field(grid,'Währung',s,'currency');field(grid,'Stoffzusammensetzung',s,'composition');field(grid,'GSM',s,'gsm',{number:true});field(grid,'Lieferzeit (Beleg nötig)',s,'leadTime');
    field(grid,'Status / Konditionen / Kandidat oder bestätigt',s,'notes',{area:true});field(grid,'Offene Fragen',s,'questions',{area:true});field(grid,'Quelle / Datum',s,'source',{area:true});card.append(grid);list.append(card);
  }
  renderSamples();
}
function renderSamples(){const list=$('#sample-list');list.replaceChildren();
  for(const s of workspace.samples){const card=el('article',undefined,'card'),grid=el('div',undefined,'grid');
    field(grid,'Muster / Swatch',s,'title');field(grid,'Hersteller',s,'supplier',{choices:workspace.suppliers.map(x=>({value:x.id,label:x.name}))});field(grid,'Status',s,'status',{choices:statuses});
    field(grid,'Angefragt am',s,'requested',{type:'date'});field(grid,'Eingegangen am',s,'received',{type:'date'});field(grid,'Prüfung: Fit / Stoff / Waschen / nächste Schritte',s,'review',{area:true});field(grid,'Quelle / Datum',s,'source',{area:true});card.append(grid);list.append(card);
  }
}
function render(){renderTech();renderTasks();renderSuppliers();}
async function load(){
  const r=await fetch('/api/workspace');if(!r.ok)throw new Error('Arbeitsstand konnte nicht geladen werden');
  const body=await r.json();workspace=body.data;revision=body.revision;csrf=body.csrf;methods=body.methods;catalog=body.catalog;dirty=false;render();$('#save-state').textContent='Gespeichert · Revision '+revision;$('#save').disabled=false;
}
async function save(){
  if(busy)return false;
  if(![...document.querySelectorAll('input')].every(i=>i.checkValidity())){message('Bitte ungültige Zahlen oder Datumsfelder korrigieren.');return false;}
  busy=true;$('#save').disabled=true;
  // Freeze the submitted snapshot; edits made while the request runs stay unsaved.
  const submitted=JSON.stringify(workspace);
  try{const r=await fetch('/api/workspace',{method:'POST',headers:{'Content-Type':'application/json','X-ARVO-CSRF':csrf},body:JSON.stringify({revision,data:JSON.parse(submitted)})});const body=await r.json();if(!r.ok)throw new Error(body.error);
    revision=body.revision;dirty=JSON.stringify(workspace)!==submitted;$('#save-state').textContent=dirty?'Weitere Änderungen ungespeichert':'Gespeichert · Revision '+revision;message(dirty?'Gesendeter Stand gespeichert; neuere Eingaben bitte nochmals speichern.':'Änderungen gespeichert.');return !dirty;
  }catch(e){message(e.message+'\nDeine Eingaben bleiben hier erhalten. Bei Konflikt zuerst JSON sichern, dann neu laden.');return false;}
  finally{busy=false;$('#save').disabled=false;}
}
$('#save').onclick=save;
$('#pdf').onclick=async()=>{if(busy)return;if(dirty&&!(await save()))return;window.location.assign('/api/techpack.pdf?product='+workspace.activeProduct);};
$('#backup').onclick=()=>{if(!workspace)return;const blob=new Blob([JSON.stringify({revision,data:workspace},null,2)],{type:'application/json'});const a=el('a');a.href=URL.createObjectURL(blob);a.download='ARVO-Arbeitsstand.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);};
$('#import').onchange=async e=>{try{const f=e.target.files[0];if(!f)return;if(f.size>2000000)throw new Error('Datei zu groß');const body=JSON.parse(await f.text());if(!body.data||![1,2].includes(body.data.schemaVersion))throw new Error('Unbekanntes Dateiformat');if(!confirm('JSON in den Editor laden? Vorhandene Eingaben werden ersetzt. Die Datenbank ändert sich erst beim Speichern.'))return;
  // Validate first without writing. Server-side save remains authoritative.
  const candidate=body.data;if(!candidate.techpack||!Array.isArray(candidate.tasks)||!Array.isArray(candidate.suppliers)||!Array.isArray(candidate.samples))throw new Error('Arbeitsbereiche fehlen');
  const r=await fetch('/api/validate',{method:'POST',headers:{'Content-Type':'application/json','X-ARVO-CSRF':csrf},body:JSON.stringify(candidate)});const result=await r.json();if(!r.ok)throw new Error(result.error);
  workspace=result.data;selectedPoint='';changed();render();message('JSON im Editor geladen; noch nicht gespeichert.');
}catch(err){message('Import fehlgeschlagen: '+err.message);}finally{e.target.value='';}};
$('#reload').onclick=()=>{if(!dirty||confirm('Ungespeicherte Änderungen verwerfen und gespeicherten Stand neu laden?'))load().then(()=>message()).catch(e=>message(e.message));};
for(const b of document.querySelectorAll('[data-tab]'))b.onclick=()=>{for(const panel of document.querySelectorAll('.panel'))panel.hidden=panel.id!==b.dataset.tab;for(const btn of document.querySelectorAll('[data-tab]'))btn.classList.toggle('active',btn===b);};
$('#owner-filter').onchange=renderTasks;$('#status-filter').onchange=renderTasks;
const id=()=>crypto.randomUUID();
$('#add-task').onclick=()=>{if(!workspace)return;const title=prompt('Aufgabentitel (vorher vorhandene Aufgaben prüfen):');if(!title?.trim())return;if(workspace.tasks.some(t=>t.title.trim().toLocaleLowerCase()===title.trim().toLocaleLowerCase()))return message('Aufgabe mit diesem Titel existiert bereits.');workspace.tasks.push({id:id(),title:title.trim(),owner:'Gemeinsam',status:'OPEN',due:'',notes:'',source:''});$('#owner-filter').value='';$('#status-filter').value='';changed();renderTasks();};
$('#add-supplier').onclick=()=>{if(!workspace)return;const name=prompt('Herstellername:');if(!name?.trim())return;if(workspace.suppliers.some(s=>s.name.trim().toLocaleLowerCase()===name.trim().toLocaleLowerCase()))return message('Hersteller existiert bereits.');workspace.suppliers.push({id:id(),name:name.trim(),status:'OPEN',notes:'',source:'',composition:'',gsm:null,moq:null,sampleCost:null,currency:'EUR',leadTime:'',questions:''});changed();renderSuppliers();};
$('#add-sample').onclick=()=>{if(!workspace?.suppliers.length)return message('Zuerst einen Hersteller anlegen.');workspace.samples.push({id:id(),supplier:workspace.suppliers[0].id,title:'Neues Muster',status:'OPEN',requested:'',received:'',review:'',source:''});changed();renderSamples();};
window.addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue='';}});
load().catch(e=>message(e.message));
