from app.modules.form_j import PowershellSync, CommandSync
from app.modules.log import log

logger = log(__name__)

# specifically for automatically constructing FormJ messages with SyncKeys
# not in form_j, as this has things specifically for the GUI, such as the help method
# if that ever gets moved, this may get moved as well

class CommandParser:
    def __init__(self):
        self.class_mapping = {
            "powershell": PowershellSync,
            "command": CommandSync
            #"net": NetCommandSync,
            #"bash": BashSync,
            # Add more mappings as needed
        }

    def parse_command(self, command_str):
        parts = command_str.split(maxsplit=1)
        if len(parts) < 2:
            logger.warning(f"Command submitted with seemingly only one part: {command_str}")
            raise ValueError("Command must have at least a head and an argument.")

        head = parts[0].lower()
        tail = parts[1]

        # Create the key based on the head and initialize the appropriate class
        key = self.create_key_from_head(head)
        if key is None:
            raise ValueError("Unknown command type.")

        # Instantiate the class and create the command structure
        command_class = self.class_mapping[head]
        command_instance = command_class(tail)
        command_structure = command_instance.create()

        return command_structure

    def create_key_from_head(self, head):
        """
        Returns the key based on the head value.
        """
        return head.capitalize() if head in self.class_mapping else None

    def help(self):
        """Construct a help menu"""

        help_list = []
        help_list.append("HELP Menu:\n")
        for key, _class in self.class_mapping.items():  
            help_list.append(f"{_class.help()}\n")
        
        help_menu = ''.join(help_list)
        return help_menu 
