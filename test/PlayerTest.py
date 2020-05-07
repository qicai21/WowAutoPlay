import unittest
import time
import pywintypes

import sys
sys.path.append("..")
from WowClient import WowClient
from Player import Player

def confirm_skip():
    """测试跳过"""
    return input("按P跳过本测试:\n") == "p"



class PlayerTest(unittest.TestCase):
    def setUp(self):
        try:
            print(self.player)
        except Exception as e:
            client_start = False
            while(not client_start):
                client_start = input("游戏准备好打1") == "1"
                if client_start:
                    break
                else:
                    time.sleep(5)
            client = WowClient()
            self.player = Player(client)

    @unittest.skipIf(confirm_skip(), confirm_skip.__doc__)
    def test_can_turn_around(self):
        """测试角色可以转一圈360"""
        self.player.turnaround()
        is_satisfy = input("效果还满意么？1:good, 2:bad")
        self.assertEqual(int(is_satisfy), 1) 

    @unittest.skipIf(confirm_skip(), confirm_skip.__doc__)
    def st_avoid_afk_is_satisfy(self):
        """测试防止掉线功能好用"""
        self.player.avoid_afk()
        is_satisfy = input("1:good, 2:bad")
        self.assertEqual(is_satisfy, 1) 

    @unittest.skipIf(confirm_skip(), confirm_skip.__doc__)
    def st_can_relogon(self):
        """测试角色断线后可以重新登录"""
        is_offline = self.player.checkOffline()
        if is_offline:
            self.player.reLogon()
            is_offline = self.player.checkOffline()
            self.assertFalse(is_offline)
        else:
            self.fail('识别为没断线')
    
    @unittest.skipIf(confirm_skip(), confirm_skip.__doc__)
    def test_can_logout(self):
        self.player.refreshWindow()
        time.sleep(3)
        self.player.logout()
        time.sleep(8)
        self.assertRaises(pywintypes.error, self.player.refreshWindow)
        