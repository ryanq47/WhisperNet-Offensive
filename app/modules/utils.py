from modules.config import Config
from modules.log import log
import importlib
import sys
import flask

logger = log(__name__)


# Add warnings N stuff to this
def plugin_loader():
    logger.info("Loading plugins")
    # Plugin Root Dir
    plugin_dir = Config().launch_path / "plugins"

    for plugin_path in plugin_dir.iterdir():
        if plugin_path.is_file() and plugin_path.suffix == ".py":
            plugin_name = plugin_path.stem
            logger.info(f"{plugin_name} discovered")

            try:
                # Load the module from the file path - better than the importlib.import_module
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[plugin_name] = module
                spec.loader.exec_module(module)

                # Get class name from Info class and execute
                if hasattr(module, "Info"):
                    Info = getattr(module, "Info")
                    class_name = getattr(Info, "classname", None)

                    if class_name and hasattr(module, class_name):
                        PluginClass = getattr(module, class_name)

                        # Instantiate the class, with flask app instance
                        # Currently, we don't need to keep access to these classes.
                        PluginClass()
                    else:
                        logger.warning(
                            f"Plugin '{plugin_name}' skipped: 'classname' not found in Info or class '{class_name}' does not exist in module."
                        )
                else:
                    logger.warning(
                        f"Plugin '{plugin_name}' skipped: 'Info' class not found."
                    )

            except Exception as e:
                logger.warning(f"Plugin '{plugin_name}' failed to load: {e}")
