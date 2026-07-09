# Daily Diet API

> API REST para controle de dieta diária, com autenticação de usuários e registro de refeições, construída com Flask, Flask-Login e MySQL

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.0-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Flask--SQLAlchemy](https://img.shields.io/badge/Flask--SQLAlchemy-3.1.1-D71F00?style=flat)](https://flask-sqlalchemy.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

---

## 📋 Sobre o projeto

**Daily Diet API** é uma API REST para acompanhamento diário de dieta, desenvolvida como projeto de estudo. Cada usuário autenticado pode registrar suas refeições, indicando se elas estão ou não dentro da dieta, e consultar, atualizar ou remover esses registros — sempre com acesso restrito às **suas próprias** refeições.

O projeto reutiliza a mesma base de autenticação por sessão do [`sample-flask-auth`](https://github.com/igorland1/sample-flask-auth) (Flask-Login + bcrypt), acrescentando a entidade `Meal` (refeição) vinculada ao usuário.

### Principais características

- ✅ **Autenticação por sessão** com Flask-Login (`register`/`login`/`logout`)
- ✅ **Senhas com hash seguro** usando `bcrypt`
- ✅ **CRUD de refeições** — criação, consulta (individual e listagem), atualização e remoção
- ✅ **Isolamento por usuário** — cada usuário só acessa e altera as próprias refeições
- ✅ **Marcação "dentro da dieta"** (`within_diet`) por refeição, com data/hora de registro
- ✅ **Rotas protegidas** com o decorator `@login_required`
- ✅ **Banco de dados MySQL** via Docker Compose

---

## 🏗️ Arquitetura

### Stack utilizada

- **Linguagem**: Python 3.10+
- **Framework Web**: Flask 2.3.0
- **ORM**: Flask-SQLAlchemy 3.1.1
- **Autenticação**: Flask-Login 0.6.2
- **Banco de dados**: MySQL (via `pymysql` 1.1.0 + `cryptography` 41.0.7)
- **Hash de senha**: bcrypt 4.1.2
- **Infraestrutura local**: Docker Compose

### Estrutura do projeto

```
daily-diet-api/
├── models/
│   ├── user.py         # Modelo User (SQLAlchemy)
│   └── meal.py          # Modelo Meal (SQLAlchemy)
├── app.py               # Aplicação Flask, rotas de auth e refeições
├── database.py            # Instância do SQLAlchemy
├── docker-compose.yml       # Container MySQL para desenvolvimento
├── requirements.txt         # Dependências do projeto
└── .gitignore
```

### Modelo de dados

**User** (`models/user.py`)

| Campo      | Tipo   | Descrição                           |
|------------|--------|---------------------------------------|
| `id`       | int    | Identificador único do usuário        |
| `username` | string | Nome de usuário, usado no login       |
| `password` | string | Hash da senha (gerado com bcrypt)     |

**Meal** (`models/meal.py`)

| Campo         | Tipo      | Descrição                                         |
|---------------|-----------|------------------------------------------------------|
| `id`          | int       | Identificador único da refeição                       |
| `user_id`     | int       | ID do usuário dono da refeição                        |
| `meal_name`   | string    | Nome da refeição                                      |
| `description` | string    | Descrição da refeição                                 |
| `date_add`    | datetime  | Data/hora do registro (preenchida automaticamente)    |
| `within_diet` | boolean   | Indica se a refeição está dentro da dieta              |

---

## 🚀 Como executar

### Pré-requisitos

- Python 3.10 ou superior
- pip
- Docker e Docker Compose (para o banco de dados MySQL)

### Instalação

**1. Clone o repositório**

```bash
git clone https://github.com/igorland1/daily-diet-api.git
cd daily-diet-api
```

**2. Instale as dependências**

```bash
pip install -r requirements.txt
```

**3. Suba o banco de dados MySQL**

```bash
docker compose up -d
```

> ⚠️ O `docker-compose.yml` original define um volume apontando para um caminho local do Windows (`C:/Users/igorlandi/mysql`). Ajuste esse caminho no arquivo conforme o seu ambiente antes de subir o container.

O banco `daily-diet-api` será criado automaticamente, acessível em `127.0.0.1:3306` com usuário `admin` e senha `admin123` (credenciais definidas para desenvolvimento local).

**4. Configure a conexão com o banco**

A string de conexão está definida diretamente em `app.py`:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:admin123@127.0.0.1:3306/daily-diet-api'
```

> 💡 Para uso além do ambiente local, recomenda-se mover essa configuração (e a `SECRET_KEY`) para variáveis de ambiente.

**5. Execute a aplicação**

```bash
python app.py
```

A API estará disponível em `http://127.0.0.1:5000`, em modo debug.

---

## 📡 Endpoints da API

### Visão geral

```http
POST    /register-user       # Cria um novo usuário
POST    /login                # Autentica um usuário e inicia a sessão
GET     /logout               # Encerra a sessão do usuário autenticado
POST    /add-meal              # Registra uma nova refeição
GET     /meal/<meal_id>         # Consulta uma refeição específica
GET     /meal                   # Lista todas as refeições do usuário autenticado
PUT     /meal/<meal_id>         # Atualiza uma refeição existente
DELETE  /meal/<meal_id>         # Remove uma refeição
```

### Regras de acesso

- Todas as rotas de refeição (`/add-meal`, `/meal`, `/meal/<meal_id>`) e `/logout` exigem sessão ativa (`@login_required`).
- Um usuário só pode visualizar, atualizar ou remover as **próprias** refeições — tentativas de acessar refeições de outro usuário retornam `403 Ação não autorizada`.

### Exemplos de requisições

**Registrar usuário**

```http
POST /register-user
Content-Type: application/json

{
  "username": "igor",
  "password": "minhasenha123"
}
```

**Login**

```http
POST /login
Content-Type: application/json

{
  "username": "igor",
  "password": "minhasenha123"
}
```

Resposta:

```json
{
  "message": "Seja bem vindo(a) igor"
}
```

**Registrar refeição**

```http
POST /add-meal
Content-Type: application/json

{
  "meal_name": "Almoço",
  "description": "Arroz, feijão, frango grelhado e salada",
  "within_diet": true
}
```

Resposta:

```json
{
  "message": "Refeição Almoço cadastrada com sucesso"
}
```

**Listar refeições**

```http
GET /meal
```

Resposta:

```json
{
  "refeições": [
    {
      "id": 1,
      "user_id": 1,
      "meal_name": "Almoço",
      "description": "Arroz, feijão, frango grelhado e salada",
      "date_add": "2026-07-09T13:00:00",
      "within_diet": true
    }
  ],
  "total de refeições": 1
}
```

**Consultar refeição por ID**

```http
GET /meal/1
```

**Atualizar refeição**

```http
PUT /meal/1
Content-Type: application/json

{
  "meal_name": "Almoço reforçado",
  "within_diet": false
}
```

Resposta:

```json
{
  "message": "Refeição atualizada com sucesso",
  "meal": {
    "id": 1,
    "user_id": 1,
    "meal_name": "Almoço reforçado",
    "description": "Arroz, feijão, frango grelhado e salada",
    "date_add": "2026-07-09T13:00:00",
    "within_diet": false
  }
}
```

**Remover refeição**

```http
DELETE /meal/1
```

Resposta:

```json
{
  "message": "Refeição removida com sucesso"
}
```

**Logout**

```http
GET /logout
```

---

## 🔒 Segurança

- **Hash de senhas** com `bcrypt`, nunca armazenadas em texto puro
- **Sessão de usuário** gerenciada pelo Flask-Login
- **Isolamento de dados por usuário** em todas as operações de refeição
- **Validação de propriedade do recurso** antes de leitura, atualização ou remoção

> ⚠️ Este projeto tem fins de estudo: a `SECRET_KEY` e as credenciais do banco estão hardcoded em `app.py`/`docker-compose.yml` para simplificar o ambiente local. Em um cenário real, essas informações devem vir de variáveis de ambiente e nunca ser versionadas.

---

## 🎯 Aprendizados demonstrados neste projeto

- Autenticação baseada em sessão com Flask-Login
- Hash e verificação segura de senhas com bcrypt
- Modelagem de dados relacionais (usuário → refeições) com Flask-SQLAlchemy
- Regras de autorização baseadas em propriedade do recurso (ownership)
- Uso de Docker Compose para provisionar dependências de desenvolvimento

---

## 📝 Licença

Este projeto está licenciado sob os termos da licença MIT.

---

## 🤝 Contato

Projeto desenvolvido por [Igor](https://github.com/igorland1).
