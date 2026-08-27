# TODO

## Current milestone

- [x] Direct Trading 212 API access
- [x] Fixed-IP VPS collector
- [x] Read-only Trading 212 API key
- [x] SQLite persistence
- [x] Raw API response retention
- [x] Dedicated `t212` Linux user
- [x] systemd service
- [x] systemd daily timer
- [x] Manual and scheduled collection tested

## Next milestone — production collector hardening

- [ ] Add canonical daily snapshot table keyed by account/date
- [ ] Add retry/backoff for transient API failures
- [ ] Add structured application logging
- [ ] Add explicit API response/schema validation
- [ ] Add database migrations
- [ ] Add collector version to stored records
- [ ] Add health/status command
- [ ] Add SQLite backup command
- [ ] Add retention policy for raw snapshots, if required
- [ ] Add tests

## Trading 212 income

- [ ] Implement historical export requests
- [ ] Import interest transactions
- [ ] Preserve GBP and EUR separately
- [ ] Import dividends
- [ ] Track gross/net/withholding tax where supplied
- [ ] Deduplicate transactions using stable transaction identifiers
- [ ] Calculate UK financial year from transaction date
- [ ] Retain original CSV/raw source
- [ ] Build financial-year interest summary
- [ ] Build financial-year dividend summary

## Google Sheets

- [ ] Decide and implement direct Google Sheets OAuth
- [ ] Keep SQLite as source of truth
- [ ] Create Sheets sync layer
- [ ] Create daily balances sheet
- [ ] Create income sheet
- [ ] Create tax summary sheet
- [ ] Create dashboard
- [ ] Make sync idempotent
- [ ] Add rebuild-from-SQLite capability

## Other accounts

- [ ] Investigate Revolut integration
- [ ] Investigate Zopa integration
- [ ] Investigate Cahoot integration
- [ ] Investigate JPMorgan integration
- [ ] Investigate Freetrade integration
- [ ] Define common account/balance schema
- [ ] Define common income/transaction schema

## Operations/security

- [ ] Document VPS firewall policy
- [ ] Review SSH hardening
- [ ] Add Tailscale administration/backup path
- [ ] Establish encrypted off-host database backup
- [ ] Document API-key rotation
- [ ] Document disaster recovery
