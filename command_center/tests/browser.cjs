// Optional browser check: npm install --no-save --prefix /tmp/arvo-browser playwright
// NODE_PATH=/tmp/arvo-browser/node_modules node command_center/tests/browser.cjs
// Start a disposable server first; never use your real workspace for this test.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
(async()=>{
  const browser=await chromium.launch({headless:true});
  const context=await browser.newContext({viewport:{width:1440,height:1000},acceptDownloads:true});
  const page=await context.newPage();const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  const url=process.env.ARVO_TEST_URL||'http://127.0.0.1:8765';
  await page.goto(url);await page.getByText('Gespeichert · Revision',{exact:false}).waitFor();
  const stale=await context.newPage();await stale.goto(url);await stale.getByText('Gespeichert · Revision',{exact:false}).waitFor();
  assert.equal(await page.locator('#measurements tbody tr').count(),19);
  assert.equal(await page.getByLabel('A S',{exact:true}).inputValue(),'');
  await page.getByLabel('A Messpunkt-Vorschlag',{exact:true}).selectOption({label:'Brustweite (1/2)'});
  assert.equal(await page.getByLabel('A Definition',{exact:true}).inputValue(),'Brustweite (1/2)');
  await page.getByLabel('A S',{exact:true}).fill('48.25');
  await page.getByLabel('A minus',{exact:true}).fill('0');
  await page.getByLabel('A Quelle / Zustand',{exact:true}).fill('TESTDATEN / kein reales ARVO-Maß');
  await page.getByRole('button',{name:'Änderungen speichern'}).click();await page.getByText('Änderungen gespeichert.',{exact:true}).waitFor();
  await stale.getByLabel('A S',{exact:true}).fill('99');
  await stale.getByRole('button',{name:'Änderungen speichern'}).click();await stale.getByText('Zwischenzeitlich geändert.',{exact:false}).waitFor();
  assert.equal(await stale.getByLabel('A S',{exact:true}).inputValue(),'99');
  // Backups keep unsaved edits even when saving conflicts.
  const downloadPromise=stale.waitForEvent('download');await stale.getByRole('button',{name:'JSON-Sicherung',exact:true}).click();
  const download=await downloadPromise;const raw=fs.readFileSync(await download.path(),'utf8');assert.equal(JSON.parse(raw).data.techpack.measurements[0].S,99);
  await page.reload();await page.getByText('Gespeichert · Revision',{exact:false}).waitFor();
  assert.equal(await page.getByLabel('A S',{exact:true}).inputValue(),'48.25');
  await page.getByRole('button',{name:'02 / Aufgaben'}).click();
  await page.locator('#owner-filter').selectOption('Robin');assert.equal(await page.locator('#task-list .card').count(),1);
  await page.locator('#owner-filter').selectOption('');await page.locator('#status-filter').selectOption('DONE');assert.equal(await page.locator('#task-list .card').count(),2);
  await page.getByRole('button',{name:'03 / Hersteller & Muster'}).click();
  await page.getByRole('button',{name:'+ Muster',exact:true}).click();
  await page.locator('#sample-list').getByLabel('Muster / Swatch',{exact:true}).last().fill('TEST / Fit-Muster');
  await page.getByRole('button',{name:'Änderungen speichern'}).click();await page.getByText('Änderungen gespeichert.',{exact:true}).waitFor();
  await page.getByRole('button',{name:'01 / Tech Pack'}).click();
  const pdfPromise=page.waitForEvent('download');await page.getByRole('button',{name:'PDF exportieren',exact:true}).click();
  const pdf=await pdfPromise;assert.ok(fs.readFileSync(await pdf.path()).subarray(0,5).equals(Buffer.from('%PDF-')));
  // Invalid import must leave current state intact.
  page.once('dialog',dialog=>dialog.accept());
  // Confirm is synchronous with the upload handler, so use handler before a second upload.
  await page.locator('#import').setInputFiles({name:'bad.json',mimeType:'application/json',buffer:Buffer.from('{"data":{"schemaVersion":1}}')});
  await page.getByText('Import fehlgeschlagen:',{exact:false}).waitFor();
  assert.equal(await page.getByLabel('A S',{exact:true}).inputValue(),'48.25');
  await page.getByRole('button',{name:'Gespeicherten Stand neu laden',exact:true}).click();
  await page.getByText('Gespeichert · Revision',{exact:false}).waitFor();
  fs.mkdirSync('command_center/test-output',{recursive:true});
  await page.evaluate(()=>window.scrollTo(0,0));
  await page.screenshot({path:'command_center/test-output/desktop.png',fullPage:false});
  await page.setViewportSize({width:390,height:844});await page.screenshot({path:'command_center/test-output/mobile.png',fullPage:false});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true);
  assert.deepEqual(errors,[]);console.log('Browser: measurements, persistence, conflict, backup, task filters, sample edit, PDF download, invalid import, mobile layout OK');
  await browser.close();
})().catch(e=>{console.error(e);process.exit(1);});
