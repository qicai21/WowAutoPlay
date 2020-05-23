import time
import tkinter as tk
from WowClient import WowClient
from Player import Player
from ScriptManager import WowScript


class Laucher(tk.Tk):
    def __init__(self, script=None):
        super(Laucher, self).__init__()
        if script==None:
            wow = WowClient()
            player = Player(wow)
            self.script = WowScript(player)
        else:
            self.script = script

        self.title('护肝神器_工程版')
        self.geometry('480x150')
        self.widgets = dict()
        self.setup_background()
        self.setup_information_label()
        self.setup_dropdown()
        self.setup_start_btn(self.click_start_btn)
        self.script.start()

    def setup_background(self):
        self.img = tk.PhotoImage(file="./resources/background2.png")
        imgLabel = tk.Label(self, image=self.img)
        imgLabel.grid(row=0, column=0, columnspan=3)
        # imgLabel.pack(side="top")

    def setup_information_label(self):
        explanation = """本软件仅用于测试，说明：
        目前还是最基础的工程版，用于alx和战歌"""
        # self.widgets['info_label'] = tk.Label(self,text=explanation,justify=tk.LEFT).place(x=10,y=85,anchor='nw')
        self.widgets['info_label'] = tk.Label(self,text=explanation,justify=tk.LEFT).grid(row=1, column=0)


    def setup_start_btn(self, btn_click_command):
        self.widgets['start_btn_content'] = tk.StringVar()
        self.widgets['start_btn_content'].set("开始")
        self.widgets['start_btn'] = tk.Button(
            self, textvariable=self.widgets['start_btn_content'], command=btn_click_command,
            width=15
        ).grid(row=1, column=2,padx=0.5, pady=4, sticky='n'+'s'+'e')

    def setup_dropdown(self):
        dropdown_items = self.script.get_enable_scripts_list()
        self.widgets['dropdown_selected'] = tk.StringVar()
        self.widgets['dropdown_selected'].set("选择脚本类型")
        dropdown = tk.OptionMenu(
           self, self.widgets['dropdown_selected'], *dropdown_items
        ).grid(row=1, column=1, padx=0.5, pady=2, sticky='n'+'s')

    def click_start_btn(self):
        if not self.script.check_in_expiration():
            self.widgets['start_btn_content'].set("过期了")
            return

        result = self.script.running_switch(self.widgets['dropdown_selected'].get())
        if result == "on":
            self.widgets['start_btn_content'].set("暂停")
        elif result == "off":
            self.widgets['start_btn_content'].set("恢复")
        else:
            raise ValueError("程序running_switch出现了错误，具体原因未知。")

