import time
import tkinter as tk
from WowClient import WowClient
from Player import Player
from ScriptManager import AlxScript, check_in_expiration


class Laucher(tk.Tk):
    def __init__(self, script=None):
        super(Laucher, self).__init__()
        if script==None:
            wow = WowClient()
            player = Player(wow)
            self.script = AlxScript(player)
        else:
            self.script = script
        self.title('护肝神器_工程版')
        self.geometry('480x150')
        self.widgets = dict()
        self.setup_background()
        self.setup_information_label()
        self.setup_start_btn(self.click_start_btn)
        self.setup_dropdown()

    def setup_background(self):
        img = tk.PhotoImage(file="./background.gif")
        imgLabel = tk.Label(self, image=img)
        imgLabel.pack(side="top")

    def setup_information_label(self):
        explanation = """本软件仅用于测试，说明：
        目前还是最基础的工程版，用于alx和战歌"""
        self.widgets['info_label'] = tk.Label(self,text=explanation,justify=tk.LEFT).place(x=10,y=85,anchor='nw')


    def setup_start_btn(self, btn_click_command):
        self.widgets['start_btn_content'] = tk.StringVar()
        self.widgets['start_btn_content'].set("开始")
        self.widgets['start_btn'] = tk.Button(self, textvariable=self.widgets['start_btn_content'], command=btn_click_command, width=15, height=2,).place(x=330,y=90,anchor='nw')

    def setup_dropdown(self):
        dropdown_items = ['阿拉希', '战歌', '奥山', '泡世界buff', '刷惩戒器']
        dropdown_selected = tk.StringVar()
        dropdown_selected.set(dropdown_items[0])
        dropdown = tk.OptionMenu(self, dropdown_selected, *dropdown_items).place(x=330, y=80, anchor='nw')


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


    def run(self):
        pass
