# API local Python

Iniciar: python -m rpa serve --port 8765 --output outbox. O servidor liga em 127.0.0.1 e utiliza biblioteca padrão.

| Método e rota | Resposta |
| --- | --- |
| GET /health | Estado da API |
| GET /api/analise | Objeto carteira com valores calculados a partir de data/carteira-demo.json |
| GET /api/noticias | Lista noticias de data/noticias-demo.json |
| POST /api/briefing | Recebe carteira e noticias, gera ou reutiliza briefing |
| GET /preview/ID | HTML do briefing gerado; ID deve conter exatamente 20 caracteres hexadecimais minúsculos |

O corpo POST é um objeto JSON com as chaves carteira e noticias, obtidas nas duas rotas GET. Consulte o nó Validar contexto unido no workflow para a composição exata. O limite do corpo é 65536 bytes e o Content-Type deve ser application/json.

A resposta de sucesso informa status=pronto_para_revisao, id, modo, gerado_por, enviado=false, texto e arquivos. A repetição acrescenta reutilizado=true. Nomes de arquivos retornados são relativos à pasta de saída; não são anexos enviados.

| Código | Situação |
| --- | --- |
| 200 | Sucesso |
| 400 | JSON inválido ou campos inconsistentes |
| 404 | Rota ou briefing inexistente |
| 413 | Corpo muito grande |
| 415 | Tipo de mídia incorreto |
| 502 | Falha no adaptador de geração |
| 500 | Falha ao persistir arquivos |

A carteira aceita somente origem ficticia e moeda BRL, 1 a 100 posições, tickers únicos, quantidade inteira positiva e preços positivos finitos. Valores monetários usam Decimal, arredondados a centavos. A geração exige o contexto fictício esperado; consulte rpa/domain.py e rpa/briefing.py para os limites.

Os arquivos usam uma chave SHA-256 truncada a 20 caracteres, derivada do contexto normalizado e da configuração de geração. A escrita substitui arquivos de forma atômica individualmente e grava JSON por último. Se faltarem arquivos, a geração é refeita. Um lock protege threads dentro do processo; não há transação entre processos.

O preview restringe o nome do arquivo e escapa o texto, com CSP e nosniff. A API não possui autenticação e se destina somente ao computador local. Não a exponha à internet como serviço de produção.
