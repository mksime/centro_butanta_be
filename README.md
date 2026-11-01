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
| `POSTGRES_USER` | `cbbe` | Usuário do PostgreSQL |
| `POSTGRES_PASSWORD` | `cbbe_secret` | Senha do PostgreSQL |
| `POSTGRES_HOST` | `localhost` | Host do PostgreSQL |
| `POSTGRES_PORT` | `5432` | Porta do PostgreSQL |
| `POSTGRES_DB` | `centro_butanta` | Nome do banco de dados |

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
│   └── routers/
│       ├── administradores.py
│       ├── moradias.py
│       ├── associados.py
│       ├── comprovantes.py
│       └── pagamentos.py
├── docker-compose.yml     # PostgreSQL local
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

O modelo `Administrador` ganhou o campo `email` (e-mail, único e obrigatório — usado como username no login) e o campo `senha_hash` (`NOT NULL`). Se a tabela já existir no PostgreSQL, adicione as colunas manualmente ou rode uma migration (Alembic) antes de iniciar:

```sql
ALTER TABLE administrador ADD COLUMN email VARCHAR(200) NOT NULL DEFAULT '';
ALTER TABLE administrador ADD COLUMN senha_hash VARCHAR(255) NOT NULL DEFAULT '';
```

> Em desenvolvimento com SQLite em memória (testes), as tabelas são recriadas automaticamente.

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

1. **CORS** — já configurado em `app/main.py`. Ajuste `allow_origins` para o domínio do Vue em produção (ex.: `https://seu-frontend.com`). Em desenvolvimento estão liberados `localhost:5173` (Vite) e `localhost:3000`.
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

Para um banco existente, antes de iniciar a API atualizada, execute a migração aditiva em `migrations/20261101_mensalidade.sql`, usando a conexão do seu PostgreSQL. Exemplo com os nomes padrão de desenvolvimento:

```sh
psql -h localhost -U cbbe -d centro_butanta -f migrations/20261101_mensalidade.sql
```

O `create_all` só cria tabelas novas; ele não acrescenta essa coluna em tabelas existentes. A migração SQL específica não executa a revisão Alembic antiga `f77b5d7380e7`, cujo `upgrade` contém comandos de exclusão de tabelas. Essa revisão precisa de revisão separada antes de qualquer `alembic upgrade head` em banco com dados.
