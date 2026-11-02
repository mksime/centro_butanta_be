-- Migração aditiva e idempotente para bancos PostgreSQL existentes.
BEGIN;
ALTER TABLE associado ADD COLUMN IF NOT EXISTS data_ultimo_pagamento DATE;
COMMIT;
