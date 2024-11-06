import tkinter as tk
import elements.images
class StatusInputWindow(tk.Toplevel):
    def __init__(self, parent:tk.Frame, prompt:str=""):
        super().__init__(parent)
        self.parent = parent
        self.prompt = prompt

        self.label = tk.Label(self, text=self.prompt)
        self.label.pack(pady=10)
        self.textbox = IDInputBox(self)
        self.textbox.pack(pady=10)
        self.textbox.entry.bind("<Return>", lambda event: self.submit())  # Also handle Enter key
        self.feedback = tk.Label(self, text="")
        self.feedback.pack(pady=10)
        # self.commands = {0: 'In Use', 1: 'Available', 2: 'Unopened', 3: 'Opened', 4: 'Empty'}
        self.commands: list[str] = ['in use', 'available', 'unopened', 'opened', 'empty']
        self.image_display = elements.images.ImageDisplay(self, commands=self.commands)
        self.image_display.pack(side="bottom", fill="both", expand=True)
        self.grab_set()
        self.wait_window(self)

    def submit(self, command: str = "")->None:
        if command == "":
            command = self.textbox.entry.get()
        if command.lower() in self.commands:
            self.result = self.commands.index(command.lower()) + 1
        else:
            self.feedback.config(text="Invalid input: \"" + command + "\", please try again.")
        print("result " + str(self.result))
        self.destroy()  # Close the window

    def get_input(self) ->int:
        return self.result
class IDInputBox(tk.Frame):
    # parent could be any number of tk.Frame children.
    def __init__(self,parent:StatusInputWindow):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.entry = tk.Entry(self)
        self.entry.pack()
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda event: parent.submit())
    def handle_command(self, command:str = ""):
        self.parent.submit(command=command)