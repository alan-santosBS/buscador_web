"""
NoAVL — o "tijolo" da árvore.

Cada nó guarda:
  - chave    : o que usamos para ordenar (no índice, é a PALAVRA)
  - valor    : o dado associado à chave (no índice, as páginas onde a palavra aparece)
  - esquerda : ponteiro para o filho com chave MENOR
  - direita  : ponteiro para o filho com chave MAIOR
  - altura   : maior distância deste nó até uma folha (folha = 1)

Ou seja: 2 ponteiros por nó + a altura, que é o que permite à AVL saber
quando está desbalanceada.
"""


class NoAVL:
    def __init__(self, chave, valor=None):
        self.chave = chave
        self.valor = valor
        self.esquerda = None
        self.direita = None
        self.altura = 1  # um nó novo sempre nasce como folha

    def __repr__(self):
        return f"NoAVL({self.chave!r}, altura={self.altura})"
