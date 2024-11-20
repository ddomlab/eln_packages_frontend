import tkinter as tk
from tkinter import ttk
import elements.scrollframe


root = tk.Tk()

frame = elements.scrollframe.ScrollableFrame(root)

for i in range(50):
    ttk.Label(frame.scrollable_frame, text="simp scrolling label").pack()

frame.pack()
root.mainloop()