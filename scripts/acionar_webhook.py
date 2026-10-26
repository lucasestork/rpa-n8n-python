"""Aciona somente o webhook local de demonstração; não envia mensagens."""
import argparse
from urllib import request
from urllib.parse import urlparse

parser=argparse.ArgumentParser()
parser.add_argument('--url',default='http://127.0.0.1:5679/webhook-test/rpa-briefing-demo')
args=parser.parse_args()
url=urlparse(args.url)
if url.scheme!='http' or url.hostname not in ('localhost','127.0.0.1','::1'):
    parser.error('Este acionador de demonstração aceita apenas o n8n local')
req=request.Request(args.url,data=b'{"executar":"demo"}',headers={'Content-Type':'application/json'},method='POST')
with request.build_opener(request.ProxyHandler({})).open(req,timeout=120) as response:
    print(response.read().decode('utf8'))
