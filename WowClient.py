#!/usr/bin/env python
# coding: utf-8

import win32gui
import win32con
import win32api
import win32print
import win32com.client as client
import time
import random
import pythoncom
import cv2
import json
import numpy as np

from PIL import Image, ImageGrab
from win32api import GetSystemMetrics
from matplotlib import pyplot as plt

import keybdAct


def convert_window_ltrb(display_ltrb):
    
    # get屏幕缩放
    zoom_horz = GetSystemMetrics(0)
    zoom_vert = GetSystemMetrics(1)

    # get分辨率设置
    hdc = win32gui.GetDC(0)
    res_horz = win32print.GetDeviceCaps(hdc, win32con.DESKTOPHORZRES)
    res_vert = win32print.GetDeviceCaps(hdc, win32con.DESKTOPVERTRES)

    # 修正尺寸
    left = round(display_ltrb[0] / zoom_horz * res_horz)
    top = round(display_ltrb[1] / zoom_vert * res_vert)
    right = round(display_ltrb[2] / zoom_horz * res_horz)
    bottom = round(display_ltrb[3] / zoom_vert * res_vert)

    return (left, top, right, bottom)


class WowClient():
    """魔兽世界窗口类，用于操作游戏的窗口，包括刷新，置顶，检测游戏内窗体，位置，按钮等。
    """
    # 创建wowclient方法可以直接拿到wowclient，包括截图，前置顶，校验前置顶，id，hwnd实例等
    
    def __init__(self):
        self.__window = win32gui.FindWindow("GxWindowClass", "魔兽世界")
        self.refresh_window()
        
    def screenshot(self, ttl=1, i=1, save=True):
        """可以支持部分截屏，比如ttl=4, i=2,就是截取上下左右分平的右上屏"""
        
        self.focus_on_window()
        time.sleep(0.5)
        ltrb = list(self.system_ltrb)
        
        # 上下左右四等分
        if ttl == 4:
            hrzt_step = (ltrb[2]-ltrb[0])/2
            vert_step = (ltrb[3]-ltrb[1])/2
            if i == 1:
                ltrb[2] = ltrb[0] + hrzt_step
                ltrb[3] = ltrb[1] + vert_step
            elif i == 2:
                ltrb[0] = ltrb[0] + hrzt_step
                ltrb[3] = ltrb[1] + vert_step
            elif i == 3:
                ltrb[2] = ltrb[0] + hrzt_step
                ltrb[1] = ltrb[1] + vert_step
            else:
                ltrb[0] = ltrb[0] + hrzt_step
                ltrb[1] = ltrb[1] + vert_step
                
        # 左中右三等分
        elif ttl == 3:
            hrzt_step = (ltrb[2]-ltrb[0])/3
            if i == 1:
                ltrb[2] = ltrb[0] + hrzt_step
            elif i == 2:
                ltrb[0] = ltrb[0] + hrzt_step
                ltrb[2] = ltrb[2] - hrzt_step
            else:
                ltrb[0] = ltrb[0] + hrzt_step*2
        # 左中右平分 
        elif ttl == 2:
            if i == 1:
                ltrb[2] = ltrb[0] + hrzt_step
            else:
                ltrb[0] = ltrb[0] + hrzt_step
        else:
            ltrb = ltrb
            
        im = ImageGrab.grab(ltrb)
        
        if save:
            now = time.localtime(time.time())
            name = f'./resources/screenshots/screenshots_{now.tm_year}_{now.tm_mon}_{now.tm_mday}_{now.tm_hour}_{now.tm_min}_{now.tm_sec}.jpg'
            im.save(name)
        
        return im
    
    def refresh_window(self):
        self.display_ltrb = win32gui.GetWindowRect(self.__window)
        self.system_ltrb = convert_window_ltrb(self.display_ltrb)
        
    def focus_on_window(self):
        pythoncom.CoInitialize()
        shell = client.Dispatch("WScript.Shell")
        shell.SendKeys('%')  
        win32gui.SetForegroundWindow(self.__window)
        pythoncom.CoInitialize()

    def getBtnPosFactor(self, btn):
        btn_dict = self.readBtnInfoFromJson()
        btn_xy = btn_dict[btn]
        x = btn_xy['x'][0] / btn_xy['x'][1]
        y = btn_xy['y'][0] / btn_xy['y'][1]
        return (x, y)

    def getBtnPos(self, btn):
        (x, y) = self.getBtnPosFactor(btn)
        pos_x = round((self.display_ltrb[2]-self.display_ltrb[0])*x+self.display_ltrb[0])
        pos_y = round((self.display_ltrb[3]-self.display_ltrb[1])*y+self.display_ltrb[1])
        return (pos_x, pos_y)

    def readBtnInfoFromJson(self):
        with open('btn_info.json', 'r') as f:
            return json.load(f)

    def imageMatch(self, template_path, screenshot_scale, parama=5, output=False):
        queryImage = cv2.imread(template_path, 0)
        screenshot = self.screenshot(*screenshot_scale)
        time.sleep(0.5)
        trainingImage = cv2.cvtColor(np.asarray(screenshot), cv2.COLOR_BGR2GRAY)
        sift=cv2.xfeatures2d.SIFT_create()#创建sift检测器
        kp1, des1 = sift.detectAndCompute(queryImage, None)
        kp2, des2 = sift.detectAndCompute(trainingImage, None)
        
        FLANN_INDEX_LSH=0
        indexParams= dict(algorithm = FLANN_INDEX_LSH,
                           table_number = 6, # 12   这个参数是searchParam,指定了索引中的树应该递归遍历的次数。值越高精度越高
                           key_size = 12,     # 20
                           multi_probe_level = 1) #2
        searchParams = dict(checks=20)
        flann = cv2.FlannBasedMatcher(indexParams,searchParams)
        
        matches = flann.knnMatch(des1,des2,k=2)
        matchesMask = [[0,0] for i in range (len(matches))]
        for i, (m,n) in enumerate(matches):
            if m.distance< 0.5*n.distance: #舍弃小于0.5的匹配结果
                matchesMask[i] = [1,0]
                
        if output:
            drawParams=dict(matchColor=(0,0,255),singlePointColor=(255,0,0),matchesMask=matchesMask,flags=0) #给特征点和匹配的线定义颜色
            resultimage=cv2.drawMatchesKnn(queryImage,kp1,trainingImage,kp2,matches,None,**drawParams) #画出匹配的结果
            plt.imshow(resultimage,),plt.show()

        print(matchesMask.count([1, 0]))
        return matchesMask.count([1, 0]) >= parama
    
    def inBattlegroundOrNot(self):
        in_battle_sysmbol = './resources/img_templates/in_btl_tplt.jpg'
        return self.imageMatch(in_battle_sysmbol, (4, 1, False), 9)
    
    def isReleaseSoulLabelShown(self):
        release_soul_label = './resources/img_templates/die_label.jpg'   
        return self.imageMatch(release_soul_label, (1, 1, False), 10)
    
    def isEnterBattleLabelShown(self):
        enter_battle_label = './resources/img_templates/enter_battle_label.jpg'
        return self.imageMatch(enter_battle_label, (3, 2, False), 5)
        
    def isLeaveBattleLabelShown(self):
        leave_battle_label = './resources/img_templates/battle_fin.jpg'
        return self.imageMatch(leave_battle_label, (1, 1, False), 5)
        
class Player():
    
    def __init__(self, wow_window):
        self.alive = "alive"
        self.in_battle = False
        self.in_sequence = False
        self.poistion = "unknow"
        self.window = wow_window
    
    
    def avoid_afk(self):
        # 防止掉线
        self.window.refresh_window()
        self.window.focus_on_window()
        r = random.randint(0, 7)
        keybdAct.press("spacebar")
        print('嗯，跳一跳，地好烫')
        self.longrest()
#         if r == 7:
#             keybdAct.press('5')
#             print('你炫酷的让大家跳了一支舞')
#             self.longrest()
            
#         elif r < 2:
#             t = random.uniform(0.5, 1)
#             keybdAct.pressAndHold('left_arrow')
#             time.sleep(t)
#             keybdAct.release('left_arrow')
#             self.longrest()
#             keybdAct.pressAndHold('right_arrow')
#             time.sleep(t)
#             keybdAct.release('right_arrow')
#             print('你刚刚完成了一圈闲逛')
#             self.longrest()
#         else:
#             keybdAct.press("spacebar")
#             print('嗯，跳一跳，地好烫')
#             self.longrest()

    def join_sequence(self):
        # 进战场
        print("尝试排队")
        self.window.refresh_window()
        self.window.focus_on_window()
        keybdAct.press('`')
        self.longrest()
        keybdAct.press('+')
        self.shortrest()
        keybdAct.press('\\')
        self.longrest()
        self.longrest()
        keybdAct.press('+')
        self.longrest()
        keybdAct.press('+')
        self.shortrest()
        self.longrest()
        keybdAct.press('2')
        self.round_wait()
        
    def enter_battle(self):
        print("检查排队进度")
        self.window.refresh_window()
        self.window.focus_on_window()
        self.shortrest()
        
        if self.window.isEnterBattleLabelShown():
            print("战场开启，进入战场")
            keybdAct.press('+')
            self.longrest()
#             (x, y) = self.window.getJoinBattleBtnXY()
#             win32api.SetCursorPos((x, y))
#             time.sleep(0.05)
#             win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)    # 鼠标左键按下
#             time.sleep(0.05)
#             win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)    # 鼠标左键弹起
            return True

        print("仍需耐心等待")
        return False
    
    def leave_battle(self):
        print("检查战场结束")
        self.window.refresh_window()
        self.window.focus_on_window()
        self.shortrest()
 
        if self.window.isLeaveBattleLabelShown():
            print("尝试离开战场")
            (x, y) = self.window.getLeaveBattleBtnXY()
            win32api.SetCursorPos((x, y))
            self.shortrest()
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)    # 鼠标左键按下
            self.shortrest()
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0) 
            return True # 成功脱离返回True
        return False 
    
    def release_soul(self):
        print("检查是否死亡")
        self.window.refresh_window()
        self.window.focus_on_window()
        self.shortrest()
        
        if self.window.isReleaseSoulLabelShown():
            print("释放尸体")
            (x, y) = self.window.getReleaseSoulBtnXY()
            win32api.SetCursorPos((x, y))
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)    # 鼠标左键按下
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)    # 鼠标左键弹起
            return False
        print("活的好好的")
        return True
            
    def delivery_battle_coins(self):
        self.window.refresh_window()
        self.window.focus_on_window()
        self.shortrest()
        keybdAct.press('-')
        self.shortrest()
        keybdAct.press('\\')
        self.longrest()
        self.longrest()
        keybdAct.press('-')
        self.longrest()
        (x, y) = self.window.getDeliveryBtnXY()
        win32api.SetCursorPos((x, y))
        self.shortrest()
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)    # 鼠标左键按下
        self.shortrest()
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)    # 鼠标左键弹起
        self.shortrest()
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)    # 鼠标左键按下
        self.shortrest()
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)    # 鼠标左键弹起
        self.shortrest()
        
    def is_in_battleground(self):
        return self.window.inBattlegroundOrNot()
    
    def cast_stealth(self):
        self.window.refresh_window()
        self.window.focus_on_window()
        self.shortrest()
        keybdAct.press('c')
        self.shortrest()
        keybdAct.press('4')
        self.shortrest()
        
        
    def shortrest(self):
        random_rest = random.uniform(0.25, 0.6)
        time.sleep(random_rest)
        
        
    def longrest(self):
        random_rest = random.uniform(1, 2.5)
        time.sleep(random_rest)
        
    def round_wait(self, max_wait=30):
        random_rest = random.uniform(5, max_wait)
        time.sleep(random_rest)
        