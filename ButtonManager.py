import tkinter as tk
import os

__all__ = ["ButtonManager"]

class ButtonManager:

    def __init__(self, text):

        self.text = text

        self.text.tag_config("folder", background="gray30", foreground="#A4541D", justify=tk.LEFT, font=("Ariel", 10, "bold"),
                             lmargin1="15", spacing1=2, spacing3=2)
        self.text.tag_config("file", background="gray30", foreground="#1DA498", justify=tk.LEFT, font=("Ariel", 10, "bold"),
                             lmargin1="15", spacing1=2, spacing3=2)

        self.text.tag_bind("folder", "<Enter>", self._enter)
        self.text.tag_bind("folder", "<Leave>", self._leave)
        self.text.tag_bind("folder", "<Button-1>", self._click)

        self.text.tag_bind("file", "<Enter>", self._enter)
        self.text.tag_bind("file", "<Leave>", self._leave)
        self.text.tag_bind("file", "<Button-1>", self._click)

        self.folder = {}
        self.file = {}

    def reset(self):
        self.folder.clear()
        self.file.clear()

    def add(self, action, folder):
        tag = "folder-%d" % len(self.folder)
        self.folder[tag] = [action, folder]
        return "folder", tag

    def addFile(self, action, file):
        tag = "file-%s" % len(self.file)
        current = "current-%s" % len(self.file)
        self.file[tag] = [action, file]
        return "file", current, tag

    def _enter(self, event):
        # self._leave()
        self.text.config(cursor="hand2")

        for tag in self.text.tag_names(tk.CURRENT):
            if tag[:7] == "folder-":
                self.text.tag_config(tag, background="blue", foreground="#A4541D", justify=tk.LEFT,
                                     font=("Ariel", 10, "bold"), lmargin1="15")
                return
            elif tag[:5] == "file-":
                self.text.tag_config(tag, background="blue", foreground="#1DA498", justify=tk.LEFT,
                                     font=("Ariel", 10, "bold"), lmargin1="15")
                return

    def _leave(self, event=""):
        self.text.config(cursor="")
        for tag in self.text.tag_names():
            if tag[:7] == "folder-":
                self.text.tag_config(tag, background="gray30", foreground="#A4541D", justify=tk.LEFT,
                                     font=("Ariel", 10, "bold"), lmargin1="15")
            elif tag[:5] == "file-":
                self.text.tag_config(tag, background="gray30", foreground="#1DA498", justify=tk.LEFT,
                                     font=("Ariel", 10, "bold"), lmargin1="15")

    def _click(self, event):
        for tag in self.text.tag_names(tk.CURRENT):
            if tag[:7] == "folder-":
                self.folder[tag][0](self.folder[tag][1])
                return
            elif tag[:5] == "file-":
                for current in self.text.tag_names():
                    if current[:8] == "current-":
                        self.text.tag_lower(current)
                self.file[tag][0](self.file[tag][1])
                self.text.tag_raise(f"current-{tag[5:]}")
                self.text.tag_config(f"current-{tag[5:]}", background="blue", foreground="#1DA498", justify=tk.LEFT,
                                     font=("Ariel", 10, "bold"), lmargin1="15")
                return

    def scroll(self, checked):
        for key, value in self.file.items():
            for val in value:
                if val == checked:
                    tag = key
        try:
            if tag[:5] == "file-":
                for current in self.text.tag_names():
                    if current[:8] == "current-":
                        self.text.tag_lower(current)
                self.file[tag][0](self.file[tag][1])
                self.text.tag_raise(f"current-{tag[5:]}")
                self.text.tag_config(f"current-{tag[5:]}", background="blue", foreground="#1DA498", justify=tk.LEFT,
                                     font=("Ariel", 10, "bold"), lmargin1="15")
                self.text.see(self.text.search(f"- {os.path.split(checked)[-1]}\n", 1.0))
                return
        except ValueError:
            return
