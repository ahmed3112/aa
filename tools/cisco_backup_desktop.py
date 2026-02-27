#!/usr/bin/env python3
"""Desktop GUI for Cisco 9200/9500 backup runner."""

from __future__ import annotations

import json
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext


def build_inventory_text(ip_targets: str, username: str, password: str, enable_password: str) -> str:
    payload = {
        "devices": [
            {
                "name_prefix": "desktop-switch",
                "ip_range": ip_targets,
                "username": username,
                "password": password,
                "enable_password": enable_password,
            }
        ]
    }
    return json.dumps(payload, indent=2)


def run_backup(ip_targets: str, username: str, password: str, enable_password: str, output_dir: str, log_widget):
    inventory_path = Path("tools/devices.desktop.json")
    inventory_path.write_text(
        build_inventory_text(ip_targets, username, password, enable_password), encoding="utf-8"
    )

    cmd = [
        "python3",
        "tools/cisco_backup.py",
        "--inventory",
        str(inventory_path),
        "--output-dir",
        output_dir,
    ]

    process = subprocess.run(cmd, capture_output=True, text=True, check=False)
    log_widget.insert(tk.END, f"$ {' '.join(cmd)}\n{process.stdout}\n{process.stderr}\n")
    log_widget.see(tk.END)

    if process.returncode == 0:
        messagebox.showinfo("Backup", "Backup completed successfully")
    else:
        messagebox.showwarning("Backup", "Backup finished with errors. Check log window.")


def main() -> None:
    root = tk.Tk()
    root.title("Cisco 9200/9500 Backup Desktop Tool")
    root.geometry("760x540")

    tk.Label(root, text="IP range(s) / CIDR / single IP (comma separated):").pack(anchor="w", padx=10, pady=(12, 0))
    ip_entry = tk.Entry(root, width=90)
    ip_entry.insert(0, "10.10.10.10-10.10.10.20,10.10.20.0/30")
    ip_entry.pack(padx=10, pady=4)

    tk.Label(root, text="Username:").pack(anchor="w", padx=10)
    user_entry = tk.Entry(root, width=40)
    user_entry.pack(padx=10, pady=4)

    tk.Label(root, text="Password:").pack(anchor="w", padx=10)
    pass_entry = tk.Entry(root, width=40, show="*")
    pass_entry.pack(padx=10, pady=4)

    tk.Label(root, text="Enable mode password:").pack(anchor="w", padx=10)
    enable_entry = tk.Entry(root, width=40, show="*")
    enable_entry.pack(padx=10, pady=4)

    tk.Label(root, text="Output directory:").pack(anchor="w", padx=10)
    output_entry = tk.Entry(root, width=60)
    output_entry.insert(0, "backups")
    output_entry.pack(padx=10, pady=4)

    log_widget = scrolledtext.ScrolledText(root, width=100, height=15)
    log_widget.pack(padx=10, pady=12, fill="both", expand=True)

    def on_run() -> None:
        ip_targets = ip_entry.get().strip()
        username = user_entry.get().strip()
        password = pass_entry.get()
        enable_password = enable_entry.get()
        output_dir = output_entry.get().strip() or "backups"

        if not ip_targets or not username or not password:
            messagebox.showerror("Input error", "IP targets, username and password are required.")
            return

        thread = threading.Thread(
            target=run_backup,
            args=(ip_targets, username, password, enable_password, output_dir, log_widget),
            daemon=True,
        )
        thread.start()

    tk.Button(root, text="Run Backup Now", command=on_run, bg="#2e7d32", fg="white").pack(pady=4)
    root.mainloop()


if __name__ == "__main__":
    main()
