import cas_grab.resourcemanage
from pypdf import PdfMerger
import io
import os

rm = cas_grab.resourcemanage.Resource_Manager()


def add_item(id: int):
    for file in rm.get_uploaded_files(id):
        if file.to_dict()["real_name"] == "label.pdf":
            merger = PdfMerger()
            new_label = io.BytesIO(
                rm.uploadsapi.read_upload(
                    "items", id, file.id, format="binary", _preload_content=False
                ).data
            )
            try:
                existing_label = open("tmp/printerqueue.pdf", "rb")
                merger.append(existing_label)
                existing_label.close()
            except FileNotFoundError:
                pass
            merger.append(new_label)
            merger.write(open("tmp/printerqueue.pdf", "wb"))
            merger.close()


def write_labels():
    os.rename("tmp/printerqueue.pdf", rm.config.PRINTER_PATH)
