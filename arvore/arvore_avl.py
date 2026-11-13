"""
ArvoreAVL — Árvore Binária de Busca AUTO-BALANCEADA, implementada do zero.

REGRA DE INSERÇÃO (igual à binária de busca):
    chave menor que o nó  -> vai para a ESQUERDA
    chave maior que o nó  -> vai para a DIREITA
    chave igual           -> atualiza o valor (não duplica)

REGRA DE BALANCEAMENTO (o que torna ela uma AVL):
    fator de balanceamento (FB) = altura(esquerda) - altura(direita)
    Todo nó precisa ter FB igual a -1, 0 ou +1.
    Se depois de inserir/remover algum nó ficar com FB = +2 ou -2,
    fazemos ROTAÇÕES para consertar.

OS 4 CASOS DE DESBALANCEAMENTO:
    LL (FB=+2, filho esq. pesa à esquerda)  -> rotação simples à DIREITA
    RR (FB=-2, filho dir. pesa à direita)   -> rotação simples à ESQUERDA
    LR (FB=+2, filho esq. pesa à direita)   -> esquerda no filho, depois direita no nó
    RL (FB=-2, filho dir. pesa à esquerda)  -> direita no filho, depois esquerda no nó

Como a altura fica sempre em torno de log2(n), buscar, inserir e remover
custam O(log n) — mesmo que as palavras cheguem em ordem alfabética
(caso em que uma binária de busca comum viraria uma "lista", O(n)).
"""

from collections import deque

from .no_avl import NoAVL


class ArvoreAVL:
    def __init__(self):
        self._raiz = None
        self._tamanho = 0
        self.rotacoes = 0  # contador só para mostrar na apresentação
        # últimas rotações feitas (texto), para o "laboratório" da interface
        self.historico_rotacoes = deque(maxlen=50)

    # ------------------------------------------------------------------ #
    # Informações básicas
    # ------------------------------------------------------------------ #
    @property
    def raiz(self):
        return self._raiz

    def __len__(self):
        return self._tamanho

    def __contains__(self, chave):
        return self._buscar_no(chave) is not None

    def esta_vazia(self):
        return self._raiz is None

    def altura(self):
        return self._altura(self._raiz)

    # ------------------------------------------------------------------ #
    # Auxiliares de altura / balanceamento
    # ------------------------------------------------------------------ #
    @staticmethod
    def _altura(no):
        return no.altura if no else 0

    def _atualizar_altura(self, no):
        no.altura = 1 + max(self._altura(no.esquerda), self._altura(no.direita))

    def fator_balanceamento(self, no):
        return self._altura(no.esquerda) - self._altura(no.direita) if no else 0

    # ------------------------------------------------------------------ #
    # Rotações
    # ------------------------------------------------------------------ #
    def _rotacao_direita(self, y):
        """
              y               x
             / \\             / \\
            x   C   --->    A   y
           / \\                 / \\
          A   B               B   C
        """
        x = y.esquerda
        b = x.direita
        x.direita = y
        y.esquerda = b
        self._atualizar_altura(y)  # y agora está embaixo: atualiza primeiro
        self._atualizar_altura(x)
        self.rotacoes += 1
        self.historico_rotacoes.append(f"Rotação à DIREITA em {y.chave!r} ({x.chave!r} sobe)")
        return x  # x é a nova raiz desta subárvore

    def _rotacao_esquerda(self, x):
        """
            x                   y
           / \\                 / \\
          A   y     --->      x   C
             / \\             / \\
            B   C           A   B
        """
        y = x.direita
        b = y.esquerda
        y.esquerda = x
        x.direita = b
        self._atualizar_altura(x)
        self._atualizar_altura(y)
        self.rotacoes += 1
        self.historico_rotacoes.append(f"Rotação à ESQUERDA em {x.chave!r} ({y.chave!r} sobe)")
        return y

    def _balancear(self, no):
        """Verifica o FB do nó e aplica a rotação certa (casos LL, RR, LR, RL)."""
        self._atualizar_altura(no)
        fb = self.fator_balanceamento(no)

        if fb > 1:  # pesado à esquerda
            if self.fator_balanceamento(no.esquerda) < 0:  # caso LR
                no.esquerda = self._rotacao_esquerda(no.esquerda)
            return self._rotacao_direita(no)  # caso LL (ou final do LR)

        if fb < -1:  # pesado à direita
            if self.fator_balanceamento(no.direita) > 0:  # caso RL
                no.direita = self._rotacao_direita(no.direita)
            return self._rotacao_esquerda(no)  # caso RR (ou final do RL)

        return no  # já estava balanceado

    # ------------------------------------------------------------------ #
    # Inserção  — O(log n)
    # ------------------------------------------------------------------ #
    def inserir(self, chave, valor=None):
        """Insere a chave. Se ela já existir, apenas troca o valor."""
        self._raiz = self._inserir(self._raiz, chave, valor)

    def _inserir(self, no, chave, valor):
        if no is None:  # achamos o lugar vazio: cria o nó aqui
            self._tamanho += 1
            return NoAVL(chave, valor)

        if chave < no.chave:
            no.esquerda = self._inserir(no.esquerda, chave, valor)
        elif chave > no.chave:
            no.direita = self._inserir(no.direita, chave, valor)
        else:
            no.valor = valor
            return no

        # na "volta" da recursão, cada ancestral confere se ficou desbalanceado
        return self._balancear(no)

    # ------------------------------------------------------------------ #
    # Busca  — O(log n)
    # ------------------------------------------------------------------ #
    def buscar(self, chave, padrao=None):
        """Retorna o valor associado à chave (ou `padrao` se não existir)."""
        no = self._buscar_no(chave)
        return no.valor if no else padrao

    def obter_no(self, chave):
        """Devolve o próprio nó (usado pela visualização da árvore)."""
        return self._buscar_no(chave)

    def _buscar_no(self, chave):
        atual = self._raiz
        while atual:
            if chave < atual.chave:
                atual = atual.esquerda
            elif chave > atual.chave:
                atual = atual.direita
            else:
                return atual
        return None

    def caminho_busca(self, chave):
        """Lista das chaves visitadas até achar (ou não) a chave.
        Usado para destacar o caminho na visualização da árvore."""
        caminho = []
        atual = self._raiz
        while atual:
            caminho.append(atual.chave)
            if chave < atual.chave:
                atual = atual.esquerda
            elif chave > atual.chave:
                atual = atual.direita
            else:
                break
        return caminho

    # ------------------------------------------------------------------ #
    # Remoção  — O(log n)
    # ------------------------------------------------------------------ #
    def remover(self, chave):
        """Remove a chave. Retorna True se removeu, False se não existia."""
        tamanho_antes = self._tamanho
        self._raiz = self._remover(self._raiz, chave)
        return self._tamanho < tamanho_antes

    def _remover(self, no, chave):
        if no is None:
            return None  # chave não existe

        if chave < no.chave:
            no.esquerda = self._remover(no.esquerda, chave)
        elif chave > no.chave:
            no.direita = self._remover(no.direita, chave)
        else:
            # achamos o nó a remover — 3 situações:
            if no.esquerda is None:          # 0 ou 1 filho (à direita)
                self._tamanho -= 1
                return no.direita
            if no.direita is None:           # 1 filho (à esquerda)
                self._tamanho -= 1
                return no.esquerda
            # 2 filhos: copiamos o SUCESSOR (menor da subárvore direita)
            # para cá e removemos o sucessor lá embaixo.
            sucessor = self._minimo(no.direita)
            no.chave, no.valor = sucessor.chave, sucessor.valor
            no.direita = self._remover(no.direita, sucessor.chave)

        return self._balancear(no)

    @staticmethod
    def _minimo(no):
        while no.esquerda:
            no = no.esquerda
        return no

    # ------------------------------------------------------------------ #
    # Percursos
    # ------------------------------------------------------------------ #
    def em_ordem(self):
        """Gera (chave, valor) em ordem crescente — percurso esquerda, raiz, direita.
        Feito com pilha (sem recursão) para não estourar o limite do Python."""
        pilha, atual = [], self._raiz
        while pilha or atual:
            while atual:
                pilha.append(atual)
                atual = atual.esquerda
            atual = pilha.pop()
            yield atual.chave, atual.valor
            atual = atual.direita

    def __iter__(self):
        for chave, _ in self.em_ordem():
            yield chave

    def buscar_prefixo(self, prefixo, limite=None):
        """Todas as chaves que começam com `prefixo`, em ordem.
        Só desce nos galhos que podem conter o prefixo (poda)."""
        resultado = []
        self._prefixo(self._raiz, prefixo, resultado, limite)
        return resultado

    def _prefixo(self, no, prefixo, resultado, limite):
        if no is None or (limite and len(resultado) >= limite):
            return
        if prefixo < no.chave[: len(prefixo)] or no.chave.startswith(prefixo):
            self._prefixo(no.esquerda, prefixo, resultado, limite)
        if no.chave.startswith(prefixo) and not (limite and len(resultado) >= limite):
            resultado.append((no.chave, no.valor))
        if prefixo > no.chave[: len(prefixo)] or no.chave.startswith(prefixo):
            self._prefixo(no.direita, prefixo, resultado, limite)

    # ------------------------------------------------------------------ #
    # Verificação (usada nos testes)
    # ------------------------------------------------------------------ #
    def esta_balanceada(self):
        def checar(no, minimo, maximo):
            if no is None:
                return 0
            if (minimo is not None and no.chave <= minimo) or (
                maximo is not None and no.chave >= maximo
            ):
                raise AssertionError(f"regra de ordem violada em {no.chave!r}")
            he = checar(no.esquerda, minimo, no.chave)
            hd = checar(no.direita, no.chave, maximo)
            if abs(he - hd) > 1:
                raise AssertionError(f"desbalanceada em {no.chave!r}")
            if no.altura != 1 + max(he, hd):
                raise AssertionError(f"altura errada em {no.chave!r}")
            return no.altura

        try:
            checar(self._raiz, None, None)
            return True
        except AssertionError:
            return False
