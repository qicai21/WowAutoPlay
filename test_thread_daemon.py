#!/usr/bin/env python
# coding: utf-8

import threading
import time
from threading import Thread

STATUS = 0 
Lock = threading.Lock()

class OutputLoop(Thread):
    def __init__(self):
        Thread.__init__(self)
        
    def run(self):
        global STATUS
        i = 0
        while True:
            time.sleep(2)
            Lock.acquire()
            print(f"the no_{i} round: status is {['human', 'bear', 'cat'][STATUS]}")
            Lock.release()
            i += 1

class MainProgress(Thread):
    def __init__(self):
        Thread.__init__(self)
        
    def run(self):
        global STATUS
        txt = None
        print("loop start")
        t = OutputLoop()
        t.setDaemon(True)
        t.start()
        while(txt != 'y'):
            txt = input("stop or not:")
            Lock.acquire()
            if txt == 'human':
                STATUS = 0
            elif txt == 'bear':
                STATUS = 1
            elif txt == 'cat':
                STATUS = 2
            else:
                STATUS = 0
            Lock.release()
            time.sleep(1)
        print("loop end")

            
if __name__ == "__main__":
    t = MainProgress()
    t.start()
