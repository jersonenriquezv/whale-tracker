# High-Level Design (HLD) - whale-tracker-v0

## 1. Introduction

### 1.1 System Overview
**whale-tracker-v0** is a financial analysis platform that combines Ethereum on-chain data with Smart Money Concepts (SMC) to detect, analyze, and alert on institutional capital movements in real-time.

The system captures large transactions (whale transfers), detects massive liquidation patterns, identifies critical liquidity zones, and provides contextual alerts for ETH intraday trading.

### 1.2 Primary Objective
Provide professional traders, quantitative analysts, and institutional operators with a comprehensive tool that:

- **Detects institutional capital movements** before they significantly impact price
- **Combines on-chain and off-chain data** to generate complete market context
- **Implements SMC concepts** to identify liquidity zones and order blocks
- **Generates automatic alerts** with intelligent anti-spam filters
- **Offers real-time visualization** of liquidity patterns

### 1.3 Target Audience
- **Institutional traders** operating ETH on intraday timeframes
- **Quantitative analysts** requiring structured whale activity data
- **Market makers** needing to anticipate liquidity movements
- **Trading teams** seeking confirmation of SMC patterns

---

## 2. General Architecture

### 2.1 System Components

```
whale-tracker-v0/
├── apps/
│   ├── backend/           # FastAPI REST API server
│   ├── frontend/          # Streamlit dashboard (v0) → Next.js (v1)
│   ├── workers/           # Real-time data processing services
│   └── n8n/              # Workflow automation (Telegram alerts)
├── packages/
│   ├── shared/           # Common utilities, constants, types
│   └── database/         # Models, migrations, queries
├── infra/
│   ├── docker/          # Docker configurations
│   ├── supabase/        # Local Supabase setup
│   └── scripts/         # Deployment and setup scripts
└── docs/
    ├── HLD.md           # This document
    ├── LLD.md           # Low-Level Design
    ├── API.md           # API documentation
    └── SETUP.md         # Environment setup guide
```

### 2.2 Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐
│   Alchemy WS    │    │   Bybit API     │
│  (Ethereum)     │    │ (Liquidations)  │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          ▼                      ▼
┌─────────────────┐    ┌─────────────────┐
│ onchain_worker  │    │  bybit_worker   │
│   (Python)      │    │   (Python)      │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          └──────────┬───────────┘
                     ▼
            ┌─────────────────┐
            │   Supabase      │
            │  (PostgreSQL)   │
            └─────────┬───────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│alert_worker │ │ Backend API │ │aggregator_  │
│             │ │  (FastAPI)  │ │worker       │
└──────┬──────┘ └─────────────┘ └─────────────┘
       │
       ▼
┌─────────────┐    ┌─────────────────┐
│     n8n     │───▶│   Telegram      │
│ (Workflows) │    │   (Alerts)      │
└─────────────┘    └─────────────────┘
       ▲
       │
┌─────────────────┐
│   Frontend      │
│  (Streamlit)    │
└─────────────────┘
```

### 2.3 Component Interactions

**Main data flow:**
1. `onchain_worker` listens to Alchemy WebSockets → detects whale transfers
2. `bybit_worker` consumes Bybit APIs → captures liquidations and order book data
3. Both workers write to Supabase asynchronously
4. `alert_worker` processes triggers from DB → sends events to n8n
5. n8n executes workflows → fires alerts to Telegram
6. `aggregator_worker` consolidates data in 1m/5m timeframes
7. Frontend queries Backend API → visualizes real-time data

---

## 3. Data Flow

### 3.1 On-Chain Flow (Alchemy → Supabase)

```mermaid
sequenceDiagram
    participant A as Alchemy WS
    participant OW as onchain_worker
    participant DB as Supabase
    participant AW as alert_worker
    participant N8N as n8n
    participant TG as Telegram

    A->>OW: Ethereum transaction
    OW->>OW: Filter whale transfers (≥800 ETH)
    OW->>DB: INSERT whale_transactions
    DB->>AW: Trigger on high-priority whale
    AW->>N8N: Send alert payload
    N8N->>TG: Telegram notification
```

### 3.2 Off-Chain Flow (Bybit → Supabase)

```mermaid
sequenceDiagram
    participant B as Bybit API
    participant BW as bybit_worker
    participant DB as Supabase
    participant AGG as aggregator_worker

    B->>BW: Liquidation data + Order book
    BW->>BW: Filter liquidations > $2M
    BW->>DB: INSERT liquidations
    BW->>DB: UPDATE liquidity_zones
    DB->>AGG: Process 1m/5m aggregations
    AGG->>DB: INSERT aggregated_data
```

### 3.3 Processing and Persistence

**Data layers:**
1. **Raw Data Layer**: Real-time transactions and liquidations
2. **Processed Layer**: Filtered and enriched data with SMC context
3. **Aggregated Layer**: Consolidations by timeframe (1m, 5m, 15m)
4. **Alert Layer**: Processed triggers and events for notifications

---

## 4. Services and Responsibilities

### 4.1 `/apps/backend` - FastAPI REST API

**Responsibilities:**
- Expose REST endpoints to query whale transactions
- Serve aggregated liquidity zones data
- Provide alert configuration (v1)
- Authentication and rate limiting

**Technologies:**
- Python 3.11+ with FastAPI
- Pydantic for schema validation
- SQLAlchemy for ORM
- Uvicorn as ASGI server

**Communication:**
- Reads from Supabase (read-only)
- Serves data to Frontend via HTTP REST
- Exposes automatic documentation with Swagger UI

### 4.2 `/apps/workers` - Data Processing Services

#### 4.2.1 `onchain_worker`
**Responsibilities:**
- Persistent connection to Alchemy WebSockets
- Whale transfer filtering (≥300 ETH)
- Priority classification (high: ≥800 ETH, normal: 300-800 ETH)
- Known exchange address exclusion
- Asynchronous writing to Supabase

**Technologies:**
- Python with `websockets` library
- Alchemy SDK for Ethereum
- `asyncpg` for async PostgreSQL

#### 4.2.2 `bybit_worker`
**Responsibilities:**
- Bybit REST API consumption (historical liquidations)
- Bybit WebSocket connection (real-time liquidations)
- Liquidity sweep detection (liquidations > $2M)
- Order book imbalance calculation (>70% one side)
- Liquidity zone updates

**Technologies:**
- Python with `aiohttp` for REST
- `websockets` for real-time
- Official Bybit SDK

#### 4.2.3 `alert_worker`
**Responsibilities:**
- High-priority trigger polling in Supabase
- Anti-spam filter application (max 3 alerts/minute)
- Contextual message formatting
- Payload sending to n8n workflows

**Technologies:**
- Python with `asyncio`
- Rate limiting with Redis (future)
- Integration with n8n REST API

#### 4.2.4 `aggregator_worker`
**Responsibilities:**
- Data consolidation in 1m and 5m timeframes
- Basic SMC metrics calculation
- Transaction clustering for liquidity zones
- Old data cleanup (>30 days)

### 4.3 `/apps/frontend` - Dashboard Interface

**v0 (Streamlit):**
- Read-only dashboard with basic widgets
- Latest whale transfers visualization
- Recent liquidations table
- Basic liquidity zones heatmap
- Real-time metrics

**v1 (Next.js + Tailwind):**
- Interactive interface with alert configuration
- Advanced charts with charting libraries
- User-customizable filters
- Data export and reports

### 4.4 `/apps/n8n` - Workflow Automation

**Responsibilities:**
- Webhook reception from alert_worker
- Message formatting for Telegram
- Telegram API rate limit handling
- Sent alert logging
- Visual workflow configuration

**Technologies:**
- Self-hosted n8n via Docker
- Telegram Bot API integration
- Webhook endpoints for alerts

---

## 5. Database

### 5.1 Supabase Decision

**Advantages:**
- Full PostgreSQL with extensions (TimescaleDB for time-series)
- Real-time subscriptions for frontend
- Built-in authentication and row-level security
- Automatic REST API
- Self-hosted via Docker for full control

### 5.2 MVP Table Schema

#### 5.2.1 `whale_transactions`
```sql
CREATE TABLE whale_transactions (
    id BIGSERIAL PRIMARY KEY,
    tx_hash VARCHAR(66) UNIQUE NOT NULL,
    block_number BIGINT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    from_address VARCHAR(42) NOT NULL,
    to_address VARCHAR(42) NOT NULL,
    value_eth DECIMAL(20,8) NOT NULL,
    value_usd DECIMAL(15,2),
    gas_used BIGINT,
    gas_price BIGINT,
    priority_level VARCHAR(10) NOT NULL, -- 'high', 'normal'
    exchange_involved BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Optimization indexes
CREATE INDEX idx_whale_tx_timestamp ON whale_transactions (timestamp DESC);
CREATE INDEX idx_whale_tx_value ON whale_transactions (value_eth DESC);
CREATE INDEX idx_whale_tx_priority ON whale_transactions (priority_level, timestamp);
```

#### 5.2.2 `liquidations`
```sql
CREATE TABLE liquidations (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL DEFAULT 'ETHUSDT',
    side VARCHAR(10) NOT NULL, -- 'Buy', 'Sell'
    price DECIMAL(15,6) NOT NULL,
    size_usd DECIMAL(15,2) NOT NULL,
    liquidation_type VARCHAR(20), -- 'forced', 'adl'
    exchange VARCHAR(20) DEFAULT 'bybit',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_liquidations_timestamp ON liquidations (timestamp DESC);
CREATE INDEX idx_liquidations_size ON liquidations (size_usd DESC);
```

#### 5.2.3 `liquidity_zones`
```sql
CREATE TABLE liquidity_zones (
    id BIGSERIAL PRIMARY KEY,
    price_level DECIMAL(15,6) NOT NULL,
    size_eth DECIMAL(20,8) NOT NULL,
    size_usd DECIMAL(15,2) NOT NULL,
    zone_type VARCHAR(20), -- 'support', 'resistance', 'cluster'
    timeframe VARCHAR(10) NOT NULL, -- '1m', '5m', '15m'
    strength_score INTEGER DEFAULT 1,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_liquidity_zones_price ON liquidity_zones (price_level);
CREATE INDEX idx_liquidity_zones_timeframe ON liquidity_zones (timeframe, last_updated);
```

#### 5.2.4 `alerts`
```sql
CREATE TABLE alerts (
    id BIGSERIAL PRIMARY KEY,
    alert_type VARCHAR(30) NOT NULL, -- 'whale_transfer', 'liquidation_sweep'
    priority VARCHAR(10) NOT NULL, -- 'high', 'medium', 'low'
    message TEXT NOT NULL,
    related_tx_hash VARCHAR(66),
    related_liquidation_id BIGINT,
    sent_to_telegram BOOLEAN DEFAULT false,
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_alerts_priority ON alerts (priority, created_at DESC);
CREATE INDEX idx_alerts_sent ON alerts (sent_to_telegram, created_at);
```

### 5.3 Migration Strategy

- Use `packages/database/migrations/` with sequentially numbered files
- Pure SQL scripts for maximum compatibility
- Rollback scripts for each migration
- Versioning through `schema_migrations` table

---

## 6. Environment Variables

### 6.1 `.env.example` File

```bash
# Environment
ENV=development # development, staging, production

# Ethereum / Alchemy
ALCHEMY_API_KEY=your_alchemy_api_key
ALCHEMY_WEBHOOK_SECRET=your_webhook_secret
ETHEREUM_NETWORK=mainnet # mainnet, goerli, sepolia

# Bybit
BYBIT_API_KEY=your_bybit_api_key
BYBIT_API_SECRET=your_bybit_api_secret
BYBIT_TESTNET=false # true for testnet

# Database (Supabase)
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
DATABASE_URL=postgresql://postgres:postgres@localhost:54322/postgres

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# n8n
N8N_ENCRYPTION_KEY=your_n8n_encryption_key
N8N_WEBHOOK_URL=http://localhost:5678/webhook/whale-alerts

# API Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_PORT=8501

# Whale Detection Thresholds
WHALE_THRESHOLD_HIGH=800 # ETH
WHALE_THRESHOLD_NORMAL=300 # ETH
LIQUIDATION_THRESHOLD=2000000 # USD
MAX_ALERTS_PER_MINUTE=3

# Data Retention
DATA_RETENTION_DAYS=30
CLEANUP_INTERVAL_HOURS=24

# Logging
LOG_LEVEL=INFO # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json # json, text
```

### 6.2 Variable Validation

Implement validation in `packages/shared/config.py`:
- Verify all API keys are present
- Validate URL and token formats
- Confirm external service accessibility
- Establish safe defaults for development

---

## 7. MVP Roadmap

### 7.1 v0.1 - Foundation (Weeks 1-2)
**Objective:** Basic whale transfer capture and alerts

**Deliverables:**
- ✅ Monorepo structure
- ✅ Docker environment setup
- 🚧 Database schema and initial migrations
- 🚧 Basic `onchain_worker` (whale detection only)
- 🚧 `alert_worker` + n8n integration
- 🚧 Functional Telegram alerts
- 🚧 Backend API with basic endpoints

**Acceptance Criteria:**
- Detects transfers ≥ 800 ETH
- Sends Telegram alerts without spam
- REST API returns last 100 whale transactions

### 7.2 v0.2 - Bybit Integration (Weeks 3-4)
**Objective:** Add off-chain context and liquidations

**Deliverables:**
- 🚧 Complete `bybit_worker` (REST + WebSocket)
- 🚧 Liquidity sweep detection
- 🚧 Populated `liquidations` table
- 🚧 `aggregator_worker` for 1m/5m timeframes
- 🚧 Streamlit frontend with basic widgets

**Acceptance Criteria:**
- Captures liquidations > $2M in real-time
- Dashboard shows latest liquidations
- Basic liquidity zones calculated

### 7.3 v0.3 - Smart Money Concepts (Weeks 5-6)
**Objective:** Implement basic SMC logic

**Deliverables:**
- 🚧 Basic order block detection
- 🚧 Whale transaction clustering
- 🚧 Liquidity zones heatmap
- 🚧 Contextual alerts (whale + liquidation correlation)
- 🚧 Performance optimization

**Acceptance Criteria:**
- Identifies order blocks in 5m timeframe
- Correlates whale movements with liquidations
- Dashboard shows functional heatmap

### 7.4 v1.0 - Production Ready (Weeks 7-8)
**Objective:** Complete and stable system

**Deliverables:**
- 🚧 Migration from Streamlit to Next.js
- 🚧 Customizable alert configuration
- 🚧 Robust rate limiting and error handling
- 🚧 Complete monitoring and logging
- 🚧 Finalized API documentation

**Acceptance Criteria:**
- System handles >1000 transactions/minute
- Uptime >99.5%
- API documented with examples
- Responsive and user-friendly frontend

---

## 8. Future Scalability

### 8.1 Smart Money Concepts Expansion

**v1.1 - Advanced Order Blocks:**
- Multi-timeframe order block detection
- Order block effectiveness backtesting
- Integration with price action patterns

**v1.2 - Fair Value Gaps (FVG):**
- Automatic FVG identification
- Fill rate tracking
- FVG + whale activity correlation alerts

**v1.3 - Delta Order Flow:**
- Real-time order flow analysis
- CVD (Cumulative Volume Delta) tracking
- Institutional footprint detection

### 8.2 Distributed Architecture

**When system grows (>10K transactions/min):**

1. **Microservices:**
   - Separate workers into independent services
   - API Gateway for routing
   - Service mesh for inter-service communication

2. **Message Queuing:**
   - Redis/RabbitMQ for decoupling
   - Event-driven architecture
   - Horizontal worker scaling

3. **Data Pipeline:**
   - Apache Kafka for streaming
   - ClickHouse for analytics
   - Separate OLTP/OLAP databases

### 8.3 Machine Learning Integration

**v2.0 - Predictive Analytics:**
- Whale behavior clustering
- Price movement prediction post-whale transfer
- Liquidity pattern anomaly detection
- Trade risk scoring

### 8.4 Multi-Chain Support

**v2.5 - Cross-Chain Whale Tracking:**
- Bitcoin whale detection
- Polygon/Arbitrum bridge monitoring
- Cross-chain liquidity flow analysis
- Unified dashboard for all chains

---

## 9. Technical Considerations

### 9.1 Performance and Latency

**Latency objectives:**
- Whale detection: <5 seconds from tx confirmation
- Alert delivery: <10 seconds end-to-end
- Dashboard updates: <3 seconds
- API response time: <500ms P99

### 9.2 Error Handling and Resilience

**Strategies:**
- Circuit breakers for external APIs
- Exponential backoff for rate limits
- Dead letter queues for failed alerts
- Health checks and auto-recovery

### 9.3 Security and Compliance

**Security measures:**
- API key rotation policy
- Per-endpoint rate limiting
- Input validation and sanitization
- Audit logs for all operations
- No private key storage

### 9.4 Monitoring and Observability

**Key metrics:**
- Whale detection rate (transactions/minute)
- Alert delivery success rate
- API error rates per endpoint
- Database query performance
- Worker health status

**Tools:**
- Prometheus + Grafana for metrics
- Structured logging (JSON format)
- Error tracking (Sentry)
- Uptime monitoring (Pingdom/UptimeRobot)

---

## 10. Conclusion

This High-Level Design establishes the architectural foundation for **whale-tracker-v0**, a comprehensive whale activity analysis system that combines on-chain and off-chain data with Smart Money concepts.

The modular architecture enables incremental development, starting with core functionality (whale detection + alerts) and gradually expanding toward more sophisticated SMC analysis.

The design prioritizes:
- **Modularity**: Independent and decoupled components
- **Scalability**: Architecture supporting future growth
- **Reliability**: Robust error handling and automatic recovery
- **Performance**: Low-latency optimizations
- **Maintainability**: Clear code and exhaustive documentation

**Next steps:**
1. Review and approve this HLD
2. Generate detailed Low-Level Design (LLD.md)
3. Development environment setup
4. v0.1 implementation according to defined roadmap

---

*Document generated for whale-tracker-v0 - Version 1.0*  
*Last updated: August 2025*