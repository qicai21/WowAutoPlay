import unittest
from pathlib import Path
from unittest import skip
from test.TestBase import FakeWowClient, ignorableTest
import sys

sys.path.append("..")


class ClientTest(unittest.TestCase):
    def setUp(self):
        self.client = FakeWowClient()

    def test_can_get_sysmbol_path_correctly(self):
        sysmbol_path = Path('./resources/img_templates/offline_tplt.jpg')
        self.assertTrue(sysmbol_path.exists())

    @ignorableTest
    def test_can_identify_offline_by_sysmbol(self):
        """请将带有蛇头的图片复制到‘fake_client.jpg’画图中。
        """
        offline_sysmbol = './resources/img_templates/offline_tplt.jpg'
        result = self.client.imageMatch(offline_sysmbol, (4, 1))
        self.assertTrue(result>15, f"matches is %d"%result)
        
    @skip
    def test_can_screenshots_apart(self):
        self.client.screenshot(4, 1)
        self.client.screenshot(4, 2)
        self.client.screenshot(4, 3)
        self.client.screenshot(4, 4)
        self.fail()
        
    @ignorableTest
    def test_can_identify_in_battleground_by_sysmbol(self):
        """copy in battle screenshot pic into fake_client.jpg MSPaintWindow
        """
        is_in_btlground_match = self.client.imageMatch('./resources/img_templates/in_btl_tplt.jpg',(1, 1))
        self.assertTrue(is_in_btlground_match>10, f"matchis %d"%is_in_btlground_match)
        
    def test_can_get_btn_pos_factor_in_config_json(self):
        pos = self.client.getBtnPosFactor('test_btn')
        _pos_x = 10/100
        _pos_y = 20/40
        self.assertEqual(pos, (_pos_x, _pos_y))

    def test_read_btn_json_return_dict(self):
        read = self.client.readBtnInfoFromJson()
        is_read_data_dict = type(read) == dict
        is_contain_right_data = 'join_queue_btn' in read
        self.assertTrue(is_read_data_dict and is_contain_right_data)


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

    @skip
    def test_can_match_right_img(self):
        self.getReady("正确匹配")
        result = self.client.imageMatch(self.sysmbol, (1, 1))
        print("匹配结果为%d"%result)
        self.assertTrue(result>10)

    @skip
    def test_cannot_match_wrong_img(self):
        self.getReady("错误匹配")
        result = self.client.imageMatch(self.sysmbol, (1, 1))
        print("匹配结果为%d"%result)
        self.assertFalse(result>10)