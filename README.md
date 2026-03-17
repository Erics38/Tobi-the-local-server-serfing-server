# 🍔 Restaurant AI — The Common House

An AI-powered restaurant ordering system featuring **Tobi**, a surfer-style chatbot
assistant with full menu awareness and order management.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.118+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![CI Status](https://github.com/Erics38/restaurant-ai-chatbot/actions/workflows/ci.yml/badge.svg)](https://github.com/Erics38/restaurant-ai-chatbot/actions/workflows/ci.yml)
[![Docker Build](https://github.com/Erics38/restaurant-ai-chatbot/actions/workflows/docker.yml/badge.svg)](https://github.com/Erics38/restaurant-ai-chatbot/actions/workflows/docker.yml)

---

## 🎯 Relevance to SaaS & Technical Roles

This project was built to demonstrate the technical patterns that underpin
modern SaaS platforms — specifically the tooling a Solutions Engineer or
Onboarding Specialist needs to understand deeply:

- **Conversational AI integration** — mirrors the in-app chatbot flows used by
  Intercom, Drift, and Help Scout to guide customers through onboarding steps
- **Self-documented REST API (Swagger/ReDoc)** — the same pattern SaaS platforms
  expose to enterprise customers for self-serve integration work
- **Environment-based configuration (`.env`)** — replicates real multi-tenant
  SaaS setup patterns that customers encounter during implementation and go-live
- **Docker containerization** — understanding this helps technical onboarding
  teams guide customers through deployment, infrastructure config, and upgrades
- **CI/CD pipeline** — demonstrates awareness of the software delivery lifecycle
  that underpins every SaaS product a customer is onboarding onto

---

## ✨ Features

- 🤖 **Menu-Aware AI Chatbot** — Tobi understands food categories, ingredients, and recommends items
- 🧠 **AI-Powered by Default** — Uses local Phi-2 model for natural language understanding (2–10s)
- ⚡ **Template Fallback** — Instant responses (<10ms) if AI unavailable or in development mode
- 🍽️ **Full Menu System** — Starters, Mains, Desserts, and Drinks
- 📋 **Order Management** — Create and track orders with presidential birth year order numbers
- 🎯 **Magic Password** — VIP treatment for special customers ("i'm on yelp")
- 💾 **SQLite Database** — Persistent order storage
- 🔒 **Production Ready** — Proper logging, health checks, and error handling
- 🐳 **Docker Support** — One-command deployment
- 🔧 **Environment-Based Config** — Easy configuration via `.env` files
- 💰 **Zero API Costs** — Run AI models locally with no external dependencies

---

## 🏗️ Infrastructure Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User's Browser                          │
│                  http://localhost:8000/static/                  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/WebSocket
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Restaurant AI (FastAPI)                      │
│                         Port 8000                               │
├─────────────────────────────────────────────────────────────────┤
│  Endpoints:                                                     │
│  • GET  /                    - Root/Health                      │
│  • GET  /menu                - Menu data                        │
│  • POST /chat                - Chat with Tobi                   │
│  • POST /order               - Create order                     │
│  • GET  /order/{id}          - Get order status                 │
└────────────┬───────────────────────────────┬────────────────────┘
             │                               │
             ▼                               ▼
┌──────────────────────┐    ┌────────────────────────────────────┐
│   SQLite Database    │    │   llama-server (Optional)          │
│   (data/orders.db)   │    │   Port 8080                        │
└──────────────────────┘    └────────────────────────────────────┘
```

---

## 🚀 Quick Start

**Prerequisites:** Docker + 1.7 GB Phi-2 model

### Step 1: Download Model (one-time setup)

```bash
mkdir -p models
curl -L -o models/phi-2.Q4_K_M.gguf \
  https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf
```

### Step 2: Start with Docker

```bash
# Windows:
start.bat

# macOS/Linux:
chmod +x start.sh && ./start.sh

# Or manually:
docker-compose up --build -d
```

**Access:** http://localhost:8000/static/restaurant_chat.html

### Optional: Fast Template Mode (No AI)

```bash
USE_LOCAL_AI=false docker-compose up -d
```

---

## 📁 Project Structure

```
restaurant-ai/
├── app/
│   ├── main.py          # FastAPI application & endpoints
│   ├── config.py        # Environment-based configuration
│   ├── models.py        # Pydantic models for validation
│   ├── database.py      # SQLite database operations
│   ├── tobi_ai.py       # AI chatbot logic (menu-aware)
│   └── menu_data.py     # Restaurant menu data
├── static/
│   └── restaurant_chat.html  # Web interface
├── tests/               # Unit tests
├── .env.example         # Environment variable template
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🔧 Configuration

Copy `.env.example` to `.env` and update as needed:

```bash
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
DATABASE_URL=sqlite:///./data/orders.db
RESTAURANT_NAME=The Common House
ENABLE_MAGIC_PASSWORD=True
MAGIC_PASSWORD=i'm on yelp
SECRET_KEY=your-secret-key-here
LOG_LEVEL=INFO
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/` | Root endpoint with basic info |
| `GET`  | `/health` | Health check for monitoring |
| `GET`  | `/menu` | Get full restaurant menu |
| `POST` | `/chat` | Chat with Tobi AI |
| `POST` | `/order` | Create a new order |
| `GET`  | `/order/{order_number}` | Get order details |

- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

---

## 💬 Chat Examples

```bash
# Ask about menu items
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What burgers do you have?"}'

# Get a recommendation
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What do you recommend?"}'
```

---

## 🧪 Testing

```bash
pytest
black app/
flake8 app/
mypy app/
```

---

## 🐳 Docker Commands

```bash
docker-compose up --build    # Build and start
docker-compose up -d         # Run in background
docker-compose logs -f app   # View logs
docker-compose down          # Stop
```

---

## 📚 Documentation

- **[SETUP.md](SETUP.md)** — Complete setup guide for new users
- **[DEPLOYMENT.md](DEPLOYMENT.md)** — Production deployment guide
- **[CICD.md](CICD.md)** — CI/CD pipeline documentation
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** — Upgrading from previous versions
- **[DOCKER_QUICK_START.md](DOCKER_QUICK_START.md)** — Fast Docker reference

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

---

## 🙋 Support

- **Issues:** https://github.com/Erics38/restaurant-ai-chatbot/issues
- **API Docs:** http://localhost:8000/api/docs (when running locally)

---

**Built with FastAPI, Python, and surfer vibes 🏄**
