# app_flet.py - telas desktop (Flet) do MoneyFlow
# Só cuida das telas: o CRUD e as validações vêm dos MESMOS módulos usados pelo Flask,
# e os dois sistemas gravam no mesmo banco MySQL.
from datetime import date

import flet as ft

from categorias_dao import (buscar_categoria, criar_categoria, editar_categoria,
                            excluir_categoria, listar_categorias)
from despesas_dao import (buscar_despesa, criar_despesa, editar_despesa,
                          excluir_despesa, listar_despesas)
from servicos import total_do_mes, total_por_categoria
from validacoes import ErroValidacao

AZUL, VERDE, CORAL, FUNDO = "#1f3a5f", "#2e9e6b", "#e4572e", "#f1f5f4"
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]


def brl(valor):
    """Formata número como moeda: 1234.5 -> R$ 1.234,50"""
    return "R$ " + f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def opcao(chave, texto):
    """Cria uma opção de Dropdown (o nome da classe muda entre versões do Flet)."""
    if hasattr(ft, "DropdownOption"):
        return ft.DropdownOption(key=chave, text=texto)
    return ft.dropdown.Option(key=chave, text=texto)


def botao(texto, ao_clicar, cor=VERDE):
    """Botão verde padrão do sistema."""
    return ft.FilledButton(texto, on_click=ao_clicar,
                           style=ft.ButtonStyle(bgcolor=cor, color="white"))


def main(page: ft.Page):
    page.title = "MoneyFlow"
    page.theme_mode = ft.ThemeMode.LIGHT  # tema claro: texto escuro e legível
    page.bgcolor = FUNDO
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    filtros = {"categoria": "todas", "essencial": "todas"}  # filtros atuais da listagem

    # ---------- peças reutilizadas em todas as telas ----------
    def mostrar_tela(*controles):
        page.clean()
        page.add(*controles)
        page.update()

    def menu():
        return ft.Row([
            ft.Text("MoneyFlow", size=26, weight=ft.FontWeight.BOLD, color=AZUL),
            ft.TextButton("Despesas", style=ft.ButtonStyle(color=AZUL),
                          on_click=lambda e: tela_despesas()),
            ft.TextButton("Categorias", style=ft.ButtonStyle(color=AZUL),
                          on_click=lambda e: tela_categorias()),
        ])

    def caixa_aviso(msg, ok=True):
        if not msg:
            return ft.Container()
        return ft.Container(
            content=ft.Text(msg, color="#1d6b46" if ok else "#a63a1a"),
            bgcolor="#dff3e8" if ok else "#fde3dc", padding=10, border_radius=8)

    def titulo(texto, acao_texto, acao):
        return ft.Row([ft.Text(texto, size=22, weight=ft.FontWeight.BOLD, color=AZUL),
                       botao(acao_texto, lambda e: acao())])

    def confirmar(pergunta, ao_confirmar, ao_cancelar):
        """Tela simples de confirmação antes de excluir."""
        mostrar_tela(menu(), ft.Text(pergunta, size=18),
                     ft.Row([botao("Sim, excluir", lambda e: ao_confirmar(), CORAL),
                             ft.OutlinedButton("Cancelar", on_click=lambda e: ao_cancelar())]))

    # ---------- despesas ----------
    def tela_despesas(msg=None, ok=True):
        try:
            cats = listar_categorias()
            itens = listar_despesas(
                None if filtros["categoria"] == "todas" else filtros["categoria"],  # filtro 1
                None if filtros["essencial"] == "todas" else filtros["essencial"])  # filtro 2
            total, por_cat = total_do_mes(), total_por_categoria()
        except ErroValidacao as erro:
            msg, ok, cats, itens, total, por_cat = str(erro), False, [], [], 0, {}

        hoje = date.today()
        resumo = ft.Container(bgcolor=AZUL, border_radius=14, padding=20, content=ft.Column([
            ft.Text(f"Total gasto em {MESES[hoje.month - 1]} de {hoje.year}", color="#cfe0f0"),
            ft.Text(brl(total), size=34, weight=ft.FontWeight.BOLD, color="white"),
            ft.Text("   ".join(f"{n}: {brl(v)}" for n, v in por_cat.items()),
                    size=13, color="#cfe0f0"),
        ]))

        dd_cat = ft.Dropdown(
            label="Categoria", width=240, value=filtros["categoria"],
            options=[opcao("todas", "Todas")] + [opcao(str(c["id"]), c["nome"]) for c in cats])
        dd_ess = ft.Dropdown(
            label="Essencial", width=200, value=filtros["essencial"],
            options=[opcao("todas", "Todas"), opcao("sim", "Essenciais"),
                     opcao("nao", "Não essenciais")])

        def filtrar(e):
            filtros["categoria"], filtros["essencial"] = dd_cat.value, dd_ess.value
            tela_despesas()

        linhas = []
        for d in itens:
            linhas.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(d["data"].strftime("%d/%m/%Y"))),
                ft.DataCell(ft.Text(d["descricao"])),
                ft.DataCell(ft.Text(d["categoria"])),
                ft.DataCell(ft.Text("Essencial" if d["essencial"] == "sim" else "Não essencial")),
                ft.DataCell(ft.Text(brl(d["valor"]))),
                ft.DataCell(ft.Row([
                    ft.TextButton("Editar", style=ft.ButtonStyle(color=AZUL),
                                  on_click=lambda e, i=d["id"]: form_despesa(i)),
                    ft.TextButton("Excluir", style=ft.ButtonStyle(color=CORAL),
                                  on_click=lambda e, i=d["id"]: pedir_exclusao_despesa(i)),
                ])),
            ]))

        if linhas:
            tabela = ft.Row([ft.DataTable(
                columns=[ft.DataColumn(ft.Text(t)) for t in
                         ("Data", "Descrição", "Categoria", "Tipo", "Valor", "")],
                rows=linhas)], scroll=ft.ScrollMode.AUTO)
        else:
            tabela = ft.Text("Nenhuma despesa encontrada.")

        mostrar_tela(
            menu(), caixa_aviso(msg, ok), resumo,
            titulo("Despesas", "Nova despesa", form_despesa),
            ft.Row([dd_cat, dd_ess, botao("Filtrar", filtrar)], wrap=True),
            ft.Text("Ordenadas do menor para o maior valor.", size=12, color="#5b6578"),
            tabela)

    def pedir_exclusao_despesa(id):
        confirmar("Excluir esta despesa?", lambda: apagar_despesa(id), tela_despesas)

    def apagar_despesa(id):
        try:
            excluir_despesa(id)
            tela_despesas("Despesa excluída.")
        except ErroValidacao as erro:
            tela_despesas(str(erro), False)

    def form_despesa(id=None):
        try:
            cats = listar_categorias()
            atual = buscar_despesa(id) if id else {}
        except ErroValidacao as erro:
            tela_despesas(str(erro), False)
            return
        if id and not atual:
            tela_despesas("Despesa não encontrada.", False)
            return

        descricao = ft.TextField(label="Descrição", value=atual.get("descricao", ""),
                                 max_length=150, width=420)
        valor = ft.TextField(label="Valor (R$)", value=str(atual.get("valor", "")), width=200)
        data = ft.TextField(label="Data (dd/mm/aaaa)", width=200,
                            value=(atual.get("data") or date.today()).strftime("%d/%m/%Y"))
        categoria = ft.Dropdown(
            label="Categoria", width=320,
            value=str(atual["categoria_id"]) if atual else None,
            options=[opcao(str(c["id"]), c["nome"]) for c in cats])
        essencial = ft.Dropdown(
            label="É uma despesa essencial?", width=320, value=atual.get("essencial", "nao"),
            options=[opcao("sim", "Sim, é essencial"), opcao("nao", "Não, posso viver sem")])
        erro_txt = ft.Text("", color=CORAL)

        def salvar(e):
            try:
                campos = (descricao.value, valor.value, data.value, essencial.value, categoria.value)
                if id:
                    editar_despesa(id, *campos)
                else:
                    criar_despesa(*campos)
                tela_despesas("Despesa salva.")
            except ErroValidacao as erro:
                erro_txt.value = str(erro)  # mantém o que a pessoa digitou
                page.update()

        mostrar_tela(menu(), ft.Text("Editar despesa" if id else "Nova despesa", size=22,
                                     weight=ft.FontWeight.BOLD, color=AZUL),
                     descricao, ft.Row([valor, data]), categoria, essencial, erro_txt,
                     ft.Row([botao("Salvar", salvar),
                             ft.OutlinedButton("Cancelar", on_click=lambda e: tela_despesas())]))

    # ---------- categorias ----------
    def tela_categorias(msg=None, ok=True):
        try:
            cats = listar_categorias()
        except ErroValidacao as erro:
            msg, ok, cats = str(erro), False, []

        linhas = [ft.DataRow(cells=[
            ft.DataCell(ft.Text(c["nome"])),
            ft.DataCell(ft.Text(c["descricao"] or "")),
            ft.DataCell(ft.Row([
                ft.TextButton("Editar", style=ft.ButtonStyle(color=AZUL),
                              on_click=lambda e, i=c["id"]: form_categoria(i)),
                ft.TextButton("Excluir", style=ft.ButtonStyle(color=CORAL),
                              on_click=lambda e, i=c["id"]: pedir_exclusao_categoria(i)),
            ])),
        ]) for c in cats]

        tabela = (ft.Row([ft.DataTable(
            columns=[ft.DataColumn(ft.Text(t)) for t in ("Nome", "Descrição", "")],
            rows=linhas)], scroll=ft.ScrollMode.AUTO)
            if linhas else ft.Text("Nenhuma categoria cadastrada."))

        mostrar_tela(menu(), caixa_aviso(msg, ok),
                     titulo("Categorias", "Nova categoria", form_categoria), tabela)

    def pedir_exclusao_categoria(id):
        confirmar("Excluir esta categoria?", lambda: apagar_categoria(id), tela_categorias)

    def apagar_categoria(id):
        try:
            excluir_categoria(id)
            tela_categorias("Categoria excluída.")
        except ErroValidacao as erro:  # ex.: categoria que ainda tem despesas
            tela_categorias(str(erro), False)

    def form_categoria(id=None):
        try:
            atual = buscar_categoria(id) if id else {}
        except ErroValidacao as erro:
            tela_categorias(str(erro), False)
            return
        if id and not atual:
            tela_categorias("Categoria não encontrada.", False)
            return

        nome = ft.TextField(label="Nome", value=atual.get("nome", ""), max_length=100, width=420)
        descricao = ft.TextField(label="Descrição (opcional)", max_length=255, width=420,
                                 value=atual.get("descricao") or "")
        erro_txt = ft.Text("", color=CORAL)

        def salvar(e):
            try:
                if id:
                    editar_categoria(id, nome.value, descricao.value)
                else:
                    criar_categoria(nome.value, descricao.value)
                tela_categorias("Categoria salva.")
            except ErroValidacao as erro:
                erro_txt.value = str(erro)
                page.update()

        mostrar_tela(menu(), ft.Text("Editar categoria" if id else "Nova categoria", size=22,
                                     weight=ft.FontWeight.BOLD, color=AZUL),
                     nome, descricao, erro_txt,
                     ft.Row([botao("Salvar", salvar),
                             ft.OutlinedButton("Cancelar", on_click=lambda e: tela_categorias())]))

    tela_despesas()  # primeira tela


if __name__ == "__main__":
    if hasattr(ft, "run"):   # Flet mais novo
        ft.run(main)
    else:                    # Flet mais antigo
        ft.app(target=main)