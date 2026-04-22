#!/usr/bin/env python3
"""HostPulse: Simple host health check CLI utility."""

from __future__ import annotations

import json
import platform
import socket
import subprocess
import time
from pathlib import Path
from typing import Any

import requests


REPORT_FILE = Path("report.json")


def parse_ports(raw_ports: str) -> list[int]:
    """Parse comma-separated ports into a list of valid port numbers."""
    if not raw_ports.strip():
        return []

    ports: list[int] = []
    for part in raw_ports.split(","):
        part = part.strip()
        if not part:
            continue
        if not part.isdigit():
            raise ValueError(f"Invalid port value: {part}")

        port = int(part)
        if not 1 <= port <= 65535:
            raise ValueError(f"Port out of range (1-65535): {port}")
        ports.append(port)

    # Preserve order while removing duplicates.
    return list(dict.fromkeys(ports))


def check_ping(host: str) -> dict[str, Any]:
    """Check if a host is reachable by pinging it once."""
    system_name = platform.system().lower()
    count_flag = "-n" if system_name == "windows" else "-c"
    timeout_flag = "-w" if system_name == "windows" else "-W"

    cmd = ["ping", count_flag, "1", timeout_flag, "2", host]
    start = time.perf_counter()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

    return {
        "reachable": result.returncode == 0,
        "response_time_ms": elapsed_ms,
        "command": " ".join(cmd),
    }


def check_tcp_port(host: str, port: int, timeout: float = 2.0) -> dict[str, Any]:
    """Check whether a TCP port is open on the host."""
    start = time.perf_counter()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        code = sock.connect_ex((host, port))
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

    return {
        "port": port,
        "open": code == 0,
        "response_time_ms": elapsed_ms,
    }


def check_http(url: str, timeout: float = 5.0) -> dict[str, Any]:
    """Check HTTP or HTTPS availability using an HTTP GET request."""
    start = time.perf_counter()
    try:
        response = requests.get(url, timeout=timeout)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        return {
            "url": url,
            "available": True,
            "status_code": response.status_code,
            "response_time_ms": elapsed_ms,
        }
    except requests.RequestException as exc:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        return {
            "url": url,
            "available": False,
            "error": str(exc),
            "response_time_ms": elapsed_ms,
        }


def print_results(report: dict[str, Any]) -> None:
    """Print the report in a readable format."""
    print("\n=== HostPulse Report ===")
    print(f"Host: {report['host']}")

    ping_data = report["ping"]
    print("\nPing check:")
    print(f"- Reachable: {'Yes' if ping_data['reachable'] else 'No'}")
    print(f"- Response time: {ping_data['response_time_ms']} ms")

    print("\nTCP port checks:")
    if not report["ports"]:
        print("- No ports selected")
    else:
        for item in report["ports"]:
            state = "Open" if item["open"] else "Closed"
            print(f"- Port {item['port']}: {state} ({item['response_time_ms']} ms)")

    print("\nWeb checks:")
    for web in report["web"]:
        if web["available"]:
            print(
                f"- {web['url']}: Available (status {web['status_code']}, "
                f"{web['response_time_ms']} ms)"
            )
        else:
            print(f"- {web['url']}: Unavailable ({web['response_time_ms']} ms)")
            print(f"  Error: {web['error']}")


def main() -> None:
    """Run HostPulse CLI flow."""
    print("HostPulse - Simple host and service checker")

    host = input("Enter host/domain (e.g., example.com): ").strip()
    while not host:
        host = input("Host/domain cannot be empty. Please enter host/domain: ").strip()

    ports_input = input("Enter TCP ports separated by commas (e.g., 22,80,443): ").strip()

    try:
        ports = parse_ports(ports_input)
    except ValueError as exc:
        print(f"Invalid ports input: {exc}")
        return

    report: dict[str, Any] = {
        "host": host,
        "ping": check_ping(host),
        "ports": [check_tcp_port(host, port) for port in ports],
        "web": [check_http(f"http://{host}"), check_http(f"https://{host}")],
    }

    print_results(report)

    save_answer = input("\nSave report to report.json? (y/n): ").strip().lower()
    if save_answer in {"y", "yes"}:
        REPORT_FILE.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Report saved to {REPORT_FILE}")
    else:
        print("Report not saved.")


if __name__ == "__main__":
    main()
