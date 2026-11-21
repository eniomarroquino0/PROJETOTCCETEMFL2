# teste_crud.py - testa o CRUD completo no terminal (apaga o que criou no final)
from categorias_dao import (buscar_categoria, criar_categoria, editar_categoria,
                            excluir_categoria, listar_categorias)
from despesas_dao import (buscar_despesa, criar_despesa, editar_despesa,
                          excluir_despesa, listar_despesas)
from servicos import total_do_mes, total_por_categoria
from validacoes import ErroValidacao

print("--- CATEGORIAS ---")
print("Total cadastradas:", len(listar_categorias()))
cid = criar_categoria("Teste", "categoria de teste")
editar_categoria(cid, "Teste editada", "nova descrição")
print("Editada:", buscar_categoria(cid))
try:
    criar_categoria("Teste editada")
except ErroValidacao as e:
    print("Erro esperado (nome repetido):", e)

print("--- DESPESAS ---")
did = criar_despesa("Despesa de teste", "12,50", "21/11/2026", "sim", cid)
editar_despesa(did, "Despesa editada", "15,00", "2026-11-21", "nao", cid)
print("Editada:", buscar_despesa(did))
try:
    criar_despesa("x", "-5", "31/02/2026", "talvez", cid)
except ErroValidacao as e:
    print("Erro esperado (dados inválidos):", e)
try:
    excluir_categoria(cid)
except ErroValidacao as e:
    print("Erro esperado (categoria com despesas):", e)

print("--- LISTAGEM (menor para maior) ---")
for d in listar_despesas(essencial="sim"):
    print(d["valor"], d["descricao"], "|", d["categoria"])

print("--- TOTAIS ---")
print("Total do mês:", total_do_mes())
print("Por categoria:", total_por_categoria())

excluir_despesa(did)
excluir_categoria(cid)
print("Teste finalizado: dados de teste removidos.")