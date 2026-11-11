'use strict';
let workspace, revision, csrf, methods, dirty = false, busy = false;
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
  const missing=[], t=workspace.techpack;
  for (const p of t.measurements) {
    const blank=['name','method','source','S','M','L','minus','plus'].filter(k=>p[k]===null||p[k]==='');
    if (blank.length) missing.push(p.code+': '+blank.join(', '));
  }
  for (const k of ['composition','gsm','source']) if(t.fabric[k]===null||t.fabric[k]==='')missing.push('Produktionsstoff: '+k);
  for (const k of ['construction','artwork']) if(!t[k])missing.push(k+': offen');
  $('#missing-count').textContent = `(${missing.length} offene Zeilen/Felder)`;
  $('#missing').replaceChildren(...missing.map(x=>el('li',x)));
}
function renderTech() {
  const t=workspace.techpack, parent=$('#tech-fields');parent.replaceChildren();
  field(parent,'Produkt',t,'title');field(parent,'Version / Arbeitsstand',t,'version');field(parent,'Kontextquelle / Datum',t,'source');
  field(parent,'Silhouette / Kontext',t,'context',{area:true});field(parent,'Verarbeitung / Nähte / Labels / Pflege',t,'construction',{area:true});field(parent,'Zeichnungen / Design / Platzierung / Dateiverweise',t,'artwork',{area:true});
  const tbody=$('#measurements tbody');tbody.replaceChildren();
  for (const p of t.measurements) {
    const tr=el('tr');tr.append(el('td',p.code)); const def=el('td');
    const suggestion=el('label','Messpunkt-Vorschlag (bewusst zuordnen)'), select=el('select');
    select.setAttribute('aria-label',p.code+' Messpunkt-Vorschlag');select.append(el('option','Keine automatische Zuordnung'));
    for(const name of Object.keys(methods)){select.append(el('option',name));}
    select.addEventListener('change',()=>{ if(methods[select.value]) { if((p.name||p.method)&&!confirm('Definition und Methode dieses Maßpunkts durch den Vorschlag ersetzen?')) {select.selectedIndex=0;return;} p.name=select.value;p.method=methods[select.value];changed();renderTech();} });
    suggestion.append(select);def.append(suggestion);
    field(def,p.code+' Definition',p,'name');field(def,p.code+' Messmethode',p,'method',{area:true});tr.append(def);
    for(const key of ['S','M','L','minus','plus']) {const cell=el('td');field(cell,p.code+' '+key,p,key,{number:true});tr.append(cell);}
    const source=el('td');field(source,p.code+' Quelle / Zustand',p,'source',{area:true});tr.append(source);tbody.append(tr);
  }
  const fabric=$('#fabric-fields');fabric.replaceChildren();
  for (const [key,label] of Object.entries({composition:'Zusammensetzung',gsm:'Flächengewicht (GSM)',stretch:'Stretch / Rücksprung',finish:'Finish / Verarbeitung',color:'Farbe / Farbcode',source:'Beleg / Datum',notes:'Stoffhinweise / Evidenzstatus'})) field(fabric,label,t.fabric,key,{number:key==='gsm',area:key==='notes'});
  const ref=$('#reference');ref.replaceChildren();field(ref,'Referenzstoff (separat, kein Produktionsstandard)',t,'reference',{area:true});updateMissing();
}
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
  const body=await r.json();workspace=body.data;revision=body.revision;csrf=body.csrf;methods=body.methods;dirty=false;render();$('#save-state').textContent='Gespeichert · Revision '+revision;$('#save').disabled=false;
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
$('#pdf').onclick=async()=>{if(busy)return;if(dirty&&!(await save()))return;window.location.assign('/api/techpack.pdf');};
$('#backup').onclick=()=>{if(!workspace)return;const blob=new Blob([JSON.stringify({revision,data:workspace},null,2)],{type:'application/json'});const a=el('a');a.href=URL.createObjectURL(blob);a.download='ARVO-Arbeitsstand.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);};
$('#import').onchange=async e=>{try{const f=e.target.files[0];if(!f)return;if(f.size>2000000)throw new Error('Datei zu groß');const body=JSON.parse(await f.text());if(!body.data||body.data.schemaVersion!==1)throw new Error('Unbekanntes Dateiformat');if(!confirm('JSON in den Editor laden? Vorhandene Eingaben werden ersetzt. Die Datenbank ändert sich erst beim Speichern.'))return;
  // Validate first without writing. Server-side save remains authoritative.
  const candidate=body.data;if(!candidate.techpack||!Array.isArray(candidate.tasks)||!Array.isArray(candidate.suppliers)||!Array.isArray(candidate.samples))throw new Error('Arbeitsbereiche fehlen');
  const r=await fetch('/api/validate',{method:'POST',headers:{'Content-Type':'application/json','X-ARVO-CSRF':csrf},body:JSON.stringify(candidate)});const result=await r.json();if(!r.ok)throw new Error(result.error);
  workspace=candidate;changed();render();message('JSON im Editor geladen; noch nicht gespeichert.');
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
