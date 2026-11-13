"""
RepositorioPaginas — onde as páginas em si ficam guardadas.

Usamos DUAS árvores AVL:
  - _por_id  : id  -> Pagina   (índice primário: abrir uma página pelo número)
  - _por_url : url -> id       (índice secundário: o crawler pergunta
                                "já tenho essa URL?" em O(log n))
É a mesma ideia de índices primário/secundário de um banco de dados.
"""

from arvore import ArvoreAVL


class RepositorioPaginas:
    def __init__(self):
        self._por_id = ArvoreAVL()
        self._por_url = ArvoreAVL()
        self._proximo_id = 1

    def __len__(self):
        return len(self._por_id)

    def adicionar(self, pagina):
        if pagina.url in self._por_url:
            raise ValueError(f"Já existe uma página com a URL {pagina.url}")
        if pagina.id is None:
            pagina.id = self._proximo_id
        self._proximo_id = max(self._proximo_id, pagina.id + 1)
        self._por_id.inserir(pagina.id, pagina)
        self._por_url.inserir(pagina.url, pagina.id)
        return pagina

    def obter(self, id_pagina):
        return self._por_id.buscar(id_pagina)

    def obter_por_url(self, url):
        id_pagina = self._por_url.buscar(url)
        return self.obter(id_pagina) if id_pagina is not None else None

    def remover(self, id_pagina):
        pagina = self.obter(id_pagina)
        if pagina is None:
            return None
        self._por_id.remover(id_pagina)
        self._por_url.remover(pagina.url)
        return pagina

    def todas(self):
        """Páginas em ordem de id (percurso em-ordem da AVL)."""
        return [pagina for _, pagina in self._por_id.em_ordem()]
