PRAGMA foreign_keys = ON;

-- Register the existing Trading 212 account from the legacy
-- daily_snapshots table.
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

-- Create canonical daily balances from the latest raw snapshot
-- for each Trading 212 account/date.
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
