"""
Crawler — robô que coleta páginas automaticamente e manda indexar.

Algoritmo: BUSCA EM LARGURA (BFS), igual à de grafos:
    fila      <- [ (url_inicial, profundidade 0) ]
    visitados <- conjunto vazio
    enquanto houver fila e não atingiu o limite de páginas:
        tira a primeira URL da fila
        baixa o HTML  (urllib, biblioteca padrão)
        extrai título, texto e links  (ExtratorHTML)
        indexa a página no Buscador  -> entra nas árvores AVL
        coloca na fila os links ainda não visitados (profundidade + 1)

Boas práticas de um crawler "educado":
  - respeita o robots.txt do site;
  - espera um intervalo entre requisições;
  - só segue links do mesmo domínio (opcional);
  - não visita a mesma URL duas vezes.

Roda em uma THREAD separada para a interface continuar respondendo,
e guarda um log que o painel de controle mostra ao vivo.
"""

import threading
import time
from collections import deque
from datetime import datetime
from urllib import robotparser
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

from .extrator_html import ExtratorHTML


class Crawler:
    USER_AGENT = "BuscaAVL-Crawler/1.0 (projeto academico)"
    EXTENSOES_IGNORADAS = (".pdf", ".jpg", ".jpeg", ".png", ".gif", ".zip", ".mp3",
                           ".mp4", ".css", ".js", ".svg", ".ico", ".webp", ".exe")
    TAMANHO_MAXIMO = 2_000_000  # bytes por página

    def __init__(self, buscador, intervalo=0.5):
        self.buscador = buscador
        self.intervalo = intervalo
        self._thread = None
        self._parar = threading.Event()
        self._robots = {}
        self.log = deque(maxlen=300)
        self._zerar_status()

    def _zerar_status(self):
        self.estado = "parado"
        self.url_inicial = ""
        self.visitadas = 0
        self.novas = 0
        self.atualizadas = 0
        self.erros = 0
        self.na_fila = 0
        self.url_atual = ""

    # ------------------------------------------------------------ #
    # Controle (usado pelo painel)
    # ------------------------------------------------------------ #
    @property
    def em_execucao(self):
        return self._thread is not None and self._thread.is_alive()

    def iniciar(self, url_inicial, max_paginas=20, max_profundidade=2, mesmo_dominio=True):
        if self.em_execucao:
            return False
        url_inicial = self.codificar_url(url_inicial)
        self._zerar_status()
        self.log.clear()
        self._parar.clear()
        self.url_inicial = url_inicial
        self._thread = threading.Thread(
            target=self._executar,
            args=(url_inicial, max_paginas, max_profundidade, mesmo_dominio),
            daemon=True,
        )
        self._thread.start()
        return True

    def parar(self):
        self._parar.set()

    def status(self):
        return {
            "estado": self.estado,
            "url_inicial": self.url_inicial,
            "url_atual": self.url_atual,
            "visitadas": self.visitadas,
            "novas": self.novas,
            "atualizadas": self.atualizadas,
            "erros": self.erros,
            "na_fila": self.na_fila,
            "log": list(self.log)[-60:],
            "estatisticas": self.buscador.estatisticas(),
        }

    def _registrar(self, tipo, mensagem):
        self.log.append({"hora": datetime.now().strftime("%H:%M:%S"), "tipo": tipo, "msg": mensagem})

    # ------------------------------------------------------------ #
    # O algoritmo (BFS)
    # ------------------------------------------------------------ #
    def _executar(self, url_inicial, max_paginas, max_profundidade, mesmo_dominio):
        self.estado = "executando"
        dominio = urlparse(url_inicial).netloc
        fila = deque([(url_inicial, 0)])
        visitados = {url_inicial}
        self._registrar("info", f"Iniciando em {url_inicial} (máx. {max_paginas} páginas, profundidade {max_profundidade})")

        while fila and not self._parar.is_set() and (self.novas + self.atualizadas) < max_paginas:
            url, profundidade = fila.popleft()
            self.na_fila = len(fila)
            self.url_atual = url

            if not self._permitido_robots(url):
                self._registrar("aviso", f"Bloqueado pelo robots.txt: {url}")
                continue
            try:
                html = self._baixar(url)
            except Exception as erro:  # rede, 404, timeout, não é HTML...
                self.erros += 1
                self._registrar("erro", f"{url} — {erro}")
                continue
            self.visitadas += 1

            extrator = ExtratorHTML(url)
            extrator.feed(html)
            self._indexar(url, extrator)

            if profundidade < max_profundidade:
                for link in extrator.links:
                    if link not in visitados and self._link_valido(link, dominio, mesmo_dominio):
                        visitados.add(link)
                        fila.append((link, profundidade + 1))
            self.na_fila = len(fila)
            time.sleep(self.intervalo)

        self.buscador.salvar()
        self.url_atual = ""
        self.estado = "interrompido" if self._parar.is_set() else "concluído"
        self._registrar("info", f"Fim: {self.novas} novas, {self.atualizadas} atualizadas, {self.erros} erros.")

    def _indexar(self, url, extrator):
        titulo = extrator.titulo or url
        conteudo = extrator.texto or extrator.descricao
        if not conteudo:
            self._registrar("aviso", f"Sem texto, ignorada: {url}")
            return
        existente = self.buscador.obter_por_url(url)
        if existente:
            self.buscador.editar(existente.id, url, titulo, conteudo, extrator.palavras_chave, salvar=False)
            self.atualizadas += 1
            self._registrar("ok", f"Atualizada: {titulo}")
        else:
            self.buscador.cadastrar(url, titulo, conteudo, extrator.palavras_chave, origem="crawler", salvar=False)
            self.novas += 1
            self._registrar("ok", f"Indexada: {titulo}")

    # ------------------------------------------------------------ #
    # Auxiliares
    # ------------------------------------------------------------ #
    @staticmethod
    def codificar_url(url):
        """'.../Árvore_AVL' -> '.../%C3%81rvore_AVL' (URLs só aceitam ASCII)."""
        return quote(url, safe=":/?#[]@!$&'()*+,;=%~")

    def _baixar(self, url):
        requisicao = Request(self.codificar_url(url), headers={"User-Agent": self.USER_AGENT})
        with urlopen(requisicao, timeout=10) as resposta:
            tipo = resposta.headers.get_content_type()
            if tipo not in ("text/html", "application/xhtml+xml"):
                raise ValueError(f"não é HTML ({tipo})")
            charset = resposta.headers.get_content_charset() or "utf-8"
            return resposta.read(self.TAMANHO_MAXIMO).decode(charset, errors="replace")

    def _link_valido(self, link, dominio, mesmo_dominio):
        partes = urlparse(link)
        if partes.scheme not in ("http", "https", "file"):
            return False
        if partes.path.lower().endswith(self.EXTENSOES_IGNORADAS):
            return False
        return not mesmo_dominio or partes.netloc == dominio

    def _permitido_robots(self, url):
        partes = urlparse(url)
        if partes.scheme not in ("http", "https"):
            return True  # arquivos locais não têm robots.txt
        base = f"{partes.scheme}://{partes.netloc}"
        if base not in self._robots:
            # baixamos o robots.txt com o NOSSO User-Agent (o leitor padrão do
            # Python usa um genérico que alguns sites recusam) e só depois analisamos
            leitor = robotparser.RobotFileParser()
            try:
                requisicao = Request(base + "/robots.txt", headers={"User-Agent": self.USER_AGENT})
                with urlopen(requisicao, timeout=10) as resposta:
                    leitor.parse(resposta.read().decode("utf-8", errors="replace").splitlines())
            except Exception:
                leitor = None  # sem robots.txt acessível: liberado
            self._robots[base] = leitor
        leitor = self._robots[base]
        return leitor is None or leitor.can_fetch(self.USER_AGENT, self.codificar_url(url))
