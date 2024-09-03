## Todo:

- [X] Config values in file rollover,e tc
- [X] rename log_action to audit
- [X] Build out these docs

# Audit

Whispernet offers robust(ish) audit logging for all the actions happening on clients. This is seperate from the main log, which contains application based logs. 

The audit log is meant to leave an audit trail for if/when you need to check back on what you've been running on hosts. 

## Usage

Usage is fairly simple

Minimum Example:
```
from modules.audit import Audit

a = Audit()
a.audit(whatever_data_you_want)

```

The `whatever_data_you_want`, can be either a dict, or a string. Dictionaries automatically have an `audit` key added to them, with a timestamp in it. Additional fields can be added if needed.

For example, the `simple_http` plugin adds in the user ID for the `/command/client_id` endpoint, to track what user is queuing commands:

```
user_identity = get_jwt_identity()
dict_data.setdefault('audit', {})  # Ensure 'audit' key exists in dict_data
dict_data['audit']['user_identity'] = user_identity  # Add user identity to the log

a = Audit()
a.audit(dict_data)
```

## Config Values
There's a few config values that go with the audit log as well.

`max_file_size`: The max file size for each log, in bytes
`max_file_backups`: The amount of log files that can exist. This is handled via the `RotatingFileHandler` class of the `logging` module.
`file_name`: Name of the audit log file.

```
server:
  ...

  audit: # audit settings
    log:
      max_file_size: !!int 1000000 # in Bytes
      max_file_backups: !!int 10   # how many files to keep after rollover
      file_name: !!str "audit.log"
```