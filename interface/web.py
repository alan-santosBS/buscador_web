"""
Camada WEB — liga o navegador às nossas classes, usando o Flask.

O Flask aqui é só o "garçom": recebe o pedido do navegador (uma ROTA, como
/buscar?q=python), chama o método certo do Buscador e devolve uma página HTML
montada a partir de um TEMPLATE (pasta templates/) com o estilo da pasta static/.
Nenhuma lógica de árvore, índice ou crawler fica aqui.
"""

from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

from .laboratorio import LaboratorioAVL
from .visualizador import VisualizadorArvore

PASTA = Path(__file__).resolve().parent


def _palavras_chave(texto):
    return [p.strip() for p in texto.split(",") if p.strip()]


def criar_app(buscador, crawler, url_site_exemplo):
    app = Flask(__name__, template_folder=str(PASTA / "templates"),
                static_folder=str(PASTA / "static"))
    app.secret_key = "busca-avl-apresentacao"
    laboratorio = LaboratorioAVL()

    @app.context_processor
    def variaveis_globais():
        return {"stats": buscador.estatisticas()}

    # ------------------------------------------------------------ #
    # Busca
    # ------------------------------------------------------------ #
    @app.get("/")
    def inicio():
        return render_template("inicio.html")

    @app.get("/buscar")
    def buscar():
        consulta = request.args.get("q", "").strip()
        modo = request.args.get("modo", "todas")
        if not consulta:
            return redirect(url_for("inicio"))
        resposta = buscador.buscar(consulta, modo)
        arvore = buscador.indice.arvore
        caminhos = {termo: arvore.caminho_busca(termo) for termo in resposta.termos}
        return render_template("resultados.html", r=resposta, caminhos=caminhos)

    @app.get("/api/sugestoes")
    def sugestoes():
        return jsonify(buscador.sugerir(request.args.get("q", "")))

    # ------------------------------------------------------------ #
    # Cadastro de páginas (CRUD)
    # ------------------------------------------------------------ #
    @app.get("/paginas")
    def paginas():
        return render_template("paginas.html", paginas=buscador.paginas())

    @app.get("/paginas/<int:id_pagina>")
    def detalhes(id_pagina):
        pagina = buscador.obter(id_pagina)
        if pagina is None:
            flash("Página não encontrada.", "erro")
            return redirect(url_for("paginas"))
        frequencias = sorted(buscador.frequencias(pagina).items(), key=lambda p: (-p[1], p[0]))
        return render_template("detalhes.html", pagina=pagina, frequencias=frequencias)

    @app.route("/paginas/nova", methods=["GET", "POST"])
    def nova_pagina():
        if request.method == "POST":
            f = request.form
            try:
                pagina = buscador.cadastrar(f["url"], f["titulo"], f["conteudo"], _palavras_chave(f["palavras_chave"]))
                flash(f"Página “{pagina.titulo}” cadastrada e indexada.", "ok")
                return redirect(url_for("paginas"))
            except ValueError as erro:
                flash(str(erro), "erro")
        return render_template("formulario.html", pagina=None, form=request.form)

    @app.route("/paginas/<int:id_pagina>/editar", methods=["GET", "POST"])
    def editar_pagina(id_pagina):
        pagina = buscador.obter(id_pagina)
        if pagina is None:
            flash("Página não encontrada.", "erro")
            return redirect(url_for("paginas"))
        if request.method == "POST":
            f = request.form
            try:
                buscador.editar(id_pagina, f["url"], f["titulo"], f["conteudo"], _palavras_chave(f["palavras_chave"]))
                flash("Página atualizada e reindexada.", "ok")
                return redirect(url_for("paginas"))
            except ValueError as erro:
                flash(str(erro), "erro")
        return render_template("formulario.html", pagina=pagina, form=request.form)

    @app.post("/paginas/<int:id_pagina>/remover")
    def remover_pagina(id_pagina):
        if buscador.remover(id_pagina):
            flash("Página removida do índice.", "ok")
        return redirect(url_for("paginas"))

    @app.post("/paginas/restaurar-exemplo")
    def restaurar_exemplo():
        if crawler.em_execucao:
            flash("Pare o crawler antes de restaurar os dados.", "erro")
        else:
            buscador.carregar(usar_exemplo=True)
            buscador.salvar()
            flash("Dados de exemplo restaurados.", "ok")
        return redirect(url_for("paginas"))

    # ------------------------------------------------------------ #
    # Painel do crawler
    # ------------------------------------------------------------ #
    @app.get("/crawler")
    def painel_crawler():
        return render_template("crawler.html", url_exemplo=url_site_exemplo)

    @app.post("/crawler/iniciar")
    def iniciar_crawler():
        f = request.form
        url = f.get("url", "").strip()
        if url and "://" not in url:
            url = "https://" + url
        if urlparse(url).scheme not in ("http", "https", "file"):
            return jsonify(ok=False, mensagem="Informe uma URL válida (http, https ou file).")
        iniciou = crawler.iniciar(
            url,
            max_paginas=max(1, min(int(f.get("max_paginas", 20)), 500)),
            max_profundidade=max(0, min(int(f.get("max_profundidade", 2)), 5)),
            mesmo_dominio=f.get("mesmo_dominio") == "on",
        )
        return jsonify(ok=iniciou, mensagem="Crawler iniciado." if iniciou else "O crawler já está rodando.")

    @app.post("/crawler/parar")
    def parar_crawler():
        crawler.parar()
        return jsonify(ok=True, mensagem="Pedido de parada enviado.")

    @app.get("/crawler/status")
    def status_crawler():
        return jsonify(crawler.status())

    # ------------------------------------------------------------ #
    # Visualização da árvore do índice
    # ------------------------------------------------------------ #
    @app.get("/arvore")
    def ver_arvore():
        arvore = buscador.indice.arvore
        profundidade = max(2, min(request.args.get("profundidade", 4, type=int), 7))
        raiz = buscador.tokenizador.normalizar(request.args.get("raiz", "").strip()) or None
        destacar = buscador.tokenizador.normalizar(request.args.get("destacar", "").strip())
        caminho = arvore.caminho_busca(destacar) if destacar else []
        if raiz is not None and raiz not in arvore:
            flash(f"A palavra “{raiz}” não está no índice.", "erro")
            raiz = None
        desenho = VisualizadorArvore(arvore).gerar(raiz, profundidade, caminho)
        return render_template("arvore.html", desenho=desenho, profundidade=profundidade,
                               destacar=destacar, caminho=caminho,
                               encontrado=bool(caminho) and caminho[-1] == destacar)

    # ------------------------------------------------------------ #
    # Laboratório AVL (demonstração das rotações)
    # ------------------------------------------------------------ #
    @app.route("/laboratorio", methods=["GET", "POST"])
    def ver_laboratorio():
        if request.method == "POST":
            acao = request.form.get("acao")
            if acao == "inserir":
                laboratorio.inserir(request.form.get("chaves", ""))
            elif acao == "remover":
                laboratorio.remover(request.form.get("chaves", ""))
            elif acao == "limpar":
                laboratorio.limpar()
            elif acao == "exemplo":
                laboratorio.carregar_exemplo(request.form.get("exemplo"))
            return redirect(url_for("ver_laboratorio"))
        desenho = VisualizadorArvore(laboratorio.arvore).gerar(profundidade=7)
        return render_template("laboratorio.html", desenho=desenho, lab=laboratorio,
                               chaves=list(laboratorio.arvore))

    return app
