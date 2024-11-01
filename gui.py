import tkinter as tk
import input_process
from pathlib import Path

current_dir = Path(__file__).parent


class MainApplication(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.ip = input_process.Processor(self)
        self.textbox = BigTextbox(self)
        self.registry_display = RegistryDisplay(self)
        self.image_display = ImageDisplay(self, commands=self.ip.commands.keys())

        self.registry_display.pack(
            side="left", fill="both", expand=True, padx=10, pady=10
        )
        self.textbox.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        self.image_display.pack(side="bottom", fill="both", expand=True)

    def input_prompt(self, prompt) -> str:
        input_window = SmallInputWindow(self, prompt)
        return input_window.get_input()
    def status_prompt(self, prompt) -> str:
        input_window = StatusInputWindow(self, prompt)
        r = input_window.get_input()
        return r
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
       
        
class SmallInputWindow(tk.Toplevel):
    def __init__(self, parent, prompt="", is_parent=False):
        super().__init__(parent)
        self.parent = parent
        self.result = None
        self.prompt = prompt

        self.label = tk.Label(self, text=self.prompt)
        self.label.pack(pady=10)
        self.textbox = IDInputBox(self)
        self.textbox.pack(pady=10)
        self.textbox.entry.bind("<Return>", self.submit)  # Also handle Enter key

        # Wait for the window to close before continuing
        if not is_parent:
            self.grab_set()
            self.wait_window(self)

    def submit(self, event=None):
        # get the input from the textbox
        self.result = self.textbox.entry.get()
        # close the window
        self.destroy()

    def get_input(self):
        return self.result

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
        self.image_display = ImageDisplay(self, commands=self.commands)
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

class BigTextbox(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.output = tk.Label(self, text="Enter Action or ID Below:")
        self.output.pack(side="top")

        self.entry = tk.Entry(self, width=50)
        self.entry.pack(padx=10, pady=5)
        self.entry.focus_set()

        self.output = tk.Label(self, text=self.parent.ip.output)
        self.output.pack(side="bottom")

        self.entry.bind("<Return>", self.handle_command)

    # Function to handle the command input
    def handle_command(self,event=None, command:str = None):
        if command is None:
            command = self.entry.get()
        # Clear the entry box after pressing return
        self.entry.delete(0, tk.END)
        # actually run the command
        self.parent.ip.from_terminal(command)
        self.parent.registry_display.update_registry(
            self.parent.ip.registry.id_registry
        )  # update the displayed registry
        self.output.config(
            text=self.parent.ip.output
        )  # print the output from gui_print()

class RegistryDisplay(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.label = tk.Label(self, text="Registry")
        self.label.pack()
        self.listbox = tk.Listbox(self, width=6, height=1)
        self.listbox.pack()

    def update_registry(self, registry):
        if self.parent.ip.registry.is_batch:
            self.listbox.config(height=10)
        else:
            self.listbox.config(height=1)
        self.listbox.delete(0, tk.END)
        for item in registry:
            self.listbox.insert(tk.END, item)


class ImageDisplay(tk.Frame):
    def __init__(self, parent, commands: list[str]=None):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.commands = commands
        self.create_grid()

    def create_grid(self):
        # Display images in a 2x4 grid
        for i, imagename in enumerate(self.commands):
            row = i // 2
            col = i % 2
            imagegroup = ImageWithCaption(self, imagename, imagename)
            imagegroup.grid(row=row, column=col, padx=40, pady=40)


class ImageWithCaption(tk.Frame):
    def __init__(self, parent, imagename, captiontext):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.image = tk.PhotoImage(
            file = str(current_dir / "images" / f"{imagename}.gif")
        )
        self.img_btn = tk.Button(
            self, 
            image=self.image,
            command=lambda: self.parent.parent.textbox.handle_command(command=imagename),
            )
        self.img_btn.pack()
        self.caption = tk.Label(self, text=captiontext)
        self.caption.pack()


def main():
    # Create the main window
    root = tk.Tk()
    root.title("Label Manager")
    root.resizable(width=False, height=False)
    MainApplication(root).pack(side="top", fill="both", expand=True)

    root.mainloop()
