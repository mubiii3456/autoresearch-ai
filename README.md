# AutoResearch AI
 
> **Autonomous multi-agent research platform** — A team of specialized AI agents that plan, research, verify, and write fact-checked reports on any topic. Built with production-grade architecture: custom MCP servers, LangGraph orchestration, self-correction loops, real-time streaming, and full Docker containerization.
 
---
 
## Demo
 
> 📹 **[Watch Demo Video](#)** — *(add your Loom/YouTube link here)*
 
| Main Research Flow | Report Output | Cost Tracker |
|:---:|:---:|:---:|
| <img src="./main.png" width="300" alt="Main Research Flow"> | <img src="./report.png" width="300" alt="Report Output"> | <img src="./cost.png" width="300" alt="Cost Tracker"> |
---
 
## What It Does
 
You give it a topic. A team of AI agents take over:
 
1. **Researcher** searches the web in real-time (via MCP tools) and collects relevant data
2. **Critic** fact-checks every claim — if it fails, it sends structured feedback back and the Researcher retries automatically
3. **Writer** turns verified findings into a clear, professional report
4. **Editor** polishes the tone, formatting, and citations
You watch it all happen live. Before the final report is generated, you review the verified claim and either approve or reject it (**human-in-the-loop**). Every report is saved to a PostgreSQL database and you can track token usage and cost across all your sessions.
 
---
 
## Architecture
 
![Architecture Diagram](docs/architecture-diagram.svg)
 
### System Design
 
```
User → Streamlit UI → FastAPI Backend → LangGraph Agent Pipeline
                                              ↓
                               [Researcher → Critic → Writer → Editor]
                                              ↓
                                    4 Custom MCP Servers
                               (Web Search, Finance, Storage, Sandbox)
                                              ↓
                               PostgreSQL (reports) + Redis (cache)
```
 
The entire system runs as **8 Docker containers** orchestrated by `docker-compose`. A single `docker-compose up` starts everything.
 
### Why This Architecture
 
| Decision | What We Chose | Why |
|---|---|---|
| Agent orchestration | LangGraph | Graph-based control flow with native loop support — essential for the self-correction retry cycle |
| Frontend | Streamlit | Python-native, fast to ship, real WebSocket streaming without a separate JS framework |
| MCP servers | Custom FastAPI HTTP servers | HTTP-based MCP over stdio allows containerization — each tool is independently deployable |
| Database | PostgreSQL (via Docker) | Structured storage for reports with proper querying, versioning, and cost tracking |
| LLM provider | Groq (Llama / GPT-OSS family) | Low-latency inference with fast API, free tier available |
| Caching | Redis | Avoid redundant LLM calls for identical queries — cuts cost and latency |
| Observability | LangSmith | Per-agent trace visibility: exact prompts, token counts, latency per call |
 
---
 
## Key Features
 
### Multi-Agent System (LangGraph)
- **4 specialized agents**: Researcher, Critic, Writer, Editor — each with a distinct role and prompt
- **Supervisor pattern**: LangGraph manages routing, state, and conditional edges between agents
- **Self-correction loop**: Critic rejects low-confidence or unsupported claims → Researcher retries with rejection context → bounded to 3 attempts to prevent runaway cost
- **Shared agent memory**: verified findings and rejected claims persist across the run so the Researcher never re-proposes what already failed
- **Agent-to-agent message protocol**: structured `AgentMessage` schema with `sender`, `receiver`, `message_type`, `confidence_score`, and `requires_clarification` flag — agents request clarification instead of guessing
### Custom MCP Servers
Each MCP server is a standalone FastAPI HTTP service — independently deployable, independently testable:
 
| Server | Port | Tools |
|---|---|---|
| Web Search MCP | 8001 | `POST /search` — live Tavily web search |
| Finance MCP | 8002 | `POST /quote`, `POST /overview` — real-time stock data via Alpha Vantage |
| Document Storage MCP | 8003 | `POST /reports`, `GET /reports/{id}`, `GET /reports` — CRUD on PostgreSQL |
| Sandbox Execution MCP | 8004 | `POST /calculate` — safe AST-based math evaluation (no `eval()`) |
 
### AI Reliability Layer
- **Fallback model**: primary model failure auto-retries with a different model — no hard crashes
- **Prompt injection filtering**: web-sourced content is sanitized before entering agent context
- **Pydantic validation**: every agent-to-agent handoff is validated against a strict schema — malformed outputs trigger the self-correction loop
- **Structured JSON output**: all agents use `response_format: json_object` to prevent partial/invalid responses
- **Conversational memory**: agents receive the last 3 Q&A exchanges as context — resolves references like "what is *its* P/E ratio?" correctly
### Real-Time Streaming (WebSockets)
- Streamlit connects to FastAPI via WebSocket (not REST polling)
- Live step-by-step updates: "Researcher searching...", "Critic validating...", etc.
- Human-in-the-loop approval checkpoint: user reviews the verified claim before Writer/Editor run
### Cost & Token Tracking
- Every LLM call records token usage and estimated cost
- Cost/tokens tracked per agent, per run
- Dedicated **Cost Tracker** dashboard page showing total spend across all sessions
---
 
## Tech Stack
 
### AI / Agent Layer
| Technology | Purpose |
|---|---|
| LangGraph | Multi-agent orchestration, state machine, conditional routing |
| Groq API | LLM inference (primary: `openai/gpt-oss-120b`, fallback: `qwen/qwen3.6-27b`) |
| LangSmith | Agent-level tracing, prompt inspection, token tracking |
| Pydantic | Structured output validation across agent handoffs |
| Model Context Protocol (MCP) | Standardized tool interface for agents |
| Tavily API | Real-time web search |
| Alpha Vantage API | Financial data (stock quotes, company overview) |
 
### Backend
| Technology | Purpose |
|---|---|
| FastAPI | REST + WebSocket API server |
| SQLAlchemy | ORM for PostgreSQL |
| PostgreSQL | Persistent report storage |
| Redis | LLM response caching |
| Celery-ready | Background job queue (architecture ready) |
 
### Frontend
| Technology | Purpose |
|---|---|
| Streamlit | Web dashboard with multi-page navigation |
| websocket-client | Real-time WebSocket communication with backend |
 
### DevOps
| Technology | Purpose |
|---|---|
| Docker | Container for every service |
| Docker Compose | Orchestrate all 8 containers locally |
| Python 3.11 | Runtime for all services |
 
---
 
## Repository Structure
 
```
autoresearch-ai/
│
├── apps/
│   ├── backend/                    # FastAPI service
│   │   ├── app/
│   │   │   ├── agents/             # 4 agent definitions
│   │   │   │   ├── researcher.py
│   │   │   │   ├── critic.py
│   │   │   │   ├── writer.py
│   │   │   │   ├── editor.py
│   │   │   │   └── llm_helper.py   # Fallback model logic
│   │   │   ├── graph/
│   │   │   │   ├── orchestrator.py # LangGraph state machine
│   │   │   │   └── state.py        # Shared agent state schema
│   │   │   ├── mcp_clients/        # HTTP clients for each MCP server
│   │   │   ├── protocol/           # Agent message schema (AgentMessage)
│   │   │   ├── schemas/            # Pydantic models (ResearchFinding, etc.)
│   │   │   ├── memory/             # Redis cache layer
│   │   │   ├── security/           # Prompt injection filtering
│   │   │   ├── db/                 # SQLAlchemy models
│   │   │   └── main.py             # FastAPI app + WebSocket endpoint
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── frontend/                   # Streamlit dashboard
│       ├── app.py                  # Main research page
│       ├── pages/
│       │   ├── 1_Report_Viewer.py  # Browse saved reports
│       │   └── 2_Cost_Tracker.py   # Token + cost analytics
│       ├── theme.py                # Custom CSS + pipeline animation
│       ├── .streamlit/
│       │   └── config.toml         # Dark theme config
│       ├── Dockerfile
│       └── requirements.txt
│
├── mcp-servers/                    # 4 standalone MCP HTTP servers
│   ├── web-search-mcp/             # Tavily web search (port 8001)
│   ├── finance-news-mcp/           # Alpha Vantage finance data (port 8002)
│   ├── document-storage-mcp/       # PostgreSQL report storage (port 8003)
│   └── sandbox-exec-mcp/           # Safe math execution (port 8004)
│
├── docs/
│   └── architecture-diagram.svg    # System architecture diagram
│
├── docker-compose.yml              # Run everything with one command
├── .gitignore
└── README.md
```
 
---
 
## Getting Started
 
### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- API keys for: [Groq](https://console.groq.com), [Tavily](https://tavily.com), [Alpha Vantage](https://www.alphavantage.co), [LangSmith](https://smith.langchain.com)
### 1. Clone the repository
```bash
git clone https://github.com/your-username/autoresearch-ai.git
cd autoresearch-ai
```
 
### 2. Set up environment variables
 
**Backend** — create `apps/backend/.env`:
```env
GROQ_API_KEY=your_groq_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=autoresearch-ai
DATABASE_URL=postgresql://postgres:admin@postgres:5432/autoresearch_db
REDIS_HOST=redis
WEB_SEARCH_MCP_URL=http://web-search-mcp:8001
FINANCE_MCP_URL=http://finance-news-mcp:8002
STORAGE_MCP_URL=http://document-storage-mcp:8003
SANDBOX_MCP_URL=http://sandbox-exec-mcp:8004
```
 
**Web Search MCP** — create `mcp-servers/web-search-mcp/.env`:
```env
TAVILY_API_KEY=your_tavily_api_key
```
 
**Finance MCP** — create `mcp-servers/finance-news-mcp/.env`:
```env
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
```
 
**Document Storage MCP** — create `mcp-servers/document-storage-mcp/.env`:
```env
DATABASE_URL=postgresql://postgres:admin@postgres:5432/autoresearch_db
```
 
### 3. Run everything
```bash
docker-compose up --build
```
 
### 4. Open the app
| Service | URL |
|---|---|
| Streamlit Dashboard | http://localhost:8501 |
| FastAPI Backend | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
 
---
 
## How the Self-Correction Loop Works
 
```
User Query
    ↓
Researcher Agent  ──────────────────────────────────────────────┐
    ↓                                                            │
[ResearchFinding validated by Pydantic]                         │
    ↓                                                            │
Critic Agent                                                     │
    ↓              ↓                                             │
 APPROVED       REJECTED ──→ Structured feedback → retry ───────┘
    ↓              ↓                                        (max 3x)
  Writer         Max retries → Human-in-loop escalation
    ↓
  Editor
    ↓
Final Report → Saved to PostgreSQL
```
 
---
 
## Agent Message Protocol
 
Every agent-to-agent handoff uses a structured `AgentMessage`:
 
```python
class AgentMessage(BaseModel):
    sender: str
    receiver: str
    message_type: MessageType  # REQUEST / RESPONSE / REJECTION / CLARIFICATION
    payload: Any
    confidence_score: Optional[float]
    requires_clarification: bool
    clarification_question: Optional[str]
```
 
If a query is ambiguous, the Researcher raises `requires_clarification=True` instead of guessing — preventing hallucinated answers on incomplete queries.
 
---
 
## API Reference
 
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/research` | Run full research pipeline (sync) |
| `WS` | `/ws/research` | Run pipeline with real-time streaming |
| `GET` | `/reports` | List all saved reports |
| `GET` | `/reports/{id}` | Get a single report |
 
---
 
## Environment Variables Reference
 
| Variable | Service | Description |
|---|---|---|
| `GROQ_API_KEY` | Backend | Groq LLM API key |
| `LANGCHAIN_API_KEY` | Backend | LangSmith tracing key |
| `TAVILY_API_KEY` | Web Search MCP | Tavily search API key |
| `ALPHA_VANTAGE_API_KEY` | Finance MCP | Alpha Vantage data API key |
| `DATABASE_URL` | Backend, Storage MCP | PostgreSQL connection string |
| `REDIS_HOST` | Backend | Redis hostname |
| `WEB_SEARCH_MCP_URL` | Backend | Web Search MCP base URL |
| `FINANCE_MCP_URL` | Backend | Finance MCP base URL |
| `STORAGE_MCP_URL` | Backend | Document Storage MCP base URL |
| `SANDBOX_MCP_URL` | Backend | Sandbox MCP base URL |
 
---
 
## Built With
 
This project was designed as a flagship portfolio piece demonstrating:
- Real multi-agent AI orchestration (not a prompt chain)
- Custom MCP server development from scratch
- Production-grade containerization and service architecture
- End-to-end observability (LangSmith + cost tracking)
- Thoughtful UX with human oversight built in
---
 
*Built by [Mubashir ahmed](https://www.linkedin.com/in/mubashir-ahmed-549577263/)*