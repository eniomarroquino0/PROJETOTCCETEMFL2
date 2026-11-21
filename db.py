# db.py - conexão com o MySQL e funções auxiliares usadas por todos os DAOs
import mysql.connector

from config import DB_CONFIG


def conectar():
    """Abre e devolve uma conexão com o banco moneyflow."""
    return mysql.connector.connect(**DB_CONFIG)


def consultar(sql, params=(), um=False):
    """Executa um SELECT.
    Devolve uma lista de dicionários, ou só um dicionário se um=True."""
    con = conectar()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(sql, params)
        return cur.fetchone() if um else cur.fetchall()
    finally:
        con.close()


def executar(sql, params=()):
    """Executa INSERT, UPDATE ou DELETE e salva a alteração.
    Devolve o id gerado (útil depois de um INSERT)."""
    con = conectar()
    try:
        cur = con.cursor()
        cur.execute(sql, params)
        con.commit()
        return cur.lastrowid
    finally:
        con.close()