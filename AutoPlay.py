import tkinter as tk
from tkinter import *

from WowClient import WowClient
from Player import Player
from ScriptManager import AlxScript, check_in_expiration

window = Tk()
window.title('护肝神器_工程版')
window.geometry('480x150')
logo = PhotoImage(file="resources/background.png")
w1 = Label(window, image=logo).pack(side="top")

explanation = """本软件仅用于测试，说明：
目前还是最基础的工程版，用于alx和战歌"""

tk.Label(window,text=explanation,justify=LEFT).place(x=10,y=85,anchor='nw')

# 开始按钮
btn_content = tk.StringVar()
btn_content.set("开始")

# dropdown
# dropdown_items = ['阿拉希', '战歌', '奥山', '泡世界buff', '刷惩戒器']
# dropdown_content = tk.StringVar(window)
# dropdown_content.set(dropdown_items[0])

# 初始化组件
wow = WowClient()
player = Player(wow)
script = AlxScript(player)

# alx = None
# warsong = None
# alterac = None
# worldbuff = None

def click_switch_btn():
    if not check_in_expiration():
        btn_content.set("过期了")
        return

    # 获取dropdown的选项
    # selection = dropdown_content.get()
    # if selection == '阿拉希':
    #     if alx == None:
    #         alx = AlxScript(player)
    #         alx.start()
    #         alx.pause()
    #     script = alx
    # elif selection == '战歌':
    #     if warsong == None:
    #         warsong = WarsongScript(player)
    #     script = warsong
    # elif selection == '奥山':
    #     if alterac == None:
    #         alterac = AlteracScript(player)
    #     script = alterac
    # elif selection == '泡世界buff':
    #     if worldbuff == None:
    #         worldbuff = WaitForBuffScript(player)
    #     script = alterac
    # else:
    #     raise Exception('还没实装')
    
    if script.is_running():
        script.pause()
        content = "恢复"

    else:
        script.resume()
        content = "暂停"
    btn_content.set(content)

script.start()


b = tk.Button(window, textvariable=btn_content, command=click_switch_btn, width=15, height=2,).place(x=330,y=90,anchor='nw')
# dropdown = tk.OptionMenu(window, dropdown_content, *dropdown_items).place(x=330, y=80, anchor='nw')

window.mainloop()