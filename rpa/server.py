"""API HTTP local construída somente com a biblioteca padrão."""
import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from .domain import analyze_portfolio, ValidationError
from .briefing import create_briefing, GenerationError

ROOT = Path(__file__).resolve().parent.parent
MAX_BODY = 65536

def load_fixture(name):
    return json.loads((ROOT/'data'/name).read_text(encoding='utf8'))

def handler_for(output, mode='demo', model='', base_url='http://127.0.0.1:11434'):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,format,*args):
            pass  # Sem registrar corpo, e-mail ou prompts no log HTTP.
        def send_json(self,status,data):
            content=json.dumps(data,ensure_ascii=False).encode('utf8')
            self.send_response(status)
            self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Content-Length',str(len(content)))
            self.send_header('Cache-Control','no-store')
            self.end_headers()
            self.wfile.write(content)
        def do_GET(self):
            if self.path.startswith('/preview/'):
                key=self.path.removeprefix('/preview/')
                if not re.fullmatch(r'[0-9a-f]{20}',key):
                    self.send_json(404,{'erro':'previa_nao_encontrada'})
                    return
                page=Path(output)/(key+'.html')
                if not page.is_file():
                    self.send_json(404,{'erro':'previa_nao_encontrada'})
                    return
                content=page.read_bytes()
                self.send_response(200)
                self.send_header('Content-Type','text/html; charset=utf-8')
                self.send_header('Content-Length',str(len(content)))
                self.send_header('X-Content-Type-Options','nosniff')
                self.send_header('Content-Security-Policy',"default-src 'none'; style-src 'unsafe-inline'")
                self.end_headers()
                self.wfile.write(content)
            elif self.path=='/health':
                self.send_json(200,{'status':'ok','modo':mode,'origem_dados':'ficticia'})
            elif self.path=='/api/analise':
                self.send_json(200,{'carteira':analyze_portfolio(load_fixture('carteira-demo.json'))})
            elif self.path=='/api/noticias':
                self.send_json(200,{'noticias':load_fixture('noticias-demo.json')})
            else:
                self.send_json(404,{'erro':'rota_nao_encontrada'})
        def do_POST(self):
            if self.path!='/api/briefing':
                self.send_json(404,{'erro':'rota_nao_encontrada'})
                return
            try:
                length=int(self.headers.get('Content-Length','0'))
                if length<=0 or length>MAX_BODY:
                    self.send_json(413,{'erro':'tamanho_de_corpo_invalido'})
                    return
                if self.headers.get('Content-Type','').split(';')[0].strip().lower()!='application/json':
                    self.send_json(415,{'erro':'application_json_obrigatorio'})
                    return
                data=json.loads(self.rfile.read(length).decode('utf8'))
                result=create_briefing(data,output,mode,model,base_url)
                self.send_json(200,result)
            except (ValueError, UnicodeError, ValidationError):
                self.send_json(400,{'erro':'dados_invalidos'})
            except GenerationError:
                self.send_json(502,{'erro':'falha_no_modelo_sem_fallback_silencioso'})
            except OSError:
                self.send_json(500,{'erro':'falha_ao_gravar_artefatos'})
    return Handler

def make_server(port=8765,output=None,mode='demo',model='',base_url='http://127.0.0.1:11434'):
    return ThreadingHTTPServer(('127.0.0.1',port),handler_for(output or ROOT/'outbox',mode,model,base_url))
