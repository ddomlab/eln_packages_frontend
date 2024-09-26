import tkinter as tk
import frontend.input_process


class MainApplication(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.textbox = InputProcessor(self)
        self.registry_display = RegistryDisplay(self)
        self.image_display = ImageDisplay(self)

        self.registry_display.pack(side="left", fill="both", expand=True)
        self.textbox.pack(side="top", fill="both", expand=True)
        self.image_display.pack(side="bottom", fill="both", expand=True)


class InputProcessor(tk.Frame):
    def __init__(self, parent):
        self.ip = frontend.input_process.Processor()
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.entry = tk.Entry(width=50)
        self.entry.pack(padx=10, pady=10)
        self.entry.bind("<Return>", self.handle_command)

    # Function to handle the command input
    def handle_command(self, event):
        # Get the input from the entry box
        command = self.entry.get()
        # Clear the entry box after pressing return
        self.entry.delete(0, tk.END)
        # Call another function to handle the command
        self.ip.from_terminal(command)
        self.parent.registry_display.update_registry(self.ip.registry.id_registry)


class RegistryDisplay(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.label = tk.Label(self, text="Registry")
        self.label.pack()
        self.listbox = tk.Listbox(self)
        self.listbox.pack()

    def update_registry(self, registry):
        self.listbox.delete(0, tk.END)
        for item in registry:
            self.listbox.insert(tk.END, item)


class ImageDisplay(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.images: list[str] = frontend.input_process.Processor.commands.keys()
        self.create_grid()

    def create_grid(self):
        # Display images in a 2x4 grid
        for i, imagename in enumerate(self.images):
            row = i // 4
            col = i % 4
            imagegroup = ImageWithCaption(self, imagename, imagename)
            imagegroup.grid(row=row, column=col, padx=10, pady=1)


class ImageWithCaption(tk.Frame):
    def __init__(self, parent, imagename, caption):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.image = tk.PhotoImage(file=f"images/{imagename}.gif")
        self.label = tk.Label(self, image=self.image)
        self.label.pack()
        self.caption = tk.Label(self, text=caption)
        self.caption.pack()


def main():
    # Create the main window
    root = tk.Tk()
    root.title("Simple Terminal")
    MainApplication(root).pack(side="top", fill="both", expand=True)

    root.mainloop()
