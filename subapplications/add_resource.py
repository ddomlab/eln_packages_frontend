import tkinter as tk
import elements.images
import eln_packages_common.fill_info as filler

class Add_Resource_Window(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Add Resource")
        self.geometry("400x400")
        self.resizable(False, False)

        self.cas_label = tk.Label(self, text="CAS:")
        self.cas_label.pack(pady=10)
        self.cas_entry = tk.Entry(self)
        self.cas_entry.bind("<Return>", self.fill_info)
        self.search_button = tk.Button(self, text="Search", command=self.fill_info)
        self.cas_entry.pack(pady=10)
        self.search_button.pack(pady=0)

        self.title_label = tk.Label(self, text="Title:")
        self.title_label.pack(pady=10)
        self.title_entry = tk.Entry(self)
        self.title_entry.pack(pady=10)

        
        self.submit_button = tk.Button(self, text="Submit", command=self.submit)
        self.submit_button.pack(pady=10)
    def fill_info(self, event=None):
        cas_entry = self.cas_entry.get()
        if filler.check_if_cas(cas_entry):
            self.title_entry.insert(0, filler.pull_values(cas_entry)["Title_0"])
    def submit(self):
        pass