# Quran Kareem Ramadan Website

This is a lightweight static website for Ramadan Kareem with Quran reflection and checklist features.

## GitHub Testing

Automated tests run on every push and pull request using **GitHub Actions**.

Workflow file: `.github/workflows/test.yml`

It runs:
1. `node -c script.js` for JavaScript syntax validation.
2. `npm test` for repository checks in `tests/site.test.mjs`.

## Cisco 9200/9500 Daily Backup Tools

This repository now includes simple tools to back up Cisco Catalyst 9200 and 9500 switches daily.

### Files
- `tools/cisco_backup.py`: Runs SSH commands and saves backup outputs.
- `tools/devices.example.json`: Example inventory for switches.
- `tools/install_daily_cron.sh`: Installs a daily cron schedule.

### 1) Create inventory file
Copy and edit inventory:

```bash
cp tools/devices.example.json tools/devices.json
```

### 2) Run backup manually

```bash
python3 tools/cisco_backup.py --inventory tools/devices.json --output-dir backups
```

### 3) Schedule daily backup
Install cron entry at 02:00 (default):

```bash
./tools/install_daily_cron.sh tools/devices.json
```

Or choose time, e.g. 01:30:

```bash
./tools/install_daily_cron.sh tools/devices.json 01:30
```

Backups are stored under `backups/<device-name>/`.
