import copy
import http.client
import json
import tempfile
import threading
import unittest
from io import BytesIO
from pathlib import Path
from pypdf import PdfReader
from command_center.model import seed, validate, missing
from command_center.storage import Store, Conflict
from command_center.server import make_server
from command_center.pdf_export import export_pdf


class ModelTests(unittest.TestCase):
    def test_unknowns_and_draft_context(self):
        data=seed()
        self.assertEqual(len(data['techpack']['measurements']),19)
        self.assertTrue(all(p['S'] is None and p['name']=='' for p in data['techpack']['measurements']))
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
        self.assertEqual(self.request('/api/workspace',payload,headers)[0],200)
        self.assertEqual(self.request('/api/workspace',payload,headers)[0],409)
        exported=json.loads(self.request('/api/export.json')[1])
        self.assertEqual(exported['data']['techpack']['fabric']['composition'],'Teststoff (nur Test)')
        status,pdf,headers=self.request('/api/techpack.pdf')
        self.assertEqual(status,200);self.assertTrue(pdf.startswith(b'%PDF'));self.assertEqual(headers['Content-Type'],'application/pdf')
        payload['data']['schemaVersion']=99
        self.assertEqual(self.request('/api/workspace',payload,{'Content-Type':'application/json','X-ARVO-CSRF':initial['csrf']})[0],400)

if __name__=='__main__':unittest.main()
