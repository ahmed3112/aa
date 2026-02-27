#!/usr/bin/env python3
"""Daily backup utility for Cisco Catalyst 9200/9500 switches."""

from __future__ import annotations

import argparse
import datetime as dt
import ipaddress
import json
import time
from pathlib import Path

DEFAULT_COMMANDS = {
    "running-config": "show running-config",
    "startup-config": "show startup-config",
    "version": "show version",
    "inventory": "show inventory",
}


def expand_ip_targets(target: str) -> list[str]:
    """Expand IP input supporting CSV of single IPs, CIDR, or start-end ranges."""
    expanded: list[str] = []
    parts = [item.strip() for item in target.split(",") if item.strip()]

    for part in parts:
        if "/" in part:
            network = ipaddress.ip_network(part, strict=False)
            expanded.extend([str(ip) for ip in network.hosts()])
            continue

        if "-" in part:
            start_raw, end_raw = [x.strip() for x in part.split("-", 1)]
            if "." not in end_raw:
                prefix = start_raw.rsplit(".", 1)[0]
                end_raw = f"{prefix}.{end_raw}"

            start_ip = ipaddress.ip_address(start_raw)
            end_ip = ipaddress.ip_address(end_raw)
            if int(end_ip) < int(start_ip):
                raise ValueError(f"Invalid range: {part}")
            expanded.extend([str(ipaddress.ip_address(i)) for i in range(int(start_ip), int(end_ip) + 1)])
            continue

        expanded.append(str(ipaddress.ip_address(part)))

    return expanded


def read_channel(shell, wait_s: float = 0.4) -> str:
    time.sleep(wait_s)
    chunks: list[str] = []
    while shell.recv_ready():
        chunks.append(shell.recv(65535).decode("utf-8", errors="ignore"))
        time.sleep(0.1)
    return "".join(chunks)


def run_show_commands(
    host: str,
    username: str,
    password: str,
    enable_password: str | None,
    port: int,
    timeout: int,
) -> dict[str, str]:
    import paramiko

    outputs: dict[str, str] = {}
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=host,
        port=port,
        username=username,
        password=password,
        look_for_keys=False,
        allow_agent=False,
        timeout=timeout,
    )

    shell = client.invoke_shell(width=200, height=2000)
    shell.settimeout(timeout)

    read_channel(shell, 0.8)
    shell.send("terminal length 0\n")
    read_channel(shell, 0.3)

    if enable_password:
        shell.send("enable\n")
        read_channel(shell, 0.3)
        shell.send(f"{enable_password}\n")
        read_channel(shell, 0.5)

    for label, command in DEFAULT_COMMANDS.items():
        shell.send(f"{command}\n")
        outputs[label] = read_channel(shell, 1.2)

    shell.close()
    client.close()
    return outputs


def load_inventory(path: Path) -> list[dict[str, str]]:
    inventory_data = json.loads(path.read_text(encoding="utf-8"))
    devices = inventory_data.get("devices", [])
    if not devices:
        raise ValueError("Inventory must include at least one device in the 'devices' list.")
    return devices


def normalize_devices(devices: list[dict[str, str]]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for device in devices:
        if "host" in device:
            normalized.append(device)
            continue

        if "ip_range" not in device:
            raise ValueError("Each device must include either 'host' or 'ip_range'.")

        ips = expand_ip_targets(device["ip_range"])
        for ip in ips:
            normalized.append(
                {
                    "name": f"{device.get('name_prefix', 'switch')}-{ip.replace('.', '-')}",
                    "host": ip,
                    "username": device["username"],
                    "password": device["password"],
                    "enable_password": device.get("enable_password", ""),
                }
            )
    return normalized


def backup_device(device: dict[str, str], backup_root: Path, port: int, timeout: int) -> dict[str, str]:
    name = device["name"]
    host = device["host"]
    username = device["username"]
    password = device["password"]
    enable_password = device.get("enable_password")

    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    device_dir = backup_root / name
    device_dir.mkdir(parents=True, exist_ok=True)

    result_summary: dict[str, str] = {"name": name, "host": host, "timestamp": timestamp, "status": "ok"}

    try:
        command_outputs = run_show_commands(
            host=host,
            username=username,
            password=password,
            enable_password=enable_password,
            port=port,
            timeout=timeout,
        )
        for label, output in command_outputs.items():
            (device_dir / f"{timestamp}_{label}.txt").write_text(output, encoding="utf-8")
    except Exception as exc:
        result_summary["status"] = "failed"
        result_summary["error"] = str(exc)
        for label in DEFAULT_COMMANDS:
            (device_dir / f"{timestamp}_{label}.txt").write_text(
                f"ERROR: backup failed for {host}\n{exc}\n", encoding="utf-8"
            )

    (device_dir / f"{timestamp}_metadata.json").write_text(json.dumps(result_summary, indent=2), encoding="utf-8")
    return result_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backup Cisco 9200/9500 switch details over SSH.")
    parser.add_argument("--inventory", default="tools/devices.json", help="JSON inventory file path")
    parser.add_argument("--output-dir", default="backups", help="Directory where backups are stored")
    parser.add_argument("--port", type=int, default=22, help="SSH port")
    parser.add_argument("--timeout", type=int, default=45, help="Timeout seconds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    devices = normalize_devices(load_inventory(Path(args.inventory)))

    summaries = [backup_device(device=d, backup_root=output_dir, port=args.port, timeout=args.timeout) for d in devices]
    failed = [item for item in summaries if item["status"] != "ok"]
    print(json.dumps({"run_at": dt.datetime.now(dt.timezone.utc).isoformat(), "results": summaries}, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
