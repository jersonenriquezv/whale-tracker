# Shared Package - Whale Tracker v0

This package contains shared utilities, types, and constants used across the Whale Tracker v0 application.

## 📋 Overview

The shared package provides common functionality that can be used by multiple services in the Whale Tracker ecosystem, including the backend API, workers, and frontend.

## 🏗️ Structure

```
packages/shared/
├── types/           # Type definitions and schemas
├── utils/           # Utility functions
├── constants/       # Application constants
├── models/          # Data models
└── exceptions/      # Custom exceptions
```

## 📚 Components

### Types
- **Transaction Types**: Ethereum transaction schemas
- **Market Types**: Order book and market data schemas
- **Alert Types**: Alert configuration and trigger schemas
- **API Types**: Request/response schemas

### Utilities
- **Crypto Utils**: Ethereum address validation, transaction parsing
- **Time Utils**: Timestamp conversion, time range calculations
- **Data Utils**: Data transformation and validation
- **Format Utils**: Number formatting, address shortening

### Constants
- **API Constants**: Endpoint URLs, rate limits
- **Blockchain Constants**: Gas limits, network IDs
- **Alert Constants**: Default thresholds, timeouts
- **Config Constants**: Environment-specific settings

### Models
- **Whale Transaction Model**: Whale transaction data structure
- **Liquidity Zone Model**: Liquidity zone data structure
- **SMC Pattern Model**: Smart Money Concept pattern structure
- **Alert Model**: Alert configuration structure

### Exceptions
- **API Exceptions**: HTTP error handling
- **Validation Exceptions**: Data validation errors
- **Processing Exceptions**: Data processing errors
- **Connection Exceptions**: Network and service connection errors

## 🚀 Usage

### Installation
```bash
# From the root directory
pip install -e packages/shared
```

### Import Examples
```python
from shared.types import WhaleTransaction
from shared.utils.crypto import validate_ethereum_address
from shared.constants import WHALE_THRESHOLD_ETH
from shared.models import LiquidityZone
from shared.exceptions import ValidationError
```

### Type Definitions
```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class WhaleTransaction(BaseModel):
    hash: str
    from_address: str
    to_address: str
    value_eth: float
    value_usd: float
    gas_price: int
    block_number: int
    timestamp: datetime
    whale_score: float
```

### Utility Functions
```python
def validate_ethereum_address(address: str) -> bool:
    """Validate Ethereum address format"""
    import re
    pattern = r'^0x[a-fA-F0-9]{40}$'
    return bool(re.match(pattern, address))

def format_eth_amount(amount: float) -> str:
    """Format ETH amount with appropriate precision"""
    if amount >= 1000:
        return f"{amount/1000:.1f}K ETH"
    elif amount >= 1:
        return f"{amount:.2f} ETH"
    else:
        return f"{amount:.4f} ETH"
```

## 🔧 Development

### Adding New Types
1. Create new type definition in `types/` directory
2. Add validation logic if needed
3. Update imports in `__init__.py`
4. Add tests in `tests/` directory

### Adding New Utilities
1. Create new utility function in `utils/` directory
2. Add proper error handling and validation
3. Add docstring with examples
4. Add tests for edge cases

### Adding New Constants
1. Add constant to appropriate file in `constants/` directory
2. Use descriptive names and add comments
3. Group related constants together
4. Update documentation

## 📝 Testing

### Running Tests
```bash
# From the shared package directory
pytest tests/

# With coverage
pytest tests/ --cov=shared --cov-report=html
```

### Test Structure
```
tests/
├── test_types/      # Type validation tests
├── test_utils/      # Utility function tests
├── test_models/     # Model tests
└── test_exceptions/ # Exception tests
```

## 🔄 Versioning

The shared package follows semantic versioning:
- **Major**: Breaking changes to public APIs
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, backward compatible

## 📚 Documentation

### Code Documentation
- All functions and classes have docstrings
- Type hints are used throughout
- Examples are provided for complex functions

### API Documentation
- Pydantic models are self-documenting
- OpenAPI schemas are generated automatically
- Examples are included in docstrings

## 🔐 Security

### Input Validation
- All external inputs are validated
- Ethereum addresses are verified
- Numeric values are range-checked
- String inputs are sanitized

### Error Handling
- Sensitive information is not logged
- Errors are properly categorized
- Stack traces are limited in production

## 🔄 Future Enhancements

### Planned Features
- **Caching Layer**: Redis integration for shared data
- **Metrics**: Prometheus metrics collection
- **Logging**: Structured logging configuration
- **Configuration**: Environment-based configuration management

### Performance Optimizations
- **Lazy Loading**: Import optimization
- **Memory Management**: Efficient data structures
- **Caching**: Frequently used data caching
- **Async Support**: Async/await patterns

## 📞 Support

For questions or issues with the shared package:
1. Check the documentation
2. Review existing tests
3. Create an issue with detailed description
4. Provide reproduction steps
