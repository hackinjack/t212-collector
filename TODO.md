# TODO

## Project status

Current release: **v0.1.0**

Current capability:

- Trading 212 API collection
- Read-only API credentials
- Fixed-IP API restriction
- SQLite persistence
- Raw API response retention
- systemd service
- Daily scheduled collection

---

# Milestone 0.2 — Production collector

## Database

- [ ] Design production schema
- [ ] Add `accounts` table
- [ ] Add canonical daily balance table
- [ ] Add `sync_runs` table
- [ ] Preserve existing `daily_snapshots` data
- [ ] Add database migration mechanism
- [ ] Add schema versioning
- [ ] Add indexes for account/date queries
- [ ] Add database integrity checks

## Collector

- [ ] Validate Trading 212 API response schema
- [ ] Add HTTP retry/backoff handling
- [ ] Handle API rate limiting
- [ ] Handle network failures cleanly
- [ ] Record collection start/end times
- [ ] Record API response latency
- [ ] Record collector version
- [ ] Return meaningful exit codes
- [ ] Add CLI/status command
- [ ] Prevent accidental duplicate canonical daily records

## systemd

- [ ] Harden service configuration
- [ ] Verify timer timezone/DST behaviour
- [ ] Verify missed-run behaviour
- [ ] Add resource limits where appropriate
- [ ] Document service administration

## Testing

- [ ] Add unit tests
- [ ] Add API response fixtures
- [ ] Add database migration tests
- [ ] Test API failure handling
- [ ] Test duplicate handling
- [ ] Test recovery after VPS reboot

---

# Milestone 0.3 — Google Sheets integration

- [ ] Choose direct Google Sheets API/OAuth architecture
- [ ] Document OAuth setup
- [ ] Store OAuth credentials securely
- [ ] Implement Sheets client
- [ ] Implement idempotent synchronisation
- [ ] Add `Accounts` sheet
- [ ] Add `Daily Balances` sheet
- [ ] Add `System Status` sheet
- [ ] Add rebuild-from-SQLite capability
- [ ] Document Sheets recovery/rebuild procedure

## Dashboard

- [ ] Portfolio total
- [ ] Value by account
- [ ] Value by currency
- [ ] Cash vs investments
- [ ] Historical portfolio value
- [ ] Daily/period performance
- [ ] Account-level performance
- [ ] Dashboard refresh/status indicator

---

# Milestone 0.4 — Trading 212 income

## Historical data

- [ ] Implement Trading 212 historical export requests
- [ ] Download and archive source CSVs
- [ ] Hash source files
- [ ] Parse transaction history
- [ ] Track import/export metadata
- [ ] Implement incremental imports

## Interest

- [ ] Identify interest transaction format
- [ ] Import GBP interest
- [ ] Import EUR interest
- [ ] Preserve original currency
- [ ] Deduplicate interest transactions
- [ ] Calculate UK financial year
- [ ] Build financial-year interest summary
- [ ] Build monthly interest summary

## Dividends

- [ ] Identify dividend transaction format
- [ ] Import dividends
- [ ] Preserve original currency
- [ ] Track gross dividend
- [ ] Track withholding tax where supplied
- [ ] Track net dividend where supplied
- [ ] Deduplicate dividend transactions
- [ ] Build financial-year dividend summary

## Tax reporting

- [ ] Create `T212 Income` sheet
- [ ] Create `Tax Summary` sheet
- [ ] GBP/EUR income breakdown
- [ ] UK financial-year summaries
- [ ] Historical-year comparison
- [ ] Document calculation methodology
- [ ] Preserve source transaction references

> Tax reports are reporting aids and should not be treated as professional tax advice.

---

# Milestone 0.5 — Other financial accounts

## Revolut

- [ ] Investigate API/Open Banking options
- [ ] Determine available balance data
- [ ] Determine transaction/income data
- [ ] Implement connector

## Zopa

- [ ] Investigate API/Open Banking options
- [ ] Determine available balance data
- [ ] Determine interest data
- [ ] Implement connector

## Cahoot

- [ ] Investigate available integration options
- [ ] Determine balance retrieval method
- [ ] Determine transaction retrieval method
- [ ] Implement connector

## JPMorgan

- [ ] Investigate available integration options
- [ ] Determine account/balance retrieval method
- [ ] Determine transaction retrieval method
- [ ] Implement connector

## Freetrade

- [ ] Investigate API/Open Banking options
- [ ] Determine portfolio valuation data
- [ ] Determine dividend/income data
- [ ] Implement connector

## Common data model

- [ ] Define provider-independent account model
- [ ] Define balance model
- [ ] Define transaction model
- [ ] Define income model
- [ ] Define currency model
- [ ] Define provider/account identifiers
- [ ] Add connector capability metadata

---

# Milestone 0.6 — Backup and disaster recovery

## Database backup

- [ ] Implement SQLite online backup
- [ ] Compress backups
- [ ] Encrypt backups
- [ ] Add backup retention policy
- [ ] Add daily backup job
- [ ] Add backup integrity verification
- [ ] Add backup age monitoring

## Cloud storage

- [ ] Select cloud storage provider
- [ ] Configure least-privilege credentials
- [ ] Upload encrypted backups
- [ ] Verify remote backups
- [ ] Document restore procedure

## Recovery

- [ ] Test complete database restore
- [ ] Test restore to clean VPS
- [ ] Test Sheets rebuild from restored SQLite
- [ ] Document disaster recovery procedure

---

# Milestone 0.7 — Monitoring and alerting

## Metrics

- [ ] Expose collector health metrics
- [ ] Last successful collection timestamp
- [ ] Last attempted collection timestamp
- [ ] Collection duration
- [ ] Trading 212 API latency
- [ ] Collection failure count
- [ ] Database size
- [ ] Snapshot count
- [ ] Income transaction count
- [ ] Last successful Sheets sync

## TIG integration

- [ ] Determine existing Telegraf architecture
- [ ] Choose Telegraf input/textfile strategy
- [ ] Export collector metrics
- [ ] Add Grafana dashboard panel
- [ ] Add collector health panel
- [ ] Add database/backup health panel

## Alerting

- [ ] Alert on collector failure
- [ ] Alert on stale data
- [ ] Alert on repeated API failures
- [ ] Alert on database failure
- [ ] Alert on backup failure
- [ ] Alert on failed Sheets synchronisation

---

# Milestone 0.8 — Operational polish

- [ ] Automated database migrations
- [ ] Configuration validation
- [ ] API credential rotation procedure
- [ ] Upgrade procedure
- [ ] Rollback procedure
- [ ] Log rotation
- [ ] Security review
- [ ] Dependency update procedure
- [ ] Release/versioning policy
- [ ] Full documentation review

---

# Future ideas

- [ ] Multi-currency portfolio valuation
- [ ] Historical FX rates
- [ ] Portfolio performance attribution
- [ ] Cost basis tracking
- [ ] Asset allocation
- [ ] Investment-level history
- [ ] Dividend yield reporting
- [ ] Interest-rate tracking
- [ ] Net worth aggregation
- [ ] Automated monthly reports
- [ ] Export tax reports as CSV/PDF
