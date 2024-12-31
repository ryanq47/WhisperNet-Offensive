# Utils Documentation

A set of random functions/utility functions.

## Usage:

```python
from modules.utils import *  # Or the name of the function you want

from modules.utils import generate_mashed_name
```

## Functions:

### `generate_unique_id() -> str`

**Description:**

Generates a unique message ID using UUID version 4.

**Returns:**

- `str`: A unique UUIDv4 string.

**Example:**

```python
unique_id = generate_unique_id()
print(unique_id)  # Output: '3f50b9d2-7e1a-4b0d-a9f0-8bdf6e7e5b3c'
```

---

### `generate_timestamp() -> int`

**Description:**

Generates the current timestamp.

**Returns:**

- `int`: The current timestamp in seconds since the epoch.

**Example:**

```python
timestamp = generate_timestamp()
print(timestamp)  # Output: 1701305600
```

---

### `generate_mashed_name() -> str`

**Description:**

Generates a mashed name by randomly selecting one adjective and one noun, then concatenating them with an underscore.

**Returns:**

- `str`: The mashed name in uppercase, e.g., `"MIGHTY_LION"`

**Example:**

```python
mashed_name = generate_mashed_name()
print(mashed_name)  # Output: "SWIFT_EAGLE"
```

---

## Function Details:

### `generate_unique_id()`

- **Purpose:**  
  Creates a unique identifier that can be used for message tracking, ensuring that each ID is distinct.

- **Implementation Details:**  
  Utilizes Python's `uuid` library to generate a UUID version 4, which is based on random numbers.

- **Dependencies:**  
  - `import uuid`

### `generate_timestamp()`

- **Purpose:**  
  Provides the current time as a Unix timestamp, which is the number of seconds that have elapsed since January 1, 1970 (the Unix epoch).

- **Implementation Details:**  
  Uses Python's `time` module to fetch the current time and convert it to an integer representing seconds.

- **Dependencies:**  
  - `import time`

### `generate_mashed_name()`

- **Purpose:**  
  Creates a fun and memorable name by combining a randomly selected adjective with a noun, separated by an underscore and converted to uppercase.

- **Implementation Details:**  
  - Defines two lists: `ADJECTIVES` and `NOUNS`.
  - Uses Python's `random.choice` to select one word from each list.
  - Concatenates the selected words with an underscore and converts the result to uppercase.

- **Dependencies:**  
  - `import random`
