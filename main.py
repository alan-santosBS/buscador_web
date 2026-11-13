"""
BuscaAVL — buscador web com índice próprio em Árvore AVL.

Para rodar:
    pip install -r requirements.txt
    python main.py
e abra http://127.0.0.1:5000 no navegador.

Este arquivo só MONTA os objetos e liga uns aos outros
(a "composição" das classes) e depois sobe o servidor web.
"""

import os
import webbrowser
from pathlib import Path

from crawler import Crawler
from interface import criar_app
from nucleo import Buscador
from persistencia import ArmazenamentoJSON

RAIZ = Path(__file__).resolve().parent
PASTA_DADOS = RAIZ / "dados"


def main():
    armazenamento = ArmazenamentoJSON(str(PASTA_DADOS / "banco.json"),
                                      str(PASTA_DADOS / "exemplo.json"))
    buscador = Buscador(armazenamento)
    buscador.carregar()  # lê as páginas e reconstrói as árvores

    crawler = Crawler(buscador)
    url_site_exemplo = (PASTA_DADOS / "site_exemplo" / "index.html").as_uri()

    app = criar_app(buscador, crawler, url_site_exemplo)
    endereco = "http://127.0.0.1:5000"
    estat = buscador.estatisticas()
    print(f"BuscaAVL: {estat['paginas']} páginas, {estat['palavras']} palavras na árvore (altura {estat['altura']}).")
    print(f"Abra {endereco} no navegador.  (Ctrl+C para encerrar)")
    if not os.environ.get("BUSCAAVL_SEM_NAVEGADOR"):
        webbrowser.open(endereco)
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)


if __name__ == "__main__":
    main()
