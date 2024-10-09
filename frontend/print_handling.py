import resourcemanage
from pypdf import PdfMerger
import io
import os
from pathlib import Path

rm = resourcemanage.Resource_Manager()
current_dir = Path(__file__).parent
temp_path = str(current_dir.parent / "tmp" / "printerqueue.pdf")


def add_item(id: int):
    for file in rm.get_uploaded_files(
        id
    ):  # looks at all the files uploaded to the item, but only selects ones named label.pdf
        if file.to_dict()["real_name"] == "label.pdf":
            merger = PdfMerger()
            new_label = io.BytesIO(  # reads the file as binary
                rm.uploadsapi.read_upload(
                    "items", id, file.id, format="binary", _preload_content=False
                ).data
            )
            try:  # if the file exsits, it merges the new label with the existing one
                existing_label = open(temp_path, "rb")
                merger.append(existing_label)
                existing_label.close()
            except (
                FileNotFoundError
            ):  # otherwise, it just doesn't worry about it and starts a new file
                pass
            merger.append(new_label)
            merger.write(open(temp_path, "wb"))
            merger.close()  # closes the merger --- potentially there would be benefit to leaving the merger open until write_labels but then this would have to be another object


def write_labels():
    os.rename(temp_path, rm.printer_path)
