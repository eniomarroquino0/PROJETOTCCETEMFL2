# config.py - configurações compartilhadas pelo Flask e pelo Flet

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "moneyflow",
    "charset": "utf8mb4",
}

ESSENCIAL_OPCOES = ["sim", "nao"]

SECRET_KEY = "moneyflow-chave-de-estudo"