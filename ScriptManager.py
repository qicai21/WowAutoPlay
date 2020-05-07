import time
import random
import json
import re
import threading
import tkinter as tk
from tkinter import *
from enum import Enum

import keybdAct
from WowClient import WowClient
from Player import Player
from WaitAndOption import shortRest, longRest, roundWait, waitingInNewBattle, druidStealWalkingInBattle
from Expiration import checkByExpiredHash
from logWrapper import log


# 每5次执行一起重新登录检验
# 这是一个cheat，最好还是放在config中
ASSITED_OPTION_BASE = 5
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

def parseScriptFileToJson(filename):
    """ Parse a JSON file
        First remove comments and then use the json module package
        Comments look like :
            // ...
        or
            /*
            ...
            */
    """
    comment_re = re.compile(
        '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
        re.DOTALL | re.MULTILINE
    )
    with open(filename, 'r', encoding='utf8') as f:
            content = ''.join(f.readlines())
            ## Looking for comments
            match = comment_re.search(content)
            while match:
                # single line comment
                content = content[:match.start()] + content[match.end():]
                match = comment_re.search(content)
    
            return json.loads(content)

class ScriptBase(threading.Thread):
    def __init__(self, player):
        threading.Thread.__init__(self)
        self.player = player
        self.loadScript()
        self.__paused = threading.Event()
        self.__paused.clear()
        self.stepter = 0 # 用于计算是否执行重新登录检查的计步器，1/5几率
        self.assitedOptionBase = ASSITED_OPTION_BASE
        self.setDaemon(True)

    def pause(self):
        self.__paused.clear()

    def resume(self):
        self.__paused.set()

    def is_running(self):
        return self.__paused.isSet()

    def running_switch(self):
        if self.__paused.isSet():
            self.pause()
            return "开始"
        else:
            self.resume()
            return "结束"

    def loadScript(self):
        self.script_json = parseScriptFileToJson(SCRIPTSFILE)

    def run_json_script_command(self, json_script):
        action_type = list(json_script.keys())[0]
        action_name = json_script[action_type][0]
        action_param = json_script[action_type][1]
        action_comment = json_script[action_type][-1]

        if action_comment != None and action_comment != "":
            print(action_comment)

        if action_type == "keyboard_action":
            _func = getattr(keybdAct, action_name)
            if _func == keybdAct.press:
                _func(action_param, action_comment)
            else:
                _func(action_param)

        elif action_type == "wait_action":
            if action_name == "short_random_wait":
                shortRest()
            else:
                time.sleep(action_param)
        elif action_type == "integrated_action":
            try:
                self.__getattribute__(action_name)()
            except AttributeError as err:
                self.player.__getattribute__(action_name)()
        
        else:
            print('bad script json command:' + action_type)
            return


    def doAssitedOption(self):
        self.stepter = self.stepter % self.assitedOptionBase + 1
        return self.stepter % self.assitedOptionBase == 1
            

    def refresh(self):
        self.player.refreshWindow()
        longRest()
        self.player.reSelectBtnBar()
        # 跳3下
        for i in range(0,3):
            keybdAct.press("spacebar")
            shortRest()

    def singleTripScript(self):
        pass

    def offlineInspection(self):
        pass
 
    @log
    def run(self):
        while True:
            self.__paused.wait()
            if self.doAssitedOption():
                # 先确认游戏是否断线了，断线就重连
                offline = self.player.checkOffline()
                if offline:
                    self.player.reLogon()
                # 刷新并进行游戏
                self.refresh()
            self.singleTripScript()

class GnomerganScript(ScriptBase):
    def __init__(self, player):
        super().__init__(player)

    def singleTripScript(self):
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


class WaitForBuffScript(ScriptBase):
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
                self.__paused.clear()

        longRest(10)
        if self.chiefRegardsBuffMin != 0:
            if self.chiefRegardsBuffRemaining is None:
                if self.player.checkChiefRegardsBuff():
                    self.chiefRegardsBuffRemaining = time.time()
            self.chiefRegardsBuffRemaining = 120*60 - (time.time() - self.chiefRegardsBuffRemaining)
            if self.chiefRegardsBuffRemaining < self.chiefRegardsBuffMin * 60:
                self.player.logout()
                self.__paused.clear()

        longRest(60)


class BattlefieldScriptBase(ScriptBase):
    def __init__(self, player):
        ScriptBase.__init__(self, player)
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

class WarsongScript(BattlefieldScriptBase):

    def __init__(self, player):
        super().__init__(player)
        self.battlename = "warsong"

    def playInBattlefield(self):
        self.player.avoid_afk()
        time.sleep(20)
 

class AlteracScript(BattlefieldScriptBase):
    def __init__(self, player):
        super().__init__(player)
        self.battlename = "alterac"

    def playInBattlefield(self):
        self.player.avoid_afk()
        time.sleep(20)


class AlxScript(BattlefieldScriptBase):

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