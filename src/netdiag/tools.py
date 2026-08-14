from __future__ import annotations

import json
import os
import platform
import re
import socket
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Iterable


@dataclass
class CommandResult:
    command: str
    return_code: int
    output: str


@dataclass
class PortResult:
    host: str
    port: int
    open: bool
    latency_ms: float | None
    error: str | None = None


def run_command(command: list[str], timeout: int = 20) -> CommandResult:
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            errors="replace",
        )
        output = (completed.stdout or completed.stderr or "").strip()
        return CommandResult(" ".join(command), completed.returncode, output)
    except subprocess.TimeoutExpired:
        return CommandResult(" ".join(command), 124, "Command timed out.")
    except OSError as exc:
        return CommandResult(" ".join(command), 1, str(exc))


def get_local_ipv4_addresses() -> list[str]:
    addresses: set[str] = set()

    try:
        hostname = socket.gethostname()
        for item in socket.getaddrinfo(hostname, None, socket.AF_INET):
            ip = item[4][0]
            if not ip.startswith("127."):
                addresses.add(ip)
    except socket.gaierror:
        pass

    # UDP connect does not send traffic; it asks the OS which local address
    # would be used for the destination.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            ip = sock.getsockname()[0]
            if not ip.startswith("127."):
                addresses.add(ip)
    except OSError:
        pass

    return sorted(addresses)


def get_default_gateway() -> str | None:
    system = platform.system().lower()

    if system == "windows":
        result = run_command(["route", "print", "-4"])
        # Match the IPv4 default route line:
        # 0.0.0.0  0.0.0.0  <gateway>  <interface>  <metric>
        for line in result.output.splitlines():
            match = re.match(
                r"^\s*0\.0\.0\.0\s+0\.0\.0\.0\s+(\d+\.\d+\.\d+\.\d+)\s+",
                line,
            )
            if match:
                return match.group(1)

    elif system == "linux":
        result = run_command(["ip", "route", "show", "default"])
        match = re.search(r"\bvia\s+(\d+\.\d+\.\d+\.\d+)", result.output)
        if match:
            return match.group(1)

    elif system == "darwin":
        result = run_command(["route", "-n", "get", "default"])
        match = re.search(r"gateway:\s+([0-9.]+)", result.output)
        if match:
            return match.group(1)

    return None


def system_info() -> dict:
    return {
        "hostname": socket.gethostname(),
        "operating_system": f"{platform.system()} {platform.release()}",
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "local_ipv4_addresses": get_local_ipv4_addresses(),
        "default_gateway": get_default_gateway(),
    }


def ping(host: str, count: int = 4, timeout: int = 15) -> dict:
    system = platform.system().lower()

    if system == "windows":
        command = ["ping", "-n", str(count), host]
    else:
        command = ["ping", "-c", str(count), host]

    result = run_command(command, timeout=timeout)
    return {
        "host": host,
        "reachable": result.return_code == 0,
        "return_code": result.return_code,
        "output": result.output,
    }


def dns_lookup(host: str) -> dict:
    try:
        canonical, aliases, addresses = socket.gethostbyname_ex(host)
        return {
            "host": host,
            "canonical_name": canonical,
            "aliases": aliases,
            "addresses": sorted(set(addresses)),
            "success": True,
            "error": None,
        }
    except socket.gaierror as exc:
        return {
            "host": host,
            "canonical_name": None,
            "aliases": [],
            "addresses": [],
            "success": False,
            "error": str(exc),
        }


def check_port(host: str, port: int, timeout: float = 1.5) -> PortResult:
    import time

    started = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            latency = (time.perf_counter() - started) * 1000
            return PortResult(host, port, True, round(latency, 2))
    except OSError as exc:
        return PortResult(host, port, False, None, str(exc))


def check_ports(
    host: str,
    ports: Iterable[int],
    timeout: float = 1.5,
) -> list[PortResult]:
    results: list[PortResult] = []
    for port in ports:
        if not 1 <= int(port) <= 65535:
            raise ValueError(f"Invalid port: {port}")
        results.append(check_port(host, int(port), timeout))
    return results


def traceroute(host: str, timeout: int = 45) -> dict:
    system = platform.system().lower()

    if system == "windows":
        command = ["tracert", "-d", host]
    else:
        command = ["traceroute", "-n", host]

    result = run_command(command, timeout=timeout)
    return {
        "host": host,
        "return_code": result.return_code,
        "output": result.output,
    }


def diagnose(
    target: str,
    ports: Iterable[int] | None = None,
    ping_count: int = 4,
) -> dict:
    selected_ports = list(ports or [80, 443])

    return {
        "tool": "Network Diagnostic Toolkit",
        "version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target": target,
        "system": system_info(),
        "dns": dns_lookup(target),
        "ping": ping(target, count=ping_count),
        "ports": [asdict(item) for item in check_ports(target, selected_ports)],
        "traceroute": traceroute(target),
    }


def save_json(data: dict, path: str) -> None:
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
