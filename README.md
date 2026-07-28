# 🤖 Agente Participa - WhatsApp com LangGraph & FastAPI

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/LangChain-LangGraph-blue?style=for-the-badge" alt="LangGraph" />
  <img src="https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge&logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/Meta-WhatsApp%20Cloud%20API-0080FF?style=for-the-badge&logo=whatsapp" alt="WhatsApp Cloud API" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker" alt="Docker" />
</p>

Este repositório contém a implementação completa da solução **Agente Participa**, um agente inteligente de inteligência artificial para o **WhatsApp**, construído utilizando **LangGraph** para orquestração de diálogos e chamadas de ferramentas (*Function Calling*), integrado a uma API **FastAPI** robusta para gerenciamento de Webhooks com a **Meta Cloud API**.

---

## 🎯 Principais Recursos

- 💬 **Integração Nativa com Meta WhatsApp Cloud API**: Recebimento de mensagens via Webhook com suporte a processamento assíncrono em segundo plano (`BackgroundTasks`).
- 🧠 **Agente ReAct com LangGraph**: Suporte a memória de conversação por usuário (`thread_id` mapeado para o telefone) e uso de ferramentas personalizadas.
- ⚡ **Multi-Provedor de LLM**: Suporte alternável e simplificado para **Groq** (Llama 3.3 70B), **Google Gemini** e **OpenAI**.
- 🛠️ **Ferramentas Extensíveis**: Sistema modular de ferramentas em `agent/tools.py` (busca em FAQ, consulta de horários, etc).
- 🛡️ **Segurança & Boas Práticas**: Validação de ambiente via `pydantic-settings` e proteção de segredos com `.gitignore`.
- 🐳 **Docker & Docker Compose**: Configuração pronta para implantação em ambiente local ou produção.

---

## 📁 Estrutura do Projeto

```text
AgenteParticipa/
├── agent/
│   ├── __init__.py
│   ├── state.py         # Schema do estado da conversa (AgentState)
│   ├── tools.py         # Ferramentas atreladas ao agente (@tool)
│   └── graph.py         # Grafo de raciocínio LangGraph e inicialização de LLMs
├── whatsapp/
│   ├── __init__.py
│   ├── parser.py        # Parser seguro de webhooks da Meta Cloud API
│   └── client.py        # Cliente HTTP (httpx) para envio de mensagens WhatsApp
├── .env.example         # Template de variáveis de ambiente
├── .gitignore           # Proteção contra commit de segredos e cache
├── config.py            # Validador de configurações via Pydantic
├── Dockerfile           # Imagem Docker otimizada
├── docker-compose.yml   # Orquestração do container
├── main.py              # Aplicação FastAPI e rotas do Webhook
└── requirements.txt     # Dependências do projeto Python
```

---

## 🚀 Como Executar Localmente

### 1. Clonar o Repositório e Instalar Dependências

```bash
git clone https://github.com/ThiagoVenturaV/Participa.git
cd Participa

# Criar e ativar ambiente virtual
python -m venv venv

# Linux/macOS:
source venv/bin/activate

# Windows (PowerShell):
.\venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Crie o arquivo `.env` a partir do template `.env.example`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` informando suas credenciais:

```env
# Chave da IA (Groq, Gemini ou OpenAI)
GROQ_API_KEY=gsk_sua_chave_groq_aqui
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile

# Credenciais da Meta Cloud API
WHATSAPP_TOKEN=EAAG...
WHATSAPP_PHONE_NUMBER_ID=1287924531064501
WEBHOOK_VERIFY_TOKEN=meu_token_secreto_whatsapp_123

# Servidor
PORT=8000
HOST=0.0.0.0
```

### 3. Executar o Servidor FastAPI

```bash
python main.py
```
*Ou via Uvicorn diretamente:*
```bash
uvicorn main:app --reload --port 8000
```

Acesse no navegador: `http://localhost:8000/docs` para visualizar a documentação interativa Swagger.

---

## 🧪 Testando com Ngrok (Webhook Local)

Para conectar seu ambiente local aos servidores da Meta (WhatsApp):

1. Baixe e instale o [Ngrok](https://ngrok.com/).
2. Exponha a porta do seu servidor:
   ```bash
   ngrok http 8000
   ```
3. Copie a URL HTTPS gerada (exemplo: `https://xxxx-xx-xx.ngrok-free.app`).
4. Sua URL final de Webhook no painel da Meta será:
   ```text
   https://xxxx-xx-xx.ngrok-free.app/webhook
   ```

---

## 📲 Configuração no Meta for Developers

1. Acesse o portal [Meta for Developers](https://developers.facebook.com/).
2. Crie ou selecione um aplicativo do tipo **Negócios / Business**.
3. Adicione o produto **WhatsApp**.
4. Na barra lateral, acesse **WhatsApp** > **Configuração**:
   - **URL de callback**: `https://seu-dominio.ngrok-free.app/webhook`
   - **Verificar token**: O mesmo valor definido em `WEBHOOK_VERIFY_TOKEN` no `.env` (ex: `meu_token_secreto_whatsapp_123`).
   - Clique em **Verificar e Salvar**.
5. Na seção **Campos do Webhook**, localize o evento **`messages`** e clique em **Assinar (Subscribe)**.
6. Obtenha seu **ID do Número de Telefone** e o **Token de Acesso** e salve no seu `.env`.

---

## 🔌 Endpoints da API

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `GET` | `/` | Retorna o status online do agente. |
| `GET` | `/health` | Healthcheck para monitoramento do container/servidor. |
| `GET` | `/webhook` | Endpoint de verificação e validação do Webhook exigido pela Meta. |
| `POST` | `/webhook` | Endpoint de recebimento das mensagens e eventos do WhatsApp. |

---

## 🐳 Executando com Docker

1. Defina o seu `NGROK_AUTHTOKEN` no arquivo `.env` (obtenha em [dashboard.ngrok.com](https://dashboard.ngrok.com/get-started/your-authtoken)).
2. Para subir a aplicação e o Ngrok via **Docker Compose**:

```bash
docker-compose up --build -d
```

3. Para ver a URL pública gerada pelo Ngrok no container:
   - Acesse `http://localhost:4040` no seu navegador, ou
   - Execute: `curl http://localhost:4040/api/tunnels`

Para visualizar os logs:
```bash
docker-compose logs -f
```

---

## ⚙️ Customizando o Agente

- **Adicionar Novas Ferramentas**: Abra `agent/tools.py`, crie a função com o decorador `@tool` e adicione à lista `tools`.
- **Alterar Prompt de Sistema**: Edite o `SYSTEM_PROMPT` em `agent/graph.py`.
- **Alternar Provedor de LLM**: Altere `LLM_PROVIDER` no `.env` para `groq`, `gemini` ou `openai`.

---

## 📄 Licença

Este projeto está licenciado sob a licença MIT. Sinta-se livre para utilizar e modificar!