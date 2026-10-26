# Validação realizada

Execução local em 25/10/2026 (America/Sao_Paulo; os registros usam UTC em 26/10). Python 3.13 e n8n 2.22.6.

| Verificação | Resultado | Evidência |
| --- | --- | --- |
| Testes Python | 16 testes aprovados | [Saída do unittest](../evidencias/testes-python.txt) |
| Workflow real via CLI | Sucesso, 8 nós executados | [Resumo permitido da execução](../evidencias/execucao-n8n.json) |
| Segunda execução | Sucesso e reutilização dos arquivos | [Resumo da repetição](../evidencias/reexecucao-n8n.json) |
| Webhook publicado em instância isolada | HTTP 200, pronto_para_revisao, enviado=false | [Resposta observada](../evidencias/webhook-local.json) |
| Arquivos gerados | JSON, HTML e EML com dados fictícios | [Exemplos](../exemplos/) |

Os resumos de execução exportam somente campos selecionados; a base e os logs internos do n8n não fazem parte do repositório. As evidências correspondem a execução real. O fluxo executa chamadas HTTP à API Python, validações Code e Merge. O webhook foi acionado em 127.0.0.1:5679 com a API em 127.0.0.1:8765.

## Reprodução

1. Na raiz do projeto, executar python -m unittest discover -s tests -v.
2. Iniciar python -m rpa serve --port 8765 --output outbox.
3. Em outro terminal PowerShell, executar .\scripts\Test-N8n.ps1.
4. Para o webhook, encerrar outros processos n8n de demonstração e usar .\scripts\Start-N8n-Demo.ps1; chamar o endereço documentado no README.

Os scripts precisam de Node e de uma instalação n8n; o caminho pode ser informado por parâmetro. O coletor scripts/coletar_evidencias.py é uma ferramenta para os logs desta sessão e pressupõe arquivos em .runtime; não é requisito para executar o projeto.

## Limites do resultado

O modo demo usa template, não IA generativa. O adaptador Ollama foi testado com servidor HTTP falso para conferir requisição, resposta e erros; não foi executado com modelo real. O Gmail está desabilitado, sem credenciais, e não houve envio. O notebook Colab foi preparado sem saídas, sem execução no serviço. Dados externos de mercado não são consultados.

A idempotência cobre a geração local: entradas iguais, modo, modelo e URL iguais reutilizam arquivos. Não garante processamento único de e-mails por serviços externos. Não foi realizado teste de carga ou de múltiplos processos.
