from app.modules.form_j import PowershellSync, CommandSync

# Add:
# Logging
# 

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
        # Return "a"
        help_list = []
        help_list.append("HELP Menu:\n")
        # Assuming self.class_mapping is a dictionary or a method returning a dictionary
        for key, _class in self.class_mapping.items():  # or self.class_mapping().items() if class_mapping is a method
            help_list.append(f"{_class.help()}\n")
        
        help_menu = ''.join(help_list)
        return help_menu  # Return the constructed help menu

# Example usage
parser = CommandParser()
print(parser.parse_command("powershell whoami"))
