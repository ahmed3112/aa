#!/usr/bin/env python3
"""Desktop GUI for Cisco 9200/9500 backup runner."""

from __future__ import annotations

import json
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from queue import Queue
from tkinter import filedialog, messagebox, ttk


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


def run_backup_process(ip_targets: str, username: str, password: str, enable_password: str, output_dir: str) -> tuple[int, str]:
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
    output = f"$ {' '.join(cmd)}\n\nSTDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}\n"
    return process.returncode, output


def main() -> None:
    root = tk.Tk()
    root.title("Cisco Backup Studio | Catalyst 9200 / 9500")
    root.geometry("980x700")
    root.minsize(880, 620)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
    style.configure("Subtitle.TLabel", font=("Segoe UI", 10))
    style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"))

    container = ttk.Frame(root, padding=18)
    container.pack(fill="both", expand=True)

    ttk.Label(container, text="Cisco Backup Studio", style="Title.TLabel").grid(row=0, column=0, sticky="w")
    ttk.Label(
        container,
        text="Daily backup tool for Cisco 9200/9500 • IP range/CIDR • Credentials • Enable mode",
        style="Subtitle.TLabel",
    ).grid(row=1, column=0, sticky="w", pady=(0, 16))

    form = ttk.LabelFrame(container, text="Backup Settings", padding=14)
    form.grid(row=2, column=0, sticky="nsew")

    container.rowconfigure(3, weight=1)
    container.columnconfigure(0, weight=1)
    form.columnconfigure(1, weight=1)

    ttk.Label(form, text="IP range / CIDR / IP list:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=6)
    ip_var = tk.StringVar(value="10.10.10.10-10.10.10.20,10.10.20.0/30")
    ip_entry = ttk.Entry(form, textvariable=ip_var)
    ip_entry.grid(row=0, column=1, sticky="ew", pady=6)

    ttk.Label(form, text="Username:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=6)
    user_var = tk.StringVar()
    ttk.Entry(form, textvariable=user_var).grid(row=1, column=1, sticky="ew", pady=6)

    ttk.Label(form, text="Password:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=6)
    pass_var = tk.StringVar()
    ttk.Entry(form, textvariable=pass_var, show="•").grid(row=2, column=1, sticky="ew", pady=6)

    ttk.Label(form, text="Enable password:").grid(row=3, column=0, sticky="w", padx=(0, 10), pady=6)
    enable_var = tk.StringVar()
    ttk.Entry(form, textvariable=enable_var, show="•").grid(row=3, column=1, sticky="ew", pady=6)

    ttk.Label(form, text="Output directory:").grid(row=4, column=0, sticky="w", padx=(0, 10), pady=6)
    output_var = tk.StringVar(value=str(Path("backups").resolve()))
    output_entry = ttk.Entry(form, textvariable=output_var)
    output_entry.grid(row=4, column=1, sticky="ew", pady=6)

    def choose_output_dir() -> None:
        selected = filedialog.askdirectory(title="Choose output directory for backups")
        if selected:
            output_var.set(selected)

    ttk.Button(form, text="Browse…", command=choose_output_dir).grid(row=4, column=2, padx=(10, 0), pady=6)

    status_var = tk.StringVar(value="Ready")
    status_frame = ttk.Frame(container)
    status_frame.grid(row=3, column=0, sticky="ew", pady=(12, 8))
    status_frame.columnconfigure(0, weight=1)

    ttk.Label(status_frame, textvariable=status_var).grid(row=0, column=0, sticky="w")
    progress = ttk.Progressbar(status_frame, mode="indeterminate", length=200)
    progress.grid(row=0, column=1, sticky="e")

    logs = ttk.LabelFrame(container, text="Execution Log", padding=8)
    logs.grid(row=4, column=0, sticky="nsew")
    container.rowconfigure(4, weight=1)
    logs.columnconfigure(0, weight=1)
    logs.rowconfigure(0, weight=1)

    log_widget = tk.Text(logs, wrap="word", font=("Consolas", 10))
    log_widget.grid(row=0, column=0, sticky="nsew")
    scrollbar = ttk.Scrollbar(logs, orient="vertical", command=log_widget.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    log_widget.configure(yscrollcommand=scrollbar.set)

    controls = ttk.Frame(container)
    controls.grid(row=5, column=0, sticky="ew", pady=(12, 0))
    controls.columnconfigure(0, weight=1)

    run_queue: Queue[tuple[int, str]] = Queue()
    is_running = {"value": False}

    def append_log(text: str) -> None:
        log_widget.insert("end", text + "\n")
        log_widget.see("end")

    def poll_queue() -> None:
        if not run_queue.empty():
            return_code, output = run_queue.get()
            append_log(output)
            progress.stop()
            is_running["value"] = False
            run_button.configure(state="normal")

            if return_code == 0:
                status_var.set("Backup completed successfully")
                messagebox.showinfo("Backup", "Backup completed successfully")
            else:
                status_var.set("Backup completed with errors")
                messagebox.showwarning("Backup", "Backup finished with errors. Check execution log.")

        root.after(250, poll_queue)

    def background_run(ip_targets: str, username: str, password: str, enable_password: str, output_dir: str) -> None:
        run_queue.put(run_backup_process(ip_targets, username, password, enable_password, output_dir))

    def on_run() -> None:
        if is_running["value"]:
            return

        ip_targets = ip_var.get().strip()
        username = user_var.get().strip()
        password = pass_var.get()
        enable_password = enable_var.get()
        output_dir = output_var.get().strip()

        if not ip_targets or not username or not password or not output_dir:
            messagebox.showerror("Input error", "IP targets, username, password, and output directory are required.")
            return

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        is_running["value"] = True
        run_button.configure(state="disabled")
        status_var.set("Backup in progress...")
        progress.start(10)
        append_log("Starting backup job...\n")

        thread = threading.Thread(
            target=background_run,
            args=(ip_targets, username, password, enable_password, output_dir),
            daemon=True,
        )
        thread.start()

    run_button = ttk.Button(controls, text="Run Backup Now", command=on_run, style="Primary.TButton")
    run_button.grid(row=0, column=1, sticky="e")

    root.after(250, poll_queue)
    root.mainloop()


if __name__ == "__main__":
    main()
