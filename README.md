# SISRITHA

Sistema de Gerenciamento Administrativo do Grupo Ritha Capelato.

## Instalação local

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export DATA_DIR=./data
python run.py
```

Acesse `http://127.0.0.1:8000`.

## Deploy (EasyPanel)

1. Repositório GitHub → branch `main`, caminho `/`.
2. Build via `Dockerfile` (Docker/Gunicorn, porta 8000).
3. Configurar volume persistente em `/data`.
4. Variáveis de ambiente conforme tabela abaixo.
5. Após o deploy, verificar `/healthz` retornando `200`.

## Variáveis de ambiente

| Variável | Descrição | Padrão |
|---|---|---|
| `DATA_DIR` | Diretório persistente (banco, anexos, backups, logos) | `/data` |
| `SECRET_KEY` | Chave de sessão Flask | gerada automaticamente em dev |
| `APP_HOST` | Host do servidor | `0.0.0.0` |
| `APP_PORT` | Porta do servidor | `8000` |
| `GUNICORN_WORKERS` | Número de workers Gunicorn | `2` |
| `SESSION_LIFETIME_MIN` | Duração da sessão (min) | `60` |
| `COOKIES_SEGUROS` | Cookies com flag `Secure` | `1` |
| `PROXY_FIX` | Habilita ProxyFix (atrás de proxy/Traefik) | `1` |
| `WEBHOOK_N8N_URL` | URL do webhook N8N (opcional) | vazio |
| `UPLOAD_MAX_MB` | Tamanho máximo de upload (MB) | `32` |
| `SENHA_MIN` | Tamanho mínimo de senha | `10` |
| `LOGIN_MAX_TENTATIVAS` | Tentativas de login antes do bloqueio | `5` |
| `LOGIN_JANELA_SEG` | Janela de tempo para contagem de tentativas (s) | `900` |
| `LOGIN_BLOQUEIO_SEG` | Duração do bloqueio após excesso de tentativas (s) | `900` |

## Credenciais iniciais

- Email: `admin@sisritha.local`
- Senha: `Admin@2025!`
- Papel: `master`

No primeiro login, o sistema solicitará a configuração do 2FA (TOTP) via QR Code.

## Módulos

- **Secretariado Executivo** (implementado): Cadastro, Saúde, Recibos e Reembolsos, Viagens, Despesas, Fornecedores, Configurações.
- Administrativo, RH, Marketing, Jurídico, Financeiro, Cursos: previstos para fases futuras.
