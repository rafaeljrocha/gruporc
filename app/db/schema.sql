-- SISRITHA — schema completo

CREATE TABLE IF NOT EXISTS schema_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL,
    aplicado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- CONTROLE DE ACESSO
CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    papel TEXT NOT NULL DEFAULT 'padrao',
    modulos_habilitados TEXT DEFAULT '[]',
    totp_secret TEXT,
    totp_ativo INTEGER DEFAULT 0,
    ativo INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- CONFIGURAÇÃO DO SISTEMA
CREATE TABLE IF NOT EXISTS configuracao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chave TEXT UNIQUE NOT NULL,
    valor TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- CONFIGURAÇÃO DOS MÓDULOS
CREATE TABLE IF NOT EXISTS modulo_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    logo_path TEXT,
    responsavel TEXT,
    email_contato TEXT,
    telefone_contato TEXT,
    ativo INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- MÓDULO SECRETARIADO — INTEGRANTES FAMILIARES
CREATE TABLE IF NOT EXISTS integrante (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    data_nascimento DATE,
    cpf TEXT,
    rg TEXT,
    numero_passaporte TEXT,
    validade_passaporte DATE,
    numero_convenio_saude TEXT,
    validade_convenio_saude DATE,
    tipo_sanguineo TEXT,
    altura_cm REAL,
    peso_kg REAL,
    calcado TEXT,
    tamanho_calca TEXT,
    tamanho_camiseta TEXT,
    tamanho_camisa TEXT,
    medida_cintura REAL,
    medida_ombro REAL,
    outras_medidas TEXT,
    biometria_atualizada_em DATE,
    ativo INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS documento_digital (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    integrante_id INTEGER NOT NULL REFERENCES integrante(id),
    tipo_documento TEXT NOT NULL,
    descricao TEXT,
    validade DATE,
    caminho_arquivo TEXT,
    nome_arquivo TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS medicamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    integrante_id INTEGER NOT NULL REFERENCES integrante(id),
    nome TEXT NOT NULL,
    principio_ativo TEXT,
    dosagem TEXT,
    horarios TEXT,
    dias_tratamento INTEGER,
    uso_continuo INTEGER DEFAULT 0,
    data_inicio DATETIME,
    ativo INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS consulta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    integrante_id INTEGER NOT NULL REFERENCES integrante(id),
    medico_nome TEXT NOT NULL,
    especialidade TEXT,
    crm TEXT,
    data_consulta DATE NOT NULL,
    horario TIME,
    telefone TEXT,
    endereco TEXT,
    email TEXT,
    valor REAL,
    status TEXT DEFAULT 'agendada',
    lembrete_enviado INTEGER DEFAULT 0,
    google_agenda_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS exame (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    integrante_id INTEGER NOT NULL REFERENCES integrante(id),
    medico_solicitante TEXT,
    finalidade TEXT,
    data_coleta DATE,
    horario TIME,
    laboratorio TEXT,
    endereco_laboratorio TEXT,
    valor REAL,
    status TEXT DEFAULT 'agendado',
    resultado_path TEXT,
    lembrete_enviado INTEGER DEFAULT 0,
    google_agenda_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS receita_medica (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    integrante_id INTEGER NOT NULL REFERENCES integrante(id),
    medico_nome TEXT,
    especialidade TEXT,
    finalidade TEXT,
    data_receita DATE,
    caminho_arquivo TEXT,
    nome_arquivo TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recibo_saude (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    integrante_id INTEGER NOT NULL REFERENCES integrante(id),
    emitente TEXT NOT NULL,
    data_emissao DATE NOT NULL,
    valor REAL,
    caminho_arquivo TEXT,
    nome_arquivo TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reembolso (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recibo_id INTEGER REFERENCES recibo_saude(id),
    integrante_id INTEGER NOT NULL REFERENCES integrante(id),
    data_pedido DATE NOT NULL,
    valor_solicitado REAL,
    status TEXT DEFAULT 'solicitado',
    data_pagamento DATE,
    valor_pago REAL,
    observacoes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS viagem (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    finalidade TEXT DEFAULT 'pessoal',
    origem TEXT,
    destino TEXT,
    aeroporto_partida TEXT,
    aeroporto_chegada TEXT,
    data_ida DATE,
    horario_ida TIME,
    data_volta DATE,
    horario_volta TIME,
    numero_passageiros INTEGER DEFAULT 1,
    valor_compra REAL,
    status TEXT DEFAULT 'a_comprar',
    agente_nome TEXT,
    agente_telefone TEXT,
    hotel_nome TEXT,
    hotel_endereco TEXT,
    hotel_telefone TEXT,
    hotel_checkin DATE,
    hotel_checkout DATE,
    lembrete_enviado INTEGER DEFAULT 0,
    google_agenda_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS viagem_passageiro (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    viagem_id INTEGER NOT NULL REFERENCES viagem(id),
    integrante_id INTEGER NOT NULL REFERENCES integrante(id)
);

CREATE TABLE IF NOT EXISTS despesa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero INTEGER,
    fornecedor TEXT NOT NULL,
    valor REAL NOT NULL,
    data_servico DATE,
    data_vencimento DATE,
    modo_pagamento TEXT,
    especificacao_parceria TEXT,
    chave_pix TEXT,
    caminho_arquivo TEXT,
    nome_arquivo TEXT,
    integrante_id INTEGER REFERENCES integrante(id),
    status_pagamento TEXT DEFAULT 'pendente',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fornecedor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    telefone TEXT,
    email TEXT,
    descricao TEXT,
    categoria TEXT,
    chave_pix TEXT,
    endereco TEXT,
    ativo INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- FASE 2 — Sistema transversal de Projetos + Despesas, Administrativo, Marketing
-- (todas as tabelas com CREATE TABLE IF NOT EXISTS — idempotentes)
-- ============================================================================

-- PROJETOS (agrupador de despesas, transversal a todos os módulos)
CREATE TABLE IF NOT EXISTS projeto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    modulo_slug TEXT NOT NULL DEFAULT 'secretariado',
    status TEXT DEFAULT 'aberto',
    data_inicio DATE,
    data_fim DATE,
    orcamento REAL,
    responsavel TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- MÓDULO ADMINISTRATIVO
CREATE TABLE IF NOT EXISTS empresa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    razao_social TEXT NOT NULL,
    nome_fantasia TEXT,
    cnpj TEXT,
    tipo TEXT DEFAULT 'ltda',
    pais TEXT DEFAULT 'Brasil',
    estado TEXT,
    cidade TEXT,
    endereco TEXT,
    cep TEXT,
    email TEXT,
    telefone TEXT,
    site TEXT,
    objeto_social TEXT,
    capital_social REAL,
    data_constituicao DATE,
    data_encerramento DATE,
    status TEXT DEFAULT 'ativa',
    observacoes TEXT,
    logo_path TEXT,
    ativo INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS socio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cpf_passaporte TEXT,
    tipo_pessoa TEXT DEFAULT 'fisica',
    empresa_id INTEGER REFERENCES empresa(id),
    percentual REAL,
    cargo TEXT,
    data_entrada DATE,
    data_saida DATE,
    ativo INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contrato (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero TEXT,
    objeto TEXT NOT NULL,
    empresa_id INTEGER REFERENCES empresa(id),
    contraparte TEXT,
    valor REAL,
    data_inicio DATE,
    data_fim DATE,
    renovacao_automatica INTEGER DEFAULT 0,
    status TEXT DEFAULT 'vigente',
    caminho_arquivo TEXT,
    nome_arquivo TEXT,
    observacoes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS documento_adm (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER REFERENCES empresa(id),
    tipo_documento TEXT NOT NULL,
    descricao TEXT,
    validade DATE,
    caminho_arquivo TEXT,
    nome_arquivo TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS obrigacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER REFERENCES empresa(id),
    descricao TEXT NOT NULL,
    periodicidade TEXT DEFAULT 'anual',
    proximo_vencimento DATE,
    responsavel TEXT,
    status TEXT DEFAULT 'pendente',
    observacoes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- MÓDULO MARKETING
CREATE TABLE IF NOT EXISTS canal_marketing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    plataforma TEXT NOT NULL,
    url_handle TEXT,
    seguidores INTEGER DEFAULT 0,
    status TEXT DEFAULT 'ativo',
    responsavel TEXT,
    observacoes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conteudo_marketing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    canal_id INTEGER REFERENCES canal_marketing(id),
    formato TEXT,
    data_prevista DATE,
    data_publicacao DATE,
    status TEXT DEFAULT 'ideia',
    tags TEXT,
    descricao TEXT,
    url_publicado TEXT,
    caminho_arquivo TEXT,
    nome_arquivo TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS campanha_marketing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    objetivo TEXT,
    canais TEXT DEFAULT '[]',
    orcamento REAL,
    data_inicio DATE,
    data_fim DATE,
    status TEXT DEFAULT 'planejada',
    resultado TEXT,
    observacoes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS metrica_marketing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    canal_id INTEGER REFERENCES canal_marketing(id),
    periodo_mes INTEGER,
    periodo_ano INTEGER,
    seguidores INTEGER,
    alcance INTEGER,
    impressoes INTEGER,
    engajamento REAL,
    cliques INTEGER,
    conversoes INTEGER,
    observacoes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS arquivo_marketing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    tipo_arquivo TEXT DEFAULT 'outro',
    descricao TEXT,
    tags TEXT,
    caminho_arquivo TEXT,
    nome_arquivo TEXT,
    tamanho_bytes INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
