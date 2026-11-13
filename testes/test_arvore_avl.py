"""Testes automáticos da ArvoreAVL.  Rodar com:  python -m unittest discover testes"""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from arvore import ArvoreAVL  # noqa: E402


class TesteArvoreAVL(unittest.TestCase):
    def test_insercao_em_ordem_continua_balanceada(self):
        # pior caso de uma BST comum: chaves já ordenadas
        arvore = ArvoreAVL()
        for i in range(1000):
            arvore.inserir(i, str(i))
        self.assertTrue(arvore.esta_balanceada())
        self.assertEqual(len(arvore), 1000)
        self.assertLessEqual(arvore.altura(), 15)  # ~1.44*log2(1000)

    def test_casos_de_rotacao(self):
        for sequencia in (["c", "b", "a"], ["a", "b", "c"], ["c", "a", "b"], ["a", "c", "b"]):
            arvore = ArvoreAVL()
            for chave in sequencia:
                arvore.inserir(chave)
            self.assertEqual(arvore.raiz.chave, "b", f"falhou em {sequencia}")
            self.assertTrue(arvore.esta_balanceada())

    def test_busca_e_atualizacao(self):
        arvore = ArvoreAVL()
        arvore.inserir("python", 1)
        arvore.inserir("python", 2)
        self.assertEqual(arvore.buscar("python"), 2)
        self.assertEqual(len(arvore), 1)
        self.assertIsNone(arvore.buscar("java"))

    def test_remocao_aleatoria(self):
        random.seed(42)
        arvore, conjunto = ArvoreAVL(), set()
        for _ in range(3000):
            chave = random.randint(0, 500)
            if random.random() < 0.6:
                arvore.inserir(chave)
                conjunto.add(chave)
            else:
                self.assertEqual(arvore.remover(chave), chave in conjunto)
                conjunto.discard(chave)
            self.assertTrue(arvore.esta_balanceada())
        self.assertEqual(list(arvore), sorted(conjunto))

    def test_prefixo(self):
        arvore = ArvoreAVL()
        for palavra in ["programa", "python", "progresso", "arvore", "prova", "zebra", "pro"]:
            arvore.inserir(palavra)
        chaves = [c for c, _ in arvore.buscar_prefixo("pro")]
        self.assertEqual(chaves, ["pro", "programa", "progresso", "prova"])


if __name__ == "__main__":
    unittest.main()
