import tkinter as tk
from pathlib import Path
current_dir = Path(__file__).parent

class ImageDisplay(tk.Frame):
    def __init__(self, parent, commands: list[str]):
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
            file = str(current_dir.parent / "images" / f"{imagename}.gif")
        )
        self.img_btn = tk.Button(
            self, 
            image=self.image,
            command=lambda: self.parent.parent.textbox.handle_command(command=imagename),
            )
        self.img_btn.pack()
        self.caption = tk.Label(self, text=captiontext)
        self.caption.pack()
