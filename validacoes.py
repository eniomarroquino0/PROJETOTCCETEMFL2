# validacoes.py - validações de dados usadas pelo Flask e pelo Flet
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from config import ESSENCIAL_OPCOES


class ErroValidacao(Exception):
    """Erro com mensagem amigável, pronta para mostrar ao usuário."""


def validar_texto(texto, campo, minimo=3, maximo=100, obrigatorio=True):
    """Remove espaços das pontas e confere o tamanho do texto."""
    texto = (texto or "").strip()
    if not texto:
        if obrigatorio:
            raise ErroValidacao(f"O campo {campo} é obrigatório.")
        return None  # campo opcional vazio
    if not minimo <= len(texto) <= maximo:
        raise ErroValidacao(f"O campo {campo} deve ter entre {minimo} e {maximo} caracteres.")
    return texto


def validar_valor(valor):
    """Aceita '25,90' ou '25.90'. Devolve Decimal positivo com 2 casas."""
    try:
        v = Decimal(str(valor).strip().replace(",", "."))
    except InvalidOperation:
        raise ErroValidacao("Informe um valor numérico, por exemplo 25,90.")
    if not v.is_finite():
        raise ErroValidacao("Informe um valor numérico, por exemplo 25,90.")
    if v <= 0:
        raise ErroValidacao("O valor deve ser maior que zero.")
    if v > Decimal("99999999.99"):
        raise ErroValidacao("O valor é muito alto.")
    return v.quantize(Decimal("0.01"))


def validar_data(data):
    """Aceita aaaa-mm-dd ou dd/mm/aaaa. Devolve um objeto date."""
    if isinstance(data, datetime):
        return data.date()
    if isinstance(data, date):
        return data
    for formato in ("%Y-%m-%d", "%d/%m/%Y"):  # testa os dois formatos
        try:
            return datetime.strptime(str(data).strip(), formato).date()
        except ValueError:
            continue
    raise ErroValidacao("Informe uma data válida, por exemplo 21/11/2026.")


def validar_essencial(valor):
    """Aceita sim/nao (com ou sem acento). Devolve 'sim' ou 'nao'."""
    v = str(valor).strip().lower().replace("ã", "a")
    if v not in ESSENCIAL_OPCOES:
        raise ErroValidacao("Em 'essencial', escolha sim ou não.")
    return v


def validar_id(valor, campo="registro"):
    """Garante que o id é um número inteiro positivo."""
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        raise ErroValidacao(f"Escolha um(a) {campo} válido(a).")
    if numero <= 0:
        raise ErroValidacao(f"Escolha um(a) {campo} válido(a).")
    return numero