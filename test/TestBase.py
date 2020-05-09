import unittest
import os
from WowClient import WowClient
import time
import pathlib
import win32api
import win32gui
from keybdAct import *
from KeyboardRecorder import KeyboardRecorder as kybd


# 遍历路径下所有文件中的test，暂时不用
class RunCase(unittest.TestCase):
    def _test_case(self):
        case_path = os.getcwd() #case所在路径
        discover = unittest.defaultTestLoader.discover(case_path,pattern="test_*.py")
        runner = unittest.TextTestRunner(verbosity=2)
        # runner.run(discover)
        test_unit = unittest.TestSuite()
        for test_suite in discover:
            for test_case in test_suite:
                test_unit.addTest(test_case)
        runner.run(test_unit)
        

class FakeWowClient(WowClient):
    """ 通过打开画图，并命名为fake_client.jpg，伪造一个游戏窗口，然后进行图标检测。
        这需要进行一些手动配置，图片设置好了之后按1开始测试.:w
    """
    def __init__(self):
        self.window = win32gui.FindWindow("MSPaintApp", "fake_client.jpg - 画图")
        self.refresh_window()


def ignorableTest(test_func):
    def wrapper(*args, **kwargs):
        print(f"\n将运行{test_func.__name__}: \n{test_func.__doc__}\n")
        print("跳过请按p，任意键执行测试")
        if input() != "p":
            test_func(*args, **kwargs)
    return wrapper