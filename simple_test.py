#!/usr/bin/env python3
"""
Simple test script to check basic connectivity without complex CCXT operations.
"""

import os
import sys
from pathlib import Path
import asyncio
import aiohttp

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


async def test_basic_connectivity():
    """Test basic internet connectivity."""
    print("Testing basic connectivity...")
    
    urls = [
        ("Google", "https://www.google.com"),
        ("Coinbase", "https://api.coinbase.com"),
        ("Kraken", "https://api.kraken.com")
    ]
    
    async with aiohttp.ClientSession() as session:
        for name, url in urls:
            try:
                async with session.get(url, timeout=5) as response:
                    print(f"✅ {name}: {response.status}")
            except Exception as e:
                print(f"❌ {name}: {e}")


def test_config_parsing():
    """Test if config can be loaded without issues."""
    print("\nTesting config parsing...")
    
    try:
        from config import config
        print(f"✅ Config loaded successfully")
        print(f"   Environment: {config.environment}")
        print(f"   Trading Mode: {config.trading_mode}")
        print(f"   Active Exchanges: {config.active_exchanges}")
        print(f"   Primary Pairs: {config.primary_pairs}")
        
        # Check if API keys are set (without showing them)
        if config.coinbase_api_key:
            print(f"   Coinbase API Key: Set ({len(config.coinbase_api_key)} chars)")
        else:
            print(f"   Coinbase API Key: Not set")
            
        if config.kraken_api_key:
            print(f"   Kraken API Key: Set ({len(config.kraken_api_key)} chars)")
        else:
            print(f"   Kraken API Key: Not set")
            
    except Exception as e:
        print(f"❌ Config error: {e}")
        import traceback
        traceback.print_exc()


def test_env_file():
    """Check if .env file exists and is readable."""
    print("\nChecking .env file...")
    
    env_path = Path(".env")
    if env_path.exists():
        print(f"✅ .env file exists")
        
        # Check if it's readable
        try:
            with open(env_path, 'r') as f:
                lines = f.readlines()
                print(f"   File has {len(lines)} lines")
                
                # Count actual config lines (not comments or empty)
                config_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
                print(f"   {len(config_lines)} configuration lines")
        except Exception as e:
            print(f"❌ Error reading .env: {e}")
    else:
        print(f"❌ .env file not found")


async def main():
    """Run all simple tests."""
    print("=" * 50)
    print("Simple Trading Bot Test")
    print("=" * 50)
    
    test_env_file()
    test_config_parsing()
    await test_basic_connectivity()
    
    print("\n" + "=" * 50)
    print("Test complete!")


if __name__ == "__main__":
    asyncio.run(main())
