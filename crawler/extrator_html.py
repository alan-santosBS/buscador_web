"""
ExtratorHTML — lê o HTML de uma página e separa o que interessa ao buscador:
  - título  (tag <title>)
  - texto visível (ignorando <script>, <style>...)
  - links   (atributo href das tags <a>), já convertidos para URL completa
  - palavras-chave e descrição (tags <meta>)

Herda de html.parser.HTMLParser (biblioteca PADRÃO do Python, que só
"quebra" o HTML em tags — a lógica de crawler e indexação é nossa).
O parser chama nossos métodos handle_starttag / handle_data / handle_endtag
conforme vai lendo o arquivo (é o polimorfismo da orientação a objetos).
"""

from html.parser import HTMLParser
from urllib.parse import urldefrag, urljoin


class ExtratorHTML(HTMLParser):
    IGNORAR = {"script", "style", "noscript", "svg", "head"}

    def __init__(self, url_base):
        super().__init__(convert_charrefs=True)
        self.url_base = url_base
        self.links = []
        self.palavras_chave = []
        self.descricao = ""
        self._titulo = []
        self._texto = []
        self._no_titulo = False
        self._ignorando = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self._no_titulo = True
        elif tag in self.IGNORAR:
            self._ignorando += 1
        elif tag == "a" and attrs.get("href"):
            url = urldefrag(urljoin(self.url_base, attrs["href"].strip()))[0]
            self.links.append(url)
        elif tag == "meta":
            nome = (attrs.get("name") or "").lower()
            if nome == "keywords":
                self.palavras_chave = [p.strip() for p in (attrs.get("content") or "").split(",")]
            elif nome == "description":
                self.descricao = attrs.get("content") or ""

    def handle_endtag(self, tag):
        if tag == "title":
            self._no_titulo = False
        elif tag in self.IGNORAR and self._ignorando:
            self._ignorando -= 1

    def handle_data(self, data):
        if self._no_titulo:
            self._titulo.append(data)
        elif not self._ignorando:
            self._texto.append(data)

    @property
    def titulo(self):
        return " ".join("".join(self._titulo).split())

    @property
    def texto(self):
        return " ".join(" ".join(self._texto).split())
