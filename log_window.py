import tkinter as tk
from queue import Empty
import ctypes

def get_caps_lock_state():
    hllDll = ctypes.WinDLL("User32.dll")
    VK_CAPITAL = 0x14
    return hllDll.GetKeyState(VK_CAPITAL)

class LogWindow:
    def __init__(self, queue):
        self.root = tk.Tk()
        self.root.title("Mouse Control Log")
        self.root.geometry("300x150")
        self.root.attributes('-topmost', True)
        
        self.log_text = tk.Text(self.root, height=5, width=40)
        self.log_text.pack(pady=10)
        
        self.caps_lock_label = tk.Label(self.root, text="Caps Lock: OFF")
        self.caps_lock_label.pack()
        
        self.queue = queue
        self.update_gui()

    def update_log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        if self.log_text.index('end-1c').split('.')[0] > '5':
            self.log_text.delete('1.0', '2.0')

    def update_caps_lock_state(self):
        if get_caps_lock_state():
            self.caps_lock_label.config(text="Caps Lock: ON")
        else:
            self.caps_lock_label.config(text="Caps Lock: OFF")

    def update_gui(self):
        try:
            while True:
                message = self.queue.get_nowait()
                if message == "QUIT":
                    self.root.quit()
                    return
                self.update_log(message)
        except Empty:
            pass
        self.update_caps_lock_state()
        self.root.after(100, self.update_gui)
