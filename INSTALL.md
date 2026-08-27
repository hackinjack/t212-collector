# Installation

This document installs the current Trading 212 collector on Ubuntu 24.04 LTS.

The commands assume an administrator/root-capable account and a fixed public IP on the VPS.

## 1. System packages

```bash
sudo apt update
sudo apt full-upgrade -y

sudo apt install -y \
    python3 \
    python3-venv \
    python3-pip \
    sqlite3 \
    curl \
    jq
```

## 2. Create the service account

```bash
sudo useradd \
    --system \
    --home /opt/t212-collector \
    --shell /usr/sbin/nologin \
    t212
```

Create the application directory:

```bash
sudo mkdir -p /opt/t212-collector
sudo chown t212:t212 /opt/t212-collector
```

If the user already exists, skip the `useradd` command.

## 3. Install the application

Copy the repository contents into:

```text
/opt/t212-collector
```

For example:

```bash
sudo rsync -a --delete ./ /opt/t212-collector/
sudo chown -R t212:t212 /opt/t212-collector
```

Do not copy `.env`, `portfolio.db`, or logs from a development machine.

## 4. Python virtual environment

```bash
sudo -u t212 python3 -m venv /opt/t212-collector/venv

sudo -u t212 \
    /opt/t212-collector/venv/bin/pip install \
    --upgrade pip

sudo -u t212 \
    /opt/t212-collector/venv/bin/pip install \
    -r /opt/t212-collector/requirements.txt
```

## 5. Configure Trading 212 credentials

Create the environment file using vim:

```bash
sudo -u t212 vim /opt/t212-collector/.env
```

Add:

```text
T212_API_KEY=YOUR_API_KEY
T212_API_SECRET=YOUR_API_SECRET
```

Set ownership and permissions:

```bash
sudo chown t212:t212 /opt/t212-collector/.env
sudo chmod 600 /opt/t212-collector/.env
```

Do not commit this file.

## 6. Initialise the database

The collector creates its SQLite schema automatically on first run.

## 7. Manual test

Run:

```bash
sudo -u t212 \
    /opt/t212-collector/venv/bin/python \
    /opt/t212-collector/collector.py
```

A successful run should print the returned JSON and:

```text
Snapshot saved successfully.
```

Check the database:

```bash
sudo -u t212 sqlite3 /opt/t212-collector/portfolio.db \
    "SELECT captured_at,total_value,currency FROM daily_snapshots ORDER BY id DESC LIMIT 10;"
```

## 8. Install systemd units

Copy the supplied units:

```bash
sudo cp systemd/t212-collector.service \
    /etc/systemd/system/

sudo cp systemd/t212-collector.timer \
    /etc/systemd/system/
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now t212-collector.timer
```

Check the timer:

```bash
systemctl list-timers --all | grep t212
```

## 9. Test the service

Run immediately:

```bash
sudo systemctl start t212-collector.service
```

Inspect status:

```bash
sudo systemctl status t212-collector.service
```

Inspect logs:

```bash
sudo journalctl \
    -u t212-collector.service \
    -n 50 \
    --no-pager
```

## 10. Verify scheduled operation

The timer is configured for 08:00 Europe/London and uses `Persistent=true`, so a missed run can be triggered after the VPS comes back online.

Check:

```bash
systemctl status t212-collector.timer
```

## Trading 212 API restriction

The production API key should be configured as read-only and restricted to the VPS's fixed public IPv4 address.

Verify the VPS public address with:

```bash
curl -4 https://api.ipify.org
echo
```

Do not put the public IP, API key, or secret into this repository.

## Updating

Stop the scheduled collector before replacing application files:

```bash
sudo systemctl stop t212-collector.timer
```

Update the files, then:

```bash
sudo chown -R t212:t212 /opt/t212-collector

sudo -u t212 \
    /opt/t212-collector/venv/bin/pip install \
    -r /opt/t212-collector/requirements.txt

sudo systemctl daemon-reload
sudo systemctl start t212-collector.timer
```

Do not overwrite:

```text
.env
portfolio.db
```

unless you intentionally have a migration/recovery procedure.

## Backup

The SQLite database is the local source of truth.

At minimum, periodically back it up using SQLite's online backup facilities or a filesystem snapshot. A future version will add an explicit backup/export command.
