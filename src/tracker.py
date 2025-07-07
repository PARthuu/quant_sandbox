import json
from datetime import datetime
import os

EXPERIMENTS_DIR = "experiments"

os.makedirs(EXPERIMENTS_DIR, exist_ok=True)

def save_experiment(result: dict, tag: str = ""):
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{EXPERIMENTS_DIR}/experiment_{tag}_{now}.json"
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)