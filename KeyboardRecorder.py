import time
import json
from pynput import keyboard


class KeyboardRecorder():

    def __init__(self):
        self.script = []
        self.hold_keys = []
        self.time_cursor = time.time() 

    def get_duration_and_reset_time_cursor(self):
        new_cursor = time.time()
        duration = round(new_cursor - self.time_cursor, 2)
        self.time_cursor = new_cursor
        return duration

    def parse_key_to_str(self, key):
        print(key)
        if key == keyboard.Key.space:
            return "spacebar"
        elif key == keyboard.Key.backspace:
            return "backspace"
        elif key == keyboard.Key.enter:
            return "enter"
        elif key == keyboard.Key.alt_l:
            return "alt"
        elif key == keyboard.Key.tab:
            return "tab"
        elif key == keyboard.Key.up:
            return "up_arrow"
        elif key == keyboard.Key.left:
            return "left_arrow"
        elif key == keyboard.Key.right:
            return "right_arrow"
        else:
            return key.char

    def on_press(self, key):
        if key == keyboard.Key.esc:
            return False

        key_str = self.parse_key_to_str(key)

        if not key_str in self.hold_keys:
            duration = self.get_duration_and_reset_time_cursor()
            # 先添加空白等待
            if duration > 0.05:
                self.add_wait_record(duration)
            # 再添加按键记录
            self.add_press_hold_record(key_str)
            self.hold_keys.append(key_str)

    def on_release(self, key):
        key_str = self.parse_key_to_str(key)
        duration = self.get_duration_and_reset_time_cursor()

        (last_action, last_key) = self.get_last_record_info()
        if last_action == "pressAndHold" and last_key == key_str:
            self.add_press_record(key_str, duration)
        else:
            self.add_wait_record(duration)
            self.add_release_record(key_str)

        try:
            self.hold_keys.remove(key_str)
        except ValueError as e:
            pass


    def get_last_record_info(self):
        last_record = list(self.script[-1].values())[0]
        last_action = last_record[0]
        last_key = last_record[1]
        return last_action, last_key

    def start(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

    def add_press_record(self, key, _time):
        index = self.script.pop(-1)
        self.script.append(
            {"keyboard_action": ["press", key, _time]}
        )

    def add_press_hold_record(self, key):
        self.script.append(
            {"keyboard_action": ["pressAndHold", key, 0]}
        )

    def add_release_record(self, key):
        self.script.append(
            {"keyboard_action": ["release", key, 0]}
        )

    def add_wait_record(self, _time):
        self.script.append(
            {"wait_action": ["wait_in_second", _time]}
        )

def TakeRecord():
    recorder = KeyboardRecorder()
    print('录制开始')
    recorder.start()
    with open('./scripts/script_records.json', 'w+') as f:
        json.dump({'scripts': recorder.script}, f)
    print('录制结束')


if __name__ == "__main__":
    TakeRecord()

