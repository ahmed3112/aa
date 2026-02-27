# Quran Kareem Ramadan Website

This is a lightweight static website for Ramadan Kareem with Quran reflection and checklist features.

## GitHub Testing

Automated tests run on every push and pull request using **GitHub Actions**.

Workflow file: `.github/workflows/test.yml`

It runs:
1. `node -c script.js` for JavaScript syntax validation.
2. `npm test` for repository checks in `tests/site.test.mjs`.

## Cisco 9200/9500 Daily Backup Tools

This repository includes backup tools for Cisco Catalyst 9200 and 9500 with support for:
- IP ranges and CIDR
- username/password login
- enable mode password
- desktop GUI launcher

### Files
- `tools/cisco_backup.py`: Main backup CLI tool.
- `tools/cisco_backup_desktop.py`: Desktop GUI tool.
- `tools/devices.example.json`: Example inventory with single IP and IP range.
- `tools/install_daily_cron.sh`: Installs a daily cron schedule.

### Python dependency
Install Paramiko first:

```bash
pip install paramiko
```

### 1) Create inventory file

```bash
cp tools/devices.example.json tools/devices.json
```

### 2) Run backup manually

```bash
python3 tools/cisco_backup.py --inventory tools/devices.json --output-dir backups
```

### 3) Run desktop tool

```bash
python3 tools/cisco_backup_desktop.py
```

Then add:
- IPs (`10.10.10.10-10.10.10.20` or `10.10.20.0/24` or comma-separated mix)
- username
- password
- enable password

### 4) Schedule daily backup

```bash
./tools/install_daily_cron.sh tools/devices.json 01:30
```

Backups are stored under `backups/<device-name>/`.
