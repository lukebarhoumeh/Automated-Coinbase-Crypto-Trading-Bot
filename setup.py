"""
Setup script for the trading bot.
Handles database creation, virtual environment setup, and initial configuration.
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_database():
    """Create the PostgreSQL database if it doesn't exist."""
    print("📊 Setting up PostgreSQL database...")
    
    # Get database URL and parse it
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/trading_bot")
    
    # Parse the URL to get components
    parts = db_url.replace("postgresql://", "").split("@")
    user_pass = parts[0].split(":")
    host_db = parts[1].split("/")
    
    db_user = user_pass[0]
    db_pass = user_pass[1] if len(user_pass) > 1 else ""
    db_host = host_db[0].split(":")[0]
    db_port = host_db[0].split(":")[1] if ":" in host_db[0] else "5432"
    db_name = host_db[1]
    
    try:
        # Connect to PostgreSQL server (not to a specific database)
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_pass
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"✅ Database '{db_name}' created successfully")
        else:
            print(f"✅ Database '{db_name}' already exists")
        
        cursor.close()
        conn.close()
        
        # Now connect to the created database and run schema
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_pass,
            database=db_name
        )
        cursor = conn.cursor()
        
        # Read and execute schema
        schema_path = Path(__file__).parent / "schema.sql"
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            cursor.execute(schema_sql)
            conn.commit()
            print("✅ Database schema created successfully")
        else:
            print("⚠️  schema.sql not found, skipping schema creation")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        print("\nPlease ensure:")
        print("1. PostgreSQL is installed and running")
        print("2. The password in your .env file matches your PostgreSQL password")
        print("3. You can connect to PostgreSQL using the credentials in .env")
        return False
    
    return True


def test_connections():
    """Test exchange API connections."""
    print("\n🔌 Testing exchange connections...")
    
    try:
        import ccxt
        from config import config, exchange_config
        
        # Test Coinbase if configured
        if "coinbase" in config.active_exchanges and config.coinbase_api_key:
            print("\nTesting Coinbase connection...")
            exchange = ccxt.coinbase(exchange_config.get_coinbase_config())
            try:
                balance = exchange.fetch_balance()
                print(f"✅ Coinbase connected successfully")
                # Don't print actual balance for security
            except Exception as e:
                print(f"❌ Coinbase connection error: {e}")
        
        # Test Kraken if configured  
        if "kraken" in config.active_exchanges and config.kraken_api_key:
            print("\nTesting Kraken connection...")
            exchange = ccxt.kraken(exchange_config.get_kraken_config())
            try:
                balance = exchange.fetch_balance()
                print(f"✅ Kraken connected successfully")
            except Exception as e:
                print(f"❌ Kraken connection error: {e}")
                
    except ImportError:
        print("❌ Required packages not installed. Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Connection test error: {e}")
        return False
    
    return True


def main():
    """Main setup function."""
    print("🚀 Trading Bot Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Check if .env exists
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        print("❌ .env file not found!")
        print("Please copy .env.example to .env and add your API keys")
        sys.exit(1)
    
    # Check if virtual environment is activated
    if sys.prefix == sys.base_prefix:
        print("\n⚠️  Virtual environment not activated!")
        print("Please run:")
        print("  python -m venv venv")
        print("  .\\venv\\Scripts\\activate  (Windows)")
        print("  source venv/bin/activate   (Mac/Linux)")
        print("\nThen run this setup again.")
        response = input("\nContinue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Install requirements
    print("\n📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        sys.exit(1)
    
    # Create necessary directories
    print("\n📁 Creating directories...")
    dirs = ['logs', 'data', 'backups']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    print("✅ Directories created")
    
    # Setup database
    if not create_database():
        print("\n⚠️  Database setup failed, but continuing...")
    
    # Test connections
    test_connections()
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\nNext steps:")
    print("1. Add your API keys to the .env file")
    print("2. Update the DATABASE_URL password in .env")
    print("3. Run: python test_setup.py")
    print("4. Start coding your trading strategies!")


if __name__ == "__main__":
    main()
