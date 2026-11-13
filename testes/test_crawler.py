"""Testa o crawler percorrendo o mini-site local (sem internet)."""

import os
import sys
import time
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from crawler import Crawler  # noqa: E402
from nucleo import Buscador  # noqa: E402


class TesteCrawler(unittest.TestCase):
    def test_percorre_site_local(self):
        buscador = Buscador()
        crawler = Crawler(buscador, intervalo=0)
        inicio = (RAIZ / "dados" / "site_exemplo" / "index.html").as_uri()
        crawler.iniciar(inicio, max_paginas=20, max_profundidade=2)
        while crawler.em_execucao:
            time.sleep(0.05)

        self.assertEqual(crawler.novas, 6)   # index + 5 páginas existentes
        self.assertEqual(crawler.erros, 1)   # caruaru.html não existe (link quebrado)
        self.assertEqual(len(buscador.buscar("bolo de rolo").resultados), 1)
        self.assertEqual(len(buscador.buscar("console").resultados), 0)  # <script> ignorado


if __name__ == "__main__":
    unittest.main()
