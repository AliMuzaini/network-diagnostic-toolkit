from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from . import __version__
from .tools import (
    check_ports,
    diagnose,
    dns_lookup,
    ping,
    save_json,
    system_info,
    traceroute,
)


def heading(text: str) -> None:
    print(f"\n{'=' * 64}\n{text}\n{'=' * 64}")


def print_system_info() -> None:
    info = system_info()
    heading("SYSTEM & NETWORK INFORMATION")
    print(f"Hostname        : {info['hostname']}")
    print(f"Operating System: {info['operating_system']}")
    print(f"Python Version  : {info['python_version']}")
    print(f"Default Gateway : {info['default_gateway'] or 'Not detected'}")
    addresses = info["local_ipv4_addresses"] or ["Not detected"]
    print(f"Local IPv4      : {', '.join(addresses)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="netdiag",
        description="Network Diagnostic Toolkit",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("info", help="Show local system and network information")

    ping_parser = subparsers.add_parser("ping", help="Ping a host")
    ping_parser.add_argument("host")
    ping_parser.add_argument("-c", "--count", type=int, default=4)

    dns_parser = subparsers.add_parser("dns", help="Resolve a DNS name")
    dns_parser.add_argument("host")

    port_parser = subparsers.add_parser("port", help="Check selected TCP ports")
    port_parser.add_argument("host")
    port_parser.add_argument("ports", nargs="+", type=int)
    port_parser.add_argument("--timeout", type=float, default=1.5)

    trace_parser = subparsers.add_parser("trace", help="Run traceroute/tracert")
    trace_parser.add_argument("host")

    diag_parser = subparsers.add_parser(
        "diagnose",
        help="Run a complete diagnostic against a target",
    )
    diag_parser.add_argument("target")
    diag_parser.add_argument("--ports", nargs="+", type=int, default=[80, 443])
    diag_parser.add_argument("-c", "--count", type=int, default=4)
    diag_parser.add_argument(
        "-o",
        "--output",
        help="Save the complete report as JSON",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "info":
        print_system_info()
        return 0

    if args.command == "ping":
        result = ping(args.host, args.count)
        heading(f"PING: {args.host}")
        print(result["output"])
        return 0 if result["reachable"] else 1

    if args.command == "dns":
        result = dns_lookup(args.host)
        heading(f"DNS LOOKUP: {args.host}")
        if result["success"]:
            print(f"Canonical name : {result['canonical_name']}")
            print("Addresses      : " + ", ".join(result["addresses"]))
        else:
            print(f"Lookup failed  : {result['error']}")
        return 0 if result["success"] else 1

    if args.command == "port":
        heading(f"TCP PORT CHECK: {args.host}")
        results = check_ports(args.host, args.ports, args.timeout)
        for result in results:
            status = "OPEN" if result.open else "CLOSED / UNREACHABLE"
            latency = f" ({result.latency_ms} ms)" if result.latency_ms else ""
            print(f"{result.port:>5}/tcp  {status}{latency}")
        return 0

    if args.command == "trace":
        result = traceroute(args.host)
        heading(f"TRACEROUTE: {args.host}")
        print(result["output"])
        return result["return_code"]

    if args.command == "diagnose":
        report = diagnose(args.target, args.ports, args.count)

        heading("NETWORK DIAGNOSTIC REPORT")
        print(f"Target          : {report['target']}")
        print(f"Generated       : {report['generated_at']}")

        info = report["system"]
        print("\n[LOCAL SYSTEM]")
        print(f"Hostname        : {info['hostname']}")
        print(f"OS              : {info['operating_system']}")
        print(f"Default Gateway : {info['default_gateway'] or 'Not detected'}")
        print(f"Local IPv4      : {', '.join(info['local_ipv4_addresses']) or 'Not detected'}")

        dns = report["dns"]
        print("\n[DNS]")
        if dns["success"]:
            print("Addresses       : " + ", ".join(dns["addresses"]))
        else:
            print(f"Failed          : {dns['error']}")

        print("\n[PING]")
        print(f"Reachable       : {'Yes' if report['ping']['reachable'] else 'No'}")

        print("\n[TCP PORTS]")
        for item in report["ports"]:
            status = "OPEN" if item["open"] else "CLOSED / UNREACHABLE"
            latency = (
                f" ({item['latency_ms']} ms)"
                if item["latency_ms"] is not None
                else ""
            )
            print(f"{item['port']:>5}/tcp  {status}{latency}")

        print("\n[TRACEROUTE]")
        print(report["traceroute"]["output"])

        if args.output:
            save_json(report, args.output)
            print(f"\nReport saved to: {args.output}")

        return 0

    parser.print_help()
    return 2
