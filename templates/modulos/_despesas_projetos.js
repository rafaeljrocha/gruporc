/* ============================================================================
   Lógica compartilhada de Projetos + Despesas (transversal a módulos)
   Requer no escopo: MODULO_SLUG (string), CATEGORIAS_DESPESA (array)
   e os helpers de comum.js (API, escapeHtml, formatarBRL, abrirModal, etc).
   ============================================================================ */
let projetosCache = [];
let despesasCache = [];
let fornecedoresDespCache = [];

function _linkArqDesp(caminho, nome) {
  if (!caminho) return "—";
  return `<a href="#" onclick="window.open('/data-arquivo?caminho='+encodeURIComponent('${caminho}'),'_blank');return false;">${escapeHtml(nome || "abrir")}</a>`;
}

const BADGE_PROJETO = { aberto: "azul", concluido: "verde", cancelado: "vermelho" };
const BADGE_PAGAMENTO = { pendente: "amarelo", pago: "verde", cancelado: "vermelho" };

/* ---------------- Projetos ---------------- */
async function carregarProjetos() {
  try {
    const totais = await API.get(`/api/projetos/totais?modulo_slug=${MODULO_SLUG}`);
    projetosCache = totais;
    renderizarProjetos(totais);
    preencherFiltroProjetos(totais);
  } catch (e) { avisar(e.message); }
}

function renderizarProjetos(projetos) {
  const cont = document.getElementById("lista-projetos");
  if (!projetos.length) { cont.innerHTML = '<p class="vazio">Nenhum projeto cadastrado.</p>'; return; }
  cont.innerHTML = projetos.map((p) => {
    const orc = p.orcamento || 0;
    const gasto = p.total_gasto || 0;
    const saldo = orc - gasto;
    return `
    <div class="card-projeto">
      <div class="card-projeto-header">
        <span class="card-projeto-nome">🗂 ${escapeHtml(p.nome)}</span>
        <span class="badge badge-${BADGE_PROJETO[p.status] || "cinza"}">${escapeHtml(p.status || "")}</span>
      </div>
      <div class="card-projeto-stats">
        <span>Orçamento: <strong>${formatarBRL(orc)}</strong></span>
        <span>Gasto: <strong>${formatarBRL(gasto)}</strong></span>
        <span>Saldo: <strong>${formatarBRL(saldo)}</strong></span>
        <span>${p.qtd_despesas || 0} despesa(s)</span>
      </div>
      <div class="card-projeto-acoes">
        <button class="botao secundario" onclick="filtrarPorProjeto(${p.id})">Ver despesas</button>
        <button class="botao secundario" onclick='editarProjeto(${JSON.stringify(p)})'>Editar</button>
        <button class="botao secundario" onclick="excluirProjeto(${p.id})">Excluir</button>
      </div>
    </div>`;
  }).join("");
}

function preencherFiltroProjetos(projetos) {
  const sel = document.getElementById("filtro-projeto");
  const atual = sel.value;
  sel.innerHTML = `<option value="">Todas as despesas</option>` +
    projetos.map((p) => `<option value="${p.id}">${escapeHtml(p.nome)}</option>`).join("");
  sel.value = atual;
}

function _opcoesProjetoSelect(selId) {
  return `<option value="">Sem projeto</option>` + projetosCache.map((p) =>
    `<option value="${p.id}" ${p.id === selId ? "selected" : ""}>${escapeHtml(p.nome)}</option>`).join("");
}

function abrirModalProjeto() {
  const f = document.getElementById("form-projeto");
  f.reset(); f.id.value = ""; f.modulo_slug.value = MODULO_SLUG;
  document.getElementById("titulo-modal-projeto").textContent = "Novo Projeto";
  inicializarMascarasMonetarias(f);
  abrirModal("modal-projeto");
}
function editarProjeto(p) {
  const f = document.getElementById("form-projeto");
  f.reset(); f.modulo_slug.value = MODULO_SLUG;
  preencherFormulario(f, p);
  document.getElementById("titulo-modal-projeto").textContent = "Editar Projeto";
  inicializarMascarasMonetarias(f);
  abrirModal("modal-projeto");
}
async function salvarProjeto() {
  const f = document.getElementById("form-projeto");
  if (!f.nome.value.trim()) { avisar("Nome do projeto é obrigatório"); return; }
  const dados = lerFormulario(f);
  dados.modulo_slug = MODULO_SLUG;
  const id = f.id.value;
  try {
    if (id) await API.put(`/api/projetos/${id}`, dados);
    else await API.post("/api/projetos", dados);
    fecharModal("modal-projeto");
    carregarProjetos();
    avisar("Projeto salvo", "sucesso");
  } catch (e) { avisar(e.message); }
}
async function excluirProjeto(id) {
  if (!confirm("Excluir este projeto? As despesas serão mantidas e desvinculadas.")) return;
  try { await API.delete(`/api/projetos/${id}`); carregarProjetos(); carregarDespesas(); } catch (e) { avisar(e.message); }
}
function filtrarPorProjeto(id) {
  document.getElementById("filtro-projeto").value = String(id);
  carregarDespesas();
}

/* ---------------- Despesas ---------------- */
async function carregarDespesas() {
  try {
    const filtro = document.getElementById("filtro-projeto").value;
    let url = `/api/modulo-despesas?modulo_slug=${MODULO_SLUG}`;
    if (filtro) url += `&projeto_id=${filtro}`;
    despesasCache = await API.get(url);
    renderizarDespesas(despesasCache);
    atualizarTotalDespesas(despesasCache);
  } catch (e) { avisar(e.message); }
}

function renderizarDespesas(despesas) {
  const corpo = document.getElementById("tabela-despesas");
  corpo.innerHTML = despesas.map((d) => `
    <tr>
      <td>${d.numero || ""}</td>
      <td>${escapeHtml(d.fornecedor || "")}</td>
      <td>${escapeHtml(d.descricao || "")}</td>
      <td>${escapeHtml(d.projeto_nome || "—")}</td>
      <td>${formatarBRL(d.valor)}</td>
      <td>${escapeHtml(d.data_vencimento || "")}</td>
      <td><span class="badge badge-${BADGE_PAGAMENTO[d.status_pagamento] || "cinza"}">${escapeHtml(d.status_pagamento || "")}</span></td>
      <td>${_linkArqDesp(d.caminho_arquivo, d.nome_arquivo)}</td>
      <td>
        <button class="botao secundario" onclick='editarDespesa(${JSON.stringify(d)})'>Editar</button>
        <button class="botao secundario" onclick="excluirDespesa(${d.id})">Excluir</button>
      </td>
    </tr>`).join("") || `<tr><td colspan="9">Nenhuma despesa registrada.</td></tr>`;
}

function atualizarTotalDespesas(despesas) {
  const total = despesas.reduce((s, d) => s + (Number(d.valor) || 0), 0);
  document.getElementById("total-despesas").textContent = formatarBRL(total);
}

async function _prepararModalDespesa(d) {
  const f = document.getElementById("form-despesa");
  f.reset();
  f.modulo_slug.value = MODULO_SLUG;
  // Projetos
  f.projeto_id.innerHTML = _opcoesProjetoSelect(d ? d.projeto_id : null);
  // Categorias
  f.categoria.innerHTML = `<option value="">— Categoria —</option>` +
    CATEGORIAS_DESPESA.map((c) => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join("");
  // Fornecedores (datalist)
  try {
    fornecedoresDespCache = await API.get("/api/fornecedores");
    document.getElementById("lista-fornecedores-desp").innerHTML =
      fornecedoresDespCache.map((x) => `<option value="${escapeHtml(x.nome)}"></option>`).join("");
  } catch (e) { /* opcional */ }
  inicializarMascarasMonetarias(f);
}

async function abrirModalDespesa() {
  await _prepararModalDespesa(null);
  const f = document.getElementById("form-despesa");
  f.id.value = "";
  document.getElementById("titulo-modal-despesa").textContent = "Nova Despesa";
  togglePagamentoCampos();
  abrirModal("modal-despesa");
}
async function editarDespesa(d) {
  await _prepararModalDespesa(d);
  const f = document.getElementById("form-despesa");
  preencherFormulario(f, d);
  document.getElementById("titulo-modal-despesa").textContent = "Editar Despesa";
  togglePagamentoCampos();
  abrirModal("modal-despesa");
}
function togglePagamentoCampos() {
  const modo = document.getElementById("form-despesa").modo_pagamento.value;
  document.getElementById("campo-chave-pix").style.display = (modo === "pix") ? "" : "none";
  document.getElementById("campo-parceria").style.display = (modo === "parceria") ? "" : "none";
}
function fornecedorSelecionado() {
  const f = document.getElementById("form-despesa");
  const nome = f.fornecedor.value.trim();
  const forn = fornecedoresDespCache.find((x) => x.nome === nome);
  if (forn && forn.chave_pix && !f.chave_pix.value) f.chave_pix.value = forn.chave_pix;
}
async function salvarDespesa() {
  const f = document.getElementById("form-despesa");
  if (!f.fornecedor.value.trim()) { avisar("Fornecedor é obrigatório"); return; }
  const id = f.id.value;
  try {
    if (id) {
      const dados = lerFormulario(f);
      dados.modulo_slug = MODULO_SLUG;
      await API.put(`/api/modulo-despesas/${id}`, dados);
    } else {
      const fd = new FormData(f);
      fd.set("modulo_slug", MODULO_SLUG);
      // valor mascarado → enviar número
      fd.set("valor", f.valor.dataset.valorNumerico || "0");
      await API.postForm("/api/modulo-despesas", fd);
    }
    fecharModal("modal-despesa");
    carregarProjetos();
    carregarDespesas();
    avisar("Despesa salva", "sucesso");
  } catch (e) { avisar(e.message); }
}
async function excluirDespesa(id) {
  if (!confirm("Excluir esta despesa?")) return;
  try { await API.delete(`/api/modulo-despesas/${id}`); carregarProjetos(); carregarDespesas(); } catch (e) { avisar(e.message); }
}
