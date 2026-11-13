"""Testes do buscador completo (índice + motor de busca)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nucleo import Buscador  # noqa: E402


class TesteBuscador(unittest.TestCase):
    def setUp(self):
        self.b = Buscador()  # sem armazenamento: só em memória
        self.p1 = self.b.cadastrar("u1", "Árvore AVL", "A árvore AVL é balanceada.", ["avl"])
        self.p2 = self.b.cadastrar("u2", "Python", "Python é uma linguagem. Árvore em Python.")

    def test_busca_ignora_acentos_e_maiusculas(self):
        ids = [r.pagina.id for r in self.b.buscar("ARVORE").resultados]
        self.assertEqual(sorted(ids), [self.p1.id, self.p2.id])
        self.assertEqual(ids[0], self.p1.id)  # mais relevante (título + 2x no texto)

    def test_modos_todas_e_qualquer(self):
        self.assertEqual(len(self.b.buscar("avl python", "todas").resultados), 0)
        self.assertEqual(len(self.b.buscar("avl python", "qualquer").resultados), 2)

    def test_editar_e_remover_atualizam_indice(self):
        self.b.editar(self.p1.id, "u1", "Grafos", "Conteúdo sobre grafos.")
        self.assertEqual(len(self.b.buscar("avl").resultados), 0)
        self.assertEqual(len(self.b.buscar("grafos").resultados), 1)
        self.b.remover(self.p1.id)
        self.assertNotIn("grafos", self.b.indice.arvore)  # nó removido da AVL
        self.assertTrue(self.b.indice.arvore.esta_balanceada())

    def test_url_duplicada(self):
        with self.assertRaises(ValueError):
            self.b.cadastrar("u1", "x", "y")

    def test_sugestoes(self):
        self.assertIn("python", self.b.sugerir("py"))


if __name__ == "__main__":
    unittest.main()
