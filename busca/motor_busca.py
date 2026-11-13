"""
MotorBusca — recebe a consulta do usuário e devolve as páginas ordenadas
por relevância.

1. A consulta passa pelo MESMO tokenizador usado na indexação
   ("Árvores AVL" -> ["arvores", "avl"]).
2. Para cada termo, buscamos na AVL do índice invertido  -> O(log n) cada.
3. Combinamos os resultados:
     modo "todas"    -> páginas que têm TODOS os termos   (interseção)
     modo "qualquer" -> páginas que têm PELO MENOS UM     (união)
4. Calculamos uma pontuação TF-IDF simplificada:
     TF  (frequência do termo)  : quanto mais vezes aparece na página, melhor
                                  -> 1 + log(freq)
     IDF (raridade do termo)    : palavra rara vale mais que palavra comum
                                  -> log(1 + total_paginas / paginas_com_o_termo)
     pontuação = soma de TF * IDF de cada termo encontrado
"""

import math
import re
import time
from dataclasses import dataclass, field


@dataclass
class Resultado:
    pagina: object
    pontuacao: float
    termos_encontrados: list
    trecho: list = field(default_factory=list)  # [(texto, destacar?), ...]


@dataclass
class RespostaBusca:
    consulta: str
    termos: list
    termos_ausentes: list
    resultados: list
    tempo_ms: float
    modo: str


class MotorBusca:
    TAMANHO_TRECHO = 220

    def __init__(self, indice, repositorio, tokenizador):
        self._indice = indice
        self._repositorio = repositorio
        self._tokenizador = tokenizador

    def buscar(self, consulta, modo="todas", limite=50):
        inicio = time.perf_counter()
        termos = list(dict.fromkeys(self._tokenizador.tokens(consulta)))  # sem repetidos

        # 1) uma busca na AVL por termo
        ocorrencias = {termo: self._indice.buscar(termo) for termo in termos}
        ausentes = [t for t, oc in ocorrencias.items() if not oc]

        # 2) combina os conjuntos de páginas
        conjuntos = [set(oc) for oc in ocorrencias.values()]
        if not conjuntos:
            ids = set()
        elif modo == "qualquer":
            ids = set().union(*conjuntos)
        else:
            ids = set.intersection(*conjuntos)

        # 3) pontua cada página (TF-IDF)
        total = max(len(self._repositorio), 1)
        resultados = []
        for id_pagina in ids:
            pontuacao, encontrados = 0.0, []
            for termo, oc in ocorrencias.items():
                if id_pagina in oc:
                    tf = 1 + math.log(oc[id_pagina])
                    idf = math.log(1 + total / len(oc))
                    pontuacao += tf * idf
                    encontrados.append(termo)
            pagina = self._repositorio.obter(id_pagina)
            if pagina:
                resultados.append(Resultado(pagina, round(pontuacao, 3), encontrados,
                                            self.gerar_trecho(pagina.conteudo, termos)))

        # 4) ordena: maior pontuação primeiro
        resultados.sort(key=lambda r: (-r.pontuacao, r.pagina.id))
        tempo = (time.perf_counter() - inicio) * 1000
        return RespostaBusca(consulta, termos, ausentes, resultados[:limite], round(tempo, 3), modo)

    def gerar_trecho(self, texto, termos):
        """Recorta um pedaço do texto em volta do primeiro termo encontrado e
        marca quais palavras devem aparecer destacadas no resultado."""
        termos = set(termos)
        posicao = 0
        for m in re.finditer(r"\w+", texto):
            if self._tokenizador.normalizar(m.group()) in termos:
                posicao = m.start()
                break
        inicio = max(0, posicao - 60)
        fim = min(len(texto), inicio + self.TAMANHO_TRECHO)
        recorte = ("…" if inicio > 0 else "") + texto[inicio:fim] + ("…" if fim < len(texto) else "")

        partes = []
        for pedaco in re.split(r"(\w+)", recorte):
            if pedaco:
                partes.append((pedaco, self._tokenizador.normalizar(pedaco) in termos))
        return partes
