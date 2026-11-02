#!/usr/bin/env bash
#
# Testa um backup de verdade: restaura em um banco descartável, aplica as
# migrations pendentes, confere o schema e roda a suíte de testes.
#
# Uso:
#   DRILL_DATABASE_URL=postgresql://... ./scripts/restore_drill.sh caminho/backup.dump
#
# Variáveis:
#   DRILL_DATABASE_URL  banco descartável (NUNCA o de produção)
#   SKIP_PYTEST=1       pula a suíte (a suíte apaga linhas entre os testes)
#
# Requer pg_restore, psql e alembic no PATH.
set -euo pipefail

BACKUP_FILE="${1:-${BACKUP_FILE:-}}"
: "${BACKUP_FILE:?informe o arquivo do dump (argumento ou BACKUP_FILE)}"
: "${DRILL_DATABASE_URL:?defina DRILL_DATABASE_URL (banco descartável)}"

[ -f "$BACKUP_FILE" ] || { echo "dump não encontrado: $BACKUP_FILE" >&2; exit 1; }
command -v pg_restore >/dev/null || { echo "pg_restore não encontrado no PATH" >&2; exit 1; }
command -v psql >/dev/null || { echo "psql não encontrado no PATH" >&2; exit 1; }

# Proteção contra rodar o drill no banco de produção por engano.
if [ "$DRILL_DATABASE_URL" = "${DATABASE_URL:-}" ]; then
  echo "DRILL_DATABASE_URL não pode ser igual a DATABASE_URL (produção)" >&2
  exit 1
fi

echo "Restaurando $BACKUP_FILE em $DRILL_DATABASE_URL"
ERROS="$(mktemp)"
trap 'rm -f "$ERROS"' EXIT

# O pg_dump 18 grava "SET transaction_timeout = 0", GUC que só existe a partir
# do Postgres 17. Se o alvo for mais antigo que o cliente, ignoramos apenas
# esse ajuste de sessão — qualquer outro erro aborta o drill.
if ! pg_restore \
  --clean --if-exists \
  --no-owner --no-privileges \
  --dbname="$DRILL_DATABASE_URL" \
  "$BACKUP_FILE" 2> "$ERROS"; then
  if grep -q 'unrecognized configuration parameter "transaction_timeout"' "$ERROS" \
    && [ "$(grep -c 'error:' "$ERROS")" -eq 1 ]; then
    echo "Aviso: SET transaction_timeout ignorado (alvo mais antigo que o pg_dump)."
  else
    cat "$ERROS" >&2
    exit 1
  fi
fi

if [ -s "$ERROS" ]; then
  grep -v -e 'transaction_timeout' -e 'errors ignored on restore' "$ERROS" >&2 || true
fi

echo "Aplicando migrations pendentes..."
DATABASE_URL="$DRILL_DATABASE_URL" alembic upgrade head
DATABASE_URL="$DRILL_DATABASE_URL" alembic check

echo "Contagens no banco restaurado:"
psql "$DRILL_DATABASE_URL" -At -F '=' -c "
  SELECT 'administrador', count(*) FROM administrador
  UNION ALL SELECT 'moradia', count(*) FROM moradia
  UNION ALL SELECT 'associado', count(*) FROM associado
  UNION ALL SELECT 'comprovante_residencia', count(*) FROM comprovante_residencia
  UNION ALL SELECT 'pagamento', count(*) FROM pagamento
  ORDER BY 1;"

if [ "${SKIP_PYTEST:-0}" = "1" ]; then
  echo "SKIP_PYTEST=1: suíte não executada."
  exit 0
fi

echo "Rodando a suíte contra o banco restaurado (destrutivo: banco descartável)..."
DATABASE_URL="$DRILL_DATABASE_URL" TEST_DATABASE_URL="$DRILL_DATABASE_URL" pytest -q
