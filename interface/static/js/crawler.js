// Painel do crawler: envia os comandos (iniciar/parar) e, a cada segundo,
// pergunta o status ao servidor para atualizar contadores e log ao vivo.
const form = document.getElementById("form-crawler");
const retorno = document.getElementById("retorno");
const logEl = document.getElementById("log");

document.querySelectorAll("[data-url]").forEach((botao) => {
  botao.addEventListener("click", () => { form.url.value = botao.dataset.url; });
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const resposta = await fetch(ROTAS.iniciar, { method: "POST", body: new FormData(form) });
  const dados = await resposta.json();
  retorno.textContent = dados.mensagem;
  atualizar();
});

document.getElementById("btn-parar").addEventListener("click", async () => {
  const resposta = await fetch(ROTAS.parar, { method: "POST" });
  retorno.textContent = (await resposta.json()).mensagem;
});

function definir(id, valor) { document.getElementById(id).textContent = valor; }

async function atualizar() {
  const s = await (await fetch(ROTAS.status)).json();
  const estado = document.getElementById("estado");
  estado.textContent = s.estado;
  estado.className = "estado " + s.estado;
  definir("c-novas", s.novas);
  definir("c-atualizadas", s.atualizadas);
  definir("c-fila", s.na_fila);
  definir("c-visitadas", s.visitadas);
  definir("c-erros", s.erros);
  definir("c-palavras", s.estatisticas.palavras);
  definir("arvore-info", `${s.estatisticas.paginas} páginas · altura da AVL ${s.estatisticas.altura}`);
  definir("url-atual", s.url_atual ? "Visitando: " + s.url_atual : "");
  document.getElementById("btn-iniciar").disabled = s.estado === "executando";

  const noFim = logEl.scrollTop + logEl.clientHeight >= logEl.scrollHeight - 20;
  logEl.innerHTML = "";
  s.log.forEach((linha) => {
    const div = document.createElement("div");
    const hora = document.createElement("span");
    hora.className = "hora";
    hora.textContent = linha.hora;
    const msg = document.createElement("span");
    msg.className = linha.tipo;
    msg.textContent = linha.msg;
    div.append(hora, msg);
    logEl.appendChild(div);
  });
  if (noFim) logEl.scrollTop = logEl.scrollHeight;
}

atualizar();
setInterval(atualizar, 1000);
