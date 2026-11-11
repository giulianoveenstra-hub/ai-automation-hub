import copy
import http.client
import json
import tempfile
import threading
import unittest
from io import BytesIO
from pathlib import Path
from pypdf import PdfReader
from command_center.model import seed, legacy_seed, validate, missing, migrate
from command_center.storage import Store, Conflict
from command_center.server import make_server
from command_center.pdf_export import export_pdf


class ModelTests(unittest.TestCase):
    def test_unknowns_and_draft_context(self):
        data=seed()
        self.assertEqual(len(data['techpack']['measurements']),43)
        self.assertTrue(all(p['S'] is None and p['name']=='' for p in data['techpack']['measurements'][:19]))
        self.assertIsNone(data['techpack']['fabric']['gsm'])
        self.assertEqual(data['samples'][0]['status'],'WAITING')
        self.assertTrue(missing(data))
        validate(data)

    def test_bad_data(self):
        for value in (-1,float('nan'),float('inf'),True,'50'):
            data=seed();data['techpack']['measurements'][0]['S']=value
            with self.subTest(value=value),self.assertRaises(ValueError):validate(data)
        data=seed();data['tasks'].append(copy.deepcopy(data['tasks'][0]))
        with self.assertRaises(ValueError):validate(data)
        data=seed();data['samples'][0]['supplier']='missing'
        with self.assertRaises(ValueError):validate(data)
        data=seed();data['tasks'][0]['due']='2026-02-30'
        with self.assertRaises(ValueError):validate(data)
        data=seed();data['techpack']['measurements'].reverse()
        with self.assertRaises(ValueError):validate(data)

    def test_seed_only_once_and_concurrency(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'workspace.db';store=Store(path)
            a=store.read();b=store.read();a['data']['tasks'][0]['status']='DONE'
            # A response must identify its own transaction, even if another read
            # could already observe a newer writer.
            from unittest.mock import patch
            with patch.object(store, 'read', return_value={'revision':999,'data':seed()}):
                saved=store.save(a['revision'],a['data'])
            self.assertEqual(saved['revision'],a['revision']+1)
            self.assertEqual(saved['data'],a['data'])
            with self.assertRaises(Conflict):store.save(b['revision'],b['data'])
            self.assertEqual(Store(path).read(),saved)
            self.assertEqual(len(saved['data']['tasks']),len(seed()['tasks']))

    def test_pdf_preserves_blanks_zero_and_user_text(self):
        data=seed();p=data['techpack']['measurements'][0]
        p.update(name='Brustweite',method='Flach <ohne Zug> & trocken',source='Testbeleg',S=48.25,minus=0)
        pdf=export_pdf(data,7)
        text='\n'.join(page.extract_text() for page in PdfReader(BytesIO(pdf)).pages)
        self.assertIn('48.25',text);self.assertIn('OFFEN',text)
        self.assertIn('KEINE PRODUKTIONSFREIGABE',text)
        self.assertIn('Revision 7',text);self.assertIn('<ohne Zug> & trocken',text)
        self.assertGreater(len(PdfReader(BytesIO(pdf)).pages),1)

    def test_long_pdf_fields(self):
        data=seed();data['techpack']['measurements'][0]['method']='Langes Messprotokoll. '*180
        self.assertTrue(export_pdf(data,0).startswith(b'%PDF'))


    def test_lossless_version_one_migration(self):
        old=legacy_seed()
        old['techpack']['measurements'][5].update(name='F aus Originalbeleg',method='Nicht automatisch umdeuten',S=51.2,source='Privater Beleg')
        old['tasks'][0]['notes']='Bestehende Aufgabe behalten'
        old['techpack']['construction']='Bestehende Verarbeitungsnotiz'
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'db'
            import sqlite3
            with sqlite3.connect(path) as db:
                db.execute('CREATE TABLE workspace (id INTEGER PRIMARY KEY,revision INTEGER,data TEXT)')
                db.execute('INSERT INTO workspace VALUES (1,7,?)',(json.dumps(old),))
            store=Store(path);new=store.read()
            self.assertEqual(new['revision'],8)
            self.assertEqual(new['data']['techpack']['measurements'][:19],old['techpack']['measurements'])
            for key in ('tasks','suppliers','samples'):
                self.assertEqual(new['data'][key],old[key])
            self.assertEqual(new['data']['techpack']['construction'],old['techpack']['construction'])
            self.assertTrue(all(p['S'] is None for p in new['data']['regularTechpack']['measurements']))
            self.assertEqual(Store(path).read(),new)
            with sqlite3.connect(path) as db:
                self.assertEqual(json.loads(db.execute('SELECT data FROM migration_backup').fetchone()[0]),old)
            with self.assertRaises(Conflict):store.save(7,migrate(old))

    def test_geometry_ids_and_separate_measurement_systems(self):
        from command_center.technical import definitions
        from command_center.drawings import scene,svg
        for product,prefix in (('cutoff','AT'),('regular','RF')):
            data=seed();pack=data['techpack'] if product=='cutoff' else data['regularTechpack']
            known={p['code'] for p in pack['measurements']}
            drawn=set()
            for view in ('front','back','side'):
                nodes=scene(product,view)
                ids={n['point'] for n in nodes if 'point' in n}
                self.assertTrue(ids<=known);drawn|=ids
                if view in ('front','back'):
                    self.assertTrue({prefix+str(i) for i in range(10,17)}<=ids)
                    self.assertTrue(any(n['kind']=='circle' and n['x']==154 and n['y']==100 and 'point' not in n for n in nodes))
                xml=svg(product,view)
                self.assertIn('tabindex="0"',xml)
            self.assertEqual(drawn,{d['code'] for d in definitions(product)})
            self.assertIn(prefix+'02',{n.get('point') for n in scene(product,'front')})
            self.assertNotIn(prefix+'03',{n.get('point') for n in scene(product,'front')})
            self.assertTrue({prefix+str(i) for i in range(40,44)}<={n.get('point') for n in scene(product,'side')})
            d=next(d for d in definitions(product) if d['code']==prefix+'42')
            self.assertEqual(d['kind'],'projection')
        data=seed();data['techpack']['measurements'][19]['name']='Neu umgedeutet'
        with self.assertRaises(ValueError):validate(data)

    def test_pdf_structure_and_variant_isolation(self):
        data=seed();data['techpack']['measurements'][19]['S']=49.125
        data['regularTechpack']['measurements'][0]['S']=73.875
        for product,own,other in (('cutoff','49.125','73.875'),('regular','73.875','49.125')):
            pdf=export_pdf(data,9,product)
            text='\n'.join(page.extract_text() for page in PdfReader(BytesIO(pdf)).pages)
            self.assertIn(own,text);self.assertNotIn(other,text)
            headings=['01 / Product Overview','02 / Front View','03 / Back View','04 / Side View','05 / Measurement Table','06 / Fabric & Construction','07 / Care Label','08 / Neck Label','09 / Hang Tag','10 / Offene Angaben']
            self.assertEqual([text.index(h) for h in headings],sorted(text.index(h) for h in headings))
            self.assertNotIn('Seitenschlitz',text)
            self.assertIn('KEINE direkten Flachmaße',text)


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder=tempfile.TemporaryDirectory()
        cls.server=make_server(Path(cls.folder.name)/'db',0)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join();cls.folder.cleanup()
    def request(self,path,body=None,headers=None):
        conn=http.client.HTTPConnection('127.0.0.1',self.server.server_port)
        conn.request('GET' if body is None else 'POST',path,body=json.dumps(body) if body is not None else None,headers=headers or {})
        response=conn.getresponse();result=(response.status,response.read(),dict(response.getheaders()));conn.close();return result
    def test_real_roundtrip_and_security(self):
        status,raw,_=self.request('/api/workspace');self.assertEqual(status,200)
        initial=json.loads(raw);headers={'Content-Type':'application/json','X-ARVO-CSRF':initial['csrf']}
        initial['data']['techpack']['fabric']['composition']='Teststoff (nur Test)'
        payload={k:initial[k] for k in ('revision','data')}
        self.assertEqual(self.request('/api/workspace',payload)[0],403)
        self.assertEqual(self.request('/api/workspace',payload,{**headers,'Origin':'https://evil.example'})[0],403)
        self.assertEqual(self.request('/api/workspace',headers={'Host':'evil.example'})[0],403)
        self.assertEqual(self.request('/private/workspace.sqlite3')[0],404)
        self.assertEqual(self.request('/api/validate',payload['data'],headers)[0],200)
        self.assertEqual(self.request('/api/drawing?product=regular&view=side')[0],200)
        self.assertEqual(self.request('/api/drawing?product=bad&view=side')[0],400)
        self.assertEqual(self.request('/api/workspace',payload,headers)[0],200)
        self.assertEqual(self.request('/api/workspace',payload,headers)[0],409)
        exported=json.loads(self.request('/api/export.json')[1])
        self.assertEqual(exported['data']['techpack']['fabric']['composition'],'Teststoff (nur Test)')
        status,pdf,headers=self.request('/api/techpack.pdf')
        self.assertEqual(status,200);self.assertTrue(pdf.startswith(b'%PDF'));self.assertEqual(headers['Content-Type'],'application/pdf')
        payload['data']['schemaVersion']=99
        self.assertEqual(self.request('/api/workspace',payload,{'Content-Type':'application/json','X-ARVO-CSRF':initial['csrf']})[0],400)

if __name__=='__main__':unittest.main()
