import unittest
from unittest import skip
from win32 import win32gui
import json
import time
from pathlib import Path
import sys

sys.path.append('..')
from ScriptManager import TxtScript, parseScriptFileToJson


def write_json_script_and_return_timestamp(filename):
    _t = time.localtime(time.time())
    time_stamp =  f"{_t.tm_hour}:{_t.tm_min}:{_t.tm_sec}"
    data = [
        {"integrated_action": ["focus_on_window", ""]},
        {"wait_action": ["wait_a_second", 1]},
        {"keyboard_action": ["typer", "it is %s," % time_stamp]},
        {"wait_action": ["wait_a_second", 1.5]},
        {"keyboard_action": ["pressHoldRelease", *("left_control", "s")]},
        {"wait_action": ["wait_a_second", 1]}
    ]
    with open(filename, 'w+') as f:
        json_data = json.dump(data, f)
    return time_stamp


class ScriptsTest(unittest.TestCase):
    """关于json脚本与python_engine的测试
    """
    def tearDown(self):
        if self.test_json_file.exists():
            Path.unlink(self.test_json_file)
        self.switch_to_terminal_window()
        return super().tearDown()

    def switch_to_terminal_window(self):
        if win32gui.GetForegroundWindow() == self.script.window:
            window2 = win32gui.FindWindow("ConsoleWindowClass", "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe")
            self.script.focus_on_window(window2)

    def setUp(self):
        self.test_json_file = Path('test_json_file.json')
        self.time_stamp = write_json_script_and_return_timestamp(str(self.test_json_file)) 
        self.script = TxtScript(str(self.test_json_file), loop_running=True)
        
    @skip
    def test_read_json_script(self):
        read = parseScriptFileToJson(str(self.test_json_file))
        self.assertIn("now is %s," % self.time_stamp, *read[2].values())

    @skip
    def test_focus_on_window_can_set_target_window_to_forgetground(self):
        self.script.focus_on_window()
        time.sleep(1)
        current_window = win32gui.GetForegroundWindow()
        self.assertEqual(current_window, self.script.window)

    @skip
    def test_script_work(self):
        self.script.singleTripScript()
        with open('test.txt', 'r') as f:
            read = f.readline()
            self.assertIn("it is %s," % self.time_stamp, read)

    @skip
    def test_start_script_running_control(self):
        self.script.start()
        self.assertEqual(self.script.is_running(), False)
        self.script.resume()
        self.assertEqual(self.script.is_running(), True)
        self.script.pause()
        time.sleep(6)
        self.assertEqual(self.script.is_running(), False)
        self.script.resume()
        self.assertEqual(self.script.is_running(), True)

    def test_reload_script(self):
        self.script.start()
        self.script.resume()
        time.sleep(10)
        new_time_stamp = write_json_script_and_return_timestamp(str(self.test_json_file))
        self.script.can_reload_script.wait()
        print(f"\n-----------current.script can_relaod status:{self.script.can_reload_script.isSet()}--------\n")
        self.script.pause()
        self.script.loadScript()
        self.script.resume()
        time.sleep(3)
        self.script.can_reload_script.wait()
        with open('test.txt', 'r') as f:
            read = f.read()
            self.assertIn(new_time_stamp, read)