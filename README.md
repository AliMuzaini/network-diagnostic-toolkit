# Network Diagnostic Toolkit

A lightweight cross-platform network troubleshooting toolkit written in Python.

Built for quick diagnostics on Windows and Linux systems without requiring third-party Python packages.

## Features

- Hostname and operating system information
- Local IPv4 address discovery
- Default gateway detection
- Ping testing
- DNS resolution
- TCP port connectivity checks
- Traceroute / Tracert
- Full diagnostic report
- Export reports to JSON
- Windows and Linux support

## Requirements

- Python 3.10+
- No external Python packages required

## Installation

Clone the repository:

```bash
git clone https://github.com/AliMuzaini/network-diagnostic-toolkit.git
cd network-diagnostic-toolkit
```

Run directly:

```bash
python netdiag.py --help
```

## Usage

### System and network information

```bash
python netdiag.py info
```

### Ping a host

```bash
python netdiag.py ping 8.8.8.8
```

Change the number of packets:

```bash
python netdiag.py ping 8.8.8.8 -c 5
```

### DNS lookup

```bash
python netdiag.py dns github.com
```

### Check TCP ports

```bash
python netdiag.py port github.com 80 443
```

You can also test administrative services on systems you manage:

```bash
python netdiag.py port 192.168.1.10 22 3389
```

### Traceroute

```bash
python netdiag.py trace 8.8.8.8
```

### Full diagnostic

```bash
python netdiag.py diagnose github.com --ports 80 443
```

Export the result:

```bash
python netdiag.py diagnose github.com --ports 80 443 --output report.json
```

## Example

```text
Network Diagnostic Toolkit
Target: github.com

[INFO]
Hostname        : WORKSTATION
Operating System: Windows 11
Default Gateway : 192.168.1.1

[PING]
Target          : github.com
Reachable       : Yes

[DNS]
github.com -> 140.82.x.x

[PORT CHECK]
80/tcp   OPEN
443/tcp  OPEN
```

## Project Structure

```text
network-diagnostic-toolkit/
├── netdiag.py
├── src/
│   └── netdiag/
│       ├── __init__.py
│       ├── cli.py
│       └── tools.py
├── tests/
│   └── test_tools.py
├── .gitignore
├── LICENSE
├── pyproject.toml
└── README.md
```

## Security Note

Use this toolkit only on systems and networks you own or are authorized to test.

## Roadmap

- Network interface details
- Subnet calculator
- DNS server diagnostics
- DHCP troubleshooting
- Latency statistics
- CSV and TXT report export
- Optional graphical interface

## Author

**Ali Muzaini**

IT Infrastructure • Networking • Systems Administration • Cybersecurity

GitHub: [@AliMuzaini](https://github.com/AliMuzaini)

## License

MIT License
