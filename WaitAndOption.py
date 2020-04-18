import random
import time
import keybdAct


def waitingInNewBattle():
    """刚刚进战场
    """
    longRest(30)
    keybdAct.press("spacebar")
    longRest(30)
    keybdAct.press("spacebar")


def druidStealWalkingInBattle():
    keybdAct.press('5')
    shortRest()
    keybdAct.press('4')
    shortRest()
    simpleWalkingInBattle()

def simpleWalkingInBattle():
    """简单的战场游走宏,30s
    """
    for i in range(0, 3):
        keybdAct.press('up_arrow')
        longRest(7)
        keybdAct.pressAndHold('d')
        shortRest(0.15)
        keybdAct.release('d')
        keybdAct.press('up_arrow')
        longRest(7)
        keybdAct.pressAndHold('a')
        shortRest(0.15)
        keybdAct.release('a')
        longRest(5)
        keybdAct.press('down_arrow')
        longRest(5)


def shortRest(rest=None):
    """短暂停滞0.4，0.5s，默认0.25-0.6秒随机数，可以rest参数指定
    """
    if rest == None:
        rest = random.uniform(0.25, 0.6)
    time.sleep(rest)
    
    
def longRest(rest=None):
    """中等停滞1.5-2s，默认1-2.5秒随机数，可以rest参数指定
    """
    if rest == None:
        rest = random.uniform(1, 2.5)
    time.sleep(rest)
    

def roundWait(max_wait=30):
    """轮次停滞，用于页面刷新，过场等，默认最长30秒，可以手动指定
    """
    random_rest = random.uniform(5, max_wait)
    time.sleep(random_rest)
    