# Whale Tracker v0 - Setup Guide

This guide will help you set up the complete development environment for Whale Tracker v0.

## 📋 Prerequisites

Before starting, ensure you have the following installed:

- **Docker** (v20.10+) and **Docker Compose** (v2.0+)
- **Git** (v2.30+)
- **Node.js** (v18+) - for local development tools
- **Python** (v3.9+) - for local development

### Docker Installation

#### Windows
1. Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)
2. Install and restart your computer
3. Ensure WSL2 is enabled (Docker Desktop will guide you)

#### macOS
1. Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)
2. Install and start Docker Desktop

#### Linux (Ubuntu/Debian)
```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
```

## 🚀 Quick Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd whale-tracker-v0
```

### 2. Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit the .env file with your API keys
# Use your preferred text editor
code .env  # or nano .env, vim .env, etc.
```

### 3. Required API Keys

You'll need to obtain the following API keys and add them to your `.env` file:

#### Supabase
1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Get your project URL and API keys from Settings > API
4. Update in `.env`:
   ```
   SUPABASE_URL=your_project_url
   SUPABASE_ANON_KEY=your_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   ```

#### Alchemy (Ethereum Data)
1. Go to [alchemy.com](https://alchemy.com)
2. Create a new app for Ethereum Mainnet
3. Get your API key and WebSocket URL
4. Update in `.env`:
   ```
   ALCHEMY_API_KEY=your_api_key
   ALCHEMY_WEBSOCKET_URL=wss://eth-mainnet.g.alchemy.com/v2/your_api_key
   ALCHEMY_HTTP_URL=https://eth-mainnet.g.alchemy.com/v2/your_api_key
   ```

#### Bybit (Exchange Data)
1. Go to [bybit.com](https://bybit.com)
2. Create an account and API key
3. Get your API key and secret
4. Update in `.env`:
   ```
   BYBIT_API_KEY=your_api_key
   BYBIT_SECRET_KEY=your_secret_key
   ```

#### Telegram (Alerts)
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot and get the token
3. Get your chat ID (you can use [@userinfobot](https://t.me/userinfobot))
4. Update in `.env`:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

### 4. Start the Services

```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 5. Verify Installation

Once all services are running, you can access:

- **Frontend (Streamlit)**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Supabase Studio**: http://localhost:54321
- **N8N Workflows**: http://localhost:5678
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## 🔧 Development Setup

### Local Development

For local development without Docker:

#### Backend (Python/FastAPI)
```bash
cd apps/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend (Streamlit)
```bash
cd apps/frontend
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

#### Workers
```bash
cd apps/workers
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Database Management

#### Supabase Local Development
```bash
# Access Supabase CLI
docker-compose exec supabase supabase

# Run migrations
docker-compose exec supabase supabase db reset

# Generate types
docker-compose exec supabase supabase gen types typescript --local > packages/shared/types.ts
```

#### Direct Database Access
```bash
# Connect to PostgreSQL
docker-compose exec supabase psql -U postgres -d postgres

# Or use a GUI tool like pgAdmin or DBeaver
# Host: localhost
# Port: 54330
# Database: postgres
# Username: postgres
# Password: postgres
```

## 🐛 Troubleshooting

### Common Issues

#### Port Conflicts
If you get port conflicts, check what's running on the required ports:
```bash
# Windows
netstat -ano | findstr :8000

# macOS/Linux
lsof -i :8000
```

#### Docker Issues
```bash
# Reset Docker
docker-compose down -v
docker system prune -a
docker-compose up -d
```

#### Supabase Issues
```bash
# Reset Supabase
docker-compose down supabase
docker volume rm whale-tracker-v0_supabase_data
docker-compose up -d supabase
```

#### Memory Issues
If you encounter memory issues, increase Docker resources:
1. Open Docker Desktop
2. Go to Settings > Resources
3. Increase memory allocation (recommended: 8GB+)

### Service Health Checks

```bash
# Check all services
docker-compose ps

# Check specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs workers
docker-compose logs n8n

# Check service health
curl http://localhost:8000/health
curl http://localhost:8501
```

## 📁 Project Structure

```
whale-tracker-v0/
├── apps/
│   ├── backend/          # FastAPI application
│   ├── frontend/         # Streamlit dashboard
│   ├── workers/          # Data ingestion services
│   └── n8n/             # Workflow automation
├── packages/
│   ├── shared/          # Common utilities
│   └── database/        # Database models & migrations
├── infra/
│   ├── docker/          # Docker configurations
│   └── scripts/         # Setup scripts
├── docs/                # Documentation
├── docker-compose.yml   # Main orchestration
├── env.example          # Environment template
└── README.md           # Project overview
```

## 🔄 Next Steps

After successful setup:

1. **Review Architecture**: Read [HLD.md](HLD.md) for system overview
2. **Database Schema**: Design your database schema in `packages/database/`
3. **API Development**: Start building endpoints in `apps/backend/`
4. **Frontend**: Develop the Streamlit dashboard in `apps/frontend/`
5. **Data Ingestion**: Implement workers in `apps/workers/`
6. **Workflows**: Set up N8N workflows in `apps/n8n/`

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review service logs: `docker-compose logs -f`
3. Verify environment variables are correctly set
4. Ensure all prerequisites are installed
5. Check Docker resources allocation

## 🔐 Security Notes

- Never commit `.env` files to version control
- Use strong passwords for all services
- Regularly update API keys and tokens
- Monitor service logs for suspicious activity
- Keep Docker images updated
