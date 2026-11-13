// Autocompletar da caixa de busca.
// A cada letra digitada, pergunta ao servidor (/api/sugestoes) quais palavras
// do índice começam com aquele prefixo — no servidor isso é uma busca por
// PREFIXO na árvore AVL, que só desce nos galhos que podem conter o prefixo.
document.querySelectorAll("[data-autocompletar]").forEach((campo) => {
  const lista = campo.parentElement.querySelector(".sugestoes");
  let itens = [];
  let ativo = -1;
  let espera;

  const ultimaPalavra = () => campo.value.split(/\s+/).pop();

  function fechar() {
    lista.classList.remove("aberta");
    ativo = -1;
  }

  function escolher(palavra) {
    const partes = campo.value.split(/\s+/);
    partes[partes.length - 1] = palavra;
    campo.value = partes.join(" ") + " ";
    fechar();
    campo.focus();
  }

  function desenhar(prefixo) {
    lista.innerHTML = "";
    itens.forEach((palavra, i) => {
      const li = document.createElement("li");
      const negrito = document.createElement("b");
      negrito.textContent = palavra.slice(0, prefixo.length);
      li.append(negrito, palavra.slice(prefixo.length));
      li.classList.toggle("ativa", i === ativo);
      li.addEventListener("mousedown", (e) => { e.preventDefault(); escolher(palavra); });
      lista.appendChild(li);
    });
    lista.classList.toggle("aberta", itens.length > 0);
  }

  campo.addEventListener("input", () => {
    clearTimeout(espera);
    const prefixo = ultimaPalavra();
    if (prefixo.length < 1) { fechar(); return; }
    espera = setTimeout(async () => {
      const resposta = await fetch("/api/sugestoes?q=" + encodeURIComponent(prefixo));
      itens = await resposta.json();
      ativo = -1;
      desenhar(prefixo.toLowerCase());
    }, 120);
  });

  campo.addEventListener("keydown", (e) => {
    if (!lista.classList.contains("aberta")) return;
    if (e.key === "ArrowDown") { ativo = (ativo + 1) % itens.length; desenhar(ultimaPalavra()); e.preventDefault(); }
    else if (e.key === "ArrowUp") { ativo = (ativo - 1 + itens.length) % itens.length; desenhar(ultimaPalavra()); e.preventDefault(); }
    else if (e.key === "Enter" && ativo >= 0) { escolher(itens[ativo]); e.preventDefault(); }
    else if (e.key === "Escape") { fechar(); }
  });

  campo.addEventListener("blur", fechar);
});
