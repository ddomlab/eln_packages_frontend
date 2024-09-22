import json
from printer.generate_label import LabelGenerator


class Processor:
    def __init__(self):
        self.registry: Registry = Registry()
        self.labelgen: LabelGenerator = LabelGenerator()

    ### Actions ###
    def open_page(id: int):
        raise NotImplementedError("Tried to open {id}")

    def archive_item(id: int):
        raise NotImplementedError

    def mark_open(id: int):
        raise NotImplementedError

    def batch_action():
        pass

    def clear():
        pass

    def assosciate(resource_id: int):
        raise NotImplementedError

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

    def register(self, input: str | int):
        if input == "clear":
            self.registry = Registry()
        elif input == "batch":
            self.registry.toggle_batch()

        elif type(input) is int or input.isdigit():  # if it's an id number
            self.registry.add_id(
                int(input)
            )  # add the integer id to the registry, if it isn't in batch mode, it will simply replace the old id in the reigstry with the new one
        elif input in self.commands:
            self.registry.action = input
        else:
            raise ValueError(
                "Input not processed, please check spelling/formatting and try again, or use a QR Code"
            )

        if (
            self.registry.action != "" and len(self.registry.id_registry) > 0
        ):  # execute the action
            for id in (
                self.registry.id_registry
            ):  # for each id in the id_registry, run the command on it
                self.commands[self.registry.action](self, id)
            self.registry = Registry()  # reset
            print("regisrest")

    def from_data(
        self, input: str | dict
    ):  # register items from a python dictionary or json file
        if type(input) is str:
            data = json.loads(input)  # if it's json, turn it into a dict
        else:
            data = input  # if it's already a python dict, use that

        for key in data.keys():
            if key == "id":
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
