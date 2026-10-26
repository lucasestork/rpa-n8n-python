import argparse
import json
import os
from pathlib import Path
from .server import make_server, load_fixture
from .domain import analyze_portfolio
from .briefing import create_briefing

parser=argparse.ArgumentParser(description='RPA educativo — dados fictícios, sem envio de e-mails')
parser.add_argument('command',choices=['demo','serve'])
parser.add_argument('--output',default='outbox')
parser.add_argument('--port',type=int,default=8765)
args=parser.parse_args()
mode=os.environ.get('RPA_LLM_MODE','demo')
model=os.environ.get('OLLAMA_MODEL','')
base=os.environ.get('OLLAMA_BASE_URL','http://127.0.0.1:11434')
if mode not in ('demo','ollama'):
    parser.error('RPA_LLM_MODE deve ser demo ou ollama')
if args.command=='demo':
    data={'carteira':analyze_portfolio(load_fixture('carteira-demo.json')),
          'noticias':load_fixture('noticias-demo.json')}
    print(json.dumps(create_briefing(data,Path(args.output),mode,model,base),ensure_ascii=False,indent=2))
else:
    server=make_server(args.port,Path(args.output),mode,model,base)
    print(f'API local: http://127.0.0.1:{server.server_port} — modo {mode}',flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
