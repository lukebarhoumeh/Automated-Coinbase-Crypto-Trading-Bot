"""
Configuration management for the trading bot.
Loads settings from environment variables and provides validation.
"""

import os
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv
from pydantic import validator
from pydantic_settings import BaseSettings
from decimal import Decimal

# Load .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)


class TradingConfig(BaseSettings):
    """Main configuration class for the trading bot."""
    
    # Coinbase API Configuration
    coinbase_api_key: str = os.getenv("COINBASE_API_KEY", "")
    coinbase_api_secret: str = os.getenv("COINBASE_API_SECRET", "")
    coinbase_api_passphrase: Optional[str] = os.getenv("COINBASE_API_PASSPHRASE", "")
    
    # Kraken API Configuration
    kraken_api_key: str = os.getenv("KRAKEN_API_KEY", "")
    kraken_private_key: str = os.getenv("KRAKEN_PRIVATE_KEY", "")
    
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/trading_bot")
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "5"))
    db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    
    # Redis Configuration
    redis_url: Optional[str] = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Trading Configuration
    environment: str = os.getenv("ENVIRONMENT", "development")
    trading_mode: str = os.getenv("TRADING_MODE", "paper")
    
    # Risk Management
    max_position_pct: Decimal = Decimal(os.getenv("MAX_POSITION_PCT", "0.20"))
    daily_loss_limit_pct: Decimal = Decimal(os.getenv("DAILY_LOSS_LIMIT_PCT", "0.006"))
    max_memecoin_exposure_pct: Decimal = Decimal(os.getenv("MAX_MEMECOIN_EXPOSURE_PCT", "0.15"))
    
    # Position Limits
    max_position_size_usd: Decimal = Decimal("2000")  # $2000 max per position
    max_total_exposure_usd: Decimal = Decimal("6000")  # $6000 max total
    max_overnight_per_coin_usd: Decimal = Decimal("500")  # $500 max overnight per coin
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file_path: str = os.getenv("LOG_FILE_PATH", "logs/trading_bot.log")
    
    # Monitoring
    telegram_bot_token: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: Optional[str] = os.getenv("TELEGRAM_CHAT_ID", "")
    
    # Exchange Selection
    active_exchanges: List[str] = os.getenv("ACTIVE_EXCHANGES", "coinbase,kraken").split(",")
    primary_pairs: List[str] = os.getenv("PRIMARY_PAIRS", "WIF-USD,PEPE-USD,BONK-USD").split(",")
    
    # Time Configuration
    timezone: str = os.getenv("TIMEZONE", "America/Chicago")
    
    # WebSocket Configuration
    ws_heartbeat_interval: int = 30  # seconds
    ws_reconnect_delay: int = 5  # seconds
    ws_max_reconnect_attempts: int = 10
    
    # Rate Limiting
    coinbase_rate_limit_per_second: int = 10
    kraken_rate_limit_per_second: int = 6
    
    @validator("trading_mode")
    def validate_trading_mode(cls, v):
        if v not in ["paper", "live"]:
            raise ValueError("trading_mode must be either 'paper' or 'live'")
        return v
    
    @validator("environment")
    def validate_environment(cls, v):
        if v not in ["development", "staging", "production"]:
            raise ValueError("environment must be one of: development, staging, production")
        return v
    
    class Config:
        case_sensitive = False


class ExchangeConfig:
    """Exchange-specific configuration."""
    
    def __init__(self, config: TradingConfig):
        self.config = config
    
    def get_coinbase_config(self) -> dict:
        """Get Coinbase-specific configuration."""
        return {
            "apiKey": self.config.coinbase_api_key,
            "secret": self.config.coinbase_api_secret,
            "passphrase": self.config.coinbase_api_passphrase,
            "enableRateLimit": True,
            "rateLimit": self.config.coinbase_rate_limit_per_second * 1000,  # ms
            "options": {
                "defaultType": "spot",
            }
        }
    
    def get_kraken_config(self) -> dict:
        """Get Kraken-specific configuration."""
        return {
            "apiKey": self.config.kraken_api_key,
            "secret": self.config.kraken_private_key,
            "enableRateLimit": True,
            "rateLimit": self.config.kraken_rate_limit_per_second * 1000,  # ms
        }


# Create global config instance
config = TradingConfig()
exchange_config = ExchangeConfig(config)

# Validate required API keys based on active exchanges
def validate_config():
    """Validate that required configuration is present."""
    errors = []
    
    if "coinbase" in config.active_exchanges:
        if not config.coinbase_api_key or not config.coinbase_api_secret:
            errors.append("Coinbase API credentials are required but not set")
    
    if "kraken" in config.active_exchanges:
        if not config.kraken_api_key or not config.kraken_private_key:
            errors.append("Kraken API credentials are required but not set")
    
    if config.trading_mode == "live" and config.environment == "development":
        errors.append("WARNING: Running in LIVE mode with development environment!")
    
    if errors:
        print("\n".join(errors))
        if any("required" in e for e in errors):
            raise ValueError("Configuration validation failed. Please check your .env file.")


if __name__ == "__main__":
    # Test configuration loading
    print(f"Environment: {config.environment}")
    print(f"Trading Mode: {config.trading_mode}")
    print(f"Active Exchanges: {config.active_exchanges}")
    print(f"Primary Pairs: {config.primary_pairs}")
    validate_config()
