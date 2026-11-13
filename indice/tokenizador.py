"""
Tokenizador — transforma um texto em uma lista de palavras ("tokens")
prontas para entrar no índice.

Passos:
  1. tudo em minúsculas           "Árvore AVL"  -> "árvore avl"
  2. remove acentos               "árvore"      -> "arvore"
  3. separa em palavras           só letras e números
  4. descarta "stopwords"         palavras muito comuns (de, a, o, que...)
     que aparecem em quase todo texto e não ajudam a diferenciar páginas.

Assim, quem busca "ARVORE" encontra páginas que escreveram "árvore".
"""

import re
import unicodedata
from collections import Counter


class Tokenizador:
    STOPWORDS = set("""
        a o e é as os um uma uns umas de do da dos das no na nos nas em ao aos à às
        por para pelo pela pelos pelas com sem sob sobre entre até que se ou mas
        como mais menos muito muita muitos muitas já não sim seu sua seus suas
        ele ela eles elas eu tu nós vós você vocês isso isto aquilo esse essa este esta
        foi ser são está estão era há ter tem têm também quando onde qual quais
        lhe me te nos lo la the of and to in is it for on with as by an be this that are
    """.split())

    _PALAVRA = re.compile(r"[a-z0-9]+")

    def __init__(self, tamanho_minimo=2):
        self.tamanho_minimo = tamanho_minimo
        self._stopwords = {self.normalizar(p) for p in self.STOPWORDS}

    @staticmethod
    def normalizar(texto):
        """Minúsculas e sem acentos (NFD separa 'á' em 'a' + acento, e o acento é descartado)."""
        decomposto = unicodedata.normalize("NFD", texto.lower())
        return "".join(c for c in decomposto if unicodedata.category(c) != "Mn")

    def tokens(self, texto):
        return [
            p for p in self._PALAVRA.findall(self.normalizar(texto))
            if len(p) >= self.tamanho_minimo and p not in self._stopwords
        ]

    def frequencias(self, texto):
        """{palavra: quantas vezes aparece}"""
        return Counter(self.tokens(texto))
