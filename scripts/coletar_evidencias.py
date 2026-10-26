"""Exporta apenas campos permitidos dos logs; nunca publica tokens ou a base do n8n."""
import json
import platform
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent

def extract_execution(path):
    text=path.read_text(encoding='utf-8-sig')
    decoder=json.JSONDecoder()
    for i,char in enumerate(text):
        if char!='{': continue
        try: value,_=decoder.raw_decode(text[i:])
        except ValueError: continue
        if isinstance(value,dict) and value.get('mode')=='cli' and 'finished' in value:
            return value
    raise ValueError('Resultado de execução não encontrado')

for logfile,outfile in [('execucao-n8n.log','execucao-n8n.json'),('reexecucao-n8n.log','reexecucao-n8n.json')]:
    result=extract_execution(ROOT/'.runtime'/logfile)
    run=result['data']['resultData']
    last=run['lastNodeExecuted']
    lastdata=run['runData'][last][-1]['data']['main'][0][0]['json']
    summary={'n8n_version':'2.22.6','python_version':platform.python_version(),
             'status':result['status'],'finished':result['finished'],
             'started_at_utc':result['startedAt'],'stopped_at_utc':result['stoppedAt'],
             'last_node':last,'nodes_executed':[{'name':name,'status':runs[-1].get('executionStatus')} for name,runs in run['runData'].items()],
             'output':lastdata,'scope':'CLI em base isolada; dados fictícios; sem envio de e-mail'}
    if summary['status']!='success' or not summary['finished']:
        raise ValueError('Execução sem sucesso')
    (ROOT/'evidencias'/outfile).write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')

shutil.copyfile(ROOT/'.runtime'/'testes-python.log',ROOT/'evidencias'/'testes-python.txt')
for item in (ROOT/'outbox').iterdir():
    if item.suffix in ('.json','.eml','.html'):
        shutil.copyfile(item,ROOT/'exemplos'/item.name)
print('Evidências resumidas e exemplos copiados; logs completos permanecem em .runtime/.')
