# Automated Crypto Trading Bot

A sophisticated cryptocurrency trading bot for Coinbase Advanced Trade and Kraken Pro, focusing on memecoin market making and arbitrage opportunities.

## Features

- **Market Making**: Automated quote placement on volatile memecoins (WIF, PEPE, BONK)
- **DEX-CEX Arbitrage**: Opportunistic arbitrage between DEXs (Uniswap, Jupiter) and CEXs
- **Risk Management**: Position limits, daily loss limits, and circuit breakers
- **State Recovery**: Write-ahead logging for crash recovery
- **Tax Tracking**: Full FIFO/LIFO support with Form 8949 export

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 16+
- Windows/Mac/Linux

### Installation

1. Clone the repository:
```bash
git clone https://github.com/lukebarhoumeh/Automated-Coinbase-Crypto-Trading-Bot.git
cd Automated-Coinbase-Crypto-Trading-Bot
```

2. Create virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
   - Copy `.env.example` to `.env`
   - Add your API keys:
     - Coinbase Advanced Trade API keys
     - Kraken Pro API keys
   - Update PostgreSQL password in DATABASE_URL

5. Setup database:
```bash
python setup.py
```

6. Test setup:
```bash
python test_setup.py
```

## Configuration

### API Keys Required

**Coinbase Advanced Trade**:
- View permission ✓
- Trade permission ✓
- Transfer permission ✗

**Kraken Pro**:
- Query funds ✓
- Query/Create/Cancel orders ✓
- Withdraw funds ✗

### Environment Variables

Key settings in `.env`:
- `TRADING_MODE`: paper or live
- `MAX_POSITION_PCT`: Maximum position size (default 20%)
- `DAILY_LOSS_LIMIT_PCT`: Daily stop loss (default 0.6%)
- `PRIMARY_PAIRS`: Trading pairs (WIF-USD, PEPE-USD, BONK-USD)

## Project Structure

```
├── core/           # Core trading engine
│   └── exchanges/  # Exchange adapters
├── mm/             # Market making strategies
├── arb/            # Arbitrage strategies
├── risk/           # Risk management
├── tax/            # Tax tracking
├── tests/          # Test suite
└── logs/           # Trading logs
```

## Usage

### Paper Trading (Recommended Start)

```bash
# Set TRADING_MODE=paper in .env
python main.py
```

### Live Trading

```bash
# Set TRADING_MODE=live in .env
# Start with small capital!
python main.py
```

## Risk Warning

⚠️ **IMPORTANT**: Cryptocurrency trading involves substantial risk of loss. 

- Start with paper trading
- Never trade more than you can afford to lose
- This bot is experimental software
- Past performance doesn't guarantee future results

## Development

### Running Tests

```bash
pytest tests/
```

### Database Management

```bash
# Connect to database
psql -U postgres -d trading_bot

# Run migrations
psql -U postgres -d trading_bot -f schema.sql
```

## Sprint Plan

Following a 12-week sprint plan:
- Sprint 1-2: Core infrastructure
- Sprint 3-4: Market making implementation
- Sprint 5-6: Arbitrage & risk management
- Sprint 7-8: Testing & refinement
- Sprint 9-10: Production hardening
- Sprint 11-12: Documentation & deployment

## License

MIT License - see LICENSE file

## Disclaimer

This software is for educational purposes. Use at your own risk. The authors are not responsible for any financial losses.
