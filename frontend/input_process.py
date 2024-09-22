import json
from printer.generate_label import LabelGenerator
import cas_grab.resourcemanage


class Processor:
    def __init__(self):
        self.registry: Registry = Registry()
        self.labelgen: LabelGenerator = LabelGenerator()
        self.rm = cas_grab.resourcemanage.Resource_Manager()

    ### Actions ###
    def open_page(self, id: int):
        raise NotImplementedError("Tried to open {id}")

    def archive_item(self, id: int):
        raise NotImplementedError

    def mark_open(self, id: int):
        raise NotImplementedError

    def batch_action(self, *args):
        self.registry.toggle_batch()

    def clear(self, *args):
        self.registry = Registry()
        print("registry cleared")

    def assosciate(self, item_id: int):
        experiment_id = input("enter experiment id:\n")
        self.rm.experiment_item_link(experiment_id, item_id)  # TODO fix this

    def add_and_print_registry(self, id: int):
        self.labelgen.add_item(id)
        if id == self.registry.id_registry[-1]:
            self.labelgen.write_labels()

    ###   ###
    commands: dict = {
        "open_page": open_page,
        "mark_opened": mark_open,
        "archive": archive_item,
        "batch": batch_action,
        "clear": clear,
        "assosciate": assosciate,
        "print": add_and_print_registry,
    }
    override_commands: list[str] = ["clear", "batch"]

    # I made the interesting decision to store the data on the QR codes as json strings, rather than as plain text commands.
    # On the one hand, this requires some more processing, I suppose I could have just had the QR codes store the commands directly,
    # but I worry that there would become a need for more complex qr codes and more complex commands in the future, so I decided to store
    # each command or id in a json string.
    def register(
        self, input: str
    ):  # expect a string, but NOT json/dict-- from_data() pre-processes that
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

    def from_data(
        self, input: str | dict
    ):  # register items from a python dictionary or json file
        if type(input) is str:
            data = json.loads(input)  # if it's json, turn it into a dict
        else:
            data = input  # if it's already a python dict, use that

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
            print("Not understood, try again")


class Registry:
    def __init__(self):
        self.id_registry: list[int] = []
        self.action: str = ""
        self.is_batch: bool = False

    def toggle_batch(self):
        self.is_batch = not self.is_batch  # toggle batch mode
        if not self.is_batch:  # if you just turned off batch mode
            self.id_registry = [
                self.id_registry[-1]
            ]  # make the list have one element, the most recently added

    def add_id(self, id: int):
        self.id_registry.append(id)
        if not self.is_batch:
            self.id_registry = [
                self.id_registry[-1]
            ]  # if batch mode is not on, make sure the list is one long
