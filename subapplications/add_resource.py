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
        self.dictionary:dict = self.dropdown.clicked_dict
        self.draw_items()



    def draw_items(self):
        self.dictionary = self.dropdown.clicked_dict
        # clear all widgets in the frame
        for widget in self.winfo_children():
            # exclude self.dropdown
            if widget != self.dropdown:
                widget.destroy()

        # add search by CAS entrybox if the category is not "Instrument"
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
        self.title_entrybox = Labeled_Entrybox(self, category="title")
        self.title_entrybox.entry.insert(0, self.dropdown.clicked_dict['title'])
        self.title_entrybox.pack(pady=10)
        self.body_box = Labeled_Textbox(self, text="body")
        self.body_box.textbox.insert(tk.END, self.dropdown.clicked_dict['body'])
        self.body_box.pack(pady=10)

        self.add_metadata_fields()

        for entrybox in self.metadata_entryboxes:

            entrybox.pack(pady=10)
        self.submit_button = tk.Button(self, text="Submit", command=self.submit)
        self.submit_button.pack(pady=10)


    def add_metadata_fields(self):
        # get all metadata fields from the resource template, and have a list with an Entrybox for each
        self.metadata_entryboxes: list[Labeled_Entrybox] = []
        metadata_dict:dict = json.loads(self.dictionary['metadata'])['extra_fields']
        # for each metadata field, add an Entrybox to the list
        for field in metadata_dict:
            entrybox:Labeled_Entrybox = Labeled_Entrybox(self, category=field, value_info=metadata_dict[field])
            if metadata_dict[field]['type'] not in ['select', 'radio']:
                entrybox.entry.insert(0, metadata_dict[field]['value'])
            entrybox.pack(pady=10)
            self.metadata_entryboxes.append(entrybox)

    def fill_info(self, event=None):
        cas_entry:str = self.cas_entry.get()
        results:dict = filler.pull_values(cas_entry)
        metadata:dict = json.loads(self.dropdown.clicked_dict['metadata'])['extra_fields']
        if filler.check_if_cas(cas_entry):
            metadata['CAS']['value'] = cas_entry
        for result_field in results:
            if result_field in metadata:
                metadata[result_field]['value'] = results[result_field]
        metadata_str:str = json.dumps({"extra_fields": metadata})
        self.dictionary['metadata'] = metadata_str
        self.draw_items()
        
    def submit(self):
        new_metadata:dict = json.loads(self.dictionary['metadata'])
        for entrybox in self.metadata_entryboxes:
            entry_dict:dict = entrybox.get()[1]
            entry_name:str = entrybox.get()[0]
            new_metadata['extra_fields'][entry_name] = entry_dict
        self.dictionary['metadata'] = json.dumps(new_metadata)
        self.dictionary['title'] = self.title_entrybox.entry.get()
        self.dictionary['body'] = self.body_box.textbox.get("1.0", tk.END)
        filler.rm.create_item(self.dropdown.clicked_index, self.dictionary)
        

class Labeled_Textbox(tk.Frame):
    def __init__(self, parent, text=""):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.label = tk.Label(self, text=text+":")
        self.label.pack(pady=10)
        self.textbox = tk.Text(self, height=10, width=30)
        self.textbox.pack(pady=10)
        
class Labeled_Entrybox(tk.Frame):
    def __init__(self, parent, category: str = "", value_info: dict = {'type': "text", 'value' : ''}):
        tk.Frame.__init__(self, parent)
        self.category = category
        self.discrete_types:list[str] = ["select", "radio"]
        self.string_types:list[str] = ["text", "date"]
        self.parent = parent
        self.return_dict: dict = value_info
        self.label = tk.Label(self, text=category+":")
        self.label.pack(pady=10)

        self.textbox_frame = tk.Frame(self)
            
        if value_info['type'] == "number":
            self.entry = tk.Entry(self.textbox_frame)
            self.entry.pack(side="left")
            self.unit:tk.StringVar = tk.StringVar()
            self.unit.set(value_info['units'][0])
            self.unit_chooser:tk.OptionMenu = tk.OptionMenu(self.textbox_frame, self.unit, *value_info['units'])
            self.unit_chooser.pack(side="right",expand=True)
        elif value_info['type'] in self.string_types:
            self.entry = tk.Entry(self.textbox_frame)
            self.entry.pack()
        elif value_info['type'] in self.discrete_types:
            self.choice = tk.StringVar()
            self.choice.set(value_info['options'][0])
            self.chooser = tk.OptionMenu(self.textbox_frame, self.choice, *value_info['options'])
            self.chooser.pack()

        if value_info['type'] == "date":
            self.label.config(text=category+" (YYYY-MM-DD):")
        self.textbox_frame.pack(pady=10)
    def get(self)->tuple[str, dict]:
        if self.return_dict['type'] == "number":
            self.return_dict['value'] = self.entry.get()
            self.return_dict['units'] = self.unit.get()
        elif self.return_dict['type'] in self.string_types:
            self.return_dict['value'] = self.entry.get()
        elif self.return_dict['type'] in self.discrete_types:
            self.return_dict['value'] = self.choice.get()
        return (self.category , self.return_dict)
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
        self.clicked_index:int = 1
        self.clicked_dict: dict = self.category_dicts[1]

        self.drop = tk.OptionMenu( self , self.clicked , *self.category_names ) 
        self.drop.pack()

        # run on_category_change method when StringVar clicked is written
        self.clicked.trace_add('write', self.on_category_change)
    def on_category_change(self, *args):
        self.clicked_index: int = self.category_names.index(self.clicked.get())
        self.clicked_dict: dict = self.category_dicts[self.clicked_index]
        self.parent.draw_items()



def main():
    # Create the main window
    root = tk.Tk()
    root.title("Add Resource")
    root.resizable(width=True, height=True)
    root.geometry("600x600")
    scroll_area = elements.scrollframe.ScrollableFrame(root)
    root.bind("<Button-4>", scroll_area._on_mousewheel)
    root.bind("<Button-5>", scroll_area._on_mousewheel)

    Add_Resource_Window(scroll_area.scrollable_frame).pack(side="top", padx=20, fill="x", expand=True, ipadx=20)
    scroll_area.pack(side="top", fill="both", expand=True)
    root.mainloop()
