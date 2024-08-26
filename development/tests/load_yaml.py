## NOT A TEST, addon for tests


import os
import yaml
import munch


def load_yaml(filename="config.yaml") -> munch:
    # Get the absolute path of the current Python file
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the full path to the YAML file
    file_path = os.path.join(base_dir, filename)

    # Open and load the YAML file
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)

    return munch.munchify(data)


load_yaml("config.yaml")
