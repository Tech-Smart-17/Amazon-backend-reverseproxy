# Amazon Backend System

[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0%20Async-orange.svg)](https://www.sqlalchemy.org/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Search-purple.svg)](https://www.trychroma.com/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://www.docker.com/)

A complete, production-ready, enterprise-grade backend system replicating Amazon's core services, built with **FastAPI**, **SQLAlchemy 2.0 Async**, **Motor (MongoDB)**, **Redis**, and **ChromaDB Vector Store**.

---

## 🌟 Key Architecture & Features

- **Authentication & Security**: JWT Access/Refresh tokens, bcrypt password hashing, OAuth2 Bearer, Role-Based Access Control (RBAC: Admin, Customer, Vendor, Manager).
- **User Management**: Profile CRUD, Avatar upload, Account Deactivation, Password updates.
- **Product Catalog**: Categories, Subcategories, Brands, Discounts, SKU tracking, Pagination, Sorting, Filtering.
- **Semantic Search Engine**: ChromaDB vector similarity embeddings search, Hybrid keyword search, Autocomplete suggestions, Trending items.
- **LangChain AI Features**: Local sentence-transformer embeddings, PDF-grounded RAG answers, a read-only admin SQL agent, and an authenticated STT/LLM/TTS voice shopping assistant.
- **Inventory & Warehouse**: Multi-warehouse stock management, Stock reservation during checkout, Low-stock alerts.
- **Cart & Wishlist**: MongoDB document-backed dynamic shopping cart, Move to Cart from Wishlist.
- **Address Management**: Multiple shipping addresses per user with default flags.
- **Orders & Tracking**: Checkout pipeline, Stock reservation, Status transitions (`pending` -> `processing` -> `shipped` -> `delivered` / `cancelled`), Live tracking timeline.
- **Payment Processing**: Dummy Payment Gateway supporting UPI, Credit Card, Debit Card, Cash On Delivery (COD), Refunds.
- **PDF Invoice Generation**: Automatic PDF invoice generation using ReportLab stored in `/uploads/invoice/`.
- **Recommendation Engine**: Vector-based similar product discovery and frequently bought together items.
- **Notifications & Audit**: MongoDB notifications feed, Unread count, Audit logging.
- **Admin & Analytics**: Dashboard metrics (total revenue, total orders, low stock counters), User management, Warehouse creation.
- **Resilient Multi-DB Manager**: Runs out-of-the-box using SQLite, In-Memory ChromaDB, and resilient Mongo/Redis failover layers, with full support for PostgreSQL, real MongoDB, and Redis in production.

---

## 📁 Directory Structure

```
Amazon_Backend/
├── app/
│   ├── main.py                # FastAPI Application Entrypoint & Middleware Stack
│   ├── config.py              # Pydantic BaseSettings Environment Configuration
│   ├── database.py            # Multi-DB Manager (SQL, Mongo, Redis, ChromaDB)
│   ├── dependencies.py        # Dependency Injectors (DB, Current User, RBAC, Services)
│   ├── exceptions.py          # Custom Exceptions & Exception Handlers
│   ├── middleware.py          # Logging, Correlation ID, Execution Timer, Rate Limiting
│   ├── security.py            # Hashing (bcrypt) & JWT Token Utils
│   ├── utils.py               # ReportLab PDF Invoice Generator & File Utils
│   ├── constants.py           # App Enums (Roles, Statuses, Payment Methods)
│   ├── models/
│   │   ├── sql_models.py      # SQLAlchemy 2.0 Async Entity Models
│   │   └── mongo_models.py    # MongoDB Pydantic Document Schemas
│   ├── schemas/
│   │   └── all_schemas.py     # Pydantic v2 DTO Request/Response Schemas
│   ├── repositories/          # Data Access Layer (Repository Pattern)
│   │   ├── base_repository.py
│   │   ├── user_repository.py
│   │   ├── product_repository.py
│   │   ├── order_repository.py
│   │   ├── cart_repository.py
│   │   ├── wishlist_repository.py
│   │   ├── search_repository.py
│   │   └── notification_repository.py
│   ├── services/              # Business Logic Layer
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── product_service.py
│   │   ├── search_service.py
│   │   ├── knowledge_service.py
│   │   ├── sql_agent_service.py
│   │   ├── voice_agent_service.py
│   │   └── langchain_runtime.py
│   │   ├── cart_service.py
│   │   ├── order_service.py
│   │   ├── payment_service.py
│   │   ├── invoice_service.py
│   │   └── recommendation_service.py
│   └── routers/               # API Endpoints (/api/v1/...)
│       ├── auth_router.py
│       ├── users_router.py
│       ├── products_router.py
│       ├── categories_router.py
│       ├── search_router.py
│       ├── ai_router.py
│       ├── voice_router.py
│       ├── cart_router.py
│       ├── orders_router.py
│       ├── payments_router.py
│       ├── invoices_router.py
│       ├── recommendations_router.py
│       └── analytics_router.py
├── seed/
│   └── seed_data.py           # Initial Data Seeder (Admin User, Catalog, Warehouses)
├── tests/                     # Pytest Async Integration Suite
├── docs/                      # ER Diagram, API Docs & Postman Collection
├── uploads/                   # Local Filesystem Storage (Invoices, Images, Embeddings)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.13+ installed.

### 2. Environment Setup

```bash
# Navigate to project directory
cd Amazon_Backend

# Create Python Virtual Environment
cd Amazon_Backend

# Activate Virtual Environment
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install Dependencies
pip install -r requirements.txt
```

### 3. Seed Database & Run Server

```bash
# Seed default data (Creates Admin user: admin@amazon.com / Admin@123456)
python -m seed.seed_data

# Build the semantic index for products already in the SQL database
python -m scripts.reindex_products

# Run FastAPI Development Server
uvicorn app.main:app --reload
```

Server will start at `http://127.0.0.1:8000`.

The first product search or index operation downloads the configured local embedding model. Product create/update requests index their product automatically; run the reindex command after upgrading from the older hand-built vectors.

## LangChain AI endpoints

Copy `.env.example` to `.env` and configure `GOOGLE_API_KEY` for chat and agent answers. The embedding model runs locally. PDF Q&A uses a Deep Agent: it retrieves PDF chunks, writes them to a per-request filesystem backend, and delegates chunk analysis to a subagent. The PDF and SQL endpoints are:

- `POST /api/v1/ai/knowledge/pdfs` — index a PDF; administrator only.
- `POST /api/v1/ai/knowledge/ask` — answer from indexed PDF passages with source/page citations; authenticated.
- `POST /api/v1/ai/sql/ask` — ask about catalog and inventory data; administrator only. The agent sees only `products`, `categories`, and `inventory`, and the SQL connection is set read-only.

The voice endpoint is `WS /api/v1/voice/ws?token=<access-token>`. Set `ASSEMBLYAI_API_KEY` and `CARTESIA_API_KEY` to enable it. Send 16 kHz mono PCM16 audio as binary frames, followed by `{"type":"end_turn"}`. Agent text streams as JSON `agent_chunk` messages; synthesized audio arrives as 24 kHz PCM16 binary frames between `audio_start` and `audio_end` events. The client should send live chunks of 50–1000 ms.

---

## 🔗 Swagger API Documentation & ReDoc

- **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 Running Pytest Test Suite

```bash
pytest -v tests/
```

---

## 🐳 Running with Docker & Docker Compose

To deploy with PostgreSQL, MongoDB, Redis, and FastAPI in Docker:

```bash
docker-compose up --build
```

### Nginx reverse proxy

Nginx is the public entry point in the Docker Compose setup. A reverse proxy receives a browser or client request and forwards it to the application server:

```text
Browser / API client  ->  Nginx (:80)  ->  FastAPI web container (:8000)
                                             -> PostgreSQL / MongoDB / Redis
```

The Compose service named `nginx` publishes port `80` and uses [`nginx/reverse-proxy.conf`](nginx/reverse-proxy.conf). That configuration forwards requests to `http://web:8000`; Docker Compose resolves `web` to the FastAPI container. It also forwards the original host, client IP, and request protocol headers.

server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://web:8000;

        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}



With the Compose stack running, open the API through Nginx:

- API: `http://localhost/`
- Swagger UI: `http://localhost/docs`
- ReDoc: `http://localhost/redoc`

The FastAPI container also publishes port `8000`, so `http://localhost:8000/docs` reaches it directly. In a deployed setup, Nginx gives you one front door for the API and can be extended for a domain, HTTPS/TLS, request limits, or load balancing. The current configuration only proxies HTTP requests; the voice assistant's WebSocket route needs WebSocket upgrade headers configured in Nginx before using that route through the proxy.

Useful Compose commands:

```bash
docker compose ps
docker compose logs -f nginx web
docker compose down
```

---

## 📜 Default Credentials

| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@amazon.com` | `Admin@123456` |
