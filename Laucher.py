import time
import tkinter as tk
from WowClient import WowClient
from Player import Player
from ScriptManager import WowScript
from KeyboardRecorder import TakeRecord


class Laucher(tk.Tk):
    def __init__(self, script=None):
        super(Laucher, self).__init__()
        if script==None:
            wow = WowClient()
            player = Player(wow)
            self.script = WowScript(player)
        else:
            self.script = script

        self.title('护肝神器_beta1')
        self.geometry('480x200')
        self.widgets = dict()
        self.setup_background()
        self.setup_take_record_btn(self.click_take_record_btn)
        self.setup_dropdown()
        self.setup_start_btn(self.click_start_btn)
        self.setup_information_label()
        self.script.start()

    def setup_background(self):
        self.img = tk.PhotoImage(file="./resources/background2.png")
        imgLabel = tk.Label(self, image=self.img)
        imgLabel.grid(row=0, column=0, columnspan=3)
        # imgLabel.pack(side="top")

    def setup_information_label(self):
        explanation = """
战场挂机有风险，谨慎操作!
奥山仅支持排进战场，战场内行动暂未定义，(支持自定义)
录脚本功能：点录制开始，按esc结束, 文件在‘./script_records_日期_时间.json’"""
        self.widgets['info_label'] = tk.Label(self,text=explanation,justify=tk.LEFT).grid(row=2, column=0, columnspan=3)

    def setup_take_record_btn(self, take_record_btn_click_command):
        self.widgets['take_record_btn_content'] = tk.StringVar()
        self.widgets['take_record_btn_content'].set("录制")
        self.widgets['take_record_btn'] = tk.Button(
            self, textvariable=self.widgets['take_record_btn_content'], command=take_record_btn_click_command,
            width=15
        ).grid(row=1, column=0, padx=0.5, pady=4, sticky='n')

    def setup_start_btn(self, script_run_btn_click_command):
        self.widgets['start_btn_content'] = tk.StringVar()
        self.widgets['start_btn_content'].set("开始")
        self.widgets['start_btn'] = tk.Button(
            self, textvariable=self.widgets['start_btn_content'], command=script_run_btn_click_command,
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

    def click_take_record_btn(self):
        self.widgets['take_record_btn_content'].set("录像中")
        TakeRecord()
        self.widgets['take_record_btn_content'].set("录制")
        return
        
if __name__ == "__main__":
    window = WowClient()
    player = Player(window)
    script = WowScript(None, player)
    laucher = Laucher(script)
    laucher.mainloop()
