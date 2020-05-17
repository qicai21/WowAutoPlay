import tkinter as tk
from tkinter import *

from WowClient import WowClient
from Player import Player
from ScriptManager import AlxScript, check_in_expiration


class Laucher(Tk):
    def __init__(self, script=None):
        super(Laucher, self).__init__()
        if script==None:
            wow = WowClient()
            player = Player(wow)
            self.script = AlxScript(player)
        else:
            self.script = script
        # alx = None
        # warsong = None
        # alterac = None
        # worldbuff = None
        self.title('护肝神器_工程版')
        self.geometry('480x150')
        explanation = """本软件仅用于测试，说明：
        目前还是最基础的工程版，用于alx和战歌"""
        self.setup_background()
        self.widgets = dict()
        self.setup_background()
        self.setup_information_label(explanation)
        self.setup_start_btn(self.click_start_btn)

    def setup_background(self):
        logo = PhotoImage(file="./resources/background.png")
        self.background = Label(self, image=logo).pack(side="top")

    def setup_information_label(self, explanation):
        self.widgets['info_label'] = tk.Label(self,text=explanation,justify=LEFT).place(x=10,y=85,anchor='nw')


    def setup_start_btn(self, btn_click_command):
        self.widgets['start_btn_content'] = tk.StringVar()
        self.widgets['start_btn_content'].set("开始")
        self.widgets['start_btn'] = tk.Button(self, textvariable=self.widgets['start_btn_content'], command=btn_click_command, width=15, height=2,).place(x=330,y=90,anchor='nw')

        # dropdown
        # dropdown_items = ['阿拉希', '战歌', '奥山', '泡世界buff', '刷惩戒器']
        # dropdown_content = tk.StringVar(window)
        # dropdown_content.set(dropdown_items[0])

        # 初始化组件

    def click_start_btn(self):
        if not check_in_expiration():
            self.widgets['start_btn_content'] = '过期了'
            return

        if self.script.is_running():
            self.script.pause()
            content = "恢复"
        else:
            self.script.resume()
            content = "暂停"

        self.widgets['start_btn_content'] = content
        self.script.start()


# dropdown = tk.OptionMenu(window, dropdown_content, *dropdown_items).place(x=330, y=80, anchor='nw')
    def run(self):
        return self.mainloop()