import tkinter as tk
import input_process


class MainApplication(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.ip = input_process.Processor(self)
        self.textbox = InputProcessor(self)
        self.registry_display = RegistryDisplay(self)
        self.image_display = ImageDisplay(self)

        self.registry_display.pack(
            side="left", fill="both", expand=True, padx=10, pady=10
        )
        self.textbox.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        self.image_display.pack(side="bottom", fill="both", expand=True)

    def input_prompt(self, prompt):
        input_window = SmallInputWindow(self, prompt)
        return input_window.get_input()


class SmallInputWindow(tk.Toplevel):
    def __init__(self, parent, prompt=""):
        super().__init__(parent)
        self.parent = parent
        self.result = None
        self.prompt = prompt

        self.label = tk.Label(self, text=self.prompt)
        self.label.pack(pady=10)

        self.entry = tk.Entry(self)
        self.entry.pack(pady=5)
        self.entry.focus_set()

        self.entry.bind("<Return>", self.submit)  # Also handle Enter key

        # Wait for the window to close before continuing
        self.grab_set()
        self.wait_window(self)

    def submit(self, event=None):
        self.result = self.entry.get()  # Get the input value
        self.destroy()  # Close the window

    def get_input(self):
        return self.result


class InputProcessor(tk.Frame):
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
    def handle_command(self, event):
        # Get the input from the entry box
        command = self.entry.get()
        # Clear the entry box after pressing return
        self.entry.delete(0, tk.END)

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
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.images: list[str] = self.parent.ip.commands.keys()
        self.create_grid()

    def create_grid(self):
        # Display images in a 2x4 grid
        for i, imagename in enumerate(self.images):
            row = i // 4
            col = i % 4
            imagegroup = ImageWithCaption(self, imagename, imagename)
            imagegroup.grid(row=row, column=col, padx=40, pady=40)


class ImageWithCaption(tk.Frame):
    def __init__(self, parent, imagename, captiontext):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.image = tk.PhotoImage(file=f"images/{imagename}.gif")
        self.label = tk.Label(self, image=self.image)
        self.label.pack()
        self.caption = tk.Label(self, text=captiontext)
        self.caption.pack()


def main():
    # Create the main window
    root = tk.Tk()
    root.title("Label Manager")
    root.resizable(width=False, height=False)
    MainApplication(root).pack(side="top", fill="both", expand=True)

    root.mainloop()
