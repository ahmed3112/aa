#!/usr/bin/env python3
"""Daily backup utility for Cisco Catalyst 9200/9500 switches over SSH."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path


DEFAULT_COMMANDS = {
    "running-config": "terminal length 0 ; show running-config",
    "startup-config": "terminal length 0 ; show startup-config",
    "version": "terminal length 0 ; show version",
    "inventory": "terminal length 0 ; show inventory",
}


def run_ssh_command(
    host: str,
    username: str,
    command: str,
    port: int,
    ssh_key: str | None,
    timeout: int,
) -> subprocess.CompletedProcess[str]:
    ssh_cmd = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        "-p",
        str(port),
    ]

    if ssh_key:
        ssh_cmd.extend(["-i", ssh_key])

    ssh_cmd.extend([f"{username}@{host}", command])

    return subprocess.run(
        ssh_cmd,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def load_inventory(path: Path) -> list[dict[str, str]]:
    inventory_data = json.loads(path.read_text(encoding="utf-8"))
    devices = inventory_data.get("devices", [])
    if not devices:
        raise ValueError("Inventory must include at least one device in the 'devices' list.")
    return devices


def backup_device(
    device: dict[str, str],
    backup_root: Path,
    port: int,
    ssh_key: str | None,
    timeout: int,
) -> dict[str, str]:
    name = device["name"]
    host = device["host"]
    username = device["username"]

    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    device_dir = backup_root / name
    device_dir.mkdir(parents=True, exist_ok=True)

    result_summary: dict[str, str] = {
        "name": name,
        "host": host,
        "timestamp": timestamp,
        "status": "ok",
    }

    for label, command in DEFAULT_COMMANDS.items():
        result = run_ssh_command(
            host=host,
            username=username,
            command=command,
            port=port,
            ssh_key=ssh_key,
            timeout=timeout,
        )

        output_file = device_dir / f"{timestamp}_{label}.txt"
        if result.returncode == 0:
            output_file.write_text(result.stdout, encoding="utf-8")
        else:
            output_file.write_text(
                f"ERROR: command failed\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}",
                encoding="utf-8",
            )
            result_summary["status"] = "failed"
            result_summary[f"error_{label}"] = (result.stderr or "Unknown SSH error").strip()

    metadata_file = device_dir / f"{timestamp}_metadata.json"
    metadata_file.write_text(json.dumps(result_summary, indent=2), encoding="utf-8")
    return result_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backup Cisco 9200/9500 switch config and hardware details over SSH."
    )
    parser.add_argument(
        "--inventory",
        default="tools/devices.json",
        help="JSON inventory file path (default: tools/devices.json)",
    )
    parser.add_argument(
        "--output-dir",
        default="backups",
        help="Directory where backup files are stored (default: backups)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=22,
        help="SSH port on network devices (default: 22)",
    )
    parser.add_argument(
        "--ssh-key",
        default=None,
        help="Optional SSH private key path",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=45,
        help="Timeout in seconds per SSH command (default: 45)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    inventory_path = Path(args.inventory)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    devices = load_inventory(inventory_path)

    summaries = []
    for device in devices:
        summaries.append(
            backup_device(
                device=device,
                backup_root=output_dir,
                port=args.port,
                ssh_key=args.ssh_key,
                timeout=args.timeout,
            )
        )

    failed = [item for item in summaries if item["status"] != "ok"]
    print(json.dumps({"run_at": dt.datetime.now(dt.timezone.utc).isoformat(), "results": summaries}, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
