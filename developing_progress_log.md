# WOW挂机脚本制作随笔

选择anaconda作为挂机脚本制作的IDE，可以方便的管理用到的package。anaconda的安装过程掠过，安装好后创建wowScript环境，专门用于本插件的制作。

本文主要思路来自于：[Python写一个痒痒鼠脚本](https://mp.weixin.qq.com/s/Dj_s-t8MPEUkwNyfS9Uwag)，文中是为其他游戏设置自动化脚本，但核心思路异曲同工。依文中所述，用到的核心库：有opencv、numpy、pywin32、Pillow、tkinter等。

## 库的安装

在win10下利用anaconda安装和管理python库，安装号anaconda后，在home页面选择Powershell-Prompt，意思就是anaconda的shell，使用Powershell来管理，等同于linux下的bash。选择刚才创建的`wowScript`环境,然后运行prompt，就是在目标环境下运行和维护anaconda相关库了。（省掉大量网文中写的单独配置virtualenv的过程）

opencv，numpy，pywin32， Pillow, tkinter

### opencv

用于图像视频识别。

- opencv-python: 只包含opencv库的主要模块. 一般不推荐安装.
- opencv-contrib-python: 包含主要模块和contrib模块, 功能基本完整, 推荐安装.
- opencv-python-headless: 和opencv-python一样, 但是没有GUI功能, 无外设系统可用.
- opencv-contrib-python-headless: 和opencv-contrib-python一样但是没有GUI功能. 无外设系统可用.

因此一般来说都会选择安装opencv-contrib-python

### numpy 

计算模块,直接pip安装即可。

### pywin32

它直接包装了几乎所有的Windows API，可以方便地从Python直接调用，该模块另一大主要功能是通过Python进行COM编程.直接pip安装即可。参考:[Windows平台Python编程必会模块之pywin32](https://www.cnblogs.com/achillis/p/10462585.html)。

### Pillow

绘图模块,pip install directly.

### tkinter

将application封装为gui插件用的,`pip install pythotk`。

```bash
$ pip install opencv-contrib-python, Pillow, pywin32, pythotk
```



### python类命名规范

> 惭愧啊，都快忘光了！

```python

#类的定义
class Dog:                        #类:驼峰
    __name=""                    #私有实例变量(__name)前有2个下划线
    def __init__(self,name):   
        self.__name=name
    def getName(self):         #方法名小驼峰(getName);或get_name
        return self.__name
 
#对象的创建  
if __name__=="__main__":
    
    dog=Dog("alice")
    print(dog.getName())
```



# 过程记录

现在的想法是先获取窗口，然后能跳一下。

1. 获取窗口

   获取窗口的过程中主要发生了2个问题，一个是按文中方法获取窗口并将窗口前置会抛出异常，通过添加win32com.client.Dispatch解决：

    ```python
    import win32gui, win32com.client
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    win32gui.SetForegroundWindow(window.hwnd)
    ```
   
   另一个是截图不完整，通过分析，了解了win32gui.GetWindowRect()捕获坐标和尺寸的结果是系统当前分辨率经过系统缩放后的结果。简单的说在2560*1440分辨率下，一个（0，0， 200， 100）的窗口，缩放为100%时为（0,0,200,100）, 但系统缩放为200%，则为（0,0,100,50).我捕获的就是后者，需通过`win32print.GetDeviceCaps`获取系统分辨率，并通过`GetSystemMetrics(0)`获取缩放比例，然后反推计算得出真实坐标信息，再传输给ImageGrab截图。具体的办法我写在代码中，此处略去。

2. 模拟空格跳动

   通过win32api.keybd_event模拟范例

   ```python
   import win32con
   import win32api
   import time
   #第一个参数，键盘对应数字，查表
   #第二个，第四个没用
   #第三个参数，0代表按下，win32con.KEYEVENTF_KEYUP松开
   while True:
       win32api.keybd_event(91, 0, 0, 0)  # 键盘按下 91win
       time.sleep(1)
       win32api.keybd_event(77, 0, 0, 0)  # 键盘按下  68  D
       time.sleep(1)
       win32api.keybd_event(77, 0, win32con.KEYEVENTF_KEYUP, 0)  # 键盘松开  D 68
       win32api.keybd_event(91, 0, win32con.KEYEVENTF_KEYUP, 0)  # 键盘松开
   
   # 模拟"shift+["输出"{"符号的范例
   win32api.keybd_event(16, 0, 0, 0)  # 按下shift
   win32api.keybd_event(219, 0, 0, 0)  # 按下“[{”
   win32api.keybd_event(219, 0, win32con.KEYEVENTF_KEYUP, 0)  # 松开shift
   win32api.keybd_event(16, 0, win32con.KEYEVENTF_KEYUP, 0)  # 松开“[{”
   ```
   
   **键盘键码对照表**

   | 按键      | 键码 | 按键        | 键码 | 按键        | 键码 | 按键        | 键码 |
   | --------- | ---- | ----------- | ---- | ----------- | ---- | ----------- | ---- |
   | A         | 65   | 6(数字键盘) | 102  | ;           | 59   | :           | 58   |
   | B         | 66   | 7(数字键盘) | 103  | =           | 61   | +           | 43   |
   | C         | 67   | 8(数字键盘) | 104  | ,           | 44   | <           | 60   |
   | D         | 68   | 9(数字键盘) | 105  | -           | 45   | _           | 95   |
   | E         | 69   | *           | 106  | .           | 46   | >           | 62   |
   | F         | 70   | !           | 33   | /           | 47   | ?           | 63   |
   | G         | 71   | Enter       | 13   | `           | 96   | ~           | 126  |
   | H         | 72   | @           | 64   | [           | 91   | {           | 123  |
   | I         | 73   | #           | 35   | \           | 92   | \|          | 124  |
   | J         | 74   | $           | 36   | }           | 125  | ]           | 93   |
   | K         | 75   | F1          | 112  | a           | 97   | b           | 98   |
   | L         | 76   | F2          | 113  | c           | 99   | d           | 100  |
   | M         | 77   | F3          | 114  | e           | 101  | f           | 102  |
   | N         | 78   | F4          | 115  | g           | 103  | h           | 104  |
   | O         | 79   | F5          | 116  | i           | 105  | j           | 106  |
   | P         | 80   | F6          | 117  | k           | 107  | l           | 108  |
   | Q         | 81   | F7          | 118  | m           | 109  | n           | 110  |
   | R         | 82   | F8          | 119  | o           | 111  | p           | 112  |
   | S         | 83   | F9          | 120  | q           | 113  | r           | 114  |
   | T         | 84   | F10         | 121  | s           | 115  | t           | 116  |
   | U         | 85   | F11         | 122  | u           | 117  | v           | 118  |
   | V         | 86   | F12         | 123  | w           | 119  | x           | 120  |
   | W         | 87   | Backspace   | 8    | y           | 121  | z           | 122  |
   | X         | 88   | Tab         | 9    | 0(数字键盘) | 96   | Up Arrow    | 38   |
   | Y         | 89   | Clear       | 12   | 1(数字键盘) | 97   | Right Arrow | 39   |
   | Z         | 90   | Shift       | 16   | 2(数字键盘) | 98   | Down Arrow  | 40   |
   | 0(小键盘) | 48   | Control     | 17   | 3(数字键盘) | 99   | Insert      | 45   |
   | 1(小键盘) | 49   | Alt         | 18   | 4(数字键盘) | 100  | Delete      | 46   |
   | 2(小键盘) | 50   | Cap Lock    | 20   | 5(数字键盘) | 101  | Num Lock    | 144  |
   | 3(小键盘) | 51   | Esc         | 27   | 2(数字键盘) | 98   | Down Arrow  | 40   |
   | 4(小键盘) | 52   | Spacebar    | 32   | 3(数字键盘) | 99   | Insert      | 45   |
   | 5(小键盘) | 53   | Page Up     | 33   | 4(数字键盘) | 100  | Delete      | 46   |
   | 6(小键盘) | 54   | Page Down   | 34   | 5(数字键盘) | 101  | Num Lock    | 144  |
   | 7(小键盘) | 55   | End         | 35   |             |      |             |      |
   | 8(小键盘) | 56   | Home        | 36   |             |      |             |      |
   | 9(小键盘) | 57   | Left Arrow  | 37   |             |      |             |      |

3. 创建Player类，有status来记录当前玩家状态包括：

   - alive

   - in_battle

   - posi

   - in_sequence

   xy（*）--坐标

   

   | alive | in_battle | posi | in_sequence | 任务                   | action         | 其他                    |
   | ----- | --------- | ---- | ----------- | ---------------------- | -------------- | ----------------------- |
   | alive | false     | 大厅 | false       | 排队                   | 执行“=”宏      | 等号宏有缺陷，=\=才好用 |
   | alive | false     | 大厅 | true        | 等候排队，防掉线       | 防掉线         | --                      |
   | alive | false     | 大厅 | true        | 识别加入战场窗口       | 点击加入       | --                      |
   | alive | true      | 旗房 | true        | 防止掉线，战场结束退出 | 跳一跳，走一走 |                         |
   | alive | true      | 墓地 | true        | 防止掉线，战场结束退出 | 跳一跳，走一走 |                         |
   | dead  | true      | 其他 | true        | 释放尸体               | 点击尸体释放   |                         |
   | alive | true      | 其他 | true        | 战场结束退出           | 点击离开       |                         |

4. 防掉线动作

   一组动作

   ​	跳一下

   ​	左平移+右平移

   ​	使用饰品+“挂毛，给老子跳舞”

   ​	

5. 识别图像

   已经能够识别是否在战场

   是否需要放魂

   待识别的离开战场

   

6. log

7. 还需要一个键盘记录器：[详解：keybd_event模拟键盘输入，附键码表](https://blog.csdn.net/polyhedronx/article/details/81988948)

8. 模拟使用技能

9. 第一次封装