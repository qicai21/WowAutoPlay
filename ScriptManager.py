import time
import random
import json
import re
import threading
import tkinter as tk
from tkinter import *
from enum import Enum
import win32gui
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
MODE = "product"
DEFAULT_TRIGGER_BASE = 5
CONFIG_FILE = './config.json'
SCRIPTS_FILE ='./scripts.json' 

class PlayerBattleFieldStatus(Enum):
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
        关键属性：
        self.configs: 从configs.json读取的，所有关于脚本游戏控制的config都在这里。
        self.singleTripScript: 单轮循环脚本的执行，这个必须在子类中实现.
    """
    def __init__(self, script_file=None, period_trigger='off', loop_running=True,
                 running_time=None, *args, **kwargs):
        super(ScriptBase, self).__init__()
        self.script_file = script_file
        self.set_period_trigger(period_trigger, **kwargs)
        self.loop_running = loop_running
        self.running_time = running_time
        self.read_config()
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
        if self.script_file:
            while(not self.is_running()):
                self.script_json = parseScriptFileToJson(f'./scripts/{self.script_file}')
                return 
    
    def run_json_list(self, json_list):
        for j in json_list:
            self.run_json_script_command(j)

    def run_json_script_command(self, json_script):
        self.can_go_on.wait()
        action_type = list(json_script.keys())[0]
        action_name = json_script[action_type][0]
        action_param = json_script[action_type][1]
        action_comment = json_script[action_type][-1]

        if MODE == "test" and action_comment != None and action_comment != "":
            print(action_comment)

        if action_type == "keyboard_action":
            _func = getattr(keybdAct, action_name)
            if _func == keybdAct.press:
                if type(action_comment) == str:
                    _func(action_param)
                else:
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
            if type(action_param) == float:
                self.__getattribute__(action_name)(action_param)
            else:
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

    def check_in_expiration(self, expired_hash=None):
        if not expired_hash:
            expired_hash = self.configs['expired_hash']
        return checkByExpiredHash(expired_hash)
    
    def read_config(self, config_file=CONFIG_FILE):
        with open(config_file, "r", encoding='utf-8') as file:
            read = json.dumps(eval(file.read()))
            self.configs = json.loads(read)

    def get_enable_scripts_list(self):
        return list(self.configs["enable_scripts"].keys())

    def running_switch(self, script_name):
        if self.is_running():
            self.pause()
            return 'off'
        else:
            print('触发了等待')
            self.can_reload_script.wait()
            print('等到了，程序继续执行')
            self.script_file = self.configs['enable_scripts'][script_name]
            self.loadScript()
            self.resume()
            return 'on'
        

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
        time.sleep(1.5)
        self.focus_on_window()
        time.sleep(1.5)

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
        self.run_json_list(self.script_json)


class WowScript(WindowScript):
    def __init__(self, script_file, player, window2_class=None, window_name=None,
                 period_trigger='on', loop_running=True, running_time=None, *args, **kwargs):
        self.player = player
        super(WowScript, self).__init__(script_file, window2_class, window_name, period_trigger=period_trigger, 
                                        loop_running=loop_running, running_time=running_time, *args, **kwargs)
        self.is_battlefield_new = True 
        self.player_battle_filed_status = None
        self.enableBuffDict = {k:[v, 0] for k,v in self.configs['auto_afk_after_buff_remaining'].items() if v > 0}
        self.loadJoinQueueScript()

    def __getattr__(self, attr_name):
        """[SUGAR]: 以属性方式返回cript_json中的一些设置."""
        if attr_name == "battlefield":
            return self.script_json['battle_field_name']
        elif attr_name == "script_type":
            return self.script_json['script_type']
        else:
            raise AttributeError(f"{__class__.__name__} object has no attribute {attr_name}")

    def getWindow(self, window_class, window_name):
        self.window = self.player.window.getWowWindow()

    def loadJoinQueueScript(self):
        json_data = parseScriptFileToJson('./scripts/JoinQueue.json')
        self.join_queue_scripts = json_data['join_queue_scripts']

    def singleTripScript(self):
        """脚本单循环
        
        所有的wow脚本都分为这几个部分：
        1. 周期性触发段，主要是断线重连；可以用cancelAutoRelogon关闭
        2. 根据脚本类型来执行不同的操作逻辑
        """
        if self.period_trigger:
            self.period_trigger.go_a_step()
            if self.period_trigger.activated():
                if self.player.checkOffline():
                    self.player.reLogon()
        self.refresh()
        if self.script_type == "battlefield_script":
            self.runBattleFieldScript()
        elif self.script_type == "dungeon_script":
            self.runDungeonScript()
        elif self.script_type == "wait_buff_script":
            self.runWaitBuffScript()
        else:
            raise NotImplementedError("Unknow script type, check script_type setting in json")

    def runWaitBuffScript(self):
        for buff,time_set in self.enableBuffDict.items():
            if time_set[1] == 0:
                if self.player.checkBuff(buff):
                    if time_set[0] == 120:
                        self.cancelAutoRelogon()
                        self.loop_running = False
                        self.player.logout()
                        return
                    else:
                        time_set[1] = time.time() + (120 - time_set[0]) * 60
            else:
                if time.time() > time_set[1]:
                    self.cancelAutoRelogon()
                    self.loop_running = False
                    self.player.logout()
                    return
        # 执行一些无谓的操作，防止掉线
        self.run_json_list(self.script_json['main_scripts'])
        longRest(60)

    def runDungeonScript(self):
        self.run_json_list(self.script_json["main_scripts"])

    def runBattleFieldScript(self):
        self.switchPlayerBattleFieldStatus()
        if self.player_battle_filed_status in [
                 PlayerBattleFieldStatus.new_to_hall,
                 PlayerBattleFieldStatus.queueing_in_hall
                ]:
            print(f'大厅很安逸，交交牌子排排队,当前状态为{self.player_battle_filed_status}')
            self.run_json_list(self.join_queue_scripts)
            longRest(18) # 延迟30秒，本轮结束 
        else:
            print('哟，在战场呢')
            self.playInBattlefield()
            self.player_battle_filed_status = PlayerBattleFieldStatus.play_in_battlefield

    def switchPlayerBattleFieldStatus(self):
        """通过player_battle_field_status的切换来为不同逻辑启动提供依据.

        具体切换：
        上轮状态为None，表示程序启动时人已经在战场了，肯定不是新场
        上轮状态为new_to_battlefield,play_in_battlefield,本轮都不是新场
        上轮状态为 *in_hall, 表示新来到战场，本轮是新进场
        上轮传入状态为new_to_battlefield or play_in_battle or None,则本轮开始转为new_to_hall;如果刚启动检测是在战场里，那是断线重连的，不能算新场
        上轮传入状态为 queueing_in_hall,则本轮开始变queueing_in_hall
        """
        in_battlefield = self.checkInBattlefieldOrNot()
        if in_battlefield:
            if self.player_battle_filed_status in [
                 None, 
                 PlayerBattleFieldStatus.new_to_battlefield,
                 PlayerBattleFieldStatus.play_in_battlefield
                ]:
                self.player_battle_filed_status = PlayerBattleFieldStatus.play_in_battlefield
            else:
                self.player_battle_filed_status = PlayerBattleFieldStatus.new_to_battlefield
        else:
            if self.player_battle_filed_status in [
                 None,
                 PlayerBattleFieldStatus.new_to_battlefield,
                 PlayerBattleFieldStatus.play_in_battlefield
                ]:
                self.player_battle_filed_status = PlayerBattleFieldStatus.new_to_hall 
            else:
                self.player_battle_filed_status = PlayerBattleFieldStatus.queueing_in_hall

    def checkInBattlefieldOrNot(self):
        return self.player.checkInBattlefield()

    def playInBattlefield(self):
        alive = self.player.checkAlive()
        if alive:
            print('运气不错，活着')
            if self.player_battle_filed_status == PlayerBattleFieldStatus.new_to_battlefield:
                print('新场，等一下')
                self.run_json_list(self.script_json['standby_scripts'])
            else:
                print('执行战场挂机跑动')
                self.run_json_list(self.script_json['main_scripts'])
        else:
            print('死鬼别动，小心灵魂被风吹散')
            keybdAct.press("spacebar")
            longRest(15)

##############     integrated_actions [供script_json调用的方法]  ###############

    def refresh(self):
        self.player.refreshWindow()
        longRest()
        self.player.reSelectBtnBar()
        # 跳2下
        # for i in range(0,2):
        #     keybdAct.press("spacebar")
        #     shortRest(1.5)

    def pass_corner_1(self, _t):
        keybdAct.press("s", 0.1)
        shortRest(0.5)
        keybdAct.press("spacebar")
        shortRest(1.5)

        keybdAct.press("a", _t)
        shortRest(0.5)
        keybdAct.press("up_arrow")
        shortRest(4.1)
        keybdAct.press("s", 0.45)
        shortRest(0.5)
        keybdAct.press("d", 0.35)
        shortRest(0.5)
        keybdAct.press("up_arrow")
        shortRest(1.6)
        keybdAct.press("a", 0.2)
        shortRest(0.8)
        keybdAct.press("a", 0.4)
        shortRest(2.5)
        keybdAct.press("a", 0.42)
        shortRest(2.2)
        keybdAct.press("a", 0.11)
        shortRest(2.63)
        keybdAct.press("s")

    def cancelAutoRelogon(self):
        """关闭周期性触发器，周期性方法如自动重新登录将关闭"""
        self.set_period_trigger("off")

    def postHonormarkIfNewEnterHall(self):
        if self.player_battle_filed_status == PlayerBattleFieldStatus.new_to_hall:
            self.player.postHonormark(self.battlefield)
            longRest()

    def joinQueueIfNewEnterHall(self):
        if self.player_battle_filed_status == PlayerBattleFieldStatus.new_to_hall:
            keybdAct.press(self.player.tarQueueNpc)
            longRest()
            keybdAct.press(self.player.tarQueueNpc)
            longRest()

    def resetDungeon(self):
        while self.player.checkInDungeon():
            keybdAct.press("s", 3)
            time.sleep(10)
        keybdAct.press("8", 0.05)

    def attack_60(self):
        self.player.attackLoop(60)

    def enable_key_bar_2(self):
        self.player.reSelectBtnBar()

    def attack_120(self):
        self.player.turnaround(180)
        shortRest()
        self.player.attackLoop(120, force_to_target=True)

    def check_combat_and_attack(self):
        self.player.check_combat_and_attack()

    def openDoor(self):
        self.player.openDoor()

################################################################################


def console_run():
    option = None
    wow = WowClient()
    player = Player(wow)
    script = WowScript(player)
    print("挂机防掉线开始")
    script.start()
    script.resume()
    
    while(option!='q'):
        option = input("是否停止？输入q停止挂机")
    print("挂机结束")
            

if __name__ == "__main__":
    console_run()