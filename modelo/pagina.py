"""
Pagina — representa um documento indexado pelo buscador
(cadastrado à mão ou coletado pelo crawler).
"""

from datetime import datetime


class Pagina:
    def __init__(self, url, titulo, conteudo, palavras_chave=None,
                 origem="manual", id=None, data_indexacao=None):
        self.id = id
        self.url = url.strip()
        self.titulo = titulo.strip()
        self.conteudo = conteudo.strip()
        self.palavras_chave = [p.strip() for p in (palavras_chave or []) if p.strip()]
        self.origem = origem  # "manual" ou "crawler"
        self.data_indexacao = data_indexacao or datetime.now().strftime("%d/%m/%Y %H:%M")

    def texto_completo(self):
        return f"{self.titulo} {self.conteudo} {' '.join(self.palavras_chave)}"

    # Conversão para/de dicionário (usada na persistência em JSON)
    def para_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "titulo": self.titulo,
            "conteudo": self.conteudo,
            "palavras_chave": self.palavras_chave,
            "origem": self.origem,
            "data_indexacao": self.data_indexacao,
        }

    @classmethod
    def de_dict(cls, dados):
        return cls(**dados)

    def __repr__(self):
        return f"Pagina(id={self.id}, titulo={self.titulo!r})"
