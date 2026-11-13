"""
LaboratorioAVL — uma árvore AVL pequena, separada do índice, só para
DEMONSTRAR na apresentação como a árvore se rebalanceia.

Digite "10 20 30" e veja a rotação à esquerda acontecer (caso RR).
Os exemplos prontos mostram os 4 casos clássicos de rotação.
"""

import re

from arvore import ArvoreAVL


class LaboratorioAVL:
    EXEMPLOS = {
        "rr": ("Caso RR → rotação simples à esquerda", "10 20 30"),
        "ll": ("Caso LL → rotação simples à direita", "30 20 10"),
        "lr": ("Caso LR → rotação dupla (esquerda + direita)", "30 10 20"),
        "rl": ("Caso RL → rotação dupla (direita + esquerda)", "10 30 20"),
        "ordem": ("1 a 15 em ordem (BST comum viraria uma lista!)",
                  " ".join(str(i) for i in range(1, 16))),
        "palavras": ("Palavras", "manga banana abacaxi uva caju goiaba pitanga acerola"),
    }

    def __init__(self):
        self.arvore = ArvoreAVL()
        self.mensagens = []

    def _chaves(self, texto):
        chaves = []
        for parte in re.split(r"[\s,;]+", texto.strip()):
            if parte:
                chaves.append(int(parte) if re.fullmatch(r"-?\d+", parte) else parte.lower())
        return chaves

    def _tipo_compativel(self, chave):
        raiz = self.arvore.raiz
        return raiz is None or type(raiz.chave) is type(chave)

    def inserir(self, texto):
        self.mensagens = []
        for chave in self._chaves(texto):
            if not self._tipo_compativel(chave):
                self.mensagens.append(("erro", f"{chave!r}: não dá para misturar números e palavras na mesma árvore."))
                continue
            antes = self.arvore.rotacoes
            existia = chave in self.arvore
            self.arvore.inserir(chave)
            self._registrar("inseriu", chave, antes, existia)

    def remover(self, texto):
        self.mensagens = []
        for chave in self._chaves(texto):
            antes = self.arvore.rotacoes
            if not self._tipo_compativel(chave) or not self.arvore.remover(chave):
                self.mensagens.append(("erro", f"{chave!r} não está na árvore."))
                continue
            self._registrar("removeu", chave, antes, False)

    def _registrar(self, acao, chave, rotacoes_antes, existia):
        feitas = self.arvore.rotacoes - rotacoes_antes
        if existia:
            self.mensagens.append(("info", f"{chave!r} já existia (sem duplicar)."))
        elif feitas == 0:
            self.mensagens.append(("ok", f"{acao.capitalize()} {chave!r} — continuou balanceada, sem rotação."))
        else:
            detalhes = list(self.arvore.historico_rotacoes)[-feitas:]
            self.mensagens.append(("rotacao", f"{acao.capitalize()} {chave!r} → " + " ; ".join(detalhes)))

    def carregar_exemplo(self, nome):
        if nome in self.EXEMPLOS:
            self.limpar()
            self.inserir(self.EXEMPLOS[nome][1])

    def limpar(self):
        self.arvore = ArvoreAVL()
        self.mensagens = []
