# Whale Tracker v0

A comprehensive tool that combines on-chain data, exchange order book data, and Smart Money Concepts (SMC) to track whale transactions, liquidity zones, and generate contextual trading insights for ETH.

## 🎯 Project Goals

- Track whale transactions on Ethereum
- Monitor liquidity zones and order book dynamics
- Generate contextual trading insights
- Provide real-time alerts via Telegram
- Focus on ETH intraday trading patterns

## 🏗️ Architecture

```
apps/
├── backend/          # Python + FastAPI API server
├── frontend/         # Streamlit dashboard (v0)
├── workers/          # Real-time data ingestion & processing
└── n8n/             # Workflow automation for alerts

packages/
├── shared/          # Common utilities & types
└── database/        # Database models & migrations

infra/
├── docker/          # Docker configurations
└── scripts/         # Setup & deployment scripts

docs/
├── SETUP.md         # Environment setup guide
├── HLD.md           # High-Level Design
├── LLD.md           # Low-Level Design
└── API.md           # API documentation
```

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd whale-tracker-v0
   ```

2. **Setup environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Access services**
   - Frontend: http://localhost:8501
   - API: http://localhost:8000
   - Supabase: http://localhost:54321
   - N8N: http://localhost:5678

## 📚 Documentation

- [Setup Guide](docs/SETUP.md) - Complete environment setup
- [High-Level Design](docs/HLD.md) - System architecture overview
- [Low-Level Design](docs/LLD.md) - Technical implementation details
- [API Documentation](docs/API.md) - API endpoints & schemas

## 🛠️ Tech Stack

- **Backend**: Python + FastAPI
- **Frontend**: Streamlit (v0), Next.js (future)
- **Database**: Supabase (PostgreSQL) via Docker
- **Data Sources**: 
  - Alchemy WebSockets (Ethereum on-chain data)
  - Bybit REST + WebSocket (order book, liquidations)
- **Alerts**: Telegram Bot API via N8N
- **Infrastructure**: Docker + docker-compose

## 📝 Development Status

- ✅ Project structure setup
- ✅ Docker environment configuration
- 🔄 Database schema design (pending)
- 🔄 API development (pending)
- 🔄 Frontend development (pending)
- 🔄 Data ingestion services (pending)
- 🔄 Alert system (pending)

## 🤝 Contributing

This is a single-user project for now. Future collaboration guidelines will be added as the project evolves.

## 📄 License

Private project - All rights reserved.
