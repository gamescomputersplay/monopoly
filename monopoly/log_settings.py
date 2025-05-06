from pathlib import Path

from monopoly.log import Log

project_root = Path(__file__).resolve().parent
results_dir = project_root.parent / "results"


class LogSettings:
    KEEP_GAME_LOG = True
    EVENTS_LOG_PATH = results_dir / "events.log"
    BANKRUPTCIES_PATH = results_dir / "bankruptcies.tsv"

    @classmethod
    def init_logs(cls):
        """Initiate & reset both logs; return (events_log, bankruptcies_log)."""

        # 1) events log
        events_log = Log(cls.EVENTS_LOG_PATH, disabled=not cls.KEEP_GAME_LOG)
        events_log.reset("Events log")

        # 2) bankruptcies summary log
        bankruptcies_log = Log(cls.BANKRUPTCIES_PATH)
        bankruptcies_log.reset("game_number\tplayer_bankrupt\tturn")

        return events_log, bankruptcies_log
