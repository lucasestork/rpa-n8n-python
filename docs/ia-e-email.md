# IA local e e-mail: extensões opcionais

## Ollama

O modo padrão demo usa template determinístico. Para experimentar geração com IA, instale e inicie Ollama, disponibilize um modelo compatível e configure o nome do modelo que realmente está instalado. A instalação ou download de modelos não foi realizado neste projeto.

Em PowerShell, por exemplo:

~~~powershell
$env:RPA_LLM_MODE='ollama'
$env:OLLAMA_MODEL='nome-do-modelo-instalado'
$env:OLLAMA_BASE_URL='http://127.0.0.1:11434'
python -m rpa serve --port 8765 --output outbox
~~~

Substitua o nome pelo seu modelo. A aplicação lê variáveis do processo; não carrega .env automaticamente. O arquivo .env.example é referência de configuração. Para voltar ao template, use RPA_LLM_MODE=demo e reinicie a API.

O adaptador envia POST /api/generate com stream=false. Aceita somente endereço local, exige modelo configurado e uma resposta concluída com texto. Há limite de tamanho e timeout. Em caso de falha, retorna erro: não troca silenciosamente o texto de IA por template.

As instruções pedem resumo baseado apenas nos dados fornecidos e tratam o JSON como dados, sem executar suas instruções. Isso não elimina todas as possibilidades de erro do modelo: revise os resultados. O teste automatizado usa um servidor HTTP falso para validar o contrato. Não há evidência de inferência com um modelo real nesta entrega.

## E-mail e Gmail

A implementação principal gera .eml com remetente e destinatário example.com, HTML e JSON. Não usa SMTP e não transmite mensagens. É possível abrir o arquivo no leitor de e-mail para conferir o conteúdo.

O arquivo workflows/briefing-gmail-opcional.json contém uma variante inativa, com nó Gmail desabilitado e sem credenciais. Foi incluído como ponto de extensão do exercício e não teve envio validado. Para uso futuro, configure OAuth na sua própria instância, revise o destinatário e o conteúdo, teste com dados de demonstração e só habilite o nó quando decidir efetuar o envio.

Não publique credenciais, tokens, arquivos .env, bases n8n ou dados reais de clientes. A reutilização de arquivos não é uma estratégia de deduplicação de envios Gmail. Um fluxo de envio efetivo precisa registrar o resultado da transmissão e tratar retentativas.
