"""Visita todas as telas da interface web com o cliente de testes do Flask."""

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from crawler import Crawler  # noqa: E402
from interface import criar_app  # noqa: E402
from nucleo import Buscador  # noqa: E402
from persistencia import ArmazenamentoJSON  # noqa: E402


class TesteWeb(unittest.TestCase):
    def setUp(self):
        exemplo = str(RAIZ / "dados" / "exemplo.json")
        self.buscador = Buscador(ArmazenamentoJSON(exemplo, exemplo))
        self.buscador.carregar()
        self.buscador.armazenamento = None  # não grava nada durante o teste
        app = criar_app(self.buscador, Crawler(self.buscador), "file:///x")
        self.cliente = app.test_client()

    def ok(self, url):
        resposta = self.cliente.get(url)
        self.assertEqual(resposta.status_code, 200, url)
        return resposta.get_data(as_text=True)

    def test_telas(self):
        self.assertIn("BuscaAVL", self.ok("/"))
        html = self.ok("/buscar?q=árvore+avl")
        self.assertIn("<mark>", html)
        self.assertIn("Como a AVL encontrou", html)
        self.ok("/buscar?q=xyzinexistente&modo=qualquer")
        self.ok("/paginas")
        self.ok("/paginas/1")
        self.ok("/paginas/nova")
        self.ok("/paginas/1/editar")
        self.ok("/crawler")
        self.ok("/crawler/status")
        self.assertIn("<svg", self.ok("/arvore?destacar=python&profundidade=6"))
        self.ok("/arvore?raiz=python")
        self.assertEqual(self.cliente.get("/api/sugestoes?q=pro").json[0][:3], "pro")

    def test_crud_pela_interface(self):
        r = self.cliente.post("/paginas/nova", data={
            "url": "https://teste", "titulo": "Capivara", "conteudo": "A capivara é um roedor.", "palavras_chave": "animal"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(len(self.buscador.buscar("capivara").resultados), 1)
        pagina = self.buscador.obter_por_url("https://teste")
        self.cliente.post(f"/paginas/{pagina.id}/remover")
        self.assertEqual(len(self.buscador.buscar("capivara").resultados), 0)

    def test_laboratorio(self):
        self.cliente.post("/laboratorio", data={"acao": "exemplo", "exemplo": "rr"})
        html = self.ok("/laboratorio")
        self.assertIn("Rotação à ESQUERDA", html)


if __name__ == "__main__":
    unittest.main()
