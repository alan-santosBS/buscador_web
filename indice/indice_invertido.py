"""
IndiceInvertido — a estrutura central de qualquer buscador.

Um índice "normal" (como o de um livro ao contrário) seria:
    página -> palavras que ela contém
O índice INVERTIDO guarda o oposto:
    palavra -> páginas onde ela aparece (e quantas vezes)

Exemplo:
    "python"  -> {1: 4, 7: 1}     (aparece 4x na página 1 e 1x na página 7)
    "arvore"  -> {2: 3}

Aqui, cada palavra é um NÓ da nossa ÁRVORE AVL (chave = palavra,
valor = dicionário {id_da_pagina: frequência}). Assim, achar as páginas
de uma palavra custa O(log n), onde n = número de palavras distintas.
"""

from arvore import ArvoreAVL


class IndiceInvertido:
    def __init__(self):
        self._arvore = ArvoreAVL()

    @property
    def arvore(self):
        return self._arvore

    def adicionar(self, id_pagina, frequencias):
        """Registra todas as palavras de uma página no índice."""
        for palavra, freq in frequencias.items():
            ocorrencias = self._arvore.buscar(palavra)
            if ocorrencias is None:          # palavra nova -> novo nó na AVL
                self._arvore.inserir(palavra, {id_pagina: freq})
            else:                            # palavra já existe -> só acrescenta a página
                ocorrencias[id_pagina] = freq

    def remover(self, id_pagina, palavras):
        """Tira a página das palavras indicadas. Se a palavra ficar sem
        nenhuma página, o nó é REMOVIDO da AVL (e a árvore se rebalanceia)."""
        for palavra in palavras:
            ocorrencias = self._arvore.buscar(palavra)
            if ocorrencias is None:
                continue
            ocorrencias.pop(id_pagina, None)
            if not ocorrencias:
                self._arvore.remover(palavra)

    def buscar(self, palavra):
        """{id_pagina: frequência} da palavra (vazio se não existir)."""
        return self._arvore.buscar(palavra, {})

    def palavras_com_prefixo(self, prefixo, limite=8):
        return self._arvore.buscar_prefixo(prefixo, limite)

    def total_palavras(self):
        return len(self._arvore)
