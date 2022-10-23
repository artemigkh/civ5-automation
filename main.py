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
    'GameResult_Log'
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

        self.fire_tuner_executable = Path(cfg['fire_tuner_executable'])
        if not self.fire_tuner_executable.is_file():
            logging.error(f'firetuner executable {self.fire_tuner_executable} not found')
            return

        self.logs_dir = self.local_dir / 'Logs'
        self.cache_dir = self.local_dir / 'cache'
        self.application_load_screen_duration = config['application_load_screen_duration']
        self.game_load_screen_duration = config['game_load_screen_duration']
        self.turn_timeout = config['turn_timeout']
        self.screen_width = config['screen_width']
        self.ff = 15

        self.game_start_time = time.time()
        self.game_unique_dir_name = datetime.now().isoformat().replace(':','.')

        self.civ5_app = None
        self.civ5_dlg = None
        self.game_window = None
        self.fire_tuner_app = None
        self.fire_tuner_dlg = None
        self.current_turn = 0

    def run_autoplay_game(self):
        game_completed_successfully = False
        last_failed_turn = -1
        
        while not game_completed_successfully:
            self.clear_logs_dir()
            self.start_game()
            
            if last_failed_turn > 0:
                self.continue_from_last_saved_game()
            else:
                self.start_game_from_main_menu()
                self.start_autoplay()

            game_completed_successfully = self.wait_for_game_end()

            try:
                self.civ5_app.kill()
                self.fire_tuner_app.kill()
            except Exception as e:
                logging.warning(e)
                logging.warning('failed to kill running processes')
            time.sleep(10)
            if game_completed_successfully:
                self.save_old_data()
            else:
                if self.current_turn > last_failed_turn:
                    logging.info(f'Failed on a new turn - attemping to restart and continue from latest autosave')
                    self.save_old_data(data_suffix=f'-{self.current_turn}')
                    last_failed_turn = self.current_turn
                else:
                    logging.error("Failed on the same turn twice in a row. Saving crash info and starting next game")
                    self.save_failed_game_debug_files()
                    return False
        return True
    
    def debug_run(self):
        self.civ5_app = Application().connect(title="Sid Meier's Civilization V (DX9)", timeout=120)
        self.civ5_dlg = self.civ5_app.top_window()
        logging.info(self.civ5_dlg.client_rect().height)
        self.civ5_dlg.move_window(x=self.screen_width - 1024)
        self.game_window = self.civ5_dlg.wrapper_object()
        self.continue_from_last_saved_game()
        
        
    
    def continue_from_last_saved_game(self):
        logging.info("Continuing from most recent autosave game from main menu")
        self.click_first_menu_option()
        time.sleep(2)
        self.click_third_menu_option()
        time.sleep(2)
        self.click_autosaves_button()
        time.sleep(2)
        self.click_topmost_save_entry()
        time.sleep(2)
        self.click_load_game_button()
        self.start_game_from_game_loadscreen()
        
    
    def clear_logs_dir(self):
        shutil.rmtree(self.logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def click_first_menu_option(self):
        logging.info("clicking first menu option")
        self.game_window.click_input(button='right', pressed='', coords=(512, 280+self.ff))
        time.sleep(1)
        self.game_window.click_input(button='left', pressed='', coords=(512, 280+self.ff))
        
    def click_third_menu_option(self):
        logging.info("clicking third menu option")
        self.game_window.click_input(button='right', pressed='', coords=(512, 370+self.ff))
        time.sleep(1)
        self.game_window.click_input(button='left', pressed='', coords=(512, 370+self.ff))
        
    def click_autosaves_button(self):
        logging.info("clicking autosaves button")
        self.game_window.click_input(button='right', pressed='', coords=(927, 188+self.ff))
        time.sleep(1)
        self.game_window.click_input(button='left', pressed='', coords=(927, 188+self.ff))
        
    def click_topmost_save_entry(self):
        logging.info("clicking topmost save entry")
        self.game_window.click_input(button='right', pressed='', coords=(730, 265+self.ff))
        time.sleep(1)
        self.game_window.click_input(button='left', pressed='', coords=(730, 265+self.ff))
        
    def click_load_game_button(self):
        logging.info("clicking load game button")
        self.game_window.click_input(button='right', pressed='', coords=(830, 700+self.ff))
        time.sleep(1)
        self.game_window.click_input(button='left', pressed='', coords=(830, 700+self.ff))
        
    def start_game_from_game_loadscreen(self):
        logging.info(f"waiting {self.game_load_screen_duration} seconds for load screen to complete")
        time.sleep(self.game_load_screen_duration)
        self.game_window.send_keystrokes("{ENTER}")
        time.sleep(5)
        self.game_window.send_keystrokes("{ENTER}")
        logging.info(f"game has started")

    def start_game_from_main_menu(self):
        logging.info("starting game from main menu")
        self.click_first_menu_option()
        time.sleep(3)
        self.click_first_menu_option()
        self.start_game_from_game_loadscreen()

    def start_game(self):
        self.civ5_app = Application(backend="uia").start(str(self.civ5_executable))
        while self.civ5_app.is_process_running():
            logging.info("waiting for launched process to start...")
            time.sleep(1)

        logging.info("connecting to Sid Meier's Civilization V (DX9)")
        self.civ5_app = Application().connect(title="Sid Meier's Civilization V (DX9)", timeout=120)
        logging.info("connected!")

        logging.info(f"waiting {self.application_load_screen_duration} seconds for load screen to complete")
        time.sleep(self.application_load_screen_duration)

        logging.info("in main menu")

        self.civ5_dlg = self.civ5_app.top_window()
        self.civ5_dlg.move_window(x=self.screen_width - 1024)
        self.game_window = self.civ5_dlg.wrapper_object()

    def start_autoplay(self):
        logging.info("launching firetuner")
        self.fire_tuner_app = Application(backend="uia").start(str(self.fire_tuner_executable))
        self.fire_tuner_dlg = self.fire_tuner_app.top_window()
        logging.info("starting autoplay...")
        autoplay_button = self.fire_tuner_dlg['Autoplay 1']
        autoplay_button.wait("exists enabled visible ready")
        autoplay_button.click_input()
        logging.info("autoplay started")
        time.sleep(10)
        autoplay_button.click_input()  # sometimes the first time doesn't work?

    def get_turn(self):
        try:
            progress_log_df = pd.read_csv(self.logs_dir / 'WorldState_Log.csv')
            if progress_log_df.shape is not None and progress_log_df.shape[0] > 0:
                return progress_log_df.iloc[-1]['Turn']
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

            time.sleep(60)
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
	while success_count < 999:
	    print(f'starting game #{success_count+1}')
	    automated_game = AutomatedGame(config)
	    game_completed_successfully = automated_game.run_autoplay_game()
	    if game_completed_successfully:
	        success_count += 1


if __name__ == '__main__':
    main()