# BuscaAVL

    PROJETO FEITO TOTALMENTE USANDO CLAUDE CODE, com intuito estritamente acadêmico sem fins lucrativos

Buscador web com índice próprio em **Árvore AVL**: trabalho de Algoritmos e Estruturas de Dados (IFPE).

## Como rodar
```bash
pip install -r requirements.txt
python main.py
```
O navegador abre em http://127.0.0.1:5000.

## Testes
```bash
python -m unittest discover testes
```

## Estrutura
| Pasta | Conteúdo |
|-------|----------|
| `arvore/` | `NoAVL` e `ArvoreAVL` (inserção, remoção, busca, rotações) |
| `indice/` | `Tokenizador`, `IndiceInvertido` (AVL de palavras), `RepositorioPaginas` (AVL por id e por URL) |
| `busca/` | `MotorBusca` (consultas E/OU, ranking TF-IDF) |
| `nucleo/` | `Buscador`, a fachada que liga tudo |
| `crawler/` | `Crawler` (BFS) e `ExtratorHTML` |
| `persistencia/` | `ArmazenamentoJSON` |
| `interface/` | Flask (`web.py`), templates HTML, CSS, visualizador da árvore e laboratório AVL |
| `dados/` | `exemplo.json` (20 páginas), `site_exemplo/` (mini-site para o crawler), `banco.json` (gerado) |
| `docs/EXPLICACAO.md` | roteiro da apresentação |
