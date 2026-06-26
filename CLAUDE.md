# CLAUDE.md — SISRITHA (Sistema de Gerenciamento Administrativo do Grupo Ritha Capelato)

> Memória durável do projeto. Leia no início de cada sessão. Trabalhe sempre em **português**.
> Mantenha este arquivo atualizado ao concluir cada fase.

---

## O que é

Sistema web de gestão administrativa do Grupo Ritha Capelato, usado pelo master e usuários habilitados.
URL de produção: **https://sisritha.rafaeljrocha.cloud**

---

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.12 + Flask 3.0+ |
| Banco | SQLite3 em `/data/sisritha.db` (modo WAL) |
| Frontend | Jinja2 + JavaScript Vanilla + HTML5/CSS3 |
| Auth | bcrypt (senhas) + pyotp (2FA TOTP obrigatório) |
| Servidor | Gunicorn 23+ com tini |
| Deploy | Docker → EasyPanel (VPS Hostinger 72.61.42.105) |
| PDF/Excel | reportlab + openpyxl |

- `DATA_DIR=/data` guarda o banco e **todos** os anexos/uploads. Nada de dados fora dali.
- `app/services/` é a **única** camada que toca o banco.
- Tema visual: **rosa** (`--cor-primaria: #e91e8c`) sobre fundo branco/rosê.

---

## Repositório

- Repo privado: `rafaeljrocha/gruporc`
- Branch de produção: **`main`**
- Deploy: EasyPanel → serviço `sisritha` → botão "Implantar"
- Destino no EasyPanel: **HTTP**, porta **8000** (HTTPS no destino causa erro SSL no Gunicorn)

---

## Credenciais iniciais

- Email: `admin@sisritha.local`
- Senha: `Admin@2025!`
- Papel: master (acesso total)

---

## Estrutura de arquivos

```
sisritha/
├── app/
│   ├── __init__.py              # create_app() factory + registro de blueprints
│   ├── auth.py                  # @login_required, @master_required, @api_login_required
│   ├── config.py                # AppConfig dataclass (lê env vars)
│   ├── database.py              # init_db(), get_db(), row_to_dict() + migração defensiva
│   ├── seguranca.py             # rate limiter de login
│   ├── routes/
│   │   ├── auth_routes.py       # /login /logout /2fa
│   │   ├── paginas_routes.py    # rotas HTML + context_processor config_sistema
│   │   └── api/
│   │       ├── secretariado_api.py   # CRUD secretariado + usuários + config sistema
│   │       ├── administrativo_api.py # CRUD administrativo (Fase 2)
│   │       ├── marketing_api.py      # CRUD marketing (Fase 2)
│   │       ├── despesas_api.py       # projetos + despesas transversais (Fase 2)
│   │       └── backup_api.py         # geração de backup
│   ├── services/                # um arquivo por entidade
│   └── db/
│       └── schema.sql           # schema completo (nunca modificar tabelas existentes)
├── templates/
│   ├── base.html                # layout base (topo rosa, nav, config_sistema injetado)
│   ├── login.html
│   ├── home.html                # cards de módulos
│   ├── configuracoes.html       # gestão de usuários (master)
│   ├── configuracoes_sistema.html # logo, nome, dados do sistema (master)
│   └── modulos/
│       ├── secretariado/        # index.html + _modais.html
│       ├── administrativo/      # index.html + _modais.html (Fase 2)
│       └── marketing/           # index.html + _modais.html (Fase 2)
├── static/
│   ├── css/estilo.css
│   └── js/comum.js              # lerFormulario, formatarBRL, inicializarMascarasMonetarias, API obj
├── Dockerfile
├── requirements.txt
└── wsgi.py
```

---

## Módulos do sistema

| Slug | Nome | Status | URL |
|------|------|--------|-----|
| `secretariado` | Secretariado Executivo | Produção (Fase 1) | `/secretariado` |
| `administrativo` | Administrativo | Produção (Fase 2) | `/administrativo` |
| `marketing` | Marketing | Produção (Fase 2) | `/marketing` |
| `rh` | Recursos Humanos | Fase futura | — |
| `juridico` | Jurídico | Fase futura | — |
| `financeiro` | Financeiro | Fase futura | — |
| `cursos` | Cursos | Fase futura | — |

---

## Tabelas do banco (schema.sql)

**Controle:** schema_migrations, usuario, configuracao, modulo_config

**Secretariado:** integrante, documento_digital, medicamento, consulta, exame, receita_medica, recibo_saude, reembolso, viagem, viagem_passageiro, fornecedor

**Transversal:** despesa (expandida na Fase 2 com: modulo_slug, projeto_id, descricao, fornecedor_id, categoria, observacoes), projeto

**Administrativo:** empresa, socio, contrato, documento_adm, obrigacao

**Marketing:** canal_marketing, conteudo_marketing, campanha_marketing, metrica_marketing, arquivo_marketing

---

## Regras de ouro (inegociáveis)

1. **Migrações idempotentes**: CREATE TABLE IF NOT EXISTS; ALTER TABLE ADD COLUMN apenas após checar existência. Nunca drop&recreate destrutivo.
2. **Backup antes de cada deploy** (há dados reais em produção).
3. **Valores monetários**: sempre type="text" data-money="" + inicializarMascarasMonetarias(). Nunca type="number" para campos financeiros.
4. **Cookies seguros**: COOKIES_SEGUROS=0 enquanto SSL não estiver com certificado válido. Trocar para 1 após cadeado verde.
5. **Porta interna**: destino no EasyPanel sempre HTTP:8000 — nunca HTTPS interno.
6. **Tema rosa**: --cor-primaria: #e91e8c. Não usar laranja (pertence ao sistema motociclismo/bens).

---

## Padrões de desenvolvimento

### Service (padrão obrigatório)
Cada service importa _crud.py e implementa: _normalizar(dados), listar(db_path), criar(db_path, dados), editar(db_path, id_, dados), remover(db_path, id_).

### API Blueprint (padrão obrigatório)
Blueprint com url_prefix="/api". Todos os endpoints com @api_login_required. Endpoints de configuração com @master_required. Erros retornam {"erro": "mensagem"} com status HTTP correto.

### Webhook N8N (best-effort)
from app.services.webhook_service import disparar_webhook
disparar_webhook("tipo_evento", {"dados": ...})
Falha silenciosa se WEBHOOK_N8N_URL não configurado.

### Upload de arquivo
from app.services.upload_service import salvar_arquivo
caminho, nome = salvar_arquivo(arquivo, config.data_dir / "subpasta")

### Abrir arquivo no frontend
window.open('/data-arquivo?caminho=' + encodeURIComponent(caminho), '_blank');

---

## Variáveis de ambiente (EasyPanel)

| Variável | Valor | Observação |
|----------|-------|-----------|
| SECRET_KEY | hex 64 chars | Gerado uma vez, nunca mudar |
| COOKIES_SEGUROS | 0 | Trocar para 1 após SSL válido |
| PROXY_FIX | 1 | Necessário atrás do EasyPanel |
| SESSION_LIFETIME_MIN | 60 | Tempo de sessão em minutos |
| DATA_DIR | /data | Volume persistente |
| WEBHOOK_N8N_URL | opcional | URL do webhook N8N |

---

## Fluxo de deploy (EasyPanel)

1. Fazer backup: Configurações do Sistema → Backup
2. Push do código para origin/main
3. No EasyPanel → serviço sisritha → botão "Implantar"
4. Acompanhar logs: aguardar "Listening at: http://0.0.0.0:8000"
5. Verificar /healthz retornando 200
6. Testar login em https://sisritha.rafaeljrocha.cloud

---

## Estado das fases

| Fase | Conteúdo | Status |
|------|----------|--------|
| Fase 1 | Login + 2FA TOTP + Módulo Secretariado (7 abas: Cadastro, Saúde, Recibos/Reembolsos, Viagens, Despesas, Fornecedores, Configurações) + Configurações do sistema + Gestão de usuários | Produção |
| Fase 2 | Módulo Administrativo (Empresas, Sócios, Contratos, Documentos, Obrigações, Despesas, Config) + Módulo Marketing (Canais, Conteúdo, Campanhas, Métricas, Arquivos, Despesas, Config) + Sistema transversal de Despesas por Projeto | Produção |
| Fase 3 | RH | Planejada |
| Fase 4 | Jurídico | Planejada |
| Fase 5 | Financeiro | Planejada |
| Fase 6 | Cursos | Planejada |

---

## Como trabalhar neste projeto

- Uma fase por sessão. O prompt de cada fase deve ser autossuficiente.
- Leia este arquivo no início de cada sessão para ter contexto completo.
- Implemente por etapas, testando localmente com python run.py antes de commitar.
- Migrações rodam automaticamente no boot via init_db() — sem scripts manuais.
- Ao concluir uma fase, atualize a tabela "Estado das fases" neste arquivo.
- Commit sempre para main com mensagem descritiva em português.
