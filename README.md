# Trading 212 Portfolio Collector

A small, self-hosted Python collector for Trading 212 account snapshots.

The current snapshot intentionally does **one thing well**:

> Poll the Trading 212 API on a schedule and persist account snapshots locally in SQLite.

Google Sheets, income/tax reporting, dividends, and the other portfolio accounts are **not implemented yet**. See `TODO.md`.

## Current architecture

```text
Trading 212 API
       |
       | HTTPS
       v
Ubuntu VPS (fixed public IP)
       |
       +--> Python collector
       |
       +--> SQLite database
       |
       +--> systemd timer
```

The Trading 212 API key can be restricted to the VPS's fixed public IP. The collector runs as a dedicated unprivileged `t212` user.

## Current API data

The collector currently consumes the Trading 212 account summary response and stores:

- account ID
- account currency
- total account value
- available cash
- reserved cash
- cash in Pies
- current investment value
- investment cost
- realised P/L
- unrealised P/L
- raw JSON response
- UTC capture timestamp

## Requirements

- Linux system; developed/tested on Ubuntu 24.04 LTS
- Python 3
- systemd
- SQLite 3
- A Trading 212 API key with read-only access
- Network access to `https://live.trading212.com`

## Installation

See [`INSTALL.md`](INSTALL.md).

## Repository layout

```text
.
├── README.md
├── INSTALL.md
├── TODO.md
├── CHANGELOG.md
├── LICENSE
├── collector.py
├── requirements.txt
├── systemd/
│   ├── t212-collector.service
│   └── t212-collector.timer
└── .gitignore
```

## Security

**Never commit credentials, `.env`, SQLite databases, or generated logs.**

The production installation stores credentials in:

```text
/opt/t212-collector/.env
```

with mode `0600`, owned by the `t212` service account.

The Trading 212 API key should be read-only and, where practical, restricted to the VPS's fixed public IP.

## Status

This repository represents the **working scheduled collector snapshot** as of the initial project build.

It is deliberately small. The next stages will add Google Sheets synchronisation and Trading 212 income/tax data without changing the collector's role as the local source of truth.
