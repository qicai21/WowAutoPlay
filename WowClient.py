#!/usr/bin/env python
# coding: utf-8

import win32gui
import win32con
import win32print
import win32com.client as client
import time
import pythoncom
import cv2
import json
import numpy as np
from pywintypes import error

from PIL import Image, ImageGrab
from win32api import GetSystemMetrics

import keybdAct


SAVE_SCREENSHOT_IMG = False

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
        self.getWowWindow()
        self.refresh_window()

    def getWowWindow(self):
        self.window = win32gui.FindWindow("GxWindowClass", "魔兽世界")

    def getLaucherWindow(self):
        return win32gui.FindWindow("Qt5QWindowOwnDCIcon", "暴雪战网")

    def screenshot(self, ttl=1, i=1):
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
        
        if SAVE_SCREENSHOT_IMG:
            now = time.localtime(time.time())
            name = f'./resources/screenshots/screenshots_{now.tm_year}_{now.tm_mon}_{now.tm_mday}_{now.tm_hour}_{now.tm_min}_{now.tm_sec}.jpg'
            im.save(name)
        
        return im
    
    def refresh_window(self):
        self.display_ltrb = win32gui.GetWindowRect(self.window)
        self.system_ltrb = convert_window_ltrb(self.display_ltrb)
        
    def focus_on_window(self, window=None):
        if window == None:
            window = self.window
        pythoncom.CoInitialize()
        shell = client.Dispatch("WScript.Shell")
        shell.SendKeys('%')  
        try:
            win32gui.SetForegroundWindow(window)
        except error as e:
            titles = set()

            def getAllActiveWindow(hwnd, mouse):
                # 去掉下面这句就所有都输出了，但是我不需要那么多
                if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
                    titles.add(win32gui.GetWindowText(hwnd) + "   " + win32gui.GetClassName(hwnd))

            win32gui.EnumWindows(getAllActiveWindow, 0)
            lt = [t for t in titles if t]
            lt.sort()
            for t in lt:
                print(t)
            raise e


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
        with open('config.json', 'r') as f:
            return json.load(f)['btn_pos_factor']

    def imageMatch(self, template_path, screenshot_scale):
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

        return matchesMask.count([1, 0])
