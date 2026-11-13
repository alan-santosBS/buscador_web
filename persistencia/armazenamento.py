"""
ArmazenamentoJSON — grava e lê as páginas em um arquivo JSON.

Só as PÁGINAS são salvas. As árvores (índice invertido, por id, por URL)
são RECONSTRUÍDAS na hora de abrir o programa, reindexando cada página.
Isso mantém o arquivo simples e garante que o índice sempre bate com as páginas.

Se o arquivo principal ainda não existe, carregamos os dados de exemplo
(para a demonstração não começar vazia).
"""

import json
import os


class ArmazenamentoJSON:
    def __init__(self, caminho, caminho_exemplo=None):
        self.caminho = caminho
        self.caminho_exemplo = caminho_exemplo

    def carregar(self):
        for caminho in (self.caminho, self.caminho_exemplo):
            if caminho and os.path.exists(caminho):
                with open(caminho, encoding="utf-8") as arquivo:
                    return json.load(arquivo)
        return []

    def carregar_exemplo(self):
        with open(self.caminho_exemplo, encoding="utf-8") as arquivo:
            return json.load(arquivo)

    def salvar(self, lista_de_dicts):
        os.makedirs(os.path.dirname(self.caminho), exist_ok=True)
        temporario = self.caminho + ".tmp"
        with open(temporario, "w", encoding="utf-8") as arquivo:
            json.dump(lista_de_dicts, arquivo, ensure_ascii=False, indent=2)
        os.replace(temporario, self.caminho)  # troca só quando terminou de gravar
