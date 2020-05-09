import unittest
import time
import pywintypes

import sys
sys.path.append("..")
from WowClient import WowClient
from Player import Player
from test.TestBase import ignorableTest


class PlayerTest(unittest.TestCase):

    @ignorableTest
    def test_player_can_turn_around(self):
        """测试角色可以转一圈360,请先上线"""
        self.player.turnaround()
        is_satisfy = input("效果还满意么？1:good, 2:bad")
        self.assertEqual(int(is_satisfy), 1) 

    @ignorableTest
    def test_can_relogon(self):
        """测试角色断线后可以重新登录,
            请断掉WiFi，等候角色离线后再开启WiFi
        """
        is_offline = self.player.checkOffline()
        if is_offline:
            self.player.reLogon()
            is_offline = self.player.checkOffline()
            self.assertFalse(is_offline)
        else:
            self.fail('识别为没断线')
    