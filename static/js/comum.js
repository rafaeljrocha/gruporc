function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function formatarBRL(valor) {
  const numero = Number(valor) || 0;
  return numero.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function _parseValorMoeda(texto) {
  if (!texto) return 0;
  const limpo = String(texto).replace(/[^\d,.-]/g, "").replace(/\./g, "").replace(",", ".");
  return parseFloat(limpo) || 0;
}

function definirValorMoedaInput(input, valor, moeda = "BRL") {
  const numero = Number(valor) || 0;
  input.dataset.valorNumerico = numero;
  input.value = numero.toLocaleString("pt-BR", { style: "currency", currency: moeda });
}

function inicializarMascarasMonetarias(raiz) {
  const escopo = raiz || document;
  escopo.querySelectorAll("input[data-money]").forEach((input) => {
    if (input.dataset.mascaraAtiva) return;
    input.dataset.mascaraAtiva = "1";
    input.addEventListener("input", () => {
      const numero = _parseValorMoeda(input.value);
      input.dataset.valorNumerico = numero;
      input.value = numero.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
    });
    input.addEventListener("focus", () => {
      const numero = _parseValorMoeda(input.value);
      input.value = numero ? numero.toFixed(2).replace(".", ",") : "";
    });
    input.addEventListener("blur", () => {
      const numero = _parseValorMoeda(input.value);
      input.dataset.valorNumerico = numero;
      input.value = numero.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
    });
  });
}

function lerFormulario(form) {
  const dados = {};
  form.querySelectorAll("input, select, textarea").forEach((campo) => {
    if (!campo.name) return;
    if (campo.type === "checkbox") {
      dados[campo.name] = campo.checked;
    } else if (campo.dataset.money !== undefined) {
      dados[campo.name] = campo.dataset.valorNumerico ? Number(campo.dataset.valorNumerico) : _parseValorMoeda(campo.value);
    } else if (campo.type === "file") {
      // arquivos tratados separadamente via FormData
    } else {
      dados[campo.name] = campo.value;
    }
  });
  return dados;
}

function preencherFormulario(form, dados) {
  form.querySelectorAll("input, select, textarea").forEach((campo) => {
    if (!campo.name || !(campo.name in dados)) return;
    const valor = dados[campo.name];
    if (campo.type === "checkbox") {
      campo.checked = !!valor;
    } else if (campo.dataset.money !== undefined) {
      definirValorMoedaInput(campo, valor);
    } else {
      campo.value = valor === null || valor === undefined ? "" : valor;
    }
  });
}

function mostrarMensagem(el, texto, tipo = "info") {
  if (!el) return;
  el.className = `alerta alerta-${tipo}`;
  el.textContent = texto;
  el.style.display = "block";
}

function limparMensagem(el) {
  if (!el) return;
  el.textContent = "";
  el.style.display = "none";
}

function fecharModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.remove("aberto");
}

function abrirModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.add("aberto");
}

const API = {
  async _resposta(resposta) {
    let corpo = null;
    try { corpo = await resposta.json(); } catch (e) { corpo = null; }
    if (!resposta.ok) {
      const mensagem = (corpo && corpo.erro) || `Erro ${resposta.status}`;
      throw new Error(mensagem);
    }
    return corpo;
  },
  async get(url) {
    const resposta = await fetch(url, { headers: { Accept: "application/json" } });
    return API._resposta(resposta);
  },
  async post(url, dados) {
    const resposta = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados || {}),
    });
    return API._resposta(resposta);
  },
  async put(url, dados) {
    const resposta = await fetch(url, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados || {}),
    });
    return API._resposta(resposta);
  },
  async delete(url) {
    const resposta = await fetch(url, { method: "DELETE" });
    return API._resposta(resposta);
  },
  async postForm(url, formData, metodo = "POST") {
    const resposta = await fetch(url, { method: metodo, body: formData });
    return API._resposta(resposta);
  },
};
