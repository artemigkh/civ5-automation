import pywinauto
from pywinauto.application import Application
from pywinauto import Desktop
from pathlib import Path
import time
from datetime import timedelta
from datetime import datetime
import shutil
import pandas as pd
import logging
import numpy as np

from config import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("log.txt"),
        logging.StreamHandler()
    ]
)

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("log.txt"),
        logging.StreamHandler()
    ]
)

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("log.txt"),
        logging.StreamHandler()
    ]
)

log_patterns_to_save = [
    'TechAILog',
    'Score_Log',
    'GameResult_Log',
    'PolicyAILog',
    'ReligionLog',
]


class AutomatedGame:
    def __init__(self, cfg):
        self.install_dir = Path(cfg['install_dir'])
        if not self.install_dir.is_dir():
            logging.error(f'install directory {self.install_dir} not found')
            return
        self.civ5_executable = self.install_dir / "CivilizationV"

        self.local_dir = Path(cfg['local_dir'])
        if not self.local_dir.is_dir():
            logging.error(f'local directory {self.local_dir} not found')
            return

        self.logs_dir = self.local_dir / 'Logs'
        self.cache_dir = self.local_dir / 'cache'
        self.turn_timeout = config['turn_timeout']

        self.game_start_time = time.time()
        self.game_unique_dir_name = datetime.now().isoformat().replace(':', '.')

        self.civ5_app = None
        self.civ5_dlg = None
        self.game_window = None
        self.current_turn = 0

    def run_autoplay_game(self):
        self.clear_logs_dir()
        self.start_game()

        game_completed_successfully = self.wait_for_game_end()

        try:
            self.civ5_app.kill()
        except Exception as e:
            logging.warning(e)
            logging.warning('failed to kill running process')
        time.sleep(10)
        if game_completed_successfully:
            self.save_old_data()
        else:
            self.save_failed_game_debug_files()

        return game_completed_successfully

    def clear_logs_dir(self):
        shutil.rmtree(self.logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def start_game(self):
        self.civ5_app = Application(backend="uia").start(str(self.civ5_executable))
        while self.civ5_app.is_process_running():
            logging.info("waiting for launched process to start...")
            time.sleep(1)

        logging.info("connecting to Sid Meier's Civilization V (DX9)")
        self.civ5_app = Application().connect(title="Sid Meier's Civilization V (DX9)", timeout=120)
        logging.info("connected!")

        self.civ5_dlg = self.civ5_app.top_window()
        self.game_window = self.civ5_dlg.wrapper_object()

    def get_turn(self):
        try:
            progress_log_df = pd.read_csv(self.logs_dir / 'WorldState_Log.csv')
            if progress_log_df.shape is not None and progress_log_df.shape[0] > 0:
                if type(progress_log_df.iloc[-1]['Turn']) == np.int64:
                    return progress_log_df.iloc[-1]['Turn']
                else:
                    logging.warning(f"Got non-integer turn type {type(progress_log_df.iloc[-1]['Turn'])}")
                    return 0
            else:
                return 0
        except Exception as e:
            logging.warning(e)
            logging.warning("Could not get current turn")
            return 0

    def wait_for_game_end(self):
        start = time.time()
        last_turn = 0
        last_turn_time = start

        while not (self.logs_dir / 'GameResult_Log.csv').is_file():
            if not self.civ5_app.is_process_running():
                logging.error('Game process has crashed :(')
                return False

            now = time.time()
            logging.info(f'waiting for game to end... (time elapsed: {timedelta(0, now - start)})')

            self.current_turn = self.get_turn()
            logging.info(f'Current turn is {self.current_turn}')

            if self.current_turn > last_turn:
                last_turn = self.current_turn
                last_turn_time = now
            else:
                turn_time = now - last_turn_time
                logging.info(f'{turn_time} seconds has elapsed since the start of the last turn')
                if turn_time > self.turn_timeout:
                    logging.error('Game process has hung (turn took too long)')
                    return False

            time.sleep(10)
        logging.info("game has ended\n\n================================\n\n")
        return True

    def save_old_data(self, data_suffix=''):
        logging.info("saving game data...")
        loc = self.local_dir / 'complete' / (self.game_unique_dir_name + data_suffix)
        loc.mkdir(parents=True, exist_ok=True)
        shutil.make_archive(loc / 'logs', 'zip', root_dir=self.logs_dir, base_dir='.')
        shutil.copyfile(self.cache_dir / 'Civ5DebugDatabase.db', loc / 'Civ5DebugDatabase.db')
        for file in self.logs_dir.iterdir():
            for lp in log_patterns_to_save:
                if lp in str(file):
                    shutil.copyfile(file, loc / file.name)

        most_recent_save = self.get_most_recent_save_file()
        if most_recent_save is not None:
            logging.info(f'Saving most recent autosave: {most_recent_save}')
            shutil.copyfile(most_recent_save, loc / most_recent_save.name)

        # Save map terrain file
        shutil.copyfile(self.install_dir / 'Maps' / 'Civ5MapmapState_Turn000.Civ5Map', loc / 'Civ5MapmapState_Turn000.Civ5Map')

        logging.info("finished saving game data")

    def get_most_recent_save_file(self):
        save_file_dir = self.local_dir / 'Saves' / 'single' / 'auto'
        if save_file_dir.is_dir():
            return max(save_file_dir.glob('*'), key=lambda p: p.stat().st_ctime)
        else:
            logging.warning("Could not find autosave file directory")
            return None

    def save_failed_game_debug_files(self):
        logging.info("saving failed game debug files...")
        loc = self.local_dir / 'failed' / datetime.now().isoformat().replace(':', '.')
        loc.mkdir(parents=True, exist_ok=True)

        minidump_file = self.install_dir / 'CvMiniDump.dmp'
        if minidump_file.is_file():
            if minidump_file.stat().st_mtime < self.game_start_time:
                logging.info("Minidump was from a previous game, ignoring")
            else:
                shutil.copyfile(minidump_file, loc / minidump_file.name)

        most_recent_save = self.get_most_recent_save_file()
        if most_recent_save is not None:
            logging.info(f'Saving most recent autosave: {most_recent_save}')
            shutil.copyfile(most_recent_save, loc / most_recent_save.name)

        logging.info("finished saving failed game debug files")


def main():
    success_count = 0
    while success_count < config['runs_count']:
        print(f'starting game #{success_count + 1}')
        automated_game = AutomatedGame(config)
        game_completed_successfully = automated_game.run_autoplay_game()
        if game_completed_successfully:
            success_count += 1


if __name__ == '__main__':
    main()
