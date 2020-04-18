import time
import random
import json
from enum import Enum
from threading import Thread

import keybdAct
from WowClient import WowClient
from Player import Player
from WaitAndOption import shortRest, longRest, roundWait, waitingInNewBattle, druidStealWalkingInBattle


ASSITED_OPTION_BASE = 5
class PlayStatus(Enum):
    # 在大厅未排队
    # 在大厅排队了
    # 进战场第一轮
    # 在战场持续中
    new_to_hall = 0
    queueing_in_hall = 1
    new_to_battlefield = 2
    play_in_battlefield = 3

class ScriptBase(Thread):
    def __init__(self, player):
        Thread.__init__(self)
        self.player = player
        self.continue_game = True
        self.factor = 0
        self.assitedOptionBase = ASSITED_OPTION_BASE

    def doAssitedOption(self):
        self.factor = self.factor % self.assitedOptionBase + 1
        return self.factor % self.assitedOptionBase == 1
            

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
 
    def run(self):
        i = 0
        while(self.continue_game):
            if self.doAssitedOption():
                # 先确认游戏是否断线了，断线就重连
                offline = self.player.checkOffline()
                if offline:
                    self.player.reLogon()
                # 刷新并进行游戏
                self.refresh()
            self.singleTripScript()

class WaitForBuffScript(ScriptBase):
    def __init__(self, player):
        ScriptBase.__init__(self, player)
        self.dragonHeadBuffRemaining = None
        self.chiefRegardsBuffRemaining = None
        with open('./config.json', 'r') as f:
            read = json.load(f)
            self.dragonHeadBuffMin = read['dragon_slayer_buff']
            self.chiefRegardsBuffMin = read['chief_regards_buff']

    def singleTripScript(self):
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
                self.continue_game = False

        longRest(10)
        if self.chiefRegardsBuffMin != 0:
            if self.chiefRegardsBuffRemaining is None:
                if self.player.checkChiefRegardsBuff():
                    self.chiefRegardsBuffRemaining = time.time()
            self.chiefRegardsBuffRemaining = 120*60 - (time.time() - self.chiefRegardsBuffRemaining)
            if self.chiefRegardsBuffRemaining < self.chiefRegardsBuffMin * 60:
                self.player.logout()
                self.continue_game = False

        longRest(60)


class BattlefieldScriptBase(ScriptBase):
    def __init__(self, player):
        ScriptBase.__init__(self, player)
        self.is_battlefield_new = True 
        self.player_status = None

    def checkInBattlefieldOrNot(self):
        return self.player.checkInBattlefield()

    def joinQueueAndPostHonorMark(self):
        # 防止仍然处于跑动状态
        keybdAct.press('down_arrow')
        shortRest()
        # 这里需要游戏中有排队-进场宏, 选定军需官宏, 并设NPC互动键
        # 选择军需官为目标 
        keybdAct.press(self.player.tarHonorNpc)
        shortRest()

        # 与军需官互动（朝军需官走去，抵达身边后打开frame
        keybdAct.press(self.player.interactBtn)
        longRest(5)

        # 选择要交的章按钮
        # 如果是进了大厅还没排队，交章
        if self.player_status == PlayStatus.new_to_hall:
            self.player.postHonormark(self.battlename)
            longRest()

        # 选择排队npc
        keybdAct.press(self.player.tarQueueNpc)
        shortRest()

        # 与排队NPC互动（朝NPC走去，抵达身边后打开frame
        keybdAct.press(self.player.interactBtn)
        longRest(5)

        # 排战场---有战场就进
        if self.player_status == PlayStatus.new_to_hall:
            keybdAct.press(self.player.tarQueueNpc)
            longRest()

            keybdAct.press(self.player.tarQueueNpc)
            longRest()
        # 重置一下页面，防止报错
            self.player.clickReloadBtn()


    def playInBattlefield(self):
        # 各战场内不同做法，在子类中实现
        pass

    def switchPlayerStatus(self):
        # Player状态校验
        in_battlefield = self.checkInBattlefieldOrNot()
        if in_battlefield:
            # 上轮状态为None，表示程序启动时人已经在战场了，可定不是新场
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



    def singleTripScript(self):
        self.switchPlayerStatus()
        if self.player_status in [PlayStatus.new_to_hall, PlayStatus.queueing_in_hall]:
            print('大厅很安逸，交交牌子排排队')
            # 不在战场：
            # 去交一下牌子（交牌子也防掉线）
            # 去找npc排队(排队宏也可以进战场)
            self.joinQueueAndPostHonorMark()

            # 延迟40-45秒，本轮结束 
            longRest(30)
            self.player_status = PlayStatus.queueing_in_hall
        else:
            print('哟，在战场呢')
            self.playInBattlefield()
            self.player_status = PlayStatus.play_in_battlefield

class WarsongScript(BattlefieldScriptBase):

    def __init__(self, player):
        BattlefieldScriptBase.__init__(player)
        self.battlename = "warsong"

    def playInBattlefield(self):
        self.player.avoid_afk()
        time.sleep(20)
 
 
class AlxScript(BattlefieldScriptBase):

    def __init__(self, player):
        BattlefieldScriptBase.__init__(self, player)
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

def run(script):
    option = None
    script.setDaemon(True)
    print("挂机防掉线开始")
    script.start()
    
    while(option!='q'):
        option = input("是否停止？输入q停止挂机")
    print("挂机结束")
    
            
if __name__ == "__main__":
    wow = WowClient()
    player = Player(wow)
    script = AlxScript(player)
    # script = WaitForBuffScript(player)
    run(script)
