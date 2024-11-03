import tkinter as tk
import elements.images
import elements.scrollframe
import eln_packages_common.fill_info as filler
import json

class Add_Resource_Window(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.dropdown = Category_Dropdown(self)
        self.dropdown.pack()

        self.draw_items()



    def draw_items(self):
        # clear all widgets in the frame
        for widget in self.winfo_children():
            # exclude self.dropdown
            if widget != self.dropdown:
                widget.destroy()


        if self.dropdown.clicked.get() != "Instrument":
            self.cas_label = tk.Label(self, text="Search by CAS (or name if CAS unavailable):")
            self.cas_label.pack(pady=10)
            self.cas_entry = tk.Entry(self)
            self.cas_entry.bind("<Return>", self.fill_info)
            self.search_button = tk.Button(self, text="Search", command=self.fill_info)
            self.cas_entry.pack(pady=5)
            self.search_button.pack(pady=0)
            self.pack(side="left")

        # add title and body fields
        title_entrybox = Labeled_Entrybox(self, text="title")
        title_entrybox.entry.insert(0, self.dropdown.clicked_dict['title'])
        title_entrybox.pack(pady=10)
        body_box = Labeled_Textbox(self, text="body")
        body_box.textbox.insert(tk.END, self.dropdown.clicked_dict['body'])
        body_box.pack(pady=10)

        self.add_metadata_fields()

        for entrybox in self.metadata_entryboxes:
            entrybox.pack(pady=10)
        self.submit_button = tk.Button(self, text="Submit", command=self.submit)
        self.submit_button.pack(pady=10)


    def add_metadata_fields(self):
        # get all metadata fields from the resource template, and have a list with an Entrybox for each
        self.metadata_entryboxes: list[Labeled_Textbox] = []
        metadata_dict = json.loads(self.dropdown.clicked_dict['metadata'])['extra_fields']
        # for each metadata field, add an Entrybox to the list
        for field in metadata_dict:
            entrybox: Labeled_Entrybox = Labeled_Entrybox(self, text=field)
            entrybox.pack(pady=10)
            self.metadata_entryboxes.append(entrybox)

    def fill_info(self, event=None):
        cas_entry = self.cas_entry.get()
    def submit(self):
        pass
class Labeled_Textbox(tk.Frame):
    def __init__(self, parent, text=""):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.label = tk.Label(self, text=text+":")
        self.label.pack(pady=10)
        self.textbox = tk.Text(self, height=10, width=30)
        self.textbox.pack(pady=10)
        
class Labeled_Entrybox(tk.Frame):
    def __init__(self,parent, text=""):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.label = tk.Label(self, text=text+":")
        self.label.pack(pady=10)
        self.entry = tk.Entry(self)
        self.entry.pack(pady=10)
class Category_Dropdown(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.type_label: tk.Label = tk.Label(self, text="Select type of resource:")
        self.type_label.pack(pady=10)

        self.category_names: list[str] = []
        self.category_dicts: list[dict] = filler.rm.get_items_types()
        for cat in self.category_dicts:
            self.category_names.append(cat['title'])

        self.clicked: tk.StringVar = tk.StringVar()
        self.clicked.set(self.category_names[1])
        self.clicked_dict: dict = self.category_dicts[1]

        self.drop = tk.OptionMenu( self , self.clicked , *self.category_names ) 
        self.drop.pack()

        # run on_category_change method when StringVar clicked is written
        self.clicked.trace_add('write', self.on_category_change)
    def on_category_change(self, *args):
        index: int = self.category_names.index(self.clicked.get())
        self.clicked_dict: dict = self.category_dicts[index]
        self.parent.draw_items()



def main():
    # Create the main window
    root = tk.Tk()
    root.title("Add Resource")
    root.resizable(width=True, height=True)
    root.geometry("400x600")
    scroll_area = elements.scrollframe.ScrollableFrame(root)
    root.bind("<Button-4>", scroll_area._on_mousewheel)
    root.bind("<Button-5>", scroll_area._on_mousewheel)


    Add_Resource_Window(scroll_area.scrollable_frame).pack(side="top", padx=20, fill="both", expand=True)
    scroll_area.pack(side="top", fill="both", expand=True)
    root.mainloop()
