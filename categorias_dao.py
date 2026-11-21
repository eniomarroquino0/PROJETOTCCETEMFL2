# categorias_dao.py - CRUD de categorias (usado pelo Flask e pelo Flet)
import mysql.connector

from db import consultar, executar
from validacoes import ErroValidacao, validar_id, validar_texto

ERRO_BANCO = "Erro no banco de dados. Tente novamente."


def listar_categorias():
    """Lista todas as categorias em ordem alfabética."""
    try:
        return consultar("SELECT id, nome, descricao FROM categorias ORDER BY nome")
    except mysql.connector.Error:
        raise ErroValidacao(ERRO_BANCO)


def buscar_categoria(id):
    """Devolve uma categoria (dicionário) ou None se não existir."""
    id = validar_id(id, "categoria")
    try:
        return consultar("SELECT id, nome, descricao FROM categorias WHERE id = %s", (id,), um=True)
    except mysql.connector.Error:
        raise ErroValidacao(ERRO_BANCO)


def criar_categoria(nome, descricao=None):
    """Valida e cadastra uma categoria. Devolve o id criado."""
    nome = validar_texto(nome, "nome", 2, 100)
    descricao = validar_texto(descricao, "descrição", 1, 255, obrigatorio=False)
    try:
        return executar("INSERT INTO categorias (nome, descricao) VALUES (%s, %s)", (nome, descricao))
    except mysql.connector.IntegrityError:  # nome é UNIQUE
        raise ErroValidacao("Já existe uma categoria com esse nome.")
    except mysql.connector.Error:
        raise ErroValidacao(ERRO_BANCO)


def editar_categoria(id, nome, descricao=None):
    """Valida e atualiza uma categoria existente."""
    if not buscar_categoria(id):
        raise ErroValidacao("Categoria não encontrada.")
    nome = validar_texto(nome, "nome", 2, 100)
    descricao = validar_texto(descricao, "descrição", 1, 255, obrigatorio=False)
    try:
        executar("UPDATE categorias SET nome = %s, descricao = %s WHERE id = %s", (nome, descricao, id))
    except mysql.connector.IntegrityError:
        raise ErroValidacao("Já existe uma categoria com esse nome.")
    except mysql.connector.Error:
        raise ErroValidacao(ERRO_BANCO)


def excluir_categoria(id):
    """Exclui a categoria, a não ser que ela tenha despesas."""
    if not buscar_categoria(id):
        raise ErroValidacao("Categoria não encontrada.")
    try:
        executar("DELETE FROM categorias WHERE id = %s", (id,))
    except mysql.connector.IntegrityError:  # chave estrangeira (RESTRICT)
        raise ErroValidacao("Esta categoria tem despesas e não pode ser excluída.")
    except mysql.connector.Error:
        raise ErroValidacao(ERRO_BANCO)