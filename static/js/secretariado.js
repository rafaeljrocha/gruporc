let integrantes = [];
let integranteCarteiraId = null;
let integranteSaudeId = null;
let fornecedoresCache = [];
let recibosCache = [];

const msgGlobal = () => document.getElementById("mensagem-global");

function avisar(texto, tipo = "erro") {
  mostrarMensagem(msgGlobal(), texto, tipo);
  setTimeout(() => limparMensagem(msgGlobal()), 4000);
}

function abrirNoMaps(inputId) {
  const endereco = document.getElementById(inputId).value;
  if (!endereco) return;
  window.open("https://maps.google.com/?q=" + encodeURIComponent(endereco), "_blank");
}

function diasParaVencer(dataStr) {
  if (!dataStr) return null;
  const hoje = new Date();
  const data = new Date(dataStr);
  return Math.ceil((data - hoje) / 86400000);
}

/* ---------------- Navegação de abas ---------------- */
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("#abas-nav button").forEach((botao) => {
    botao.addEventListener("click", () => ativarAba(botao.dataset.aba));
  });
  const subabas = document.getElementById("subabas-saude");
  if (subabas) {
    subabas.querySelectorAll("button").forEach((botao) => {
      botao.addEventListener("click", () => ativarSubabaSaude(botao.dataset.subaba));
    });
  }
  carregarIntegrantes();
  carregarFornecedores();
});

function ativarAba(slug) {
  document.querySelectorAll("#abas-nav button").forEach((b) => b.classList.toggle("ativa", b.dataset.aba === slug));
  document.querySelectorAll(".aba-conteudo").forEach((s) => s.classList.toggle("ativa", s.id === "aba-" + slug));
  if (slug === "saude") carregarListaSaude();
  if (slug === "recibos") { carregarRecibos(); carregarReembolsos(); }
  if (slug === "viagens") carregarViagens();
  if (slug === "despesas") carregarDespesas();
  if (slug === "fornecedores") carregarFornecedores();
  if (slug === "configuracoes") carregarConfiguracoes();
}

function ativarSubabaSaude(slug) {
  document.querySelectorAll("#subabas-saude button").forEach((b) => b.classList.toggle("ativa", b.dataset.subaba === slug));
  document.querySelectorAll("#painel-saude-detalhe .aba-conteudo").forEach((s) => s.classList.toggle("ativa", s.id === "subaba-" + slug));
  if (!integranteSaudeId) return;
  if (slug === "medicamentos") carregarMedicamentos();
  if (slug === "consultas") carregarConsultas();
  if (slug === "exames") carregarExames();
  if (slug === "receitas") carregarReceitas();
}

/* ---------------- Integrantes ---------------- */
async function carregarIntegrantes() {
  try {
    integrantes = await API.get("/api/integrantes");
    renderizarIntegrantes();
    preencherSelectsIntegrantes();
    renderizarSaudeLista();
  } catch (e) { avisar(e.message); }
}

function badgeValidade(dataStr) {
  const dias = diasParaVencer(dataStr);
  if (dataStr && dias !== null && dias <= 60) {
    return ` <span class="badge badge-amarelo">vence em ${dias}d</span>`;
  }
  return "";
}

function renderizarIntegrantes() {
  const corpo = document.getElementById("tabela-integrantes");
  corpo.innerHTML = integrantes.map((i) => `
    <tr>
      <td>${escapeHtml(i.nome)}</td>
      <td>${escapeHtml(i.data_nascimento || "")}</td>
      <td>${escapeHtml(i.cpf || "")}</td>
      <td>${escapeHtml(i.numero_passaporte || "")} ${escapeHtml(i.validade_passaporte || "")}${badgeValidade(i.validade_passaporte)}</td>
      <td>${escapeHtml(i.numero_convenio_saude || "")} ${escapeHtml(i.validade_convenio_saude || "")}${badgeValidade(i.validade_convenio_saude)}</td>
      <td><button class="botao secundario" onclick="editarIntegrante(${i.id})">Editar</button></td>
    </tr>`).join("");
}

function preencherSelectsIntegrantes() {
  const opcoes = integrantes.map((i) => `<option value="${i.id}">${escapeHtml(i.nome)}</option>`).join("");
  const selectCarteira = document.getElementById("select-integrante-carteira");
  selectCarteira.innerHTML = opcoes;
  document.querySelectorAll(".select-integrante-generico").forEach((sel) => {
    sel.innerHTML = '<option value="">Selecione...</option>' + opcoes;
  });
  const selectPassageiros = document.getElementById("select-passageiros-viagem");
  if (selectPassageiros) selectPassageiros.innerHTML = opcoes;

  if (integrantes.length && !integranteCarteiraId) {
    integranteCarteiraId = integrantes[0].id;
    selectCarteira.value = integranteCarteiraId;
    carregarDocumentos();
  }
}

function abrirModalIntegrante(id) {
  const form = document.getElementById("form-integrante");
  form.reset();
  document.getElementById("titulo-modal-integrante").textContent = id ? "Editar Integrante" : "Novo Integrante";
  if (id) {
    const integrante = integrantes.find((i) => i.id === id);
    if (integrante) preencherFormulario(form, integrante);
  }
  abrirModal("modal-integrante");
}

function editarIntegrante(id) { abrirModalIntegrante(id); }

async function salvarIntegrante() {
  const form = document.getElementById("form-integrante");
  const dados = lerFormulario(form);
  const id = dados.id;
  delete dados.id;
  try {
    if (id) await API.put(`/api/integrantes/${id}`, dados);
    else await API.post("/api/integrantes", dados);
    fecharModal("modal-integrante");
    await carregarIntegrantes();
    avisar("Integrante salvo com sucesso.", "sucesso");
  } catch (e) { avisar(e.message); }
}

/* ---------------- Carteira Digital ---------------- */
async function carregarDocumentos() {
  integranteCarteiraId = Number(document.getElementById("select-integrante-carteira").value);
  try {
    const documentos = await API.get(`/api/integrantes/${integranteCarteiraId}/documentos`);
    document.getElementById("tabela-documentos").innerHTML = documentos.map((d) => `
      <tr>
        <td>${escapeHtml(d.tipo_documento)}</td>
        <td>${escapeHtml(d.descricao || "")}</td>
        <td>${escapeHtml(d.validade || "")}${badgeValidade(d.validade)}</td>
        <td>${d.caminho_arquivo ? `<a href="/data-arquivo?caminho=${encodeURIComponent(d.caminho_arquivo)}" target="_blank">Abrir</a>` : "-"}</td>
        <td><button class="botao secundario" onclick="excluirDocumento(${d.id})">Excluir</button></td>
      </tr>`).join("");
  } catch (e) { avisar(e.message); }
}

function abrirModalDocumento() {
  document.getElementById("form-documento").reset();
  abrirModal("modal-documento");
}

async function salvarDocumento() {
  const form = document.getElementById("form-documento");
  const dadosForm = new FormData(form);
  dadosForm.set("integrante_id", integranteCarteiraId);
  try {
    await API.postForm("/api/documentos", dadosForm);
    fecharModal("modal-documento");
    await carregarDocumentos();
    await carregarIntegrantes();
    avisar("Documento salvo com sucesso.", "sucesso");
  } catch (e) { avisar(e.message); }
}

async function excluirDocumento(id) {
  if (!confirm("Excluir este documento?")) return;
  try { await API.delete(`/api/documentos/${id}`); await carregarDocumentos(); } catch (e) { avisar(e.message); }
}

/* ---------------- Saúde ---------------- */
function renderizarSaudeLista() {
  const corpo = document.getElementById("tabela-saude-integrantes");
  if (!corpo) return;
  corpo.innerHTML = integrantes.map((i) => `
    <tr><td>${escapeHtml(i.nome)}</td>
    <td><button class="botao secundario" onclick="gerenciarSaude(${i.id}, '${escapeHtml(i.nome)}')">Gerenciar</button></td></tr>`).join("");
}

function carregarListaSaude() { renderizarSaudeLista(); }

function gerenciarSaude(id, nome) {
  integranteSaudeId = id;
  document.getElementById("painel-saude-detalhe").style.display = "block";
  document.getElementById("titulo-saude-integrante").textContent = nome;
  const integrante = integrantes.find((i) => i.id === id) || {};
  preencherFormulario(document.getElementById("form-prontuario"), integrante);
  document.getElementById("ultima-atualizacao-prontuario").textContent = integrante.biometria_atualizada_em
    ? `Última atualização: ${integrante.biometria_atualizada_em}` : "";
  ativarSubabaSaude("prontuario");
  carregarMedicamentos();
}

async function salvarProntuario(evento) {
  evento.preventDefault();
  const dados = lerFormulario(document.getElementById("form-prontuario"));
  dados.biometria_atualizada_em = new Date().toISOString().slice(0, 10);
  try {
    await API.put(`/api/integrantes/${integranteSaudeId}`, dados);
    await carregarIntegrantes();
    avisar("Prontuário atualizado.", "sucesso");
    document.getElementById("ultima-atualizacao-prontuario").textContent = `Última atualização: ${dados.biometria_atualizada_em}`;
  } catch (e) { avisar(e.message); }
}

/* Medicamentos */
async function carregarMedicamentos() {
  if (!integranteSaudeId) return;
  try {
    const lista = await API.get(`/api/integrantes/${integranteSaudeId}/medicamentos`);
    document.getElementById("tabela-medicamentos").innerHTML = lista.map((m) => `
      <tr>
        <td>${escapeHtml(m.nome)}</td><td>${escapeHtml(m.principio_ativo || "")}</td><td>${escapeHtml(m.dosagem || "")}</td>
        <td>${escapeHtml(m.horarios || "")}</td>
        <td>${m.ativo ? '<span class="badge badge-verde">ativo</span>' : '<span class="badge badge-cinza">inativo</span>'}</td>
        <td><button class="botao secundario" onclick='editarMedicamento(${m.id})'>Editar</button>
        <button class="botao secundario" onclick="excluirMedicamento(${m.id})">Excluir</button></td>
      </tr>`).join("");
    window._medicamentosCache = lista;
  } catch (e) { avisar(e.message); }
}

function abrirModalMedicamento() {
  document.getElementById("form-medicamento").reset();
  abrirModal("modal-medicamento");
}

function editarMedicamento(id) {
  const m = (window._medicamentosCache || []).find((x) => x.id === id);
  if (!m) return;
  const form = document.getElementById("form-medicamento");
  form.reset();
  preencherFormulario(form, m);
  form.querySelector("[name=horarios_texto]").value = m.horarios ? JSON.parse(m.horarios).join(", ") : "";
  abrirModal("modal-medicamento");
}

async function salvarMedicamento() {
  const form = document.getElementById("form-medicamento");
  const dados = lerFormulario(form);
  const id = dados.id;
  delete dados.id;
  dados.integrante_id = integranteSaudeId;
  const horariosTexto = dados.horarios_texto || "";
  delete dados.horarios_texto;
  dados.horarios = horariosTexto ? horariosTexto.split(",").map((h) => h.trim()).filter(Boolean) : [];
  try {
    if (id) await API.put(`/api/medicamentos/${id}`, dados);
    else await API.post("/api/medicamentos", dados);
    fecharModal("modal-medicamento");
    await carregarMedicamentos();
    avisar("Medicamento salvo.", "sucesso");
  } catch (e) { avisar(e.message); }
}

async function excluirMedicamento(id) {
  if (!confirm("Excluir este medicamento?")) return;
  try { await API.delete(`/api/medicamentos/${id}`); await carregarMedicamentos(); } catch (e) { avisar(e.message); }
}

/* Consultas */
async function carregarConsultas() {
  if (!integranteSaudeId) return;
  try {
    const lista = await API.get(`/api/integrantes/${integranteSaudeId}/consultas`);
    window._consultasCache = lista;
    document.getElementById("tabela-consultas").innerHTML = lista.map((c) => `
      <tr>
        <td>${escapeHtml(c.medico_nome)}</td><td>${escapeHtml(c.especialidade || "")}</td>
        <td>${escapeHtml(c.data_consulta)}</td><td>${escapeHtml(c.horario || "")}</td>
        <td>${badgeStatusGenerico(c.status)}</td>
        <td><button class="botao secundario" onclick="editarConsulta(${c.id})">Editar</button>
        <button class="botao secundario" onclick="excluirConsulta(${c.id})">Excluir</button></td>
      </tr>`).join("");
  } catch (e) { avisar(e.message); }
}

function badgeStatusGenerico(status) {
  return `<span class="badge badge-azul">${escapeHtml(status)}</span>`;
}

function abrirModalConsulta() { document.getElementById("form-consulta").reset(); abrirModal("modal-consulta"); }

function editarConsulta(id) {
  const c = (window._consultasCache || []).find((x) => x.id === id);
  if (!c) return;
  const form = document.getElementById("form-consulta");
  form.reset();
  preencherFormulario(form, c);
  abrirModal("modal-consulta");
}

async function salvarConsulta() {
  const form = document.getElementById("form-consulta");
  const dados = lerFormulario(form);
  const id = dados.id;
  delete dados.id;
  dados.integrante_id = integranteSaudeId;
  try {
    if (id) await API.put(`/api/consultas/${id}`, dados);
    else await API.post("/api/consultas", dados);
    fecharModal("modal-consulta");
    await carregarConsultas();
    avisar("Consulta salva.", "sucesso");
  } catch (e) { avisar(e.message); }
}

async function excluirConsulta(id) {
  if (!confirm("Excluir esta consulta?")) return;
  try { await API.delete(`/api/consultas/${id}`); await carregarConsultas(); } catch (e) { avisar(e.message); }
}

/* Exames */
async function carregarExames() {
  if (!integranteSaudeId) return;
  try {
    const lista = await API.get(`/api/integrantes/${integranteSaudeId}/exames`);
    window._examesCache = lista;
    document.getElementById("tabela-exames").innerHTML = lista.map((ex) => `
      <tr>
        <td>${escapeHtml(ex.medico_solicitante || "")}</td><td>${escapeHtml(ex.finalidade || "")}</td>
        <td>${escapeHtml(ex.data_coleta || "")}</td><td>${escapeHtml(ex.laboratorio || "")}</td>
        <td>${badgeStatusGenerico(ex.status)}</td>
        <td><button class="botao secundario" onclick="editarExame(${ex.id})">Editar</button>
        <button class="botao secundario" onclick="excluirExame(${ex.id})">Excluir</button></td>
      </tr>`).join("");
  } catch (e) { avisar(e.message); }
}

function abrirModalExame() { document.getElementById("form-exame").reset(); abrirModal("modal-exame"); }

function editarExame(id) {
  const ex = (window._examesCache || []).find((x) => x.id === id);
  if (!ex) return;
  const form = document.getElementById("form-exame");
  form.reset();
  preencherFormulario(form, ex);
  abrirModal("modal-exame");
}

async function salvarExame() {
  const form = document.getElementById("form-exame");
  const dados = lerFormulario(form);
  const id = dados.id;
  delete dados.id;
  dados.integrante_id = integranteSaudeId;
  try {
    if (id) await API.put(`/api/exames/${id}`, dados);
    else await API.post("/api/exames", dados);
    fecharModal("modal-exame");
    await carregarExames();
    avisar("Exame salvo.", "sucesso");
  } catch (e) { avisar(e.message); }
}

async function excluirExame(id) {
  if (!confirm("Excluir este exame?")) return;
  try { await API.delete(`/api/exames/${id}`); await carregarExames(); } catch (e) { avisar(e.message); }
}

/* Receitas */
async function carregarReceitas() {
  if (!integranteSaudeId) return;
  try {
    const lista = await API.get(`/api/integrantes/${integranteSaudeId}/receitas`);
    document.getElementById("tabela-receitas").innerHTML = lista.map((r) => `
      <tr>
        <td>${escapeHtml(r.medico_nome || "")}</td><td>${escapeHtml(r.especialidade || "")}</td>
        <td>${escapeHtml(r.finalidade || "")}</td><td>${escapeHtml(r.data_receita || "")}</td>
        <td>${r.caminho_arquivo ? `<a href="/data-arquivo?caminho=${encodeURIComponent(r.caminho_arquivo)}" target="_blank">Abrir</a>` : "-"}</td>
        <td><button class="botao secundario" onclick="excluirReceita(${r.id})">Excluir</button></td>
      </tr>`).join("");
  } catch (e) { avisar(e.message); }
}

function abrirModalReceita() { document.getElementById("form-receita").reset(); abrirModal("modal-receita"); }

async function salvarReceita() {
  const dadosForm = new FormData(document.getElementById("form-receita"));
  dadosForm.set("integrante_id", integranteSaudeId);
  try {
    await API.postForm("/api/receitas", dadosForm);
    fecharModal("modal-receita");
    await carregarReceitas();
    avisar("Receita salva.", "sucesso");
  } catch (e) { avisar(e.message); }
}

async function excluirReceita(id) {
  if (!confirm("Excluir esta receita?")) return;
  try { await API.delete(`/api/receitas/${id}`); await carregarReceitas(); } catch (e) { avisar(e.message); }
}

/* ---------------- Recibos e Reembolsos ---------------- */
async function carregarRecibos() {
  try {
    recibosCache = await API.get("/api/recibos");
    document.getElementById("tabela-recibos").innerHTML = recibosCache.map((r) => `
      <tr>
        <td>${escapeHtml(r.emitente)}</td><td>${escapeHtml(r.data_emissao)}</td><td>${formatarBRL(r.valor)}</td>
        <td>${escapeHtml(nomeIntegrante(r.integrante_id))}</td>
        <td>${r.caminho_arquivo ? `<a href="/data-arquivo?caminho=${encodeURIComponent(r.caminho_arquivo)}" target="_blank">Abrir</a>` : "-"}</td>
        <td><button class="botao secundario" onclick="excluirRecibo(${r.id})">Excluir</button></td>
      </tr>`).join("");
    const selectRecibo = document.getElementById("select-recibo-reembolso");
    if (selectRecibo) {
      selectRecibo.innerHTML = '<option value="">Nenhum</option>' +
        recibosCache.map((r) => `<option value="${r.id}">${escapeHtml(r.emitente)} - ${formatarBRL(r.valor)}</option>`).join("");
    }
  } catch (e) { avisar(e.message); }
}

function nomeIntegrante(id) {
  const integrante = integrantes.find((i) => i.id === id);
  return integrante ? integrante.nome : "";
}

function abrirModalRecibo() { document.getElementById("form-recibo").reset(); abrirModal("modal-recibo"); }

async function salvarRecibo() {
  const dadosForm = new FormData(document.getElementById("form-recibo"));
  try {
    await API.postForm("/api/recibos", dadosForm);
    fecharModal("modal-recibo");
    await carregarRecibos();
    avisar("Recibo salvo.", "sucesso");
  } catch (e) { avisar(e.message); }
}

async function excluirRecibo(id) {
  if (!confirm("Excluir este recibo?")) return;
  try { await API.delete(`/api/recibos/${id}`); await carregarRecibos(); } catch (e) { avisar(e.message); }
}

const BADGES_REEMBOLSO = { solicitado: "badge-azul", em_analise: "badge-amarelo", aprovado: "badge-verde-claro", rejeitado: "badge-vermelho", pago: "badge-verde" };

async function carregarReembolsos() {
  try {
    const lista = await API.get("/api/reembolsos");
    window._reembolsosCache = lista;
    document.getElementById("tabela-reembolsos").innerHTML = lista.map((r) => `
      <tr>
        <td>${escapeHtml(r.data_pedido)}</td><td>${escapeHtml(nomeIntegrante(r.integrante_id))}</td>
        <td>${formatarBRL(r.valor_solicitado)}</td>
        <td><span class="badge ${BADGES_REEMBOLSO[r.status] || "badge-cinza"}">${escapeHtml(r.status)}</span></td>
        <td>${escapeHtml(r.data_pagamento || "")}</td><td>${r.valor_pago ? formatarBRL(r.valor_pago) : "-"}</td>
        <td><button class="botao secundario" onclick="editarReembolso(${r.id})">Editar</button>
        <button class="botao secundario" onclick="excluirReembolso(${r.id})">Excluir</button></td>
      </tr>`).join("");
  } catch (e) { avisar(e.message); }
}

function abrirModalReembolso() { document.getElementById("form-reembolso").reset(); abrirModal("modal-reembolso"); }

function editarReembolso(id) {
  const r = (window._reembolsosCache || []).find((x) => x.id === id);
  if (!r) return;
  const form = document.getElementById("form-reembolso");
  form.reset();
  preencherFormulario(form, r);
  abrirModal("modal-reembolso");
}

async function salvarReembolso() {
  const form = document.getElementById("form-reembolso");
  const dados = lerFormulario(form);
  const id = dados.id;
  delete dados.id;
  try {
    if (id) await API.put(`/api/reembolsos/${id}`, dados);
    else await API.post("/api/reembolsos", dados);
    fecharModal("modal-reembolso");
    await carregarReembolsos();
    avisar("Reembolso salvo.", "sucesso");
  } catch (e) { avisar(e.message); }
}

async function excluirReembolso(id) {
  if (!confirm("Excluir este reembolso?")) return;
  try { await API.delete(`/api/reembolsos/${id}`); await carregarReembolsos(); } catch (e) { avisar(e.message); }
}

/* ---------------- Viagens ---------------- */
const BADGES_VIAGEM = { a_comprar: "badge-cinza", comprado: "badge-verde", remarcado: "badge-amarelo", expirado: "badge-vermelho" };

async function carregarViagens() {
  try {
    const lista = await API.get("/api/viagens");
    window._viagensCache = lista;
    document.getElementById("tabela-viagens").innerHTML = lista.map((v) => `
      <tr>
        <td>${escapeHtml(v.destino || "")}</td><td>${escapeHtml(v.data_ida || "")}</td><td>${escapeHtml(v.data_volta || "")}</td>
        <td><span class="badge ${BADGES_VIAGEM[v.status] || "badge-cinza"}">${escapeHtml(v.status)}</span></td>
        <td>${v.numero_passageiros}</td><td>${v.valor_compra ? formatarBRL(v.valor_compra) : "-"}</td>
        <td><button class="botao secundario" onclick="editarViagem(${v.id})">Editar</button>
        <button class="botao secundario" onclick="excluirViagem(${v.id})">Excluir</button></td>
      </tr>`).join("");
  } catch (e) { avisar(e.message); }
}

function abrirModalViagem() { document.getElementById("form-viagem").reset(); abrirModal("modal-viagem"); }

function editarViagem(id) {
  const v = (window._viagensCache || []).find((x) => x.id === id);
  if (!v) return;
  const form = document.getElementById("form-viagem");
  form.reset();
  preencherFormulario(form, v);
  const selectPassageiros = document.getElementById("select-passageiros-viagem");
  Array.from(selectPassageiros.options).forEach((opt) => {
    opt.selected = (v.passageiros_ids || []).includes(Number(opt.value));
  });
  abrirModal("modal-viagem");
}

async function salvarViagem() {
  const form = document.getElementById("form-viagem");
  const dados = lerFormulario(form);
  const id = dados.id;
  delete dados.id;
  const selectPassageiros = document.getElementById("select-passageiros-viagem");
  dados.passageiros_ids = Array.from(selectPassageiros.selectedOptions).map((o) => Number(o.value));
  try {
    if (id) await API.put(`/api/viagens/${id}`, dados);
    else await API.post("/api/viagens", dados);
    fecharModal("modal-viagem");
    await carregarViagens();
    avisar("Viagem salva.", "sucesso");
  } catch (e) { avisar(e.message); }
}

async function excluirViagem(id) {
  if (!confirm("Excluir esta viagem?")) return;
  try { await API.delete(`/api/viagens/${id}`); await carregarViagens(); } catch (e) { avisar(e.message); }
}

/* ---------------- Despesas ---------------- */
async function carregarDespesas() {
  try {
    const lista = await API.get("/api/despesas");
    window._despesasCache = lista;
    let total = 0;
    document.getElementById("tabela-despesas").innerHTML = lista.map((d) => {
      total += Number(d.valor) || 0;
      return `<tr>
        <td>${d.numero}</td><td>${escapeHtml(d.fornecedor)}</td><td>${formatarBRL(d.valor)}</td>
        <td>${escapeHtml(d.data_servico || "")}</td><td>${escapeHtml(d.data_vencimento || "")}</td>
        <td>${escapeHtml(d.modo_pagamento || "")}</td><td>${escapeHtml(nomeIntegrante(d.integrante_id))}</td>
        <td>${d.status_pagamento === "pago" ? '<span class="badge badge-verde">pago</span>' : '<span class="badge badge-amarelo">pendente</span>'}</td>
        <td><button class="botao secundario" onclick="editarDespesa(${d.id})">Editar</button>
        <button class="botao secundario" onclick="excluirDespesa(${d.id})">Excluir</button></td>
      </tr>`;
    }).join("");
    document.getElementById("total-despesas").textContent = formatarBRL(total);
    const selectFornecedor = document.getElementById("select-fornecedor-despesa");
    if (selectFornecedor) {
      selectFornecedor.innerHTML = '<option value="">Selecionar / digitar abaixo</option>' +
        fornecedoresCache.map((f) => `<option value="${f.id}">${escapeHtml(f.nome)}</option>`).join("");
    }
  } catch (e) { avisar(e.message); }
}

function alternarCamposPagamento() {
  const modo = document.getElementById("select-modo-pagamento").value;
  document.getElementById("campo-chave-pix-despesa").style.display = modo === "pix" ? "block" : "none";
  document.getElementById("campo-parceria-despesa").style.display = modo === "parceria" ? "block" : "none";
}

function preencherPixDespesa() {
  const id = Number(document.getElementById("select-fornecedor-despesa").value);
  const fornecedor = fornecedoresCache.find((f) => f.id === id);
  const form = document.getElementById("form-despesa");
  if (fornecedor) {
    form.querySelector("[name=fornecedor]").value = fornecedor.nome;
    if (fornecedor.chave_pix) form.querySelector("[name=chave_pix]").value = fornecedor.chave_pix;
  }
}

function abrirModalDespesa() {
  document.getElementById("form-despesa").reset();
  alternarCamposPagamento();
  abrirModal("modal-despesa");
}

function editarDespesa(id) {
  const d = (window._despesasCache || []).find((x) => x.id === id);
  if (!d) return;
  const form = document.getElementById("form-despesa");
  form.reset();
  preencherFormulario(form, d);
  alternarCamposPagamento();
  form.dataset.editId = id;
  abrirModal("modal-despesa");
}

async function salvarDespesa() {
  const form = document.getElementById("form-despesa");
  const id = form.dataset.editId;
  const dadosForm = new FormData(form);
  dadosForm.delete("fornecedor_select");
  try {
    if (id) {
      const dados = lerFormulario(form);
      await API.put(`/api/despesas/${id}`, dados);
      delete form.dataset.editId;
    } else {
      await API.postForm("/api/despesas", dadosForm);
    }
    fecharModal("modal-despesa");
    await carregarDespesas();
    avisar("Despesa salva.", "sucesso");
  } catch (e) { avisar(e.message); }
}

async function excluirDespesa(id) {
  if (!confirm("Excluir esta despesa?")) return;
  try { await API.delete(`/api/despesas/${id}`); await carregarDespesas(); } catch (e) { avisar(e.message); }
}

/* ---------------- Fornecedores ---------------- */
async function carregarFornecedores() {
  try {
    fornecedoresCache = await API.get("/api/fornecedores");
    document.getElementById("tabela-fornecedores").innerHTML = fornecedoresCache.map((f) => `
      <tr>
        <td>${escapeHtml(f.nome)}</td><td>${escapeHtml(f.telefone || "")}</td><td>${escapeHtml(f.email || "")}</td>
        <td>${escapeHtml(f.categoria || "")}</td><td>${escapeHtml(f.chave_pix || "")}</td>
        <td>${f.ativo ? "Sim" : "Não"}</td>
        <td><button class="botao secundario" onclick="editarFornecedor(${f.id})">Editar</button>
        <button class="botao secundario" onclick="excluirFornecedor(${f.id})">Excluir</button></td>
      </tr>`).join("");
  } catch (e) { avisar(e.message); }
}

function abrirModalFornecedor() { document.getElementById("form-fornecedor").reset(); abrirModal("modal-fornecedor"); }

function editarFornecedor(id) {
  const f = fornecedoresCache.find((x) => x.id === id);
  if (!f) return;
  const form = document.getElementById("form-fornecedor");
  form.reset();
  preencherFormulario(form, f);
  abrirModal("modal-fornecedor");
}

async function salvarFornecedor() {
  const form = document.getElementById("form-fornecedor");
  const dados = lerFormulario(form);
  const id = dados.id;
  delete dados.id;
  try {
    if (id) await API.put(`/api/fornecedores/${id}`, dados);
    else await API.post("/api/fornecedores", dados);
    fecharModal("modal-fornecedor");
    await carregarFornecedores();
    avisar("Fornecedor salvo.", "sucesso");
  } catch (e) { avisar(e.message); }
}

async function excluirFornecedor(id) {
  if (!confirm("Excluir este fornecedor?")) return;
  try { await API.delete(`/api/fornecedores/${id}`); await carregarFornecedores(); } catch (e) { avisar(e.message); }
}

/* ---------------- Configurações ---------------- */
async function carregarConfiguracoes() {
  const form = document.getElementById("form-configuracoes");
  if (!form) return;
  try {
    const config = await API.get("/api/secretariado/configuracoes");
    preencherFormulario(form, config);
  } catch (e) { avisar(e.message); }
}

async function salvarConfiguracoes(evento) {
  evento.preventDefault();
  const form = document.getElementById("form-configuracoes");
  const dadosForm = new FormData(form);
  try {
    await API.postForm("/api/secretariado/configuracoes", dadosForm, "PUT");
    avisar("Configurações salvas.", "sucesso");
  } catch (e) { avisar(e.message); }
}
