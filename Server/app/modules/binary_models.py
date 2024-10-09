
# Holds class def's for binaries. May need to rename from `binary_models` if that name is no longer appropriate

class Agent():
    def __init__(self, build_target, server_address, server_port, executable_name):
        self.build_target = build_target 
        self.server_address = server_address
        self.server_port = server_port
        self.executable_name = executable_name

        # get values based on config - unsure best way to do this
        #self.build_options = Config().config.server.binaries.agents.x86_windows_agent

    def build(self):
        ...

        # build the binary

    


class Dropper():
    def __init__(self, server_address, server_port, executable_name, server_payload_enpoint):
        self.server_address = server_address
        self.server_port = server_port
        self.executable_name = executable_name
        self.server_payload_enpoint = server_payload_enpoint

class Custom():
    def __init__(self, server_address, server_port, executable_name, payload):
        self.server_address = server_address
        self.server_port = server_port
        self.executable_name = executable_name
        self.payload = payload