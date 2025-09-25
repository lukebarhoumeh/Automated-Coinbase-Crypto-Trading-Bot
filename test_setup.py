"""
Test script to verify the trading bot setup.
Checks all components are properly configured and working.
"""

import os
import sys
import asyncio
from datetime import datetime
from colorlog import ColoredFormatter
import logging
import psycopg2
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Setup colored logging
def setup_logging():
    """Setup colored logging for better visibility."""
    handler = logging.StreamHandler()
    handler.setFormatter(ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


logger = setup_logging()


def test_imports():
    """Test that all required packages can be imported."""
    logger.info("Testing package imports...")
    
    required_packages = [
        'ccxt',
        'pandas',
        'numpy',
        'psycopg2',
        'redis',
        'dotenv',
        'colorlog',
        'websockets',
        'aiohttp'
    ]
    
    failed = []
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package} imported successfully")
        except ImportError as e:
            logger.error(f"❌ Failed to import {package}: {e}")
            failed.append(package)
    
    return len(failed) == 0


def test_environment():
    """Test environment variables are loaded."""
    logger.info("\nTesting environment configuration...")
    
    try:
        from config import config
        
        # Check critical settings
        checks = [
            ("Environment", config.environment),
            ("Trading Mode", config.trading_mode),
            ("Active Exchanges", config.active_exchanges),
            ("Primary Pairs", config.primary_pairs),
            ("Log Level", config.log_level),
            ("Timezone", config.timezone)
        ]
        
        for name, value in checks:
            logger.info(f"✅ {name}: {value}")
        
        # Check API keys (don't log the actual values)
        if config.coinbase_api_key:
            logger.info("✅ Coinbase API key is set")
        else:
            logger.warning("⚠️  Coinbase API key is not set")
            
        if config.kraken_api_key:
            logger.info("✅ Kraken API key is set")
        else:
            logger.warning("⚠️  Kraken API key is not set")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration error: {e}")
        return False


def test_database():
    """Test database connection."""
    logger.info("\nTesting database connection...")
    
    try:
        from config import config
        
        # Parse database URL
        db_url = config.database_url
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        logger.info(f"✅ PostgreSQL connected: {version}")
        
        # Check tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        if tables:
            logger.info(f"✅ Found {len(tables)} tables:")
            for table in tables:
                logger.info(f"   - {table[0]}")
        else:
            logger.warning("⚠️  No tables found. Run schema.sql to create tables.")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
        logger.error("Please check:")
        logger.error("1. PostgreSQL is running")
        logger.error("2. Database password in .env is correct")
        logger.error("3. Database 'trading_bot' exists")
        return False


async def test_exchange_connections():
    """Test exchange API connections."""
    logger.info("\nTesting exchange connections...")
    
    try:
        import ccxt.async_support as ccxt
        from config import config, exchange_config
        
        results = []
        
        # Test Coinbase
        if "coinbase" in config.active_exchanges:
            if config.coinbase_api_key:
                logger.info("Testing Coinbase API...")
                exchange = ccxt.coinbase(exchange_config.get_coinbase_config())
                
                try:
                    # Test public endpoint
                    ticker = await exchange.fetch_ticker('BTC/USD')
                    logger.info(f"✅ Coinbase public API working - BTC/USD: ${ticker['last']:,.2f}")
                    
                    # Test private endpoint (if in live mode)
                    if config.trading_mode == "live":
                        balance = await exchange.fetch_balance()
                        logger.info("✅ Coinbase private API working")
                    
                    results.append(True)
                except Exception as e:
                    logger.error(f"❌ Coinbase API error: {e}")
                    results.append(False)
                finally:
                    await exchange.close()
            else:
                logger.warning("⚠️  Coinbase API key not set")
        
        # Test Kraken
        if "kraken" in config.active_exchanges:
            if config.kraken_api_key:
                logger.info("\nTesting Kraken API...")
                exchange = ccxt.kraken(exchange_config.get_kraken_config())
                
                try:
                    # Test public endpoint
                    ticker = await exchange.fetch_ticker('BTC/USD')
                    logger.info(f"✅ Kraken public API working - BTC/USD: ${ticker['last']:,.2f}")
                    
                    # Test private endpoint (if in live mode)
                    if config.trading_mode == "live":
                        balance = await exchange.fetch_balance()
                        logger.info("✅ Kraken private API working")
                    
                    results.append(True)
                except Exception as e:
                    logger.error(f"❌ Kraken API error: {e}")
                    results.append(False)
                finally:
                    await exchange.close()
            else:
                logger.warning("⚠️  Kraken API key not set")
        
        return all(results) if results else True
        
    except Exception as e:
        logger.error(f"❌ Exchange test error: {e}")
        return False


def test_directories():
    """Test that required directories exist."""
    logger.info("\nChecking directories...")
    
    required_dirs = ['logs', 'data', 'backups']
    
    for dir_name in required_dirs:
        path = Path(dir_name)
        if path.exists():
            logger.info(f"✅ {dir_name}/ exists")
        else:
            path.mkdir(exist_ok=True)
            logger.info(f"✅ {dir_name}/ created")
    
    return True


async def main():
    """Run all tests."""
    logger.info("🧪 Trading Bot Setup Test")
    logger.info("=" * 50)
    logger.info(f"Running tests at {datetime.now()}")
    
    results = []
    
    # Run tests
    results.append(("Package Imports", test_imports()))
    results.append(("Environment Config", test_environment()))
    results.append(("Directories", test_directories()))
    results.append(("Database", test_database()))
    results.append(("Exchange APIs", await test_exchange_connections()))
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("Test Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        logger.info("\n🎉 All tests passed! Your bot is ready to trade!")
    else:
        logger.warning("\n⚠️  Some tests failed. Please check the errors above.")
    
    return passed == len(results)


if __name__ == "__main__":
    asyncio.run(main())
