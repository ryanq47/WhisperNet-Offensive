# Commands

## File System Commands

### **`mkdir`**
| **Description** | Creates a new directory. |
|----------------|--------------------------|
| **Arguments**  | `<str: directory>`       |
| **Example**    | `mkdir mydirectory`      |
| **Screenshot** | ![mkdir Command](path/to/mkdir_screenshot.png) |

---

### **`rmdir`**
| **Description** | Removes a directory. |
|----------------|----------------------|
| **Arguments**  | `<str: directory>`   |
| **Example**    | `rmdir mydirectory`  |
| **Screenshot** | ![rmdir Command](path/to/rmdir_screenshot.png) |

---

### **`cd`**
| **Description** | Changes the current directory. |
|----------------|-------------------------------|
| **Arguments**  | `<str: directory>`            |
| **Example**    | `cd mydirectory`              |
| **Screenshot** | ![cd Command](path/to/cd_screenshot.png) |

---

### **`pwd`**
| **Description** | Prints the current working directory. |
|----------------|------------------------------------|
| **Arguments**  | None                                |
| **Example**    | `pwd`                               |
| **Screenshot** | ![pwd Command](path/to/pwd_screenshot.png) |

---

## Loud Commands

### **`http_get`**
| **Description** | Gets an HTTP file and saves it to the specified file path. |
|----------------|---------------------------------------------------------|
| **Arguments**  | `<str: url> <str: filepath>`                             |
| **Example**    | `http_get http://someexample.com/file.exe C:\myfile.exe`    |
| **Screenshot** | ![http_get Command](path/to/http_get_screenshot.png) |
| **OPSEC**      | Will write file to disk                                  |

---

### **`shell`**
| **Description** | Runs a command via cmd.exe. |
|----------------|--------------------------|
| **Arguments**  | `<str: command>`           |
| **Example**    | `shell dir`               |
| **Screenshot** | ![shell Command](path/to/shell_screenshot.png) |
| **OPSEC**      | Runs a new cmd.exe process   |

---

### **`messagebox`**
| **Description** | Pops a message box with a message. |
|----------------|-----------------------------------|
| **Arguments**  | `<str: title> <str: message>`      |
| **Example**    | `messagebox "My Title" "Hello, World!"` |
| **Screenshot** | ![messagebox Command](path/to/messagebox_screenshot.png) |
| **OPSEC**      | Shows on the user's screen           |

---

## Config Commands

### **`sleep`**
| **Description** | Sets how long the agent sleeps for/updates the sleep time. |
|----------------|------------------------------------------------------|
| **Arguments**  | `<int: sleeptime (seconds)>`                           |
| **Example**    | `sleep 60`                                          |
| **Screenshot** | ![sleep Command](path/to/sleep_screenshot.png) |

---

### **`help`**
| **Description** | Prints this help message, displaying all available commands. |
|----------------|-----------------------------------------------------------|
| **Arguments**  | None                                                       |
| **Example**    | `help`                                                    |
| **Screenshot** | ![help Command](path/to/help_screenshot.png) |