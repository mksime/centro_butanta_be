# Banco de dados e backups

O Postgres **não** é provisionado pelo Render: o plano free do Render expira em
30 dias (com 14 dias de carência) e não tem backup. O banco de produção fica no
**Neon Free** e as cópias ficam no **Cloudflare R2**.

```
Render (web, virginia) ──TLS──> Neon (Postgres, us-east-1)
                                      │
GitHub Actions (diário) ──pg_dump─────┘
        │
        └──> Cloudflare R2 (10 GB grátis)

GitHub Actions (mensal) ──baixa o dump──> Postgres descartável
        └── alembic upgrade/check + contagens + pytest
```

## Por que Neon

| Item | Neon Free |
|---|---|
| Custo | US$ 0 |
| Storage | 1 GB por projeto |
| Restore | PITR de até 6h ou 1 GB de mudanças + 1 snapshot |
| Branch | cópia instantânea, ótima para testar restore sem tocar produção |
| Inatividade | compute hiberna após 5 min (primeira query ~0,5–1 s) |

Use a região **`aws-us-east-1`** (N. Virginia), a mesma do Render (`virginia`).

## Configuração inicial

1. **Neon**: crie o projeto com Postgres 17 ou 18 em `aws-us-east-1` e copie a
   connection string **pooled**, com `?sslmode=require`.
2. **Render**: no dashboard, defina `DATABASE_URL` com essa string. O
   `render.yaml` usa `sync: false` justamente para não versionar a credencial.
   O start command roda `alembic upgrade head` antes do uvicorn — o plano free
   não tem `preDeployCommand`. Com uma instância não há corrida, e o upgrade é
   idempotente: roda de novo a cada cold start.
3. **R2**: crie o bucket `cbbe-backups` e um API token com permissão
   **Object Read & Write**. Anote o endpoint
   `https://<account-id>.r2.cloudflarestorage.com`.
4. **GitHub Secrets** (Settings → Secrets and variables → Actions):

   | Secret | Valor |
   |---|---|
   | `BACKUP_DATABASE_URL` | URL **direta** do Neon (sem `-pooler`), de preferência de um usuário só de leitura |
   | `R2_ENDPOINT` | `https://<account-id>.r2.cloudflarestorage.com` |
   | `R2_BUCKET` | `cbbe-backups` |
   | `R2_ACCESS_KEY_ID` | access key do token do R2 |
   | `R2_SECRET_ACCESS_KEY` | secret do token do R2 |
   | `ALERT_WEBHOOK_URL` | opcional: Slack/Discord para avisar falhas |

5. Rode o workflow **Backup do banco** manualmente (`workflow_dispatch`) e
   depois o **Teste de restore**, antes de confiar na automação.

### Usuário só de leitura (recomendado)

O dump não precisa de escrita, e a URL do app não deve ser exposta ao CI. No
Neon, crie um role e use a URL **direta** (sem `-pooler`) dele no secret
`BACKUP_DATABASE_URL`:

```sql
CREATE ROLE backup LOGIN PASSWORD '...';
GRANT pg_read_all_data TO backup;
```

A URL pooled (`-pooler`) fica só no Render, para a aplicação.

## Rotina automática

| Workflow | Quando | O que faz |
|---|---|---|
| `backup.yml` | diário, 03:17 UTC | `pg_dump` custom → valida com `pg_restore --list` → envia ao R2 → apaga dumps com mais de 30 dias |
| `restore-drill.yml` | dia 1 de cada mês, 04:23 UTC | baixa o dump mais recente, falha se ele tiver mais de 8 dias, restaura num `postgres:18` descartável, roda `alembic upgrade head`, `alembic check`, contagens e a suíte |

O dump só é considerado concluído depois que o `pg_restore --list` consegue
lê-lo. O drill falha de propósito quando o backup mais recente está velho: um
agendamento que parou não pode passar despercebido.

## Testar um restore localmente

```bash
docker compose up -d
docker exec cbbe_postgres createdb -U cbbe cbbe_test
DATABASE_URL=postgresql://cbbe:cbbe_secret@localhost:5432/cbbe_test alembic upgrade head

# Gera o dump sem enviar (UPLOAD=0)
UPLOAD=0 DATABASE_URL=postgresql://cbbe:cbbe_secret@localhost:5432/cbbe_test \
  ./scripts/backup.sh

# Restaura em outro banco e valida
docker exec cbbe_postgres createdb -U cbbe cbbe_drill
DRILL_DATABASE_URL=postgresql://cbbe:cbbe_secret@localhost:5432/cbbe_drill \
  ./scripts/restore_drill.sh backups/backup-<timestamp>.dump
```

`SKIP_PYTEST=1` faz só restore + `alembic check` + contagens. A suíte completa
**apaga linhas entre os testes**; rode-a apenas contra um banco descartável.

## Restore de emergência (produção)

**Opção A — Neon PITR/branch (mais rápida):**

1. Pare as escritas (escale o web service para 0 ou ative manutenção).
2. No Neon, crie um branch a partir do ponto no tempo desejado (ou restaure o
   snapshot).
3. Rode `alembic current` e `alembic check` contra o branch.
4. Teste `/ready`, login e uma leitura autenticada.
5. Aponte `DATABASE_URL` para a URL pooled do branch e redeploye.

**Opção B — dump do R2:**

1. Baixe o dump mais recente do bucket.
2. Crie um banco novo e rode
   `pg_restore --no-owner --no-privileges -d "$NOVO" dump`.
3. `alembic upgrade head` e `alembic check`.
4. Aponte `DATABASE_URL` para o banco novo e redeploye.

Em qualquer caso, registre o incidente: horário, quanto dado foi perdido
(RPO real), tempo até voltar (RTO real) e o que causou.

## RPO e RTO

| Mecanismo | RPO | RTO aproximado |
|---|---|---|
| PITR do Neon | minutos (janela de 6h) | minutos |
| Snapshot do Neon | ponto do snapshot | minutos |
| Dump diário no R2 | até 24h | 10–30 min |

## Limitações e cuidados

- **GitHub Actions em repositório público**: workflows agendados são desativados
  após 60 dias sem atividade no repositório. Rode manualmente (`workflow_dispatch`)
  ou use um Render Cron Job (mínimo de US$ 1/mês) se o projeto for ficar parado.
- **Atrasos**: o `schedule` do GitHub pode atrasar ou descartar execuções sob
  carga. O teste de idade no drill cobre o caso de o backup parar.
- **Arquivos**: o banco guarda só `caminho_arquivo`. Os comprovantes estão no
  storage de objetos — ative versionamento no bucket ou copie-o separadamente.
- **LGPD**: os dumps contêm CPF, endereço e telefone. Mantenha o bucket privado,
  use token com escopo mínimo, aplique a retenção e evite baixar dumps para
  máquinas pessoais.
- **Versão do cliente**: `pg_dump`/`pg_restore` precisam ser >= a versão do
  servidor. Os workflows instalam o cliente 18; localmente, confira
  `pg_dump --version` antes de rodar.
