# HostPulse

HostPulse is a simple Python CLI utility for basic host checks.

It can:
- check host reachability with `ping`
- check selected TCP ports
- check `http://` and `https://` availability
- measure response time for each check
- optionally save results to `report.json`

## Requirements

- Python 3.10+
- `ping` command available in your system

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt