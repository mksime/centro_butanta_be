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
| GET | `/api/v1/associados/{id}` | Buscar associado |
| PUT | `/api/v1/associados/{id}` | Atualizar associado |
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

## Deploy na nuvem

O projeto já está preparado para deploy:

- **Configuração via variáveis de ambiente** — basta definir as env vars no provedor
- **Sem credenciais fixas** — tudo é lido do ambiente
- **requirements.txt** — para instalação de dependências em qualquer plataforma
- **docker-compose.yml** — pode ser adaptado para containers na nuvem

Provedores comuns: **Render**, **Railway**, **Fly.io**, **AWS (ECS/RDS)**, **GCP (Cloud Run/Cloud SQL)**, **Azure (App Service)**.
