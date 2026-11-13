"""
VisualizadorArvore — calcula ONDE desenhar cada nó da AVL na tela.

A ideia é simples e bonita:
  - eixo Y (vertical)  = nível do nó (raiz em cima, filhos embaixo)
  - eixo X (horizontal)= ordem em que o nó aparece no percurso EM-ORDEM
Como o percurso em-ordem de uma árvore de busca já sai ordenado, os nós
ficam da esquerda para a direita em ordem alfabética, e nenhum se sobrepõe.

O template HTML só pega a lista de nós/arestas e desenha círculos e linhas (SVG).
Como o índice pode ter milhares de palavras, mostramos só alguns níveis a partir
de uma raiz escolhida — clicando num nó, ele vira a nova raiz da visualização.
"""


class VisualizadorArvore:
    ESPACO_X = 86
    ESPACO_Y = 84
    MARGEM = 48
    RAIO = 26

    def __init__(self, arvore):
        self.arvore = arvore

    def gerar(self, raiz_chave=None, profundidade=4, destacar=()):
        if raiz_chave not in (None, ""):
            raiz = self.arvore.obter_no(raiz_chave)
        else:
            raiz = self.arvore.raiz
        destacar = set(destacar)
        nos, arestas = [], []
        contador = [0]
        nivel_maximo = [0]

        def visitar(no, nivel):
            if no is None or nivel >= profundidade:
                return None
            esquerda = visitar(no.esquerda, nivel + 1)       # 1) esquerda
            info = {                                          # 2) o próprio nó
                "chave": no.chave,
                "rotulo": self._rotulo(no.chave),
                "x": self.MARGEM + contador[0] * self.ESPACO_X,
                "y": self.MARGEM + nivel * self.ESPACO_Y,
                "altura": no.altura,
                "fb": self.arvore.fator_balanceamento(no),
                "qtd": len(no.valor) if isinstance(no.valor, dict) else None,
                "destaque": no.chave in destacar,
                "oculto": nivel == profundidade - 1 and (no.esquerda or no.direita) is not None,
            }
            contador[0] += 1
            nivel_maximo[0] = max(nivel_maximo[0], nivel)
            direita = visitar(no.direita, nivel + 1)          # 3) direita
            for filho in (esquerda, direita):
                if filho:
                    arestas.append({
                        "x1": info["x"], "y1": info["y"], "x2": filho["x"], "y2": filho["y"],
                        "destaque": info["destaque"] and filho["destaque"],
                    })
            nos.append(info)
            return info

        visitar(raiz, 0)
        return {
            "nos": nos,
            "arestas": arestas,
            "largura": self.MARGEM * 2 + max(contador[0] - 1, 0) * self.ESPACO_X,
            "altura": self.MARGEM * 2 + nivel_maximo[0] * self.ESPACO_Y + 24,
            "raio": self.RAIO,
            "raiz": raiz.chave if raiz else None,
        }

    @staticmethod
    def _rotulo(chave):
        texto = str(chave)
        return texto if len(texto) <= 8 else texto[:7] + "…"
