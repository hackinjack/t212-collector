PRAGMA foreign_keys = OFF;

BEGIN TRANSACTION;

CREATE TABLE daily_snapshots_new (
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
    raw_json TEXT NOT NULL,
    FOREIGN KEY(account_id) REFERENCES accounts(id)
);

INSERT INTO daily_snapshots_new (
    id,
    captured_at,
    account_id,
    currency,
    total_value,
    cash_available,
    cash_reserved,
    cash_in_pies,
    investment_value,
    investment_cost,
    realized_profit_loss,
    unrealized_profit_loss,
    raw_json
)
SELECT
    s.id,
    s.captured_at,
    a.id,
    s.currency,
    s.total_value,
    s.cash_available,
    s.cash_reserved,
    s.cash_in_pies,
    s.investment_value,
    s.investment_cost,
    s.realized_profit_loss,
    s.unrealized_profit_loss,
    s.raw_json
FROM daily_snapshots s
JOIN accounts a
    ON a.provider = 'trading212'
   AND a.external_id = CAST(s.account_id AS TEXT);

DROP TABLE daily_snapshots;

ALTER TABLE daily_snapshots_new
    RENAME TO daily_snapshots;

CREATE INDEX idx_daily_snapshots_captured_at
    ON daily_snapshots(captured_at);

CREATE INDEX idx_daily_snapshots_account
    ON daily_snapshots(account_id);

COMMIT;

PRAGMA foreign_keys = ON;
