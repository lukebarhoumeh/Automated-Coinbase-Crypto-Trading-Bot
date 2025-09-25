-- Trading Bot Database Schema
-- PostgreSQL 16+

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS trades CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS positions CASCADE;
DROP TABLE IF EXISTS tax_lots CASCADE;
DROP TABLE IF EXISTS market_data CASCADE;
DROP TABLE IF EXISTS system_state CASCADE;

-- Orders table with write-ahead logging
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    client_order_id VARCHAR(255) UNIQUE NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL CHECK (side IN ('BUY', 'SELL')),
    order_type VARCHAR(20) NOT NULL,
    quantity DECIMAL(20,8) NOT NULL,
    price DECIMAL(20,8),
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    exchange_order_id VARCHAR(255),
    filled_quantity DECIMAL(20,8) DEFAULT 0,
    filled_avg_price DECIMAL(20,8),
    fee DECIMAL(20,8),
    fee_currency VARCHAR(10),
    strategy VARCHAR(50),
    metadata JSONB
);

-- Create indexes for performance
CREATE INDEX idx_orders_exchange_symbol ON orders(exchange, symbol);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- Current positions table
CREATE TABLE positions (
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    quantity DECIMAL(20,8) NOT NULL,
    avg_price DECIMAL(20,8) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    unrealized_pnl DECIMAL(20,8),
    PRIMARY KEY (symbol, exchange)
);

-- Trades table for executed trades
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,
    quantity DECIMAL(20,8) NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    fee DECIMAL(20,8),
    fee_currency VARCHAR(10),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    pnl DECIMAL(20,8),
    strategy VARCHAR(50)
);

CREATE INDEX idx_trades_timestamp ON trades(timestamp);
CREATE INDEX idx_trades_symbol ON trades(symbol);

-- Tax lots for FIFO/LIFO tracking
CREATE TABLE tax_lots (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    quantity DECIMAL(20,8) NOT NULL,
    remaining_quantity DECIMAL(20,8) NOT NULL,
    purchase_price DECIMAL(20,8) NOT NULL,
    purchase_date TIMESTAMP WITH TIME ZONE NOT NULL,
    purchase_fee DECIMAL(20,8),
    sale_price DECIMAL(20,8),
    sale_date TIMESTAMP WITH TIME ZONE,
    sale_fee DECIMAL(20,8),
    realized_pnl DECIMAL(20,8),
    cost_basis DECIMAL(20,8),
    proceeds DECIMAL(20,8),
    holding_period VARCHAR(20) -- 'short' or 'long'
);

CREATE INDEX idx_tax_lots_symbol ON tax_lots(symbol);
CREATE INDEX idx_tax_lots_purchase_date ON tax_lots(purchase_date);

-- Market data storage (for replay/analysis)
CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    bid_price DECIMAL(20,8),
    bid_size DECIMAL(20,8),
    ask_price DECIMAL(20,8),
    ask_size DECIMAL(20,8),
    last_price DECIMAL(20,8),
    volume_24h DECIMAL(20,8),
    data_type VARCHAR(20) -- 'ticker', 'orderbook', 'trade'
);

CREATE INDEX idx_market_data_composite ON market_data(exchange, symbol, timestamp);

-- System state for recovery
CREATE TABLE system_state (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default system state
INSERT INTO system_state (key, value) VALUES 
    ('last_reconciliation', NOW()::TEXT),
    ('trading_enabled', 'false'),
    ('last_heartbeat', NOW()::TEXT);

-- Performance metrics table
CREATE TABLE performance_metrics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(20,8),
    metadata JSONB,
    UNIQUE(date, metric_name)
);

-- Audit log for compliance
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    action VARCHAR(100) NOT NULL,
    user_id VARCHAR(50),
    details JSONB
);
