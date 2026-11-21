# despesas_dao.py - CRUD de despesas (usado pelo Flask e pelo Flet)
import mysql.connector

from db import consultar, executar
from validacoes import (ErroValidacao, validar_data, validar_essencial,
                        validar_id, validar_texto, validar_valor)

ERRO_BANCO = "Erro no banco de dados. Tente novamente."

# Colunas que a listagem devolve (já com o nome da categoria)
SELECT_DESPESAS = (
    "SELECT d.id, d.descricao, d.valor, d.data, d.essencial, d.categoria_id, c.nome AS categoria "
    "FROM despesas d JOIN categorias c ON c.id = d.categoria_id"
)


def _validar_campos(descricao, valor, data, essencial, categoria_id):
    """Valida todos os campos de uma despesa e devolve uma tupla limpa."""
    return (validar_texto(descricao, "descrição", 3, 150),
            validar_valor(valor),
            validar_data(data),
            validar_essencial(essencial),
            validar_id(categoria_id, "categoria"))


def criar_despesa(descricao, valor, data, essencial, categoria_id):
    """Valida e cadastra uma despesa. Devolve o id criado."""
    campos = _validar_campos(descricao, valor, data, essencial, categoria_id)
    try:
        return executar(
            "INSERT INTO despesas (descricao, valor, data, essencial, categoria_id) "
            "VALUES (%s, %s, %s, %s, %s)", campos)
    except mysql.connector.IntegrityError:  # categoria inexistente
        raise ErroValidacao("Categoria inexistente.")
    except mysql.connector.Error:
        raise ErroValidacao(ERRO_BANCO)


def listar_despesas(categoria_id=None, essencial=None):
    """Lista despesas, ordenadas do MENOR para o MAIOR valor.
    Filtros opcionais: categoria_id (filtro 1) e essencial (filtro 2)."""
    sql, params = SELECT_DESPESAS + " WHERE 1=1", []
    if categoria_id:
        sql += " AND d.categoria_id = %s"
        params.append(validar_id(categoria_id, "categoria"))
    if essencial:
        sql += " AND d.essencial = %s"
        params.append(validar_essencial(essencial))
    sql += " ORDER BY d.valor ASC"
    try:
        return consultar(sql, params)
    except mysql.connector.Error:
        raise ErroValidacao(ERRO_BANCO)


def buscar_despesa(id):
    """Devolve uma despesa (dicionário) ou None se não existir."""
    id = validar_id(id, "despesa")
    try:
        return consultar(SELECT_DESPESAS + " WHERE d.id = %s", (id,), um=True)
    except mysql.connector.Error:
        raise ErroValidacao(ERRO_BANCO)


def editar_despesa(id, descricao, valor, data, essencial, categoria_id):
    """Valida e atualiza uma despesa existente."""
    if not buscar_despesa(id):
        raise ErroValidacao("Despesa não encontrada.")
    campos = _validar_campos(descricao, valor, data, essencial, categoria_id)
    try:
        executar(
            "UPDATE despesas SET descricao=%s, valor=%s, data=%s, essencial=%s, categoria_id=%s "
            "WHERE id=%s", (*campos, id))
    except mysql.connector.IntegrityError:
        raise ErroValidacao("Categoria inexistente.")
    except mysql.connector.Error:
        raise ErroValidacao(ERRO_BANCO)


def excluir_despesa(id):
    """Exclui uma despesa."""
    if not buscar_despesa(id):
        raise ErroValidacao("Despesa não encontrada.")
    try:
        executar("DELETE FROM despesas WHERE id = %s", (id,))
    except mysql.connector.Error:
        raise ErroValidacao(ERRO_BANCO)