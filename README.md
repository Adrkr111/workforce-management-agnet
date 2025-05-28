# 🧠 Conversational Workforce Simulation System

This project implements an enterprise-grade conversational simulation platform using:
- **Chainlit** for the conversational UI
- **Microsoft AutoGen** for multi-agent orchestration
- **Google Gemini** for NLU (intent/entity extraction)
- **FastAPI** for backend logic execution
- **DuckDB** for persistent context and historical data

Designed specifically for **banking operations**, the system empowers analysts to forecast, simulate, and evaluate workforce needs using natural language.

---

## 📁 Directory Structure

```bash
project_root/
│
├── main.py                       # Chainlit entry point
├── README.md                    # Project documentation
│
├── agents/                      # All agent definitions
│   ├── main_agent.py            # Main AutoGen manager and session router
│   ├── sub_agents.py            # Sub-agents for FTE, SLA, backlog, volume
│   ├── explanation_agent.py     # Generates user-facing summaries
│   ├── clarifier_agent.py       # Handles missing input clarifications
│   └── tools.py                 # REST API function bindings
│
├── backend/                     # FastAPI backend
│   └── fastapi_app.py           # Business logic for forecasts and metrics
│
├── storage/                     # Context persistence engine
│   └── context_store.py         # User session & forecast history using DuckDB
│
├── skills/                      # LLM-related utilities
│   └── extractor.py             # Prompt-engineered intent/entity parsing
│
└── simulation_context.duckdb    # DuckDB database file (created at runtime)
```

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install chainlit autogen fastapi pydantic uvicorn requests google-generativeai duckdb
```

### 2. Set Google Gemini API Key
```bash
export GOOGLE_API_KEY="<your_key_here>"
```

### 3. Start Backend Server
```bash
uvicorn backend.fastapi_app:app --reload
```

### 4. Launch Chainlit UI
```bash
chainlit run main.py
```

---

## ✅ Supported Scenarios

- **FTE Estimation**: Based on volume, AHT, and work hours
- **SLA Breach Risk**: Compares required vs available staff
- **Backlog Projection**: Simulates overflow from increased demand
- **Volume Forecasting**: Predicts ticket trends using business factors

Each simulation is accompanied by:
- Business rationale
- Impact statement
- Suggested next steps

---

## 📦 Tech Stack
- `Chainlit` — Conversational UI
- `AutoGen` — Modular agent framework
- `Google Gemini` — Prompt-driven NLU
- `FastAPI` — Simulation microservices
- `DuckDB` — Lightweight analytical DB

---

## 🔐 Security
- Context is session-isolated by user ID
- All inputs and outputs are logged to DuckDB

---

## 📈 Future Enhancements
- Memory-enabled forecasting via embeddings
- Confidence scoring + risk alerting
- Role-based access with RBAC

---

## 👨‍💻 Contributors
- Architect: You 🧠
- Engineered by: AutoGen + Gemini + Chainlit + FastAPI
