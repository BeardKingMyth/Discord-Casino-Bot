import json
from pathlib import Path

DATA_FILE = Path("data/balances.json")

def load_balances():
    if not DATA_FILE.exists():
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_balances(balances):
    DATA_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(balances, f, indent=4)
