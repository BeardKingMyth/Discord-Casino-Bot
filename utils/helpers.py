import json
from pathlib import Path

# File paths
BALANCES_FILE = Path("data/balances.json")
DAILY_FILE = Path("data/daily_claims.json")

# Generic JSON loader/saver
def load_json(file_path):
    if not file_path.exists():
        return {}
    with open(file_path, "r") as f:
        return json.load(f)

def save_json(data, file_path):
    file_path.parent.mkdir(exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# Convenience functions for balances
def load_balances():
    return load_json(BALANCES_FILE)

def save_balances(balances):
    save_json(balances, BALANCES_FILE)

# Convenience functions for daily claims
def load_claims():
    return load_json(DAILY_FILE)

def save_claims(claims):
    save_json(claims, DAILY_FILE)