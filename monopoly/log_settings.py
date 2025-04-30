from pathlib import Path

project_root = Path(__file__).resolve().parent
results_dir = project_root.parent / "results"

class LogSettings:
    KEEP_GAME_LOG     = True
    EVENTS_LOG_PATH = results_dir / "events.log"
    BANKRUPTCIES_PATH = results_dir / "bankruptcies.tsv"