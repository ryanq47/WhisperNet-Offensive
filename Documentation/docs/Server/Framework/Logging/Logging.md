# Standard Logging

This logger is meant for logging things 

```
.
├── app
├── audit.log     
├── audit.log.1
├── install.sh
├── prep_for_release.sh
├── README.md
├── requirements.txt
├── run_tests.sh
└── whispernet.log << Here

```

## Usage

```
from app.modules.log import log

# Set up logger
logger = log(__name__)

# Do log things:
logger.debug("debug")
logger.info("Info")
logger.warning("warning")
logger.error("error")
logger.critical("critical")

```