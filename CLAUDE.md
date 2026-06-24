# CLAUDE.md — Sistema de Administração de Bens Próprios (Grupo Capelato Rocha)

> Memória durável do projeto. Leia no início de cada sessão. Trabalhe sempre em **português**.
> Mantenha este arquivo enxuto (alvo: < 200 linhas). Ao concluir algo relevante, atualize a seção "Estado das fases".

## O que é
App web de gestão patrimonial (imóveis, locações, veículos, finanças, internacional) usado pelo administrador da holding e por poucos usuários de confiança.

## Stack
- Flask + SQLite (modo WAL) + gunicorn; bcrypt (senhas); ReportLab (PDFs).
- Containerizado (Docker); deploy via EasyPanel; Traefik faz proxy/SSL.
- `DATA_DIR=/data` guarda o banco (`sistema.db`) e **todos** os anexos. Nada de dados fora dali.
- `app/services/` é a **única** camada que toca o banco.

## Repositório e branches (ATENÇÃO)
- Repo privado `rafaeljrocha/motociclismo`.
- A branch `main` contém um scaffold ANTIGO (React "Motoviagem") que **não** é este sistema. O Flask vive nas branches de feature.
- Cada fase = uma branch + Pull Request. Sempre parta da branch de produção indicada no prompt da fase.
- **Produção atual: `fase-3d-internacional`.** Em construção: `fase-3f-conectores-ia`.

## Regras de ouro (inegociáveis)
1. **Migrações idempotentes**, controladas por `schema_migrations`: `CREATE TABLE IF NOT EXISTS`, `ADD COLUMN` só após checar. Nunca drop&recreate destrutivo. Preserve dados reais; seguras para rodar a cada reinício.
2. **Backup antes de cada deploy** (há dados reais em produção).
3. **Sem senhas**: nenhum campo de senha de portal/serviço. Só link/usuário.
4. **Mascaramento** via `MASCARA_CAMPOS` em todo export e feed de IA: nunca expor CPF, matrícula completa, dados de pagamento, PII de hóspede, série/registro de arma, senha.
5. **Armas**: domínio **admin-only**; mascarado nos exports; **excluído por completo dos conectores/feeds de IA**; alertas de registro vão por canal/token **separado**.
6. **Segurança/UX**: perfis admin/padrão + 2FA (TOTP) + CSRF + sessões intactos. O **master** controla, por perfil, a visibilidade de abas. Mantenha a identidade visual **laranja**.

## Padrões recorrentes
- **Geração preguiçosa e idempotente** de ocorrências (parcelas de locação; contas a pagar) com `UNIQUE(...)`; **sem cron**.
- **Motor de pendências** extensível via `registrar_fonte()` — alimenta `/pendencias` e o feed `/api/lembretes`.
- **Lembretes/integrações**: o app só expõe feeds JSON **só-leitura**, protegidos por token (cabeçalho `X-API-Token`). Agendamento, envio de e-mail e Notion ficam no **n8n**, fora do app. Tokens de env: `LEMBRETES_API_TOKEN`, `LEMBRETES_ARMAS_API_TOKEN` (valores só no EasyPanel; nunca neste arquivo).
- **Conectores de IA**: token gerado no app e guardado como **hash**; feeds mascarados por escopo; gerência admin-only.

## Fluxo de deploy (EasyPanel)
1. Backup (admin → Configurações → Backup).
2. (Se a fase pedir) cadastrar variáveis em **Ambiente**.
3. **Origem → aba Github** → trocar **Branch** para a da fase → Salvar (Proprietário `rafaeljrocha`, Repositório `motociclismo`, Caminho `/`).
4. **Implantações → Deploy**. Conferir nos logs: migração + `Listening at: http://0.0.0.0:8000` + `/healthz` 200.
- Destino no EasyPanel: **HTTP**, porta **8000** (HTTPS no destino causa Gateway Timeout 504).
- Rollback: voltar a branch anterior e redeploy (migrações aditivas + backup garantem segurança).

## Estado das fases
- **Concluídas e em produção:** 1 (MVP login+Acervo+Locações), 2 (multiusuário/2FA/Docker), 3A (aprimoramentos + export IA), 3B (diligência/pendências), 3B.1 (recibos numerados NN/AAAA), 3B.2 (lembretes via n8n + reajuste manual por contrato), 3C (Fornecedores/Manutenções/Veículos/Armas), 3C.1 (Contas a Pagar + não-renovação + visibilidade de abas por perfil), 3D (Internacional US$/gestor/hóspedes).
- **Em construção:** 3F (conectores de IA + ajustes: ocultar "Em construção" do padrão; Locações sem "Uso próprio"/"Em construção"; modal fecha no "Salvar") — branch `fase-3f-conectores-ia`.
- **Bloqueada:** 3E (demonstrativo de IR a inquilinos) — aguarda validação do contador (IRRF / comprovante oficial / DIMOB).

## Como trabalhar (economia de contexto)
- **Uma fase por sessão.** O prompt de cada fase é autossuficiente (branch + regras + escopo).
- Implemente **por etapas**, testando, e relate ao final (migrações e como preservam os dados).
- Ao terminar uma fase, **atualize "Estado das fases"** aqui antes de encerrar/limpar a sessão.
