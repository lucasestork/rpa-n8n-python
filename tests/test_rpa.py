import copy
import json
import tempfile
import threading
import unittest
from email import policy
from email.parser import BytesParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import request, error
from unittest.mock import patch
from rpa.domain import analyze_portfolio, ValidationError
from rpa.briefing import create_briefing, GenerationError, ollama_text
from rpa.server import make_server, load_fixture


def data():
    return {'carteira':analyze_portfolio(load_fixture('carteira-demo.json')),
            'noticias':load_fixture('noticias-demo.json')}

class DomainTests(unittest.TestCase):
    def test_expected_decimal_totals(self):
        p=data()['carteira']
        self.assertEqual((p['total_investido'],p['total_referencia'],p['variacao_absoluta'],p['variacao_percentual']),('350.00','355.00','5.00','1.43'))
    def test_non_finite_and_non_positive_values(self):
        for value in ['NaN','Infinity','-1','0',True]:
            p=load_fixture('carteira-demo.json')
            p['posicoes'][0]['preco_medio']=value
            with self.subTest(value=value),self.assertRaises(ValidationError):
                analyze_portfolio(p)
    def test_reject_duplicate_tickers(self):
        p=load_fixture('carteira-demo.json')
        p['posicoes'].append(p['posicoes'][0])
        with self.assertRaises(ValidationError): analyze_portfolio(p)
    def test_reject_boolean_quantity(self):
        p=load_fixture('carteira-demo.json')
        p['posicoes'][0]['quantidade']=True
        with self.assertRaises(ValidationError): analyze_portfolio(p)
    def test_demo_source_required(self):
        p=load_fixture('carteira-demo.json'); p['origem']='real'
        with self.assertRaises(ValidationError): analyze_portfolio(p)

class BriefingTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out=Path(self.temp.name)
    def test_demo_never_calls_llm(self):
        with patch('rpa.briefing.ollama_text',side_effect=AssertionError('LLM não deveria ser chamado')):
            result=create_briefing(data(),self.out)
        self.assertFalse(result['enviado'])
        self.assertEqual(result['gerado_por'],'template_deterministico')
    def test_idempotency_reuses_artifacts(self):
        a=create_briefing(data(),self.out)
        b=create_briefing(data(),self.out)
        self.assertEqual(a['id'],b['id'])
        self.assertEqual(a['gerado_em'],b['gerado_em'])
        self.assertTrue(b['reutilizado'])
        self.assertEqual(len(list(self.out.iterdir())),3)
    def test_html_escaping_and_email_structure(self):
        d=data(); d['noticias']['itens'][0]['titulo']='<script>alert(1)</script>'
        result=create_briefing(d,self.out)
        page=(self.out/result['arquivos']['html']).read_text(encoding='utf8')
        self.assertNotIn('<script>',page)
        self.assertIn('&lt;script&gt;',page)
        msg=BytesParser(policy=policy.default).parsebytes((self.out/result['arquivos']['email']).read_bytes())
        self.assertEqual(msg['To'],'revisao@example.com')
        self.assertTrue(msg.is_multipart())
    def test_llm_failure_has_no_silent_fallback(self):
        with patch('rpa.briefing.ollama_text',side_effect=GenerationError('falha')):
            with self.assertRaises(GenerationError):
                create_briefing(data(),self.out,mode='ollama',model='teste')
        self.assertEqual(list(self.out.iterdir()),[])
    def test_missing_analysis_rejected(self):
        with self.assertRaises(ValidationError): create_briefing({'noticias':{}},self.out)
    def test_remote_ollama_not_allowed(self):
        with self.assertRaises(GenerationError): ollama_text(data(),'teste','https://example.com')
    def test_ollama_http_contract_with_fake_server(self):
        captured=[]
        class FakeOllama(BaseHTTPRequestHandler):
            def log_message(self,*args): pass
            def do_POST(self):
                captured.append((self.path,json.loads(self.rfile.read(int(self.headers['Content-Length'])))))
                body=json.dumps({'response':'Resumo fictício de teste.','done':True}).encode()
                self.send_response(200); self.end_headers(); self.wfile.write(body)
        server=ThreadingHTTPServer(('127.0.0.1',0),FakeOllama)
        thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
        try:
            text=ollama_text(data(),'modelo-falso-de-teste',f'http://127.0.0.1:{server.server_port}')
            self.assertIn('Resumo fictício',text)
            self.assertEqual(captured[0][0],'/api/generate')
            self.assertFalse(captured[0][1]['stream'])
        finally:
            server.shutdown();server.server_close();thread.join()

class HttpTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.server=make_server(0,Path(self.temp.name))
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.base=f'http://127.0.0.1:{self.server.server_port}'
        self.opener=request.build_opener(request.ProxyHandler({}))
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();self.temp.cleanup()
    def call(self,path,body=None,content_type='application/json'):
        req=request.Request(self.base+path,data=body,headers={'Content-Type':content_type})
        return self.opener.open(req,timeout=5)
    def test_api_end_to_end_and_replay(self):
        with self.call('/api/analise') as r: p=json.load(r)
        with self.call('/api/noticias') as r: n=json.load(r)
        body=json.dumps({**p,**n}).encode()
        with self.call('/api/briefing',body) as r: result=json.load(r)
        with self.call('/api/briefing',body) as r: replay=json.load(r)
        self.assertEqual(result['status'],'pronto_para_revisao')
        self.assertTrue(replay['reutilizado'])
        self.assertFalse(result['enviado'])
    def test_invalid_json_and_unsupported_media(self):
        for body,kind,status in [(b'{','application/json',400),(b'{}','text/plain',415)]:
            with self.subTest(status=status),self.assertRaises(error.HTTPError) as caught:
                self.call('/api/briefing',body,kind)
            self.assertEqual(caught.exception.code,status)
    def test_preview_requires_generated_id(self):
        with self.assertRaises(error.HTTPError) as caught: self.call('/preview/../../arquivo')
        self.assertEqual(caught.exception.code,404)
        body=json.dumps(data()).encode()
        with self.call('/api/briefing',body) as r: result=json.load(r)
        with self.call('/preview/'+result['id']) as r:
            self.assertIn('text/html',r.headers['Content-Type'])
            self.assertIn(b'Briefing',r.read())
    def test_unknown_route(self):
        with self.assertRaises(error.HTTPError) as caught: self.call('/missing')
        self.assertEqual(caught.exception.code,404)

if __name__=='__main__': unittest.main()
