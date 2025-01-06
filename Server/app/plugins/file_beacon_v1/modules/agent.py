from modules.agent import BaseAgent
from modules.log import log

logger = log(__name__)

# This example assumes that on checkin, a class will be created to handle the Agent checking in.

# Commands would be enqueued to the redis DB from an endpoint, such as /myc2/uuid/enqueue, then popped here when the Agent checks in
# Note, you can also use BaseAgent to do that enqueuing, here's example Pseudocode:

# @flask.app("/somedest")
# def enqueue_from_user():
# command = response.json()["command"]
# agent_id = response.json()["agent_id"]
# ba = BaseAgent(agent_id)
# ba.enqueue("somecommand")


# Inherit BaseAgent into your class
class Agent(BaseAgent):
    def __init__(self, agent_id, config_file_path, client_socket):
        super().__init__(
            agent_id=agent_id, config_file_path=config_file_path
        )  # Ensure BaseAgent is properly initialized
        # Note, load_config will auto be called in BaseAgent

        self.client_socket = client_socket
        # Register the client
        self.register()

    def checkin(self):
        """
        A checkin function/what to do on checkin.
        """
        self.enqueue_command("exec:powershell whoami test")
        logger.debug(f"Agent '{self.data.agent.id}' has checked in")
        next_command = self.dequeue_command()
        self.send(next_command)

    def send(self, command):
        # The syntax for this may change as well
        # example command: exec:powershell whoami
        command_header = command.split()[
            0
        ]  # get command (in this case, exec:powershell)
        # Split on whitespace -> ["exec:powershell", "whoami", "/all??"]
        # Take everything after index 0, then rejoin
        command_arg = " ".join(command.split()[1:])

        # Then format the command according to the config file
        formatted_command = self.format_command(
            command=command_header, arguments=command_arg
        )
        # finally send the command off
        self.client_socket.sendall(formatted_command.encode("utf-8"))

    def receive(self): ...  # some receive logic
