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
```

## Usage

Run the CLI:

```bash
python main.py
```

Example flow:

```text
Enter host/domain (e.g., example.com): example.com
Enter TCP ports separated by commas (e.g., 22,80,443): 22,80,443
...
Save report to report.json? (y/n): y
```

After running, if you choose to save, a `report.json` file is created in the project directory.
