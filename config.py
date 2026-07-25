from pathlib import Path

# Project root = mission-copilot/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Standard folders
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
MISSIONS_DIR = PROJECT_ROOT / "missions"

# Ensure folders exist
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
MISSIONS_DIR.mkdir(exist_ok=True)

# Define mission scenario as one of 'earth_observation', 'lunar_exploration', or 'deep_space'
mission = 'deep_space'
