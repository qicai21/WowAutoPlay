import time
import random
from threading import Thread

import keybdAct
from WowClient import WowClient, Player


class ScriptBase(Thread):
    def __init__(self, player):
        Thread.__init__(self)
        self.player = player
        print("script初始化成功")
 
    def runScript(self):
        pass
 
    def run(self):
        while(True):
            self.runScript()


class WarsongScript(ScriptBase):
    def runScript(self):
        self.player.avoid_afk()
        time.sleep(1.1)
        self.player.join_sequence()
        time.sleep(2.55)
        self.player.enter_battle()
        time.sleep(1.5)
        self.player.leave_battle()
        time.sleep(20)
 
 
class OnlyAvoidAfk(ScriptBase):            
    def runScript(self):    
        self.player.avoid_afk()
        time.sleep(90)
            
            
class AlxScript(ScriptBase):
    def runScript(self):
        p = self.player
        # 是否在大厅检查
        # 大厅里找NPC排队
        time.sleep(2)
        is_in_battleground = p.is_in_battleground()
        while(not is_in_battleground): 
            keybdAct.pressHoldRelease('shift', '2')
            p.shortrest()
            keybdAct.press('`')
            p.longrest()
            _start = time.time()
            p.join_sequence()
            p.longrest()


            # 启动防AFK模式
            # 50秒查一下进场
            i = 10
            while(not is_in_battleground):
                i -= 1
                if i == 0:
                    break
                r = random.randint(40, 51)
                time.sleep(r)
                p.avoid_afk()
                if time.time() - _start > 200:
                    is_battle_enterable = p.is_in_battleground()

            p.round_wait()# 等待页面切换
 
        # 进入战场
        # 变猫，隐身
        # 前进5秒出门
        if is_in_battleground:
            start = time.time()
            keybdAct.press('up_arrow')
            time.sleep(3.2)
            keybdAct.press('down_arrow')

            # 等候1.5分钟，防afk一轮
            r = random.randint(60, 90)
            time.sleep(r)
            p.cast_stealth()
            r = random.randint(60, 90)
            time.sleep(r)

            # 前进，+左转
            # 60秒一次检查死亡放尸
            _r =0
            keybdAct.press('up_arrow')
            time.sleep(16)
            if _r%2 == 0:
                keybdAct.pressAndHold('a')
                time.sleep(0.12)
                keybdAct.release('a')
            else:
                keybdAct.pressAndHold('d')
                time.sleep(0.1)
                keybdAct.release('d')
            _r = _r%2 + 1
            time.sleep(20)
        is_in_battleground = True
        while (is_in_battleground):
            p.avoid_afk()
            p.round_wait()
            is_in_battleground = p.is_in_battleground()
#         alive = True
#         _r = 0 # 控制方向的
#         while(alive):
#             if time.time() - start > 420:
#                 if not p.is_in_battleground():
#                     alive = False
#                     go_on = False
#                     break
#             if time.time() - start > 300:
#                 if p.leave_battle():
#                     alive = False
#                     go_on = False
#                     break
#             keybdAct.press('up_arrow')
#             time.sleep(16)
#             if _r%2 == 0:
#                 keybdAct.pressAndHold('a')
#                 time.sleep(0.12)
#                 keybdAct.release('a')
#             else:
#                 keybdAct.pressAndHold('d')
#                 time.sleep(0.1)
#                 keybdAct.release('d')
#             _r = _r%2 + 1
#             time.sleep(20)
#             keybdAct.press('spacebar')
#             is_alive = not p.release_soul()
            
#         # 6分钟后开启离场检查
#         # 20分钟后开启是否进入大厅检查
#         while(go_on):
#             p.avoid_afk()    
#             p.round_wait()    
#             if time.time() - start > 450:
#                 if not p.is_in_battleground():
#                     go_on = False
#                     break
#             if time.time() - start > 300:
#                 if p.leave_battle():
#                     go_on = False
#                     break
#             p.avoid_afk()    
#             p.round_wait()    
#         p.round_wait()# 等待页面切换
        
        
def run(script):
    option = None
    script.setDaemon(True)
    print("挂机防掉线开始")
    script.start()
    
    while(option!='stop'):
        option = input("是否停止？输入stop停止挂机")
    print("挂机结束")
    
            
if __name__ == "__main__":
    wow = WowClient()
    player = Player(wow)
    script = AlxScript(player)
    run(script)
