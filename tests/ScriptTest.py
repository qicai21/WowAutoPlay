import unittest
from unittest import skip
from win32 import win32gui
import json
import time
from pathlib import Path
import sys

sys.path.append('..')
from ScriptManager import TxtScript, parseScriptFileToJson
from Expiration import createExpiredHash


def write_json_script_and_return_timestamp(filename):
    _t = time.localtime(time.time())
    time_stamp =  f"{_t.tm_hour}:{_t.tm_min}:{_t.tm_sec}"
    data = [
        {"integrated_action": ["swith_out_and_refocus_on_window", ""]},
        {"keyboard_action": ["typer", f"{filename}: {time_stamp},"]},
        {"wait_action": ["wait_a_second", 1]},
        {"keyboard_action": ["pressHoldRelease", *("left_control", "s")]},
        {"wait_action": ["wait_a_second", 1]}
    ]
    with open(filename, 'w+') as f:
        json_data = json.dump(data, f)
    return time_stamp

def create_fake_config_json(json1=None, json2=None):
    if not json1:
        json1 = "test1.json"
    if not json2:
        json2 = "test2.json"
    t_ = time.mktime((2020, 5, 31, 10, 0, 0, -1, -1, -1))
    h_ = createExpiredHash(t_)
    configs = {
        "enable_scripts": {
            "test_1": json1,
            "test_2": json2
        },
        "expired_hash": h_
    }
    with open("test_config.json", 'w+') as f:
        json.dump(configs, f)


class ScriptsTest(unittest.TestCase):
    """关于json脚本与python_engine的测试
    """
    def tearDown(self):
        time.sleep(2)
        for f in self.to_destorys_files:
            p = Path(f)
            if p.exists():
                Path.unlink(p)
        self.switch_to_terminal_window()
        return super().tearDown()

    def switch_to_terminal_window(self):
        if win32gui.GetForegroundWindow() == self.script.window:
            window2 = win32gui.FindWindow("ConsoleWindowClass", "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe")
            self.script.focus_on_window(window2)
            time.sleep(1)

    def setUp(self):
        self.test_json_file = 'test_json_file.json'
        self.to_destorys_files = []
        self.to_destorys_files.append(self.test_json_file)
        self.time_stamp = write_json_script_and_return_timestamp(self.test_json_file)
        self.script = TxtScript(str(self.test_json_file), loop_running=True)
        
    def test_get_scripts_name_and_path_dict_from_config_json(self):
        self.script.read_config()
        expected_dict = {
            "战歌峡谷": "Warsong.json",
            "阿拉希": "Arathi.json",
            "奥山": "Alterac.json",
            "诺莫瑞根": "Gnomeregan.json",
            "世界buff": "WorldBuff.json"
        }
        scripts = self.script.configs['enable_scripts']
        self.assertDictEqual(expected_dict, scripts)

    def test_scriptbase_check_expired(self):
        t_right = time.mktime((2020, 5, 31, 10, 0, 0, -1, -1, -1))
        t_wrong = time.mktime((2020, 5, 31, 10, 22, 0, -1, -1, -1))

        h_right = createExpiredHash(t_right)
        h_wrong = createExpiredHash(t_wrong)
        self.assertTrue(self.script.check_in_expiration(h_right))
        self.assertFalse(self.script.check_in_expiration(h_wrong))

    def test_focus_on_window_can_set_target_window_to_forgetground(self):
        self.script.focus_on_window()
        time.sleep(1)
        current_window = win32gui.GetForegroundWindow()
        self.assertEqual(current_window, self.script.window)

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

    def test_running_switch_func(self):
        json1 = "test1.json"
        json2 = "test2.json"
        write_json_script_and_return_timestamp(json1)
        write_json_script_and_return_timestamp(json2)
        create_fake_config_json(json1, json2) # 生成一个交test_config.json的临时config文件
        self.to_destorys_files += [json1, json2, "test_config.json"]
        self.script.read_config('test_config.json')

        self.script.start()
        self.script.running_switch("test_1") # 启动1号脚本运行
        time.sleep(6)
        self.script.running_switch("test_1") # 停止1号脚本运行
        time.sleep(1)
        with open('test.txt', 'r') as f:
            read = f.read()
            self.assertIn(json1, read)

        self.script.running_switch("test_2") # 启动2号脚本运行
        time.sleep(6)
        self.script.running_switch("test_2") # 停止2号脚本运行
        time.sleep(1)
        with open('test.txt', 'r') as f:
            read = f.read()
            self.assertIn(json2, read)
 
    @skip
    def test_reload_script(self):
        self.script.start()
        self.script.resume()
        time.sleep(10)
        new_time_stamp = write_json_script_and_return_timestamp(str(self.test_json_file))
        self.script.can_reload_script.wait()
        # print(f"\n-----------current.script can_relaod status:{self.script.can_reload_script.isSet()}--------\n")
        self.script.pause()
        self.script.loadScript()
        self.script.resume()
        time.sleep(3)
        self.script.can_reload_script.wait()
        self.script.pause()
        with open('test.txt', 'r') as f:
            read = f.read()
            self.assertIn(new_time_stamp, read)