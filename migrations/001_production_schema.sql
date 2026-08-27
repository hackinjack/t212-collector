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

CREATE TABLE IF NOT EXISTS sync_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    operation TEXT NOT NULL,
    status TEXT NOT NULL,
    records_processed INTEGER NOT NULL DEFAULT 0,
    error TEXT
);

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

CREATE INDEX IF NOT EXISTS idx_sync_runs_started
    ON sync_runs(started_at);

INSERT OR IGNORE INTO schema_version(version, applied_at)
VALUES (1, datetime('now'));

-- Register the known Trading 212 account.
INSERT OR IGNORE INTO accounts (
    provider,
    external_id,
    name,
    currency,
    active,
    created_at,
    updated_at
)
SELECT
    'trading212',
    CAST(account_id AS TEXT),
    'Trading 212',
    currency,
    1,
    datetime('now'),
    datetime('now')
FROM daily_snapshots
ORDER BY id
LIMIT 1;

-- Preserve existing snapshots as canonical daily balances.
--
-- For each account/date, retain the latest snapshot from that date.
INSERT OR IGNORE INTO daily_balances (
    account_id,
    business_date,
    captured_at,
    total_value,
    currency
)
SELECT
    a.id,
    substr(s.captured_at, 1, 10),
    s.captured_at,
    s.total_value,
    s.currency
FROM daily_snapshots s
JOIN accounts a
    ON a.provider = 'trading212'
   AND a.external_id = CAST(s.account_id AS TEXT)
WHERE s.id IN (
    SELECT MAX(id)
    FROM daily_snapshots
    GROUP BY account_id, substr(captured_at, 1, 10)
);
