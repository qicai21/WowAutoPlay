import unittest
from unittest import skip
import time
import json
import sys
sys.path.append('..')
from Laucher import Laucher
from ScriptManager import WowScript
from Player import Player
from test.TestBase import FakeWowClient


def write_json_script(script_name):
    data = [
        {"integrated_action": ["switch_out_and_refocus_on_window", ""]},
        {"wait_action": ["wait_a_second", 1]},
        {"keyboard_action": ["typer", "running:%s" % script_name]},
        {"wait_action": ["wait_a_second", 2]},
        {"keyboard_action": ["press", "enter"]},
        {"wait_action": ["wait_a_second", 1]},
        {"keyboard_action": ["pressHoldRelease", *("left_control", "s")]},
        {"wait_action": ["wait_a_second", 2]}
    ]
    file_path = "./%s.json" % script_name
    with open(file_path, 'w+') as f:
        json_data = json.dump(data, f)


class LaucherTest(unittest.TestCase):
    def test_click_start_btn_run_a_script(self):
        window = FakeWowClient()
        player = Player(window)
        script = WowScript('./scripts.json', player)
        laucher = Laucher(script)

        laucher.mainloop()
        # laucher.click_start_btn()
        # with open("log.txt", "r") as f:
        #     logs = f.readline()
        #     self.assertIn("hello", logs)
