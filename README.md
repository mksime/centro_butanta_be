# Centro Comunitário Butantã — API

API REST para gestão de um centro comunitário, construída com **FastAPI** e **PostgreSQL**.

## Entidades

| Entidade | Descrição |
|---|---|
| **Administrador** | Usuários administradores do sistema |
| **Moradia** | Endereços dos associados |
| **Associado** | Pessoas cadastradas no centro comunitário |
| **Comprovante de Residência** | Documentos anexados pelos associados |
| **Pagamento** | Pagamentos realizados pelos associados |

## Como rodar localmente

### 1. Subir o PostgreSQL com Docker

```bash
docker compose up -d
```

### 2. Ativar o ambiente virtual

```bash
source env_cbbe/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Rodar a API

```bash
uvicorn app.main:app --reload --port 8000
```

A API estará disponível em `http://localhost:8000`.

- **Documentação interativa (Swagger):** http://localhost:8000/docs
- **Documentação alternativa (ReDoc):** http://localhost:8000/redoc

### 5. Rodar os testes

Por padrão a suíte usa SQLite em memória (rápido, sem dependências):

```bash
pytest
```

O CI roda contra PostgreSQL 16. Para reproduzir localmente:

```bash
docker compose up -d
docker exec cbbe_postgres createdb -U cbbe cbbe_test
DATABASE_URL=postgresql://cbbe:cbbe_secret@localhost:5432/cbbe_test alembic upgrade head
TEST_DATABASE_URL=postgresql://cbbe:cbbe_secret@localhost:5432/cbbe_test pytest
```

## Endpoints

Todos os endpoints são prefixados com `/api/v1`:

| Método | Path | Descrição |
|---|---|---|
| GET | `/api/v1/administradores/` | Listar administradores |
| POST | `/api/v1/administradores/` | Criar administrador |
| GET | `/api/v1/administradores/{id}` | Buscar administrador |
| PUT | `/api/v1/administradores/{id}` | Atualizar administrador |
| DELETE | `/api/v1/administradores/{id}` | Deletar administrador |
| GET | `/api/v1/moradias/` | Listar moradias |
| POST | `/api/v1/moradias/` | Criar moradia |
| GET | `/api/v1/moradias/{id}` | Buscar moradia |
| PUT | `/api/v1/moradias/{id}` | Atualizar moradia |
| DELETE | `/api/v1/moradias/{id}` | Deletar moradia |
| GET | `/api/v1/associados/` | Listar associados |
| POST | `/api/v1/associados/` | Criar associado |
| POST | `/api/v1/associados/completo` | Criar moradia e associado juntos |
| POST | `/api/v1/associados/juntos` | Criar moradia e associado juntos |
| POST | `/api/v1/associados/com-moradia` | Criar moradia e associado juntos |
| GET | `/api/v1/associados/{id}` | Buscar associado |
| PUT | `/api/v1/associados/{id}` | Atualizar associado |
| PUT | `/api/v1/associados/completo/{id}` | Atualizar moradia e associado juntos |
| PUT | `/api/v1/associados/juntos/{id}` | Atualizar moradia e associado juntos |
| PUT | `/api/v1/associados/com-moradia/{id}` | Atualizar moradia e associado juntos |
| DELETE | `/api/v1/associados/{id}` | Deletar associado |
| GET | `/api/v1/comprovantes/` | Listar comprovantes |
| POST | `/api/v1/comprovantes/` | Criar comprovante |
| GET | `/api/v1/comprovantes/{id}` | Buscar comprovante |
| PUT | `/api/v1/comprovantes/{id}` | Atualizar comprovante |
| DELETE | `/api/v1/comprovantes/{id}` | Deletar comprovante |
| GET | `/api/v1/pagamentos/` | Listar pagamentos |
| POST | `/api/v1/pagamentos/` | Criar pagamento |
| GET | `/api/v1/pagamentos/{id}` | Buscar pagamento |
| PUT | `/api/v1/pagamentos/{id}` | Atualizar pagamento |
| DELETE | `/api/v1/pagamentos/{id}` | Deletar pagamento |

## Configuração

As variáveis de ambiente podem ser ajustadas no arquivo `.env`:

| Variável | Padrão | Descrição |
|---|---|---|
| `DATABASE_URL` | — | URL completa do Postgres; tem precedência sobre as variáveis `POSTGRES_*` |
| `POSTGRES_USER` | `cbbe` | Usuário do PostgreSQL |
| `POSTGRES_PASSWORD` | `cbbe_secret` | Senha do PostgreSQL |
| `POSTGRES_HOST` | `localhost` | Host do PostgreSQL |
| `POSTGRES_PORT` | `5432` | Porta do PostgreSQL |
| `POSTGRES_DB` | `centro_butanta` | Nome do banco de dados |
| `ENVIRONMENT` | `development` | `development`, `staging`, `production` ou `test`; em produção desabilita `/docs` e exige `SECRET_KEY` forte |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Origens permitidas, separadas por vírgula |
| `SECRET_KEY` | valor de exemplo | Chave de assinatura do JWT; em produção é obrigatória e precisa ter ao menos 32 caracteres |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Validade do token JWT |
| `RATE_LIMIT_ENABLED` | `true` | Liga/desliga o rate limit |
| `LOGIN_RATE_LIMIT` | `5/minute` | Tentativas de login permitidas por IP |
| `RATE_LIMIT_STORAGE_URI` | `memory://` | Storage do rate limit; use `redis://host:porta` ao rodar várias instâncias |
| `SENTRY_DSN` | — | DSN do projeto no Sentry; sem ele o envio fica desativado |
| `SENTRY_TRACES_SAMPLE_RATE` | `0.0` | Fração de transações enviadas para tracing (0 a 1) |
| `SENTRY_RELEASE` | — | Versão exibida no Sentry |

## Deploy no Render

O repositório inclui um Blueprint (`render.yaml`) que provisiona **apenas o web
service**. O PostgreSQL é externo (Neon), porque o Postgres free do Render expira
em 30 dias e não tem backup. O passo a passo do banco e dos backups está em
[docs/backups.md](docs/backups.md).

1. Crie o banco no Neon (região `aws-us-east-1`) e copie a connection string
   **pooled** com `?sslmode=require`.
2. Faça push do repositório e, no dashboard do Render, escolha **New > Blueprint**.
3. Selecione o repositório e o branch `main`.
4. Quando o Render pedir `DATABASE_URL`, cole a string do Neon e aplique.

Cada deploy/start executa, nesta ordem:

| Etapa | Comando |
|---|---|
| Build | `pip install -r requirements.txt` |
| Start | `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1 ...` |

Pontos de atenção:

- O web service usa o plano `free`: sem cobrança de compute. Ele dorme após
  15 min sem tráfego, e a primeira requisição depois disso demora ~1 min.
- As migrations rodam no **start command** (o plano free não tem
  `preDeployCommand`). São idempotentes e rodam de novo a cada cold start.
- O plano free inclui 750 horas de instância por mês; um serviço ligado 24/7
  consome ~730 h.
- O Render não tem região no Brasil; `virginia` é a mais próxima (~110-140 ms).
- O banco fica no Neon, em `us-east-1`, com a URL pooled e `?sslmode=require`.
  O app normaliza o prefixo para `postgresql+psycopg2://` automaticamente.
- O filesystem é efêmero: comprovantes devem ir para storage de objetos
  (S3/R2/B2), não para disco local.
- Backups diários no R2 e teste mensal de restore rodam no GitHub Actions; veja
  [docs/backups.md](docs/backups.md).
- Crie o primeiro administrador uma única vez (`ADMIN_SEED_ENABLED=true` em um deploy, ou por script) e mantenha o seed desligado depois.

### Configuração de produção

Com `ENVIRONMENT=production`:

- `/docs`, `/redoc` e `/openapi.json` ficam desabilitados;
- o app **não sobe** se `SECRET_KEY` ainda for o valor padrão ou tiver menos de 32 caracteres;
- o seed recusa senhas com menos de 12 caracteres (incluindo `admin123`);
- o login é limitado a `LOGIN_RATE_LIMIT` tentativas por IP (`5/minute` por padrão).

O rate limit usa `memory://`, ou seja, é **por instância**. Ao escalar para mais de uma instância, configure `RATE_LIMIT_STORAGE_URI` com um Redis e adicione o pacote `redis` às dependências.

### Primeiro administrador

O `render.yaml` sobe com `ADMIN_SEED_ENABLED=false`, então o banco começa sem
administrador — e `POST /api/v1/administradores/` exige autenticação. Crie o
primeiro admin uma única vez, de forma idempotente (só cria se a tabela estiver
vazia), rodando da sua máquina contra o Neon:

```bash
DATABASE_URL='postgresql://...' \
ENVIRONMENT=production \
SECRET_KEY='chave-descartavel-com-32-caracteres-ou-mais' \
ADMIN_SEED_ENABLED=true \
ADMIN_SEED_EMAIL='seu-email@exemplo.com' \
ADMIN_SEED_PASSWORD='senha-forte-com-12-ou-mais' \
python - <<'PY'
from app.config import settings
from app.database import SessionLocal
from app.seed import seed_initial_admin

db = SessionLocal()
try:
    seed_initial_admin(db, settings)
    print("Administrador criado/verificado:", settings.ADMIN_SEED_EMAIL)
finally:
    db.close()
PY
```

A senha **não pode ser alterada pela API** (`AdministradorUpdate` não tem o
campo `senha`), então escolha uma senha forte agora. Para trocar depois, é
preciso atualizar o hash no banco ou criar um endpoint de troca de senha.

## Saúde e observabilidade

| Endpoint | Uso | O que faz |
|---|---|---|
| `GET /health` | health check do Render (liveness) | responde 200 se o processo está vivo, sem tocar no banco |
| `GET /ready` | monitoramento externo (readiness) | executa `SELECT 1` e responde 503 se o banco não responder |

Não use `/ready` como health check do Render: uma oscilação do banco faria o Render reiniciar instâncias sadias. No plano free, um monitor externo que consulta o serviço com frequência também impede o spin-down e consome as 750 h/mês.

### Sentry

Defina `SENTRY_DSN` para ativar. Antes do envio, o evento é higienizado: corpo da requisição, cookies, headers `Authorization`/`Cookie` e o bloco `user` são removidos (LGPD).

### CI

`.github/workflows/ci.yml` roda em cada push/PR para `main`:

1. sobe um PostgreSQL 16;
2. valida as migrations (`upgrade` → `downgrade` → `upgrade` e `alembic check`);
3. roda a suíte com `TEST_DATABASE_URL` apontando para o Postgres;
4. valida que o app sobe com `ENVIRONMENT=production`.

O `render.yaml` usa `autoDeployTrigger: checksPass`, então o deploy só acontece com o CI verde.

## Estrutura do projeto

```
centro_butanta_be/
├── app/
│   ├── __init__.py
│   ├── main.py            # Entry point do FastAPI
│   ├── config.py          # Configurações via env vars
│   ├── database.py        # Engine e sessão do SQLAlchemy
│   ├── models.py          # Modelos ORM (tabelas)
│   ├── schemas.py         # Schemas Pydantic (validação)
│   ├── crud.py            # Operações de banco (CRUD)
│   ├── rate_limit.py      # Rate limit do login (slowapi)
│   ├── observability.py   # Integração opcional com o Sentry
│   └── routers/
│       ├── administradores.py
│       ├── moradias.py
│       ├── associados.py
│       ├── comprovantes.py
│       └── pagamentos.py
├── alembic/               # Migrations do banco de dados
├── .github/workflows/     # CI, backup diário e teste mensal de restore
├── docs/                  # Banco externo, backups e restore
├── scripts/               # backup.sh e restore_drill.sh
├── docker-compose.yml     # PostgreSQL local
├── render.yaml            # Blueprint de deploy (Render)
├── requirements.txt       # Dependências Python
├── .env                   # Variáveis de ambiente (não versionar)
└── .env.example           # Exemplo de variáveis
```

## Autenticação (JWT / OAuth2 Bearer)

A API protege seus endpoints com **JWT (stateless)** usando o padrão **OAuth2 Password Bearer** nativo do FastAPI.

### Autenticação por e-mail

Os usuários (administradores) se autenticam com **e-mail**, ou seja, o e-mail é usado como **username**:

1. O administrador cadastra-se informando seu e-mail (obrigatório) em `POST /api/v1/administradores/`.
2. No login (`POST /api/v1/auth/token`), o campo `username` deve receber o **e-mail** cadastrado e o campo `password` a senha.
3. O e-mail é único por administrador e serve como identificador de login.

Exemplo de login:

```bash
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=ana.souza@example.com&password=senha123"
```

### Como funciona

1. Cadastro de administrador: `POST /api/v1/administradores/` recebe `nome_administrador`, `email`, `cargo`, `setor` e `senha` (hash com bcrypt é gravado em `senha_hash`).
2. Login: `POST /api/v1/auth/token` com `username` (que deve ser o **email** do administrador) e `senha` devolve um `access_token` (JWT) com expiração configurável.
3. Proteção de rotas: adicionar `Depends(get_current_active_admin)` a qualquer endpoint. Exemplo:

```python
from app.dependencies import get_current_active_admin
from app import models

@router.get("/")
def list_x(..., admin: models.Administrador = Depends(get_current_active_admin)):
    ...
```

### Configurar variáveis de ambiente

Adicione ao `.env`:

```
SECRET_KEY=chave-secreta-com-pelo-minimo-32-caracteres
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Banco de dados

O schema é gerenciado pelo **Alembic** — não use `Base.metadata.create_all` em produção. Depois de configurar o banco, aplique as migrations:

```bash
alembic upgrade head
```

Se você já tinha um banco de desenvolvimento criado por `create_all`, ele pode estar desatualizado em relação aos modelos (o `create_all` não adiciona colunas novas em tabelas existentes). O caminho mais simples é recriar o banco:

```bash
docker compose down -v
docker compose up -d
alembic upgrade head
```

Se o schema já estiver idêntico aos modelos, apenas marque a versão atual sem executar o upgrade:

```bash
alembic stamp head
```

> Em desenvolvimento com SQLite em memória (testes), as tabelas são recriadas automaticamente pelo `conftest.py`.

### Proteger todas as rotas

Todas as rotas da API estão protegidas com `Depends(get_current_active_admin)`:

| Router | Endpoints protegidos |
|---|---|
| `/auth/token` | Público (login) |
| `/administradores/` | GET, POST, GET/{id}, PUT/{id}, DELETE/{id} |
| `/moradias/` | GET, POST, GET/{id}, PUT/{id}, DELETE/{id} |
| `/associados/` | GET, POST, GET/{id}, PUT/{id}, DELETE/{id} |
| `/comprovantes/` | GET, POST, GET/{id}, PUT/{id}, DELETE/{id} |
| `/pagamentos/` | GET, POST, GET/{id}, PUT/{id}, DELETE/{id} |

Qualquer requisição a esses endpoints sem o header `Authorization: Bearer <token>` retorna **401 Unauthorized**.

### Impacto de um futuro frontend Vue

O uso de Vue (SPA) **não muda o protocolo de autenticação**, mas impõe três ajustes na API:

1. **CORS** — as origens vêm da variável `CORS_ORIGINS` (lista separada por vírgula), lida em `app/main.py`. Em desenvolvimento o padrão libera `http://localhost:5173` (Vite) e `http://localhost:3000`; em produção, defina o domínio do frontend (o `render.yaml` já aponta para `https://centro-com-butanta-pi2.bazan-antonieta.workers.dev`). Ao mudar o domínio, atualize a variável e redeploye.
2. **Envio do token** — o Vue deve armazenar o JWT (ex.: `localStorage`) e enviá-lo em todo request:
   ```js
   Authorization: Bearer <access_token>
   ```
3. **Onde guardar o token** — duas opções:
   - `localStorage` / `sessionStorage`: simples, mas vulnerável a XSS.
   - Cookie `httpOnly` + `SameSite=Strict`: mais seguro contra XSS, mas exige suporte a cookies no cliente e cuidado com CSRF.

Exemplo de consumo com Axios no Vue:

```js
import axios from 'axios'

const api = axios.create({ baseURL: 'http://localhost:8000/api/v1' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Login (username = email)
await api.post('/auth/token', { username: 'admin@centrobutanta.com', password: 'senha123' })
// => { access_token, token_type }  -> guardar em localStorage
```

---

## Testes (TDD)

O projeto segue abordagem **TDD (Test-Driven Development)**: todo novo comportamento começa com um teste falhando (`Red`), depois se escreve o código mínimo para passar (`Green`) e, por fim, refatora (`Refactor`).

### Rodar os testes

```bash
# 1. Ative o ambiente virtual
source env_cbbe/bin/activate

# 2. Instale dependências de desenvolvimento
pip install -r requirements-dev.txt

# 3. Rode os testes (banco SQLite em memória, não precisa do PostgreSQL)
pytest -v

# 4. Com cobertura de código
pytest --cov=app --cov-report=term-missing
```

### Estrutura dos testes

```
tests/
├── conftest.py          # fixtures (banco SQLite isolado, TestClient)
├── test_crud.py         # testes unitários da camada CRUD
└── api/
    ├── test_associados.py
    └── test_moradias.py
```

### Regras de ouro

1. **Nenhuma linha de código novo sem um teste vermelho primeiro.**
2. Um comportamento por teste, com nomes descritivos (`test_<cenario>_<resultado_esperado>`).
3. Nunca use o banco de produção nos testes — usa-se SQLite em memória com override da dependência `get_db`.
4. Cada entidade deve cobrir: GET vazio, GET por ID (existente/inexistente), POST válido, POST com FK inválida (404), POST com dado inválido (422), PUT (existente/inexistente), DELETE (existente/inexistente).

## Deploy na nuvem

O projeto já está preparado para deploy:

- **Configuração via variáveis de ambiente** — basta definir as env vars no provedor
- **Sem credenciais fixas** — tudo é lido do ambiente
- **requirements.txt** — para instalação de dependências em qualquer plataforma
- **docker-compose.yml** — pode ser adaptado para containers na nuvem

Provedores comuns: **Render**, **Railway**, **Fly.io**, **AWS (ECS/RDS)**, **GCP (Cloud Run/Cloud SQL)**, **Azure (App Service)**.


## Registrar pagamento ou atraso

`PUT /api/v1/associados/{id}/mensalidade` exige autenticação e um cadastro `ativo` ou `mensalidade_atrasada`.

- Pagamento: `{"atraso": false, "data_pagamento": "2026-11-01"}` salva `ativo` e `data_ultimo_pagamento`.
- Atraso: `{"atraso": true, "data_pagamento": null}` salva `mensalidade_atrasada` e preserva a data do último pagamento.

A alteração aplica-se somente ao associado selecionado. Este fluxo registra situação e data, sem gerar um lançamento financeiro com valor ou forma de pagamento inventados.

O schema é gerenciado exclusivamente pelo Alembic (`alembic upgrade head`); não há migração SQL manual.
