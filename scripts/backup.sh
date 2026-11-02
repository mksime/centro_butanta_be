#!/usr/bin/env bash
#
# Gera um dump lógico do Postgres e envia para o Cloudflare R2.
#
# Variáveis obrigatórias quando UPLOAD=1:
#   DATABASE_URL                 conexão do banco (use ?sslmode=require)
#   R2_ENDPOINT                  https://<account-id>.r2.cloudflarestorage.com
#   R2_BUCKET                    nome do bucket
#   AWS_ACCESS_KEY_ID            token do R2 (Object Read & Write)
#   AWS_SECRET_ACCESS_KEY        secret do token do R2
#
# Opcionais:
#   BACKUP_DIR       diretório local do dump (padrão: backups)
#   BACKUP_PREFIX    prefixo das chaves no bucket (padrão: postgres)
#   RETENTION_DAYS   dias de retenção no bucket (padrão: 30)
#   UPLOAD=0         gera e valida o dump, mas não envia (teste local)
#
# Requer pg_dump e pg_restore no PATH, em versão >= a do servidor.
set -euo pipefail

: "${DATABASE_URL:?defina DATABASE_URL}"
BACKUP_DIR="${BACKUP_DIR:-backups}"
BACKUP_PREFIX="${BACKUP_PREFIX:-postgres}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
UPLOAD="${UPLOAD:-1}"

if ! [[ "$RETENTION_DAYS" =~ ^[0-9]+$ ]] || [ "$RETENTION_DAYS" -lt 1 ]; then
  echo "RETENTION_DAYS deve ser um inteiro >= 1 (recebido: $RETENTION_DAYS)" >&2
  exit 1
fi

command -v pg_dump >/dev/null || { echo "pg_dump não encontrado no PATH" >&2; exit 1; }
command -v pg_restore >/dev/null || { echo "pg_restore não encontrado no PATH" >&2; exit 1; }

umask 077
mkdir -p "$BACKUP_DIR"

ARQUIVO="backup-$(date -u +%Y%m%dT%H%M%SZ).dump"
CAMINHO="$BACKUP_DIR/$ARQUIVO"

echo "Gerando $CAMINHO..."
pg_dump "$DATABASE_URL" \
  --format=custom \
  --no-owner \
  --no-privileges \
  --file="$CAMINHO"

# Só considere o backup concluído se o arquivo puder ser lido pelo pg_restore.
pg_restore --list "$CAMINHO" >/dev/null

TAMANHO="$(du -h "$CAMINHO" | cut -f1)"
SHA256="$(sha256sum "$CAMINHO" | cut -d' ' -f1)"
echo "Dump válido: $TAMANHO, sha256=$SHA256"

if [ "$UPLOAD" = "1" ]; then
  : "${R2_ENDPOINT:?defina R2_ENDPOINT}"
  : "${R2_BUCKET:?defina R2_BUCKET}"
  command -v aws >/dev/null || { echo "AWS CLI (aws) não encontrado no PATH" >&2; exit 1; }

  aws s3 cp "$CAMINHO" "s3://$R2_BUCKET/$BACKUP_PREFIX/$ARQUIVO" \
    --endpoint-url "$R2_ENDPOINT" --only-show-errors
  echo "Enviado para s3://$R2_BUCKET/$BACKUP_PREFIX/$ARQUIVO"

  # Retenção: remove só o que já passou do prazo. O dump recém-enviado é mais
  # novo que o corte, então nunca é apagado aqui.
  CORTE="$(date -u -d "-${RETENTION_DAYS} days" +%Y-%m-%dT%H:%M:%SZ)"
  CHAVES="$(aws s3api list-objects-v2 \
    --bucket "$R2_BUCKET" \
    --prefix "$BACKUP_PREFIX/" \
    --endpoint-url "$R2_ENDPOINT" \
    --query "Contents[?LastModified<='${CORTE}'].Key" \
    --output text)"

  if [ -n "$CHAVES" ] && [ "$CHAVES" != "None" ]; then
    echo "$CHAVES" | tr '\t' '\n' | while IFS= read -r chave; do
      [ -n "$chave" ] || continue
      aws s3 rm "s3://$R2_BUCKET/$chave" \
        --endpoint-url "$R2_ENDPOINT" --only-show-errors
      echo "Removido (retenção de ${RETENTION_DAYS} dias): $chave"
    done
  fi
else
  echo "UPLOAD=0: dump mantido apenas em $CAMINHO"
fi

if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
  {
    echo "### Backup do banco"
    echo ""
    echo "| Item | Valor |"
    echo "|---|---|"
    echo "| Arquivo | \`$ARQUIVO\` |"
    echo "| Tamanho | $TAMANHO |"
    echo "| SHA256 | \`$SHA256\` |"
    echo "| Retenção | ${RETENTION_DAYS} dias |"
  } >> "$GITHUB_STEP_SUMMARY"
fi
