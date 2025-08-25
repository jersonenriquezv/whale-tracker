# Database Package - Whale Tracker v0

This package contains database models, migrations, and database-related utilities for the Whale Tracker v0 application.

## 📋 Overview

The database package provides the data layer for the Whale Tracker system, including PostgreSQL models, migration scripts, and database utilities. It uses Supabase as the database provider with SQLAlchemy as the ORM.

## 🏗️ Structure

```
packages/database/
├── models/          # SQLAlchemy models
├── migrations/      # Database migration scripts
├── schemas/         # Pydantic schemas for API
├── utils/           # Database utilities
└── config/          # Database configuration
```

## 📚 Components

### Models
- **WhaleTransaction**: Ethereum whale transaction data
- **LiquidityZone**: Order book liquidity zone data
- **SMCPattern**: Smart Money Concept pattern data
- **Alert**: User alert configurations
- **MarketData**: Real-time market data
- **User**: User account and preferences

### Migrations
- **Initial Schema**: Base table creation
- **Indexes**: Performance optimization indexes
- **Constraints**: Data integrity constraints
- **Views**: Complex query views

### Schemas
- **API Schemas**: Request/response validation
- **Database Schemas**: Internal data structures
- **Validation Schemas**: Input validation rules

### Utilities
- **Connection Management**: Database connection handling
- **Query Builders**: Complex query construction
- **Data Transformers**: Data format conversion
- **Migration Helpers**: Migration script utilities

## 🚀 Setup

### Prerequisites
- PostgreSQL database (via Supabase)
- Python 3.9+
- SQLAlchemy 2.0+
- Alembic for migrations

### Installation
```bash
# From the root directory
pip install -e packages/database
```

### Environment Variables
```bash
# Database connection
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_DB_PASSWORD=your_db_password

# Database configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

## 📊 Database Schema

### Core Tables

#### whale_transactions
```sql
CREATE TABLE whale_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hash VARCHAR(66) NOT NULL UNIQUE,
    from_address VARCHAR(42) NOT NULL,
    to_address VARCHAR(42) NOT NULL,
    value_eth DECIMAL(30,18) NOT NULL,
    value_usd DECIMAL(20,2),
    gas_price BIGINT NOT NULL,
    gas_used BIGINT,
    block_number BIGINT NOT NULL,
    block_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    whale_score DECIMAL(5,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### liquidity_zones
```sql
CREATE TABLE liquidity_zones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    price_level DECIMAL(20,8) NOT NULL,
    size DECIMAL(30,18) NOT NULL,
    side VARCHAR(4) NOT NULL CHECK (side IN ('bid', 'ask')),
    strength DECIMAL(5,4),
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### smc_patterns
```sql
CREATE TABLE smc_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_type VARCHAR(50) NOT NULL,
    confidence_score DECIMAL(5,4),
    price_level DECIMAL(20,8) NOT NULL,
    time_frame VARCHAR(10) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### alerts
```sql
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    alert_type VARCHAR(50) NOT NULL,
    conditions JSONB NOT NULL,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Indexes
```sql
-- Performance indexes
CREATE INDEX idx_whale_transactions_hash ON whale_transactions(hash);
CREATE INDEX idx_whale_transactions_block_number ON whale_transactions(block_number);
CREATE INDEX idx_whale_transactions_timestamp ON whale_transactions(block_timestamp);
CREATE INDEX idx_whale_transactions_value_eth ON whale_transactions(value_eth);
CREATE INDEX idx_whale_transactions_whale_score ON whale_transactions(whale_score);

CREATE INDEX idx_liquidity_zones_price_level ON liquidity_zones(price_level);
CREATE INDEX idx_liquidity_zones_side ON liquidity_zones(side);
CREATE INDEX idx_liquidity_zones_symbol ON liquidity_zones(symbol);

CREATE INDEX idx_smc_patterns_pattern_type ON smc_patterns(pattern_type);
CREATE INDEX idx_smc_patterns_price_level ON smc_patterns(price_level);
CREATE INDEX idx_smc_patterns_status ON smc_patterns(status);
```

## 🔄 Migrations

### Running Migrations
```bash
# Apply all pending migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Rollback migration
alembic downgrade -1

# Check migration status
alembic current
alembic history
```

### Migration Best Practices
1. **Always backup before migrations**
2. **Test migrations on staging first**
3. **Use descriptive migration names**
4. **Include rollback scripts**
5. **Review generated SQL**

## 📝 Usage Examples

### Model Usage
```python
from database.models import WhaleTransaction, LiquidityZone
from database.utils import get_db_session

# Create new whale transaction
async with get_db_session() as session:
    transaction = WhaleTransaction(
        hash="0x123...",
        from_address="0xabc...",
        to_address="0xdef...",
        value_eth=1000.0,
        value_usd=2000000.0,
        gas_price=20000000000,
        block_number=18000000,
        block_timestamp=datetime.utcnow(),
        whale_score=0.85
    )
    session.add(transaction)
    await session.commit()
```

### Query Examples
```python
# Get recent whale transactions
async with get_db_session() as session:
    transactions = await session.execute(
        select(WhaleTransaction)
        .where(WhaleTransaction.value_eth >= 100)
        .order_by(WhaleTransaction.block_timestamp.desc())
        .limit(10)
    )
    return transactions.scalars().all()

# Get liquidity zones for price range
async with get_db_session() as session:
    zones = await session.execute(
        select(LiquidityZone)
        .where(
            LiquidityZone.price_level.between(1900, 2100),
            LiquidityZone.side == 'bid'
        )
        .order_by(LiquidityZone.price_level)
    )
    return zones.scalars().all()
```

## 🔧 Development

### Adding New Models
1. Create model in `models/` directory
2. Add to `__init__.py` exports
3. Create migration for table
4. Add Pydantic schema
5. Add tests

### Adding New Migrations
1. Use Alembic to generate migration
2. Review generated SQL
3. Add custom logic if needed
4. Test migration on sample data
5. Update documentation

### Database Utilities
```python
from database.utils import (
    get_db_session,
    create_tables,
    drop_tables,
    reset_database
)

# Database operations
async def setup_database():
    await create_tables()

async def cleanup_database():
    await drop_tables()

async def reset_database():
    await reset_database()
```

## 📊 Performance

### Query Optimization
- Use appropriate indexes
- Limit result sets
- Use pagination
- Optimize JOIN operations
- Use database views for complex queries

### Connection Pooling
- Configure connection pool size
- Monitor connection usage
- Implement connection health checks
- Use connection timeouts

### Caching Strategy
- Cache frequently accessed data
- Use Redis for session storage
- Implement query result caching
- Cache computed values

## 🔐 Security

### Row Level Security (RLS)
```sql
-- Enable RLS on tables
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view their own alerts" ON alerts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own alerts" ON alerts
    FOR INSERT WITH CHECK (auth.uid() = user_id);
```

### Data Validation
- Use database constraints
- Validate input data
- Sanitize user inputs
- Use parameterized queries

## 🔍 Monitoring

### Database Metrics
- Query performance
- Connection pool usage
- Index usage statistics
- Table sizes and growth

### Health Checks
```python
async def check_database_health():
    try:
        async with get_db_session() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

## 🛠️ Troubleshooting

### Common Issues
1. **Connection errors**: Check database URL and credentials
2. **Migration failures**: Verify migration dependencies
3. **Performance issues**: Review query execution plans
4. **Data integrity**: Check constraints and validation

### Debug Steps
1. Check database logs
2. Verify connection parameters
3. Test queries manually
4. Review migration history
5. Check table structure

## 📚 Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🔄 Future Enhancements

### Planned Features
- **Real-time subscriptions**: Database change notifications
- **Advanced analytics**: Complex query views
- **Data archiving**: Historical data management
- **Backup automation**: Automated backup strategies

### Performance Improvements
- **Query optimization**: Advanced indexing strategies
- **Connection pooling**: Enhanced connection management
- **Caching layer**: Multi-level caching
- **Read replicas**: Load balancing for read operations
