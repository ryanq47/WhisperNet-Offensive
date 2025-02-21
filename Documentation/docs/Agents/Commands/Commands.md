# Commands

## File Commands

### `write_file`

| Description | Writes contents to a file. |
|---|---|
| Arguments | `<str: path> <str: contents>` |
| Example | `write_file my_file.txt "This is the content."` |

---

### `read_file`

| Description | Reads contents of a file. |
|---|---|
| Arguments | `<str: path>` |
| Example | `read_file my_file.txt` |

---

### `delete_file`

| Description | Deletes a file. |
|---|---|
| Arguments | `<str: path>` |
| Example | `delete_file my_file.txt` |

---

### `append_file`

| Description | Appends data to an existing file. |
|---|---|
| Arguments | `<str: path> <str: contents>` |
| Example | `append_file my_file.txt "More content."` |

---

### `rename_file`

| Description | Renames or moves a file. |
|---|---|
| Arguments | `<str: old_path> <str: new_path>` |
| Example | `rename_file my_file.txt new_file.txt` |

---

### `copy_file`

| Description | Copies a file from one location to another. |
|---|---|
| Arguments | `<str: src> <str: dest>` |
| Example | `copy_file my_file.txt copy_of_file.txt` |

---

## Directory Commands

### `mkdir`

| Description | Creates a new directory. |
|---|---|
| Arguments | `<str: directory>` |
| Example | `mkdir mydirectory` |

---

### `rmdir`

| Description | Removes a directory. |
|---|---|
| Arguments | `<str: directory>` |
| Example | `rmdir mydirectory` |

---

### `cd`

| Description | Changes the current directory. |
|---|---|
| Arguments | `<str: directory>` |
| Example | `cd mydirectory` |

---

### `pwd`

| Description | Prints the current working directory. |
|---|---|
| Arguments | None |
| Example | `pwd` |

---

### `ls`

| Description | Lists files and directories in the specified path (or current directory if none provided). |
|---|---|
| Arguments | `<str: path (optional)>` |
| Example | `ls` or `ls mydirectory` |

---

## Transfer Commands

### `http_get`

| Description | Gets an HTTP file and saves it to the specified file path. |
|---|---|
| Arguments | `<str: url> <str: filepath>` |
| Example | `http_get http://someexample.com/file.exe C:\myfile.exe` |
| OPSEC | Will write file to disk |

---

## Process Commands

### `start_process`

| Description | Starts a new process. |
|---|---|
| Arguments | `<str: command>` |
| Example | `start_process notepad.exe` |

---

### `kill_process`

| Description | Kills a process by PID. |
|---|---|
| Arguments | `<int: PID>` |
| Example | `kill_process 1234` |

---

### `suspend_process`

| Description | Suspends a process. |
|---|---|
| Arguments | `<int: PID>` |
| Example | `suspend_process 1234` |

---

### `resume_process`

| Description | Resumes a suspended process. |
|---|---|
| Arguments | `<int: PID>` |
| Example | `resume_process 1234` |

---

### `list_processes`

| Description | Lists all running processes. |
|---|---|
| Arguments | None |
| Example | `list_processes` |

---

## System Commands

### `shell`

| Description | Runs a command via cmd.exe. |
|---|---|
| Arguments | `<str: command>` |
| Example | `shell dir` |
| OPSEC | Runs a new cmd.exe process |

---

## User Interaction Commands

### `messagebox`

| Description | Pops a message box with a message. |
|---|---|
| Arguments | `<str: title> <str: message>` |
| Example | `messagebox "My Title" "Hello, World!"` |
| OPSEC | Shows on the user's screen |

---

## Config Commands

### `sleep`

| Description | Sets how long the agent sleeps for/updates the sleep time. |
|---|---|
| Arguments | `<int: sleeptime (seconds)>` |
| Example | `sleep 60` |
| Note |  Be aware of potential naming conflicts with the Windows `Sleep()` function.  Consider renaming your command (e.g., `set_sleep_time`) to avoid ambiguity. |

---

### `help`

| Description | Prints this help message, displaying all available commands. |
|---|---|
| Arguments | None |
| Example | `help` |

---

### `execution_mode`

| Description | Sets the command execution mode. |
|---|---|
| Arguments | `<str: mode (async or sync)>` |
| Example | `execution_mode async` or `execution_mode sync` |

**Execution Modes:**

| Mode | Description |
|---|---|
| Synchronous (`sync`) | Commands are executed one at a time, in order. Each command must complete before the next command can begin.  This ensures that commands are processed sequentially. |
| Asynchronous (`async`) | Commands can be initiated without waiting for previous commands to finish. Multiple commands may run concurrently. This allows for potentially faster overall execution, but the order of command completion is not guaranteed. |