import yaml
import munch
import pathlib


# import log
# logger = log.log(__name__,color=True)


def load_config(config_file: str | pathlib.Path):
    if type(config_file) == pathlib.Path:
        # if a pathlib is passed in, convert path to str
        config_file = str(config_file)

    # logger.info(f"Loading config '{config_file}'")
    # yaml loader
    with open(config_file, "r") as f:
        config = munch.munchify(yaml.safe_load(f))

    # non-config file values (env vars, etc)
    config.example = "somevalue"

    # return munch object
    return config


if __name__ == "__main__":
    # ONLY works from in here, as root path in not in app dir
    c = load_config(config_file=pathlib.Path.cwd() / "app" / "config" / "config.yaml")

    print(c.example)
    # yaml key
    print(c.server.name)
