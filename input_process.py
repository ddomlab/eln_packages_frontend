import json
from eln_packages_common.resourcemanage import Resource_Manager
from datetime import datetime
import webbrowser
from typing import Any
import print_handling


class Processor:
    def __init__(self, gui):
        self.registry: Registry = Registry()
        self.rm = Resource_Manager()
        self.output: str = ""  # use like print() but for the GUI
        self.gui = gui
        self.print_handling = print_handling
        self.experiment_id: str | None = None  # for associating items with experiments, needs to be stored outside method for batch operations
        self.new_status = None # for changing status, needs to be stored outside method for batch operations

    ### Actions ###
    def open_page(self, id: int):
        webbrowser.open(f"https://eln.ddomlab.org/database.php?mode=view&id={id}")

    def archive_item(self, id: int):
        self.rm.change_item(id, {"action": "archive"})
        self.gui.input_prompt((f"Item {id} archived"))
        

    def mark_open(self, id: int):
        body:dict[str,Any] = self.rm.get_item(id)
        metadata = json.loads(body["metadata"])
        if metadata["extra_fields"]["Opened"]["value"] != "":
            self.gui_print(f"Item {id} already marked as opened on {metadata['extra_fields']['Opened']['value']}")
            return
        metadata["extra_fields"]["Opened"]["value"] = datetime.now().isoformat()[:10]
        self.rm.change_item(id, {"metadata": json.dumps(metadata)})
        
    def edit_status(self, id: int):
        # because this task can be run in batch, it has to check if new_status has already been set, and if not, it willask
        if self.new_status is None:
            self.new_status = int(self.gui.status_prompt("Enter new status"))
            if self.new_status is None or self.new_status == "":
                self.gui_print("No experiment ID entered, status edit cancelled")
                return
        if int(self.new_status) == 4:
            # if it is marked as open
            self.mark_open(id)
        if type(self.new_status) is int and self.new_status in range(1, 5):
            self.rm.change_item(id, {"status": self.new_status})
            self.gui_print(f"Item {id} status changed to {self.new_status}")
        # when the last item is processed, reset the new_status
        if id == self.registry.id_registry[-1]:
            self.new_status = None

    def batch_action(self):
        self.registry.toggle_batch()

    def clear(self):
        self.registry = Registry()
        #self.gui_print("registry cleared")

    def associate(self, item_id: int):
        # because this task can be run in batch, it has to check if experiment_id has already been set, and if not, it willask
        if self.experiment_id is None:
            self.experiment_id = self.gui.input_prompt("Enter Experiment ID")
            if self.experiment_id is None or self.experiment_id == "":
                self.gui_print("No experiment ID entered, association cancelled")
                return
        try:
            self.rm.experiment_item_link(int(self.experiment_id), item_id)
        except ValueError:
            self.gui.show_error(f"Failed to associate item {item_id} with experiment {self.experiment_id}")
        # when the last item is processed, reset the experiment_id
        if item_id == self.registry.id_registry[-1]:
            self.experiment_id = None

    def add_and_print_registry(self, id: int):
        self.print_handling.add_item(id)
        if id == self.registry.id_registry[-1]:
            self.print_handling.write_labels()
    def add_resource(self):
        self.gui.add_resource_prompt()

    ###   ###
    commands: dict = {
        "open_page": open_page,
        "edit_status": edit_status,
        # "archive": archive_item,
        "batch": batch_action,
        "clear": clear,
        "associate": associate,
        "print": add_and_print_registry,
        "add_resource": add_resource
    }
    override_commands: list[str] = ["clear", "batch", "add_resource"]

    # I made the interesting decision to store the data on the QR codes as json strings, rather than as plain text commands.
    # On the one hand, this requires some more processing, I suppose I could have just had the QR codes store the commands directly,
    # but I worry that there would become a need for more complex qr codes and more complex commands in the future, so I decided to store
    # each command or id in a json string.
    def register(self, input: str):  
        # expect a string, but NOT json/dict-- from_data() pre-processes that
        self.registry.action = input
        # if the action is in the override_commands list, execute it immediately
        # if there is an action and at least one id in the registry, execute the command
        if self.registry.action in self.override_commands:
            self.commands[self.registry.action](self)
        elif self.registry.action != "" and len(self.registry.id_registry) > 0:
            for id in (
                self.registry.id_registry
            ):  # for each id in the id_registry, run the command on it
                self.commands[self.registry.action](self, id)
            self.clear()  # clear the registry after the commands are run
        elif len(self.registry.id_registry) == 0:
            self.gui_print("No ID in registry, please enter an ID first")

    def from_data(self, input: str | dict):  
    # register items from a python dictionary or json file
        if type(input) is str:
            data = json.loads(input)  # if it's json, turn it into a dict
        elif type(input) is dict:
            data = input  # if it's already a python dict, use that
        else:
            raise ValueError("Invalid input type")
        for key in data.keys():
            if (
                key == "id"
            ):  ## if the key is id, add it to the registry, unless it's already there, in which case remove it
                if int(data[key] in self.registry.id_registry):
                    self.registry.id_registry.remove(int(data[key]))
                else:
                    self.registry.add_id(int(data[key]))
            elif key == "action" and data[key] in self.commands:
                self.register(data[key])
            else:
                raise ValueError("Invalid key")

    def from_human(self, input: str):
        if input.isdigit():
            self.from_data({"id": int(input)})
        elif input in self.commands:
            self.from_data({"action": input})
        else:
            self.gui_print("Not understood, try again")

    def from_terminal(self, input: str):
        # decides if it's from human input in the terminal, or from qr code scanning
        self.gui_print("")  # clear output on gui
        if input == "":
            return
        if input[0] == "{":
            self.from_data(input)
        elif input[:4] == "http":
            self.from_data({"id": int(input.split("=")[-1])})
        else:
            self.from_human(input)

    def gui_print(self, output: str):
    # prints to a textbox in the gui, as well as stdout
        print(output)
        self.output = output


class Registry:
    def __init__(self):
        self.id_registry: list[int] = []
        self.action: str = ""
        self.is_batch: bool = False

    def toggle_batch(self):
        self.is_batch = not self.is_batch  # toggle batch mode
        if (
            not self.is_batch and len(self.id_registry) != 0
        ):  # if you just turned off batch mode and there are numbers in the list
            self.id_registry = [
                self.id_registry[-1]
            ]  # make the list have one element, the most recently added

    def add_id(self, id: int):
        self.id_registry.append(id)
        if not self.is_batch:
            self.id_registry = [
                self.id_registry[-1]
            ]  # if batch mode is not on, make sure the list is one long
