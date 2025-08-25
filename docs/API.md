# Whale Tracker v0 - API Documentation

## 📋 Overview

This document will contain the complete API specification for Whale Tracker v0, including all endpoints, request/response schemas, and authentication details.

## 🔄 Status

**Status**: 🚧 In Development  
**Last Updated**: [Date]  
**Version**: 0.1.0

## 🌐 Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.whaletracker.com` (TBD)

## 🔐 Authentication

### Authentication Methods
- [ ] JWT Token Authentication
- [ ] API Key Authentication
- [ ] OAuth 2.0 (Supabase Auth)

### Headers
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

## 📚 API Endpoints

### 1. Health & Status
- [ ] `GET /health` - Service health check
- [ ] `GET /status` - System status and metrics

### 2. Authentication
- [ ] `POST /auth/login` - User login
- [ ] `POST /auth/logout` - User logout
- [ ] `POST /auth/refresh` - Refresh JWT token
- [ ] `GET /auth/profile` - Get user profile

### 3. Whale Transactions
- [ ] `GET /whales/transactions` - Get whale transactions
- [ ] `GET /whales/transactions/{id}` - Get specific transaction
- [ ] `GET /whales/addresses/{address}` - Get address history
- [ ] `POST /whales/transactions/search` - Search transactions

### 4. Liquidity Zones
- [ ] `GET /liquidity/zones` - Get liquidity zones
- [ ] `GET /liquidity/zones/{id}` - Get specific zone
- [ ] `POST /liquidity/zones/search` - Search zones
- [ ] `GET /liquidity/heatmap` - Get heatmap data

### 5. Market Data
- [ ] `GET /market/orderbook` - Get order book
- [ ] `GET /market/trades` - Get recent trades
- [ ] `GET /market/liquidations` - Get liquidation events
- [ ] `GET /market/analytics` - Get market analytics

### 6. Smart Money Concepts (SMC)
- [ ] `GET /smc/patterns` - Get SMC patterns
- [ ] `GET /smc/patterns/{id}` - Get specific pattern
- [ ] `POST /smc/patterns/search` - Search patterns
- [ ] `GET /smc/analysis` - Get SMC analysis

### 7. Alerts
- [ ] `GET /alerts` - Get user alerts
- [ ] `POST /alerts` - Create new alert
- [ ] `PUT /alerts/{id}` - Update alert
- [ ] `DELETE /alerts/{id}` - Delete alert
- [ ] `GET /alerts/history` - Get alert history

### 8. Analytics
- [ ] `GET /analytics/whales` - Whale analytics
- [ ] `GET /analytics/liquidity` - Liquidity analytics
- [ ] `GET /analytics/correlation` - Data correlation analysis
- [ ] `GET /analytics/predictions` - Market predictions

### 9. System Management
- [ ] `GET /admin/status` - Admin system status
- [ ] `GET /admin/metrics` - System metrics
- [ ] `POST /admin/maintenance` - Trigger maintenance mode

## 📊 Data Models

### Common Models
- [ ] Error Response
- [ ] Pagination
- [ ] Timestamp
- [ ] Address

### Whale Transaction Model
```json
{
  "id": "string",
  "hash": "string",
  "from_address": "string",
  "to_address": "string",
  "value": "string",
  "value_usd": "number",
  "gas_price": "string",
  "block_number": "number",
  "timestamp": "string",
  "status": "string",
  "whale_score": "number"
}
```

### Liquidity Zone Model
```json
{
  "id": "string",
  "price_level": "number",
  "size": "number",
  "side": "string",
  "strength": "number",
  "created_at": "string",
  "updated_at": "string"
}
```

### Alert Model
```json
{
  "id": "string",
  "user_id": "string",
  "type": "string",
  "conditions": "object",
  "enabled": "boolean",
  "created_at": "string",
  "updated_at": "string"
}
```

## 🔄 WebSocket Endpoints

### Real-time Data
- [ ] `ws://localhost:8000/ws/whales` - Whale transaction feed
- [ ] `ws://localhost:8000/ws/liquidity` - Liquidity zone updates
- [ ] `ws://localhost:8000/ws/market` - Market data feed
- [ ] `ws://localhost:8000/ws/alerts` - Alert notifications

## 📈 Rate Limiting

- **Standard**: 1000 requests per hour
- **Premium**: 10000 requests per hour
- **WebSocket**: 100 connections per user

## 🚨 Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

## 📝 Examples

### Authentication Example
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Get Whale Transactions
```bash
curl -X GET "http://localhost:8000/whales/transactions?limit=10&offset=0" \
  -H "Authorization: Bearer <jwt_token>"
```

### WebSocket Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/whales');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Whale transaction:', data);
};
```

## 🔄 Versioning

- **Current Version**: v1
- **Version Header**: `X-API-Version: 1`
- **Deprecation Policy**: 6 months notice for breaking changes

## 📚 SDKs & Libraries

- [ ] Python SDK
- [ ] JavaScript/TypeScript SDK
- [ ] React Hooks
- [ ] Postman Collection

## 🔗 Related Documentation

- [Setup Guide](SETUP.md)
- [High-Level Design](HLD.md)
- [Low-Level Design](LLD.md)

---

**Next Steps**: Implement API endpoints and populate with actual specifications.
