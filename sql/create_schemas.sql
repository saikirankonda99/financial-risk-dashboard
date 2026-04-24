CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS staging.trades (
    trade_id       BIGINT PRIMARY KEY,
    trade_timestamp TIMESTAMP,
    ticker         VARCHAR(16),
    asset_class    VARCHAR(16),
    quantity       INTEGER,
    price          NUMERIC(12,4),
    market_value   NUMERIC(16,2)
);

CREATE TABLE IF NOT EXISTS analytics.eod_positions (
    trade_date     DATE,
    ticker         VARCHAR(16),
    quantity       BIGINT,
    market_value   NUMERIC(16,2),
    PRIMARY KEY (trade_date, ticker)
);

CREATE TABLE IF NOT EXISTS analytics.daily_var (
    calc_date        DATE PRIMARY KEY,
    method           VARCHAR(16),
    confidence       NUMERIC(4,3),
    horizon_days     INT,
    portfolio_value  NUMERIC(18,2),
    var_dollar       NUMERIC(18,2),
    es_dollar        NUMERIC(18,2)
);
