import base64
import os


def get_image_data(filename):
    with open(filename, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")
    return image_data


def get_topology_data(topology_file):
    if not topology_file:
        raise ValueError("Topology data not provided")

    image_extensions = [".png", ".jpg", ".jpeg"]
    if [i for i in image_extensions if topology_file.endswith(i)]:
        topology_data = get_image_data(topology_file)
        topology_type = "image"

    elif topology_file.endswith(".txt"):
        with open(topology_file, "r") as file:
            topology_data = file.read()
        topology_type = "text"

    elif os.path.isfile(topology_file):
        raise ValueError(
            f"Topology file must be a text file (.txt) or an image file {image_extensions}"
        )

    else:
        topology_data = topology_file
        topology_type = "text"

    return topology_type, topology_data
