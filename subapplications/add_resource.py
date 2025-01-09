import tkinter as tk
import tkinter.messagebox as messagebox

import elements.images
import elements.scrollframe
import eln_packages_common.fill_info as filler
import json

class Add_Resource_Window(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.title("Add Resource")
        self.resizable(width=False, height=True)
        self.geometry("600x600")
        
        self.scroll_area = elements.scrollframe.ScrollableFrame(self)
        self.scroll_area.scrollable_frame.bind_all("<Button-4>", self.scroll_area._on_mousewheel)
        self.scroll_area.scrollable_frame.bind_all("<Button-5>", self.scroll_area._on_mousewheel)
        self.scroll_area.scrollable_frame.bind_all("<MouseWheel>", self.scroll_area._on_mousewheel)
        
        Add_Resource_Content(self.scroll_area.scrollable_frame, self).pack(
            side="top", padx=20, fill="x", expand=True, ipadx=20
        )
        self.scroll_area.pack(side="top", fill="both", expand=True)

class Add_Resource_Content(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(parent)
        self.parent = parent
        self.container = container # the Add_Resource_Window instance
        self.dropdown = Category_Dropdown(self)
        self.dropdown.pack()
        self.dictionary: dict = self.create_dictionary(self.dropdown.clicked_dict)
        self.draw_items()

    def create_dictionary(self, template: dict) -> dict:
        dictionary = {}
        # add title, metadata, body, and status fields to dictionary
        for key in template:
            if key in ["title", "body", "metadata", "status"]:
                dictionary.update({key: template[key]})
        category: int = self.dropdown.clicked_index
        # add category field to dictionary
        dictionary.update({"category": category})
        return dictionary

    def draw_items(self):
        # clear all widgets in the frame
        for widget in self.winfo_children():
            # exclude self.dropdown
            if widget != self.dropdown:
                widget.destroy()

        # add search by CAS entrybox if the category is not "Instrument"
        if self.dropdown.clicked.get() != "Instrument":
            self.cas_label = tk.Label(
                self, text="Search by CAS (or name if CAS unavailable):"
            )
            self.cas_label.pack(pady=10)
            self.cas_entry = tk.Entry(self)
            self.cas_entry.bind("<Return>", self.fill_info)
            self.search_button = tk.Button(self, text="Search", command=self.fill_info)
            self.cas_entry.pack(pady=5)
            self.search_button.pack(pady=0)
            self.pack(side="left")

        # add title and body fields
        self.title_entrybox = Labeled_Entrybox(self, category="title")
        self.title_entrybox.entry.insert(0, self.dictionary["title"])
        self.title_entrybox.pack(pady=10)
        self.body_box = Labeled_Textbox(self, text="body")
        self.body_box.textbox.insert(tk.END, self.dropdown.clicked_dict["body"])
        self.body_box.pack(pady=10)

        self.add_metadata_fields()

        # add the rest of the metadata fields
        for entrybox in self.metadata_entryboxes:
            entrybox.pack(pady=10)

        self.submit_button = tk.Button(self, text="Submit", command=self.submit)
        self.submit_button.pack(pady=10)

    def add_metadata_fields(self):
        # get all metadata fields from the resource template, and have a list with an Entrybox for each
        metadata_dict: dict = json.loads(self.dictionary["metadata"])["extra_fields"]
        self.metadata_entryboxes: list[Labeled_Entrybox] = [Labeled_Entrybox(self)] * len(metadata_dict)
        # for each metadata field, add an Entrybox to the list
        for field in metadata_dict:
            entrybox: Labeled_Entrybox = Labeled_Entrybox(
                self, category=field, value_info=metadata_dict[field]
            )
            if metadata_dict[field]["type"] not in ["select", "radio"]:
                value = metadata_dict[field]["value"]
                if value is not None:
                    entrybox.entry.insert(0, metadata_dict[field]["value"])
                else:
                    entrybox.entry.insert(0, "")
                    messagebox.showerror("Warning", f"Field \"{field}\" not found in search results, please fill in manually", parent=self)

            try:
                position: int = metadata_dict[field]["position"]
                self.metadata_entryboxes[position] = entrybox
            except KeyError:
                print(f"Field {field} has no position, make sure to specify the order of entries in the template in the admin panel")


    def fill_info(self, event=None):
        cas_entry: str = self.cas_entry.get()
        try:
            results: dict = filler.pull_values(cas_entry)
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)
            self.draw_items()
            return    
        metadata: dict = json.loads(self.dropdown.clicked_dict["metadata"])[
            "extra_fields"
        ]
        if filler.check_if_cas(cas_entry):
            metadata["CAS"]["value"] = cas_entry
        elif "CAS" in results.keys():
            metadata["CAS"]["value"] = results["CAS"]
        
        for result_field in results:
            if result_field in metadata:
                metadata[result_field]["value"] = results[result_field]
        metadata_str: str = json.dumps({"extra_fields": metadata})
        self.dictionary["metadata"] = metadata_str
        self.dictionary["title"] = results["Title_0"]
        self.draw_items()

    def submit(self):
        has_Mn = False
        has_Mw = False
        # check that all required fields are filled
        for entrybox in self.metadata_entryboxes:
            # check that Mn or Mw is filled
            if entrybox.get()[0] == "Mn" and entrybox.get()[1]["value"] !="": 
                has_Mn = True
            if entrybox.get()[0] == "Mw" and entrybox.get()[1]["value"] !="": 
                has_Mw = True
            if "required" in entrybox.get()[1] and entrybox.get()[0] not in ["Mn", "Mw"]:
                if entrybox.get()[1]["required"] and entrybox.get()[1]["value"] == "":
                    messagebox.showerror(
                        "Error",
                        f"Field {entrybox.get()[0]} is required",
                        parent=self,
                    )
                    return
            if entrybox.get()[0] == "Opened" and entrybox.get()[1]["value"] != "":
                # mark the item status as opened if the Opened field is filled
                self.dictionary["status"] = 4
            else: 
                print(entrybox.get()[0])
        # throw error if neither Mn nor Mw is filled
        if not (has_Mn or has_Mw):
            messagebox.showerror(
                "Error",
                "Please fill in either Mn or Mw",
                parent=self,
            )
            return
        # get all the metadata values from the entryboxes, update the metadata dictionary, and put that in the main dictionary
        new_metadata: dict = json.loads(self.dictionary["metadata"])
        for entrybox in self.metadata_entryboxes:
            entry_dict: dict = entrybox.get()[1]
            entry_name: str = entrybox.get()[0]
            new_metadata["extra_fields"][entry_name] = entry_dict
        self.dictionary["metadata"] = json.dumps(new_metadata)

        # get all non-metadata values from the entryboxes and update the main dictionary
        self.dictionary["title"] = self.title_entrybox.entry.get()
        self.dictionary["body"] = self.body_box.textbox.get("1.0", tk.END)

        # create the new item in the ELN
        filler.rm.create_item(self.dropdown.clicked_index, self.dictionary)

        # close the window
        self.container.destroy()

class Labeled_Textbox(tk.Frame):
    def __init__(self, parent, text=""):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.label = tk.Label(self, text=text + ":")
        self.label.pack(pady=10)
        self.textbox = tk.Text(self, height=10, width=30)
        self.textbox.pack(pady=10)

class Labeled_Entrybox(tk.Frame):
    def __init__(
        self,
        parent,
        category: str = "",
        value_info: dict = {"type": "text", "value": ""},
    ):
        tk.Frame.__init__(self, parent)
        self.category = category
        self.discrete_types: list[str] = ["select", "radio"]
        self.string_types: list[str] = ["text", "date"]
        self.parent = parent
        self.return_dict: dict = value_info
        self.label = tk.Label(self, text=category + ":")
        self.label.pack(pady=10)

        self.textbox_frame = tk.Frame(self)

        if value_info["type"] == "number":
            self.entry = tk.Entry(self.textbox_frame)
            self.entry.pack(side="left")
            self.unit: tk.StringVar = tk.StringVar()
            self.unit.set(value_info["units"][0])
            self.unit_chooser: tk.OptionMenu = tk.OptionMenu(
                self.textbox_frame, self.unit, *value_info["units"]
            )
            self.unit_chooser.pack(side="right", expand=True)
        elif value_info["type"] in self.string_types:
            self.entry = tk.Entry(self.textbox_frame)
            self.entry.pack()
        elif value_info["type"] in self.discrete_types:
            options = [""] + value_info["options"]
            self.choice = tk.StringVar()
            self.choice.set(options[0])
            self.chooser = tk.OptionMenu(
                self.textbox_frame, self.choice, *options
            )
            self.chooser.pack()

        if value_info["type"] == "date":
            self.label.config(text=category + " (YYYY-MM-DD):")
        self.textbox_frame.pack(pady=10)

    def get(self) -> tuple[str, dict]:
        if self.return_dict["type"] == "number":
            self.return_dict["value"] = self.entry.get()
            self.return_dict["unit"] = self.unit.get()
        elif self.return_dict["type"] in self.string_types:
            self.return_dict["value"] = self.entry.get()
        elif self.return_dict["type"] in self.discrete_types:
            self.return_dict["value"] = self.choice.get()
        return (self.category, self.return_dict)

class Category_Dropdown(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        # add label
        self.type_label: tk.Label = tk.Label(self, text="Select type of resource:")
        self.type_label.pack(pady=10)

        # get category names and template dictionaries
        self.category_names: list[str] = []
        self.category_dicts: list[dict] = (
            [{"title": ""}] + filler.rm.get_items_types()
        )  # pull dicts from eln, with an empty dictionary at the beginning
        for cat in self.category_dicts:
            # for each category dictionary, add the title to the category_names list
            self.category_names.append(cat["title"])
        self.clicked_index: int = 2  # default to Chemical Compound 
        self.clicked: tk.StringVar = tk.StringVar()
        self.clicked.set(self.category_names[self.clicked_index])
        self.clicked_dict: dict = self.category_dicts[self.clicked_index]

        self.drop = tk.OptionMenu(self, self.clicked, *self.category_names)
        self.drop.pack()

        # run on_category_change method when StringVar clicked is written
        self.clicked.trace_add("write", self.on_category_change)

    def on_category_change(self, *args):
        self.clicked_index: int = self.category_names.index(self.clicked.get())
        self.clicked_dict: dict = self.category_dicts[self.clicked_index]
        # update the main dictionary to the trimmed down version of the clicked template dictionary
        self.parent.dictionary = self.parent.create_dictionary(self.clicked_dict)
        # refresh the screen to reflect the values in the new template
        self.parent.draw_items()