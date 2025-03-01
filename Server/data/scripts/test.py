from modules.agent_script_interpreter import BaseCommand
from modules.agent import BaseAgent


class PingHost(BaseCommand):
    command_name = "ping_host"
    command_help = "Pings a host. Usage: `ping_host <host ip/hostname>`"

    def __init__(self, command, args_list, agent_id):
        """
        command:command, ex ping_host

        args_list: The list of arguments which the user puts in when typing a command
            ex: command = `ping_host 127.0.0.1`, the args would be ["127.0.0.1]

        agent_id: The agent ID which gets passed in to
            operate on the agent

        """
        super().__init__(command, args_list, agent_id)
        if not command:
            raise ValueError("Missing command")
        if not args_list:
            raise ValueError("Missing args_list")
        if not agent_id:
            raise ValueError("Missing agent_id")

        # Get the args from the args list
        self.host = args_list[0]
        # self.arg_2 = args[1]

        # Spin up a BaseAgent instance with the agent_id
        self.agent_class = BaseAgent(agent_id)

    def run(self):
        # Calls base class method to enqueue sleep arg
        # self.set_sleep(2)

        # Build the ping command with the data we have
        cmd = f"shell ping {self.host}"

        ## enqueue now formatted command to be run
        shell_cmd_id = self.agent_class.enqueue_command(cmd)  # Returns command ID.

        shell_cmd_response = (self.agent_class.get_one_command_and_response(id)).get(
            "response", None
        )
        ## may need to wait on response actually being something?
        ## ex:
        # wait sleep time until checking response

        ## based on response, do something
        ## if regex ping successful, i dunno
        if "Reply from 127.0.0.1" in shell_cmd_response:
            # do whatever
            print("Successful Execution")

            # append to response: SomethignSomething host alive, performing next steps
            shell_cmd_response += "\n\nTesting Adding onto command, etc"
            self.agent_class.store_response(shell_cmd_id, shell_cmd_response)


class Populate(BaseCommand):
    command_name = "populate"
    command_help = "Populates common data fields. Usage: `populate`"

    def __init__(self, command, args_list, agent_id):
        """
        command: The command string, e.g. "populate"
        args_list: List of arguments provided by the user (not used here)
        agent_id: The agent identifier to operate on.
        """
        super().__init__(command, args_list, agent_id)
        if not agent_id:
            raise ValueError("Missing agent_id")
        # Instantiate a BaseAgent to handle command execution.
        self.agent_class = BaseAgent(agent_id)

    def run(self):
        # Enqueue a sleep command (10 seconds) before execution.
        self.agent_class.enqueue_command("sleep 10")

        # Execute shell command "ver"
        self.agent_class.enqueue_command("shell ver")

        # Execute shell command "whoami"
        self.agent_class.enqueue_command("shell whoami")

        # Execute shell command "hostname"
        self.agent_class.enqueue_command("shell hostname")

        # Enqueue a sleep command (10 seconds) after execution.
        self.agent_class.enqueue_command("sleep 10")
