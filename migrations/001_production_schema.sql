PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL,
    external_id TEXT NOT NULL,
    name TEXT,
    currency TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(provider, external_id)
);

CREATE TABLE IF NOT EXISTS daily_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    captured_at TEXT NOT NULL,
    account_id INTEGER NOT NULL,
    currency TEXT NOT NULL,
    total_value REAL NOT NULL,
    cash_available REAL NOT NULL,
    cash_reserved REAL NOT NULL,
    cash_in_pies REAL NOT NULL,
    investment_value REAL NOT NULL,
    investment_cost REAL NOT NULL,
    realized_profit_loss REAL NOT NULL,
    unrealized_profit_loss REAL NOT NULL,
    raw_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_daily_snapshots_captured_at
    ON daily_snapshots(captured_at);

CREATE INDEX IF NOT EXISTS idx_daily_snapshots_account
    ON daily_snapshots(account_id);

CREATE TABLE IF NOT EXISTS daily_balances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    business_date TEXT NOT NULL,
    captured_at TEXT NOT NULL,
    total_value REAL NOT NULL,
    currency TEXT NOT NULL,
    UNIQUE(account_id, business_date),
    FOREIGN KEY(account_id) REFERENCES accounts(id)
);

CREATE INDEX IF NOT EXISTS idx_daily_balances_account_date
    ON daily_balances(account_id, business_date);

CREATE TABLE IF NOT EXISTS income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT,
    transaction_date TEXT NOT NULL,
    financial_year TEXT NOT NULL,
    account_id INTEGER NOT NULL,
    income_type TEXT NOT NULL,
    currency TEXT NOT NULL,
    gross_amount REAL NOT NULL,
    withholding_tax REAL DEFAULT 0,
    net_amount REAL,
    instrument TEXT,
    raw_json TEXT,
    UNIQUE(transaction_id)
);

CREATE TABLE IF NOT EXISTS sync_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    operation TEXT NOT NULL,
    status TEXT NOT NULL,
    records_processed INTEGER NOT NULL DEFAULT 0,
    error TEXT
);

CREATE INDEX IF NOT EXISTS idx_sync_runs_started
    ON sync_runs(started_at);
