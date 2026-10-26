"""Cálculos determinísticos; não consulta mercado nem recomenda operações."""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

class ValidationError(ValueError):
    pass

def money(value):
    return format(value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), '.2f')

def _decimal(value, field):
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValidationError(f'{field}: número inválido')
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValidationError(f'{field}: número inválido') from exc
    if not number.is_finite() or number <= 0 or number > Decimal('1000000000'):
        raise ValidationError(f'{field}: fora do intervalo permitido')
    return number

def analyze_portfolio(payload):
    if not isinstance(payload, dict) or payload.get('origem') != 'ficticia':
        raise ValidationError('Esta demonstração aceita somente dados fictícios')
    if payload.get('moeda') != 'BRL':
        raise ValidationError('Moeda esperada: BRL')
    positions = payload.get('posicoes')
    if not isinstance(positions, list) or not 1 <= len(positions) <= 100:
        raise ValidationError('A carteira deve conter entre 1 e 100 posições')
    seen, rows, invested, current = set(), [], Decimal(0), Decimal(0)
    for position in positions:
        if not isinstance(position, dict):
            raise ValidationError('Posição inválida')
        ticker = position.get('ticker')
        if not isinstance(ticker, str) or not ticker.isascii() or not ticker.isalnum() or not 2 <= len(ticker) <= 10:
            raise ValidationError('Ticker inválido')
        if ticker in seen:
            raise ValidationError('Ticker duplicado')
        seen.add(ticker)
        quantity = position.get('quantidade')
        if type(quantity) is not int or not 1 <= quantity <= 1000000:
            raise ValidationError('Quantidade deve ser um inteiro positivo')
        average = _decimal(position.get('preco_medio'), 'preco_medio')
        reference = _decimal(position.get('preco_referencia'), 'preco_referencia')
        cost, value = average * quantity, reference * quantity
        invested += cost
        current += value
        rows.append({'ticker': ticker, 'quantidade': quantity, 'custo': money(cost),
                     'valor_referencia': money(value), 'variacao': money(value-cost)})
    return {'origem': 'ficticia', 'moeda': 'BRL', 'posicoes': rows,
            'total_investido': money(invested), 'total_referencia': money(current),
            'variacao_absoluta': money(current-invested),
            'variacao_percentual': money((current-invested) / invested * 100)}
