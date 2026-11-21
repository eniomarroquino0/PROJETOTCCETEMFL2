# servicos.py - totais e resumos (usado pelo Flask e pelo Flet)
from datetime import date

import mysql.connector

from db import consultar
from validacoes import ErroValidacao


def total_do_mes(ano=None, mes=None):
    """Soma das despesas do mês. Sem argumentos, usa o mês atual."""
    hoje = date.today()
    ano, mes = ano or hoje.year, mes or hoje.month
    try:
        r = consultar(
            "SELECT COALESCE(SUM(valor), 0) AS total FROM despesas "
            "WHERE YEAR(data) = %s AND MONTH(data) = %s", (ano, mes), um=True)
    except mysql.connector.Error:
        raise ErroValidacao("Erro no banco de dados. Tente novamente.")
    return r["total"]


def total_por_categoria(ano=None, mes=None):
    """Dicionário {categoria: total} do mês (do maior para o menor gasto)."""
    hoje = date.today()
    ano, mes = ano or hoje.year, mes or hoje.month
    try:
        linhas = consultar(
            "SELECT c.nome, SUM(d.valor) AS total FROM despesas d "
            "JOIN categorias c ON c.id = d.categoria_id "
            "WHERE YEAR(d.data) = %s AND MONTH(d.data) = %s "
            "GROUP BY c.nome ORDER BY total DESC", (ano, mes))
    except mysql.connector.Error:
        raise ErroValidacao("Erro no banco de dados. Tente novamente.")
    return {l["nome"]: l["total"] for l in linhas}