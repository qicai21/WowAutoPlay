#!/usr/bin/env python
# coding: utf-8

import random
import time
import win32con
import win32api
import json
import keybdAct

from WaitAndOption import shortRest, longRest, roundWait

class Player():
    
    def __init__(self, wow_window):
        self.alive = "alive"
        self.in_battle = False
        self.in_sequence = False
        self.poistion = "unknow"
        self.window = wow_window
        config = self.read_config()
        self.tarQueueNpc = config['queue_npc']
        self.tarHonorNpc = config['honor_npc']
        self.interactBtn = config['interact_btn']
        self.btnBarNumber = config['btn_bar']
        self.quitGameBtn = config['quit_game']
        self.reloadBtn = config['reload_btn']
        if self.quitGameBtn == '=':
            self.quitGameBtn = '+'
        
    def read_config(self):
        with open('config.json', 'r') as f:
            config = json.load(f)
            return config
    
    def avoid_afk(self):
        # 防止掉线
        r = random.randint(0, 7)
        keybdAct.press("spacebar")
        print('嗯，跳一跳，地好烫')
        longRest()

    def reSelectBtnBar(self):
        keybdAct.pressHoldRelease("shift", self.btnBarNumber)
        shortRest()

    def openDoor(self):
        (x, y) = self.window.getBtnPos('gnomeregan_door')
        keybdAct.press('`')
        longRest(3)
        keybdAct.press('s', 0.15)
        win32api.SetCursorPos((x, y))
        shortRest(2)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)    # 鼠标左键按下
        shortRest(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)    # 鼠标左键弹起
        shortRest(5)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)    # 鼠标左键按下
        shortRest(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)    # 鼠标左键弹起

    def postHonormark(self, battlefield):
        # 需要提供战场名称，alx or warsong。
        btn_name = None
        if battlefield == "alx" or battlefield == "ALX":
            btn_name = "alx_honormark_btn"
        elif battlefield == "warsong" or battlefield == "zg":
            btn_name = "warsong_honormark_btn"
        else:
            raise Exception("战场名称不对")

        # 选择要交的章
        (x1, y1) = self.window.getBtnPos(btn_name)
        win32api.SetCursorPos((x1, y1))
        shortRest()
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x1, y1, 0, 0)    # 鼠标左键按下
        shortRest()
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x1, y1, 0, 0)    # 鼠标左键弹起
        longRest()

        # 交章
        (x2, y2) = self.window.getBtnPos('post_honormark_btn')
        win32api.SetCursorPos((x2, y2))
        shortRest()
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x2, y2, 0, 0)    # 鼠标左键按下
        shortRest()
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x2, y2, 0, 0)    # 鼠标左键弹起
        longRest()
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x2, y2, 0, 0)    # 鼠标左键按下
        shortRest()
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x2, y2, 0, 0)    # 鼠标左键弹起
        shortRest()

    def right_click(self, pos):
        (x, y) = self.window.getBtnPos(tuple(pos))
        win32api.SetCursorPos((x, y))
        shortRest()
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)    # 鼠标左键按下
        shortRest()
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)    # 鼠标左键弹起
        shortRest()
 
    def checkOffline(self):
        offline_sysmbol = './resources/img_templates/offline_tplt.jpg'
        result = self.window.imageMatch(offline_sysmbol, (4, 1))
        print(f'执行了断线检查, 匹配结果为:{result}')
        return result > 10

    def reLogon(self):
        # 先离线关闭
        is_wow_window_alive = True
        while is_wow_window_alive:
            self.window.focus_on_window()
            longRest()
            keybdAct.pressHoldRelease('alt', 'F4')
            longRest()
            self.window.getWowWindow()
            is_wow_window_alive = self.window.window != None

        print("关闭所有wow窗口")

        # 再登陆
        while not is_wow_window_alive:
            laucher = self.window.getLaucherWindow()
            self.window.focus_on_window(laucher)
            longRest()
            keybdAct.press('enter')
            print("从登陆器执行了登录")

            longRest(30)
            self.window.getWowWindow()
            is_wow_window_alive = self.window.window != None
        # 检查是否登录到了人物选择页面，如果没有就等待，可能是排队了
        # 取消掉是否登录到游戏人物界面检验，因为是断线重连
        # is_in_player_select = self.checkInPlaySelectStatus()
        # _time = 30
        # while not is_in_player_select:
        #     longRest(_time)
        #     if _time < 60*5:
        #         _time += 30
        #     is_in_player_select = self.checkInPlaySelectStatus()

        keybdAct.press('enter')
        print("登录游戏")
        longRest(20)

    def logout(self):
        keybdAct.press(self.quitGameBtn)

    def checkInDungeon(self):
        sysmbol = './resources/img_templates/in_gnomeregan_tplt.jpg'
        result = self.window.imageMatch(sysmbol, (4, 1))
        print(f'进入副本匹配,匹配结果为:{result}')
        return result > 10

    def check_combat(self):
        sysmbol = './resources/img_templates/in_combat.jpg'
        result = self.window.imageMatch(sysmbol, (4,1))
        print(f'检擦是否有铅笔小怪，结果{result}')
        return result > 10

    def checkDragonHeadBuff(self):
        sysmbol = './resources/img_templates/dragon_slayer_buff_tplt.jpg'
        result = self.window.imageMatch(sysmbol, (4, 1))
        print(f'龙头buff匹配, 匹配结果为:{result}')
        return result > 10

    def checkChiefRegardsBuff(self):
        sysmbol = './resources/img_templates/chief_regards_buff_tplt.jpg'
        result = self.window.imageMatch(sysmbol, (4, 1))
        print(f'酋长祝福匹配, 匹配结果为:{result}')
        return result > 10

    def checkInPlaySelectStatus(self):
        sysmbol = './resources/img_templates/player_select_tplt.jpg'
        result = self.window.imageMatch(sysmbol, (3, 2))
        print(f'执行了人物登录页面匹配, 匹配结果为:{result}')
        return result > 10

    def checkInBattlefield(self):
        in_battle_sysmbol = './resources/img_templates/in_btl_tplt.jpg'
        result = self.window.imageMatch(in_battle_sysmbol, (4, 1))
        print(f'执行了在战场匹配, 匹配结果为:{result}')
        return result > 10

    def checkAlive(self):
        alive_sysmbol = './resources/img_templates/is_alive_tplt.jpg'
        result = self.window.imageMatch(alive_sysmbol, (4, 1))
        print(f'执行了存活匹配, 匹配结果为:{result}')
        return result > 10

    def check_combat_and_attack(self):
        r = 2 # 只做2次
        while self.check_combat():
            time.sleep(5)
            keybdAct.press('\\', 0.03)
            if r > 0:
                keybdAct.press('s', 0.03)
                r -= 1
            time.sleep(15)

    def attackLoop(self, duration, force_to_target=False):
        """attacking by second, eg: duration=20s"""
        start = time.time()
        r = True
        bass = 8
        f = 0
        while r:
            keybdAct.press("2")
            shortRest(1.5)
            keybdAct.press("3")
            shortRest(1.5)
            if f % bass == 1:
                keybdAct.press("\\")
                shortRest()
                bass -= 1
            f += 1
            r = time.time() - start < duration

    def clickReloadBtn(self):
        keybdAct.press(self.reloadBtn)
        longRest(10)


    def turnaround(self, how=360):
        btn = 'd'
        if how > 180 and how < 360:
            btn = 'a'
            how = 360 - how

        keybdAct.pressAndHold(btn)
        t = 1.98 * how/360
        time.sleep(t)
        keybdAct.release(btn)

    def refreshWindow(self):
        self.window.refresh_window()
        self.window.focus_on_window()

    def go_stright(self, t=0):
        keybdAct.pressAndHold('w')
        time.sleep(t)
        keybdAct.release('w')

    def interact(self):
        keybdAct.press(self.interactBtn)

    def jump_continue(self, t=10):
        keybdAct.pressAndHold('w', 'a')
        shortRest()
        keybdAct.press('spacebar')
        longRest()
        keybdAct.press('spacebar')
        shortRest()
        keybdAct.release('w','a')

        longRest()

        keybdAct.pressAndHold('w', 'd')
        shortRest()
        keybdAct.press('spacebar')
        longRest()
        keybdAct.press('spacebar')
        shortRest()
        keybdAct.press('spacebar')
        longRest()
        keybdAct.press('spacebar')
        longRest()
        keybdAct.press('spacebar')
        longRest()
        keybdAct.press('spacebar')
        longRest()
        keybdAct.release('w','d')

