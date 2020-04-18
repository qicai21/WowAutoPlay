import unittest
import os
from WowClient import WowClient
from Player import Player
import time
import pathlib
import win32api
import win32gui
import pywintypes
 

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
    def __init__(self):
        WowClient.__init__(self)
        self.window = win32gui.FindWindow("MSPaintApp", "fake_client.jpg - 画图")
        self.refresh_window()

class ImageMatchTest(unittest.TestCase):
    def setUp(self):
        self.client = FakeWowClient()
        self.sysmbol = './resources/img_templates/player_select_tplt.jpg'

    def getReady(self, msg): 
        read = False
        while not read:
            _input = input(f"进行{msg}测试,输入1开始")
            if _input == '1':
                read = True

    def test_can_match_right_img(self):
        self.getReady("正确匹配")
        result = self.client.imageMatch(self.sysmbol, (1, 1))
        print("匹配结果为%d"%result)
        self.assertTrue(result>10)

    def test_cannot_match_wrong_img(self):
        self.getReady("错误匹配")
        result = self.client.imageMatch(self.sysmbol, (1, 1))
        print("匹配结果为%d"%result)
        self.assertFalse(result>10)

class ClientTest(unittest.TestCase):
    def setUp(self):
        self.client = FakeWowClient()
    
    def test_can_identify_offline(self):
        offline_sysmbol = './resources/img_templates/offline_tplt.jpg'
        result = self.client.imageMatch(offline_sysmbol, (4, 1))
        self.assertTrue(result>50, f"matches is %d"%result)
        
        
    def can_screenshots_apart(self):
        self.client.screenshot(4, 1)
        self.client.screenshot(4, 2)
        self.client.screenshot(4, 3)
        self.client.screenshot(4, 4)
        self.fail()
        
    def st_can_identify_in_battleground_or_not(self):
        is_in_btlground_match = self.client.imageMatch('./resources/img_templates/in_btl_tplt.jpg',(1, 1))
        self.assertTrue(is_in_btlground_match>10, f"matchis %d"%is_in_btlground_match)
        
    def test_can_get_btn_pos_factor(self):
        pos = self.client.getBtnPosFactor('test_btn')
        _pos_x = 10/100
        _pos_y = 20/40
        self.assertEqual(pos, (_pos_x, _pos_y))

    def test_read_btn_json_return_dict(self):
        read = self.client.readBtnInfoFromJson()
        is_read_data_dict = type(read) == dict
        is_contain_right_data = 'join_queue_btn' in read
        self.assertTrue(is_read_data_dict and is_contain_right_data)

class PlayerTest(unittest.TestCase):
    def setUp(self):
        client = WowClient()
        self.player = Player(client)
        
    def st_can_turn_around(self):
        self.player.do()

        self.player.jump_continue()

        is_satisfy = input("1:good, 2:bad")
        self.assertEqual(int(is_satisfy), 1) 

    def st_avoid_afk_is_satisfy(self):
        self.player.avoid_afk()
        is_satisfy = input("1:good, 2:bad")
        self.assertEqual(is_satisfy, 1) 

    def st_can_relogon(self):
        is_offline = self.player.checkOffline()
        if is_offline:
            self.player.reLogon()
            is_offline = self.player.checkOffline()
            self.assertFalse(is_offline)
        else:
            self.fail('识别为没断线')
    
    def st_can_logout(self):
        self.player.refreshWindow()
        time.sleep(3)
        self.player.logout()
        time.sleep(8)
        self.assertRaises(pywintypes.error, self.player.refreshWindow)
        

if __name__=='__main__':
    unittest.main()
