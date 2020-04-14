import unittest
import os
from WowClient import WowClient, Player
import time
import win32api
 

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
        
        
class ClientTest(unittest.TestCase):
    def setUp(self):
        self.client = WowClient()
        
    def can_screenshots_apart(self):
        self.client.screenshot(4, 1)
        self.client.screenshot(4, 2)
        self.client.screenshot(4, 3)
        self.client.screenshot(4, 4)
        self.fail()
        
        
    def test_can_identify_in_battleground_or_not(self):
        is_in_btlground = self.client.inBattlegroundOrNot()
        self.assertTrue(is_in_btlground)
        
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
        
    def test_shortrest_lessthan_06(self):
        start = time.time()
        self.player.shortrest()
        wait = time.time() - start
        self.assertTrue(wait<0.6)
        
if __name__=='__main__':
    unittest.main()
