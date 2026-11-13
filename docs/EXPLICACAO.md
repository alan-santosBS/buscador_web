# BuscaAVL — roteiro para a apresentação

## 1. O que é (slide de abertura)
**BuscaAVL** é um buscador web feito do zero em Python. Ele:
- **coleta** páginas sozinho (crawler) ou por cadastro manual;
- **indexa** cada palavra numa **Árvore AVL** implementada pela equipe;
- **busca** por uma ou várias palavras e ordena por relevância (TF-IDF);
- mostra a **árvore desenhada** na tela e um **laboratório** para ver as rotações.

Tecnologias: Python (lógica), Flask (só entrega as páginas), HTML + CSS (interface).
Nenhuma biblioteca de árvore, crawler ou motor de busca: só a biblioteca padrão (`urllib`, `html.parser`, `json`).

---

## 2. Como um buscador funciona (e onde a árvore entra)

```
  [Crawler] --baixa HTML--> [ExtratorHTML] --texto--> [Tokenizador] --palavras-->
  [IndiceInvertido = ÁRVORE AVL]  <--consulta--  [MotorBusca]  <--  usuário
```

**Índice invertido** = palavra → páginas onde ela aparece (como o índice remissivo de um livro).

```
"python" -> {1: 10, 12: 9, 13: 1, 20: 6}   (página 1 tem peso 10, página 12 peso 9...)
"arvore" -> {2: 14, 3: 11, 4: 9, ...}
```
Cada palavra é **um nó da AVL**. Chave = palavra, valor = dicionário {id da página: frequência}.

---

## 3. A árvore escolhida: AVL

### Regra de inclusão
- Igual à binária de busca: **chave menor → esquerda, chave maior → direita** (ordem alfabética).
- Chave repetida não duplica: só atualiza o valor.
- **Regra extra da AVL:** em todo nó, `fator de balanceamento = altura(esquerda) − altura(direita)`
  precisa ser **−1, 0 ou +1**. Se virar ±2, a árvore faz **rotações**.

### Ponteiros por nó
**2 ponteiros** (esquerda e direita) + chave + valor + **altura**
(arquivo [arvore/no_avl.py](../arvore/no_avl.py)).

### Os 4 casos de rotação ([arvore/arvore_avl.py](../arvore/arvore_avl.py), método `_balancear`)
| Caso | Situação | Correção | Demo no laboratório |
|------|----------|----------|---------------------|
| LL | pesado à esquerda, filho pesa à esquerda | rotação simples à **direita** | `30 20 10` |
| RR | pesado à direita, filho pesa à direita | rotação simples à **esquerda** | `10 20 30` |
| LR | pesado à esquerda, filho pesa à direita | esquerda no filho + direita no nó | `30 10 20` |
| RL | pesado à direita, filho pesa à esquerda | direita no filho + esquerda no nó | `10 30 20` |

### Remoção
- nó com 0 ou 1 filho: o filho toma o lugar dele;
- nó com 2 filhos: copia o **sucessor** (menor da subárvore direita) e remove o sucessor;
- na volta da recursão cada ancestral é rebalanceado.

### Por que AVL? (justificativa)
1. **Desempenho garantido O(log n)** em busca, inserção e remoção, no pior caso.
   Uma binária de busca comum recebendo palavras em ordem vira uma lista (O(n)).
   *Demo:* no laboratório, botão "1 a 15 em ordem": altura 4 em vez de 15.
2. **A operação mais frequente num buscador é a BUSCA.** A AVL é a árvore binária
   mais equilibrada (mais que a rubro-negra), então tem as buscas mais curtas.
3. **Mantém as palavras em ordem.** Isso dá de graça o **autocompletar** (busca por prefixo)
   e a listagem ordenada (percurso em-ordem).
4. **Trie** gastaria um nó por letra (muita memória, desenho enorme). **B/B+** brilham em disco;
   nosso índice fica em memória.

Números reais do projeto: 395 palavras → altura **10**. O limite teórico da AVL é cerca de 1,44·log₂(n) ≈ 12.
Qualquer palavra é achada em no máximo 10 comparações.

### Onde mais usamos AVL
[indice/repositorio_paginas.py](../indice/repositorio_paginas.py): **duas** AVLs, uma por **id** (abrir a página)
e uma por **URL** (o crawler pergunta "já tenho esta URL?"). É a ideia de índice primário e secundário.

---

## 4. Orientação a objetos (peso grande na nota)

| Classe | Responsabilidade | Conceito de OO |
|--------|------------------|----------------|
| `NoAVL` | guardar chave, valor, filhos, altura | encapsulamento de dados |
| `ArvoreAVL` | inserir, buscar, remover, rotacionar | encapsulamento (`_raiz`, `_rotacao_*` privados), métodos especiais `__len__`, `__contains__`, `__iter__` |
| `Pagina` | representar um documento | modelo / entidade |
| `Tokenizador` | texto → palavras | responsabilidade única |
| `IndiceInvertido` | palavra → páginas (usa AVL) | **composição** (tem uma ArvoreAVL) |
| `RepositorioPaginas` | guardar páginas (2 AVLs) | composição |
| `MotorBusca` | consultar e ranquear | responsabilidade única |
| `Buscador` | coordena tudo | padrão **Facade** (fachada) |
| `ExtratorHTML` | ler HTML | **herança** de `HTMLParser` + **polimorfismo** (sobrescreve `handle_starttag`...) |
| `Crawler` | coletar páginas (BFS, thread) | composição com o Buscador |
| `ArmazenamentoJSON` | salvar/carregar | separa persistência da lógica |
| `VisualizadorArvore` | calcular o desenho | separa visual da estrutura |
| `LaboratorioAVL` | árvore de demonstração | reuso da ArvoreAVL |

A interface web **nunca** mexe direto na árvore. Ela chama o `Buscador`, que delega para as outras classes.

---

## 5. Detalhes que valem citar
- **Tokenizador:** minúsculas, sem acentos, sem *stopwords* ("de", "a", "que"...). Buscar "ARVORE" acha "árvore".
- **Pesos:** palavra no título vale 3×, palavra-chave cadastrada vale 5×.
- **Relevância TF-IDF:** `(1 + log freq) × log(1 + total_páginas / páginas_com_a_palavra)`.
  Palavras raras pesam mais.
- **Busca com várias palavras:** "todas" = interseção dos conjuntos de páginas; "qualquer" = união.
- **Editar página** = tirar as palavras antigas da árvore e inserir as novas.
  **Remover** = se a palavra ficar sem nenhuma página, o nó sai da AVL (e ela se rebalanceia).
- **Crawler:** busca em largura (BFS) com fila e conjunto de visitados, limite de páginas e
  profundidade, respeita `robots.txt`, espera 0,5 s entre downloads e roda numa *thread*
  (com uma trava, *lock*, para não mexer na árvore ao mesmo tempo que a busca).
- **Persistência:** salva só as páginas em `dados/banco.json`; ao abrir, as árvores são reconstruídas.

---

## 6. Roteiro da demonstração (≈ 5 min)
1. `python main.py`: abre com 20 páginas de exemplo já indexadas.
2. **Buscar** `árvore busca`: mostrar resultados, trechos destacados e o quadro
   "Como a AVL encontrou" (caminho e número de comparações).
3. Digitar `pro` e mostrar o **autocompletar** (busca por prefixo na AVL).
4. **Árvore do índice**: buscar `python`, mostrar o caminho em verde; clicar num nó para descer.
5. **Laboratório AVL**: botões RR, LL, LR, RL e "1 a 15 em ordem".
6. **Crawler**: "Site de exemplo (offline)" → Iniciar. Ver o log ao vivo e o número de palavras
   da árvore crescendo. Depois buscar `bolo de rolo`.
7. **Páginas**: cadastrar uma página nova, buscar por ela, editar e remover.
8. Mostrar o código: `arvore_avl.py` (`_balancear`, `_rotacao_direita`) e `indice_invertido.py`.

## 7. Prints sugeridos para os slides
- Página inicial e página de resultados.
- Árvore do índice com caminho destacado.
- Laboratório antes e depois de uma rotação.
- Painel do crawler rodando.
- Código: `_balancear` + `_rotacao_direita`, `IndiceInvertido.adicionar`, `MotorBusca.buscar`.

## 8. Perguntas que o professor pode fazer
- **Por que não uma binária de busca simples?** Pode degenerar em lista (O(n)). A AVL garante O(log n).
- **Por que não Trie?** Muito mais nós e memória. A AVL também resolve prefixo, por ser ordenada.
- **Complexidade da busca com k palavras?** k × O(log n) na árvore, mais a combinação dos conjuntos.
- **O que acontece com a árvore quando removo uma página?** As palavras que só existiam nela
  são removidas da AVL, que se rebalanceia.
- **Como evita visitar a mesma página duas vezes?** Conjunto de visitados no crawler e a AVL por URL.
- **Usou biblioteca pronta?** Só `urllib` (baixar), `html.parser` (separar tags) e Flask (servir HTML).
  Árvore, índice, busca, ranking e crawler foram feitos por nós.
