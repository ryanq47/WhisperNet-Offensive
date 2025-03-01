from modules.agent_script_interpreter import BaseCommand
from modules.agent import BaseAgent


class PingHost(BaseCommand):
    command_name = "ping_host"

    def __init__(self, command, args_list, agent_id):
        """
        command:command, ex ping 127.0.0.1

        agent_id: The agent ID which gets passed in to
            operate on the agent

        """
        # You could also parse and validate args here
        super().__init__(command, args_list, agent_id)
        self.command_name = "ping_host"
        self.command_help = "Pings a host. Usage: `ping_host <host ip/hostname>`"
        self.command = command
        if not command:
            raise ValueError("Missing command")

        print(command)

        parts = command.split()
        # get args - have to be positional with this setup
        # command = parts[0]  # get command iteslf
        # args = parts[1:]  # args, ex ["127.0.0.1"]

        self.host = args_list[0]
        # self.arg_2 = args[1]

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
