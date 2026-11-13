"""
Buscador — a "fachada" do sistema (padrão de projeto Facade).

A interface web e o crawler NÃO mexem direto nas árvores: eles chamam
métodos simples daqui (cadastrar, editar, remover, buscar...) e esta classe
coordena as peças:

    Tokenizador -> IndiceInvertido (AVL de palavras)
                -> RepositorioPaginas (AVL por id + AVL por URL)
                -> MotorBusca
                -> ArmazenamentoJSON

Pesos: uma palavra no TÍTULO conta como 3 ocorrências, e uma PALAVRA-CHAVE
cadastrada conta como 5 — elas descrevem melhor o assunto da página.

A trava (lock) existe porque o crawler roda em outra thread ao mesmo tempo
em que o usuário pode estar buscando; ela impede que os dois mexam na árvore
no mesmo instante e a deixem inconsistente.
"""

import threading
from collections import Counter

from busca import MotorBusca
from indice import IndiceInvertido, RepositorioPaginas, Tokenizador
from modelo import Pagina


class Buscador:
    PESO_TITULO = 3
    PESO_PALAVRA_CHAVE = 5

    def __init__(self, armazenamento=None):
        self.tokenizador = Tokenizador()
        self.indice = IndiceInvertido()
        self.repositorio = RepositorioPaginas()
        self.motor = MotorBusca(self.indice, self.repositorio, self.tokenizador)
        self.armazenamento = armazenamento
        self._trava = threading.RLock()

    # ------------------------------------------------------------ #
    def frequencias(self, pagina):
        """Palavras que a página leva para o índice e o peso de cada uma."""
        return self._frequencias(pagina)

    def _frequencias(self, pagina):
        tk = self.tokenizador
        freq = Counter(tk.frequencias(pagina.conteudo))
        for palavra, n in tk.frequencias(pagina.titulo).items():
            freq[palavra] += n * self.PESO_TITULO
        for palavra, n in tk.frequencias(" ".join(pagina.palavras_chave)).items():
            freq[palavra] += n * self.PESO_PALAVRA_CHAVE
        return freq

    def _indexar(self, pagina):
        self.repositorio.adicionar(pagina)
        self.indice.adicionar(pagina.id, self._frequencias(pagina))

    def _desindexar(self, pagina):
        self.indice.remover(pagina.id, self._frequencias(pagina).keys())
        self.repositorio.remover(pagina.id)

    # ------------------------------------------------------------ #
    # Operações pedidas no trabalho: inserir, editar, remover, buscar
    # ------------------------------------------------------------ #
    def cadastrar(self, url, titulo, conteudo, palavras_chave=(), origem="manual", salvar=True):
        with self._trava:
            pagina = Pagina(url, titulo, conteudo, list(palavras_chave), origem)
            self._indexar(pagina)
            if salvar:
                self.salvar()
            return pagina

    def editar(self, id_pagina, url, titulo, conteudo, palavras_chave=(), salvar=True):
        """Editar = tirar a versão antiga do índice e indexar a nova."""
        with self._trava:
            antiga = self.repositorio.obter(id_pagina)
            if antiga is None:
                raise KeyError(f"Página {id_pagina} não existe")
            outra = self.repositorio.obter_por_url(url.strip())
            if outra is not None and outra.id != id_pagina:
                raise ValueError(f"Já existe uma página com a URL {url}")
            self._desindexar(antiga)
            nova = Pagina(url, titulo, conteudo, list(palavras_chave), antiga.origem, id=id_pagina)
            self._indexar(nova)
            if salvar:
                self.salvar()
            return nova

    def remover(self, id_pagina, salvar=True):
        with self._trava:
            pagina = self.repositorio.obter(id_pagina)
            if pagina is None:
                return False
            self._desindexar(pagina)
            if salvar:
                self.salvar()
            return True

    def buscar(self, consulta, modo="todas"):
        with self._trava:
            return self.motor.buscar(consulta, modo)

    def sugerir(self, prefixo, limite=8):
        """Autocompletar: palavras do índice que começam com o prefixo,
        ordenadas pelo número de páginas em que aparecem."""
        prefixo = self.tokenizador.normalizar(prefixo.strip())
        if not prefixo:
            return []
        with self._trava:
            encontrados = self.indice.palavras_com_prefixo(prefixo, limite=200)
        encontrados.sort(key=lambda par: -len(par[1]))
        return [palavra for palavra, _ in encontrados[:limite]]

    def obter(self, id_pagina):
        return self.repositorio.obter(id_pagina)

    def obter_por_url(self, url):
        return self.repositorio.obter_por_url(url)

    def paginas(self):
        with self._trava:
            return self.repositorio.todas()

    def estatisticas(self):
        arvore = self.indice.arvore
        return {
            "paginas": len(self.repositorio),
            "palavras": len(arvore),
            "altura": arvore.altura(),
            "rotacoes": arvore.rotacoes,
        }

    # ------------------------------------------------------------ #
    # Persistência
    # ------------------------------------------------------------ #
    def carregar(self, usar_exemplo=False):
        if not self.armazenamento:
            return
        dados = self.armazenamento.carregar_exemplo() if usar_exemplo else self.armazenamento.carregar()
        with self._trava:
            self.indice = IndiceInvertido()
            self.repositorio = RepositorioPaginas()
            self.motor = MotorBusca(self.indice, self.repositorio, self.tokenizador)
            for item in dados:
                self._indexar(Pagina.de_dict(item))

    def salvar(self):
        if self.armazenamento:
            with self._trava:
                self.armazenamento.salvar([p.para_dict() for p in self.repositorio.todas()])
