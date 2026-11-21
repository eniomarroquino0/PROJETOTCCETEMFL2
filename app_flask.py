# app_flask.py - telas web (Flask) do MoneyFlow
# Só cuida das telas: todo o CRUD e as validações vêm dos módulos compartilhados.
from datetime import date

from flask import Flask, flash, redirect, render_template, request, url_for

from categorias_dao import (buscar_categoria, criar_categoria, editar_categoria,
                            excluir_categoria, listar_categorias)
from config import SECRET_KEY
from despesas_dao import (buscar_despesa, criar_despesa, editar_despesa,
                          excluir_despesa, listar_despesas)
from servicos import total_do_mes, total_por_categoria
from validacoes import ErroValidacao

app = Flask(__name__)
app.secret_key = SECRET_KEY

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]


@app.template_filter("brl")
def brl(valor):
    """Formata número como moeda: 1234.5 -> R$ 1.234,50"""
    return "R$ " + f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def categorias_seguras():
    """Lista categorias; se der erro no banco, avisa e devolve lista vazia."""
    try:
        return listar_categorias()
    except ErroValidacao as erro:
        flash(str(erro), "erro")
        return []


# ---------- despesas ----------
@app.route("/")
def inicio():
    return redirect(url_for("despesas"))


@app.route("/despesas")
def despesas():
    categoria = request.args.get("categoria", "")   # filtro 1
    essencial = request.args.get("essencial", "")   # filtro 2
    try:
        itens = listar_despesas(categoria or None, essencial or None)
        total, por_cat = total_do_mes(), total_por_categoria()
    except ErroValidacao as erro:
        flash(str(erro), "erro")
        itens, total, por_cat = [], 0, {}
    hoje = date.today()
    return render_template("despesas.html", itens=itens, total=total, por_cat=por_cat,
                           mes=f"{MESES[hoje.month - 1]} de {hoje.year}",
                           cats=categorias_seguras(), categoria=categoria, essencial=essencial)


@app.route("/despesas/nova", methods=["GET", "POST"])
def nova_despesa():
    dados = {"data": date.today().isoformat(), "essencial": "nao"}
    if request.method == "POST":
        f = request.form
        try:
            criar_despesa(f.get("descricao"), f.get("valor"), f.get("data"),
                          f.get("essencial"), f.get("categoria_id"))
            flash("Despesa cadastrada.", "ok")
            return redirect(url_for("despesas"))
        except ErroValidacao as erro:
            flash(str(erro), "erro")
            dados = f  # mantém o que a pessoa digitou
    return render_template("form_despesa.html", d=dados, cats=categorias_seguras(),
                           titulo="Nova despesa")


@app.route("/despesas/<int:id>/editar", methods=["GET", "POST"])
def alterar_despesa(id):
    try:
        dados = buscar_despesa(id)
    except ErroValidacao as erro:
        dados = None
        flash(str(erro), "erro")
    if not dados:
        flash("Despesa não encontrada.", "erro")
        return redirect(url_for("despesas"))
    if request.method == "POST":
        f = request.form
        try:
            editar_despesa(id, f.get("descricao"), f.get("valor"), f.get("data"),
                           f.get("essencial"), f.get("categoria_id"))
            flash("Despesa atualizada.", "ok")
            return redirect(url_for("despesas"))
        except ErroValidacao as erro:
            flash(str(erro), "erro")
            dados = f
    return render_template("form_despesa.html", d=dados, cats=categorias_seguras(),
                           titulo="Editar despesa")


@app.route("/despesas/<int:id>/excluir", methods=["POST"])
def apagar_despesa(id):
    try:
        excluir_despesa(id)
        flash("Despesa excluída.", "ok")
    except ErroValidacao as erro:
        flash(str(erro), "erro")
    return redirect(url_for("despesas"))


# ---------- categorias ----------
@app.route("/categorias")
def categorias():
    return render_template("categorias.html", cats=categorias_seguras())


@app.route("/categorias/nova", methods=["GET", "POST"])
def nova_categoria():
    dados = {}
    if request.method == "POST":
        f = request.form
        try:
            criar_categoria(f.get("nome"), f.get("descricao"))
            flash("Categoria cadastrada.", "ok")
            return redirect(url_for("categorias"))
        except ErroValidacao as erro:
            flash(str(erro), "erro")
            dados = f
    return render_template("form_categoria.html", d=dados, titulo="Nova categoria")


@app.route("/categorias/<int:id>/editar", methods=["GET", "POST"])
def alterar_categoria(id):
    try:
        dados = buscar_categoria(id)
    except ErroValidacao as erro:
        dados = None
        flash(str(erro), "erro")
    if not dados:
        flash("Categoria não encontrada.", "erro")
        return redirect(url_for("categorias"))
    if request.method == "POST":
        f = request.form
        try:
            editar_categoria(id, f.get("nome"), f.get("descricao"))
            flash("Categoria atualizada.", "ok")
            return redirect(url_for("categorias"))
        except ErroValidacao as erro:
            flash(str(erro), "erro")
            dados = f
    return render_template("form_categoria.html", d=dados, titulo="Editar categoria")


@app.route("/categorias/<int:id>/excluir", methods=["POST"])
def apagar_categoria(id):
    try:
        excluir_categoria(id)
        flash("Categoria excluída.", "ok")
    except ErroValidacao as erro:
        flash(str(erro), "erro")
    return redirect(url_for("categorias"))


if __name__ == "__main__":
    app.run(debug=True)