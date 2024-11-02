import tkinter as tk
import elements.images
class StatusInputWindow(tk.Toplevel):
    def __init__(self, parent, prompt=""):
        super().__init__(parent)
        self.parent = parent
        self.result = None
        self.prompt = prompt

        self.label = tk.Label(self, text=self.prompt)
        self.label.pack(pady=10)
        self.textbox = IDInputBox(self)
        self.textbox.pack(pady=10)
        self.textbox.entry.bind("<Return>", self.submit)  # Also handle Enter key

        # self.commands = {0: 'In Use', 1: 'Available', 2: 'Unopened', 3: 'Opened', 4: 'Empty'}
        self.commands: list[str] = ['in use', 'available', 'unopened', 'opened', 'empty']
        self.image_display = elements.images.ImageDisplay(self, commands=self.commands)
        self.image_display.pack(side="bottom", fill="both", expand=True)
        self.grab_set()
        self.wait_window(self)

    def submit(self, event=None, command:str = None):
        if command is None:
            command = self.textbox.entry.get()
        if command.lower() in self.commands:
            command = self.commands.index(command.lower()) + 1
        self.result = command
        self.destroy()  # Close the window

    def get_input(self):
        return self.result
class IDInputBox(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.entry = tk.Entry(self)
        self.entry.pack()
        self.entry.focus_set()
        self.entry.bind("<Return>", parent.submit)
    def handle_command(self, event=None, command:str = None):
        self.parent.submit(command=command)