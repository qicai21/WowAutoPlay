import time
import random
import json
import re
import threading
import tkinter as tk
from tkinter import *
from enum import Enum
from win32 import win32gui
from pywintypes import error
import win32com.client as client
import pythoncom

import keybdAct
from WowClient import WowClient
from Player import Player
from WaitAndOption import shortRest, longRest, roundWait, waitingInNewBattle, druidStealWalkingInBattle
from Expiration import checkByExpiredHash
from logWrapper import log


# 每5次执行一起重新登录检验
# 这是一个cheat，最好还是放在config中
MODE = "test"
DEFAULT_TRIGGER_BASE = 5
SCRIPTSFILE ='./scripts.json' 

class PlayStatus(Enum):
    # 在大厅未排队
    # 在大厅排队了
    # 进战场第一轮
    # 在战场持续中
    new_to_hall = 0
    queueing_in_hall = 1
    new_to_battlefield = 2
    play_in_battlefield = 3

def getAllActiveWindow():
    titles = set()
    def window_filter(hwnd, mouse):
        if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
            titles.add(win32gui.GetWindowText(hwnd) + "   " +\
                win32gui.GetClassName(hwnd))
    win32gui.EnumWindows(getAllActiveWindow, 0)
    return titles

def parseScriptFileToJson(filepath):
    """ Parse a JSON file
        First remove comments and then use the json module package
        Comments look like :
            // ...
        or
            /*
            ...
            */
    """
    comment_re = re.compile('(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
                            re.DOTALL | re.MULTILINE)
    with open(filepath, 'r', encoding='utf8') as f:
            content = ''.join(f.readlines())
            ## Looking for comments
            match = comment_re.search(content)
            while match:
                # single line comment
                content = content[:match.start()] + content[match.end():]
                match = comment_re.search(content)
    
            return json.loads(content)


class PeriodTrigger():
    def __init__(self, trigger_base):
        self.cursor = 0        
        self.trigger_base = trigger_base 

    def go_a_step(self):
        self.cursor = self.cursor % self.trigger_base + 1

    def activated(self):
        return self.cursor == 1


class ScriptBase(threading.Thread):
    """ 调用外部脚本（jsonfile），安全的线程运行。内置了周期性触发器和定时执行器，可单程运行，也可循环运行。

        period_trigger: '=on/off',触发器,可以周期性的执行脚本片段或指定方法, 
                        如果为on,则需要另提供trigger_base参数，int类型, 以“1/base”模式运行.

        loop_running: '=True/False',循环或单程执行
        
        running_time: '=None/time[%Y%m%d/%H:%M]', 定时执行，为None则不检查执行时间
    """
    def __init__(self, script_file, period_trigger='off', loop_running=True, running_time=None, *args, **kwargs):
        super(ScriptBase, self).__init__()
        self.script_file = script_file
        self.set_period_trigger(period_trigger, **kwargs)
        self.loop_running = loop_running
        self.running_time = running_time
        self.can_go_on = threading.Event()
        self.can_reload_script = threading.Event()
        self.can_reload_script.set()
        self.loadScript()
        self.setDaemon(True)

    def set_period_trigger(self, period_trigger, **kwargs):
        if period_trigger == 'on':
            try:
                trigger_base = kwargs['trigger_base']
            except KeyError as e:
                trigger_base = DEFAULT_TRIGGER_BASE
            self.period_trigger = PeriodTrigger(trigger_base)
        else:
            self.period_trigger = None

    def pause(self):
        self.can_go_on.clear()

    def resume(self):
        self.can_go_on.set()

    def is_running(self):
        return self.can_go_on.isSet()

    def loadScript(self):
        while(not self.is_running()):
            self.script_json = parseScriptFileToJson(self.script_file)
            return 
    
    def run_json_script_command(self, json_script):
        self.can_go_on.wait()
        action_type = list(json_script.keys())[0]
        action_name = json_script[action_type][0]
        action_param = json_script[action_type][1]
        action_comment = json_script[action_type][-1]

        if MODE != "test" and action_comment != None and action_comment != "":
            print(action_comment)

        if action_type == "keyboard_action":
            _func = getattr(keybdAct, action_name)
            if _func == keybdAct.press:
                _func(action_param, action_comment)
            if _func == keybdAct.pressHoldRelease:
                _func(*json_script[action_type][1:])
            else:
                _func(action_param)

        elif action_type == "wait_action":
            if action_name == "short_random_wait":
                shortRest()
            else:
                time.sleep(action_param)

        elif action_type == "integrated_action":
            self.__getattribute__(action_name)()
        
        else:
            print('bad script json command:' + action_type)
            return

    def singleTripScript(self):
        """需要被重写的方法， 完整的单循环"""
        raise NotImplementedError()
       
    def runSingleTripScriptAndBlockScriptReload(self):
        self.can_go_on.wait()
        self.can_reload_script.clear()
        self.singleTripScript()
        self.can_reload_script.set()
        time.sleep(1)

    def run(self):
        goon = True
        while goon:
            self.runSingleTripScriptAndBlockScriptReload()
            goon = self.loop_running

class WindowScript(ScriptBase):
    def __init__(self, script_file, window_class, window_name, 
                 period_trigger='off', loop_running=True, running_time=None, *args, **kwargs):
        """window_class:eg "Notepad",
            window_name: eg "test.txt - 记事本"
        """
        super().__init__(script_file, period_trigger=period_trigger,
                         loop_running=loop_running, running_time=running_time, *args, **kwargs)
        self.getWindow(window_class, window_name)

    def getWindow(self, window_class, window_name):
        self.window = win32gui.FindWindow(window_class, window_name)
        if self.window == 0:
            self.window = None

    def swith_out_and_refocus_on_window(self, window2_class, window2_name):
        window2 = win32gui.FindWindow(window2_class, window2_name)
        self.focus_on_window(window=window2)
        time.sleep(1)
        self.focus_on_window()

    def focus_on_window(self, window=None):
        if window == None:
            window = self.window
        pythoncom.CoInitialize()
        shell = client.Dispatch("WScript.Shell")
        shell.SendKeys('%')  
        try:
            win32gui.SetForegroundWindow(window)
        except error as e:
            titles = getAllActiveWindow()
            lt = [t for t in titles if t]
            lt.sort()
            for t in lt:
                print(t)
            raise e
    

class TxtScript(WindowScript):
    """only for test, make a script son, operationg on a "test.txt" txt windows."""
    def __init__(self, script_file, window_class="Notepad",
                 window_name="test.txt - 记事本", period_trigger='off',
                 loop_running=True, running_time=None, *args, **kwargs):

        super(TxtScript, self).__init__(script_file, window_class, window_name,
                         period_trigger=period_trigger, loop_running=loop_running,
                         running_time=running_time, *args, **kwargs)

    def swith_out_and_refocus_on_window(self,
                                        window2_class="ConsoleWindowClass",
                                        window2_name="C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"):
        super(TxtScript, self).swith_out_and_refocus_on_window(window2_class, window2_name)
       
    def singleTripScript(self):
        self.focus_on_window()
        for i in self.script_json:
            self.run_json_script_command(i)


class WowScript(WindowScript):
    def __init__(self, script_file, player, window2_class=None, window_name=None, period_trigger='on', loop_running=True, running_time=None, *args, **kwargs):
        self.player = player
        super(WowScript, self).__init__(script_file, window2_class, window_name, period_trigger=period_trigger, 
                                        loop_running=loop_running, running_time=running_time, *args, **kwargs)

    def getWindow(self, window_class, window_name):
        self.window = self.player.window.getWowWindow()

    def singleTripScript(self):
        if self.period_trigger:
            self.period_trigger.go_a_step()
            if self.period_trigger.activated():
            # 先确认游戏是否断线了，断线就重连
                if self.player.checkOffline():
                    self.player.reLogon()
                # 刷新并进行游戏
        self.refresh()

    def refresh(self):
        self.player.refreshWindow()
        longRest()
        self.player.reSelectBtnBar()
        # 跳3下
        for i in range(0,3):
            keybdAct.press("spacebar")
            shortRest(1)


class GnomerganScript(WowScript):
    def __init__(self, player):
        super().__init__(player)

    def singleTripScript(self):
        super(GnomerganScript, self).singleTripScript()
        script_key = self.script_json['gnomergan_script']
        script_list = self.script_json[script_key]
        for sc in script_list:
            self.run_json_script_command(sc)

    def resetDungeon(self):
        while self.player.checkInDungeon():
            keybdAct.press("s", 3)
            time.sleep(10)
        keybdAct.press("8", 0.05)

    def attack_60(self):
        self.player.attackLoop(60)

    def enable_key_bar_2(self):
        keybdAct.pressHoldRelease("shift", "2")
        time.sleep(0.5)

    def attack_120(self):
        self.player.turnaround(180)
        shortRest()
        self.player.attackLoop(120, force_to_target=True)


class WaitForBuffScript(WowScript):
    def __init__(self, player):
        super().__init__(player)
        self.dragonHeadBuffRemaining = None
        self.chiefRegardsBuffRemaining = None
        with open('./config.json', 'r') as f:
            read = json.load(f)
            self.dragonHeadBuffMin = read['dragon_slayer_buff']
            self.chiefRegardsBuffMin = read['chief_regards_buff']

    @log
    def singleTripScript(self):
        super(WaitForBuffScript, self).singleTripScript()
        for i in range(20):
            keybdAct.press('spacebar')
            longRest()

        # player能识别自己的buff，并统计时间。
        # 第一buff，龙头(屠龙者的咆哮)，第二buff酋长祝福
        ########################
        # time.time()时间戳不能像下边这样用，再改
        ########################
        if self.dragonHeadBuffMin != 0:
            if self.dragonHeadBuffRemaining is None:
                if self.player.checkDragonHeadBuff():
                    self.dragonHeadBuffRemaining = time.time()
            self.dragonHeadBuffRemaining = 120*60 - (time.time() - self.dragonHeadBuffRemaining)
            print(f"目前情况为buff时间{self.dragonHeadBuffRemaining}, 要求时间{self.dragonHeadBuffMin}")
            if self.dragonHeadBuffRemaining < self.dragonHeadBuffMin * 60:
                self.player.logout()
                self.can_go_on.clear()

        longRest(10)
        if self.chiefRegardsBuffMin != 0:
            if self.chiefRegardsBuffRemaining is None:
                if self.player.checkChiefRegardsBuff():
                    self.chiefRegardsBuffRemaining = time.time()
            self.chiefRegardsBuffRemaining = 120*60 - (time.time() - self.chiefRegardsBuffRemaining)
            if self.chiefRegardsBuffRemaining < self.chiefRegardsBuffMin * 60:
                self.player.logout()
                self.can_go_on.clear()

        longRest(60)


class BattlefieldWowScript(WowScript):
    def __init__(self, player):
        WowScript.__init__(self, player)
        self.is_battlefield_new = True 
        self.player_status = None

    def checkInBattlefieldOrNot(self):
        return self.player.checkInBattlefield()

    def postHonormarkIfNewEnterHall(self):
        # 如果是进了大厅还没排队，交章
        if self.player_status == PlayStatus.new_to_hall:
            self.player.postHonormark(self.battlename)
            longRest()

    def joinQueueIfNewEnterHall(self):
        if self.player_status == PlayStatus.new_to_hall:
            keybdAct.press(self.player.tarQueueNpc)
            longRest()

            keybdAct.press(self.player.tarQueueNpc)
            longRest()

    def joinQueueAndPostHonorMark(self):
        script_key = self.script_json['join_queue_with_script']
        script_list = self.script_json[script_key]
        for sc in script_list:
            self.run_json_script_command(sc)

    def playInBattlefield(self):
        # 各战场内不同做法，在子类中实现
        pass

    def switchPlayerStatus(self):
        # Player状态校验
        in_battlefield = self.checkInBattlefieldOrNot()
        if in_battlefield:
            # 上轮状态为None，表示程序启动时人已经在战场了，肯定不是新场
            # 上轮状态为new_to_battlefield,play_in_battlefield,本轮都不是新场
            if self.player_status in [None, PlayStatus.new_to_battlefield, PlayStatus.play_in_battlefield]:
                self.player_status = PlayStatus.play_in_battlefield
            
            # 上轮状态为 *in_hall, 表示新来到战场，本轮是新进场
            else:
                self.player_status = PlayStatus.new_to_battlefield

        # 不在战场
        else:
            # 上轮传入状态为new_to_battlefield or play_in_battle or None,则本轮开始转为new_to_hall
            if self.player_status in [None, PlayStatus.new_to_battlefield, PlayStatus.play_in_battlefield]:
                self.player_status = PlayStatus.new_to_hall # 如果刚启动检测是在战场里，那是断线重连的，不能算新场

            # 上轮传入状态为 queueing_in_hall,则本轮开始变queueing_in_hall
            else:
                self.player_status = PlayStatus.queueing_in_hall


    @log
    def singleTripScript(self):
        super(BattlefieldWowScript, self).singleTripScript()
        self.switchPlayerStatus()
        if self.player_status in [PlayStatus.new_to_hall, PlayStatus.queueing_in_hall]:
            print(f'大厅很安逸，交交牌子排排队,当前状态为{self.player_status}')
            # 不在战场：
            # 去交一下牌子（交牌子也防掉线）
            # 去找npc排队(排队宏也可以进战场)
            self.joinQueueAndPostHonorMark()
            # 延迟30秒，本轮结束 
            longRest(30)
        else:
            print('哟，在战场呢')
            self.playInBattlefield()
            self.player_status = PlayStatus.play_in_battlefield

class WarsongScript(BattlefieldWowScript):

    def __init__(self, player):
        super().__init__(player)
        self.battlename = "warsong"

    def playInBattlefield(self):
        self.player.avoid_afk()
        time.sleep(20)
 

class AlteracScript(BattlefieldWowScript):
    def __init__(self, player):
        super().__init__(player)
        self.battlename = "alterac"

    def playInBattlefield(self):
        self.player.avoid_afk()
        time.sleep(20)


class AlxScript(BattlefieldWowScript):

    def __init__(self, player):
        super().__init__(player)
        self.battlename = "alx"

    def playInBattlefield(self):
        # 检查是否存活      
        alive = self.player.checkAlive()
        # 活着：检查是否是刚刚进入新的战场
        if alive:
            print('运气不错，活着')
            if self.player_status == PlayStatus.new_to_battlefield:
                print('新场，等一下')
                waitingInNewBattle()
            else:
                print('爬山吧，山的那一边其实还是山')
                druidStealWalkingInBattle()
        else:
            print('死鬼别动，小心灵魂被风吹散')
            keybdAct.press("spacebar")
            longRest(15)


def console_run():
    option = None
    wow = WowClient()
    player = Player(wow)
    script = GnomerganScript(player)
    print("挂机防掉线开始")
    script.start()
    script.resume()
    
    while(option!='q'):
        option = input("是否停止？输入q停止挂机")
    print("挂机结束")
            

@log
def check_in_expiration():
    with open("config.json", "r") as file:
        read = json.dumps(eval(file.read()))
        configs = json.loads(read)
        expired_hash = configs['expired_hash']
        return checkByExpiredHash(expired_hash)

if __name__ == "__main__":
    console_run()