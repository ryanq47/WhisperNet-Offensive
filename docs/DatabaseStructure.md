# ORM Models Documentation

## Overview

This document describes the SQLAlchemy ORM models/Database structure used in the application for managing users and tokens. It includes details on the schema and methods of each model.

## `User` Model

### Description

The `User` model represents a user in the application. It maps to the `user` table in the database and includes information about user credentials and authentication status.

### Table: `user`

| Column       | Type     | Constraints       | Example Value           | Description                             |
|--------------|----------|-------------------|-------------------------|-----------------------------------------|
| `username`   | `String` | `unique=True`, `nullable=False` | `johndoe`               | The username of the user. Must be unique and not null. |
| `uuid`       | `String` | `primary_key=True` | `550e8400-e29b-41d4-a716-446655440000` | The UUID of the user, which serves as the primary key. This allows for changing the username. |
| `password`   | `String` |                   | `hashed_password_string` | The hashed password of the user. Optional. |
| `authenticated` | `Boolean` | `default=False` | `False`                 | Indicates whether the user is authenticated. Defaults to `False`. |

---

## `Token` Model

### Description

The `Token` model represents an authentication token issued to a user. It maps to the `tokens` table in the database and includes details about the token's validity and expiration.

### Table: `tokens`

| Column       | Type     | Constraints       | Example Value           | Description                             |
|--------------|----------|-------------------|-------------------------|-----------------------------------------|
| `id`         | `Integer` | `primary_key=True`, `autoincrement=True` | `1`                     | Primary key for indexing. Auto-increments with each new row. |
| `uuid`       | `String(36)` | `index=True`, `nullable=False` | `550e8400-e29b-41d4-a716-446655440000` | User ID associated with the token. Indexed for performance, not nullable. |
| `token`      | `String(256)` | `unique=True`, `nullable=False` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c` | The actual token string. Must be unique and not null. |
| `created_at` | `DateTime` | `default=datetime.datetime.utcnow` | `2024-08-14 12:34:56` | Timestamp when the token was created. Defaults to the current time. |
| `expires_at` | `DateTime` |                   | `2024-08-15 12:34:56` | Timestamp when the token expires. Optional. |
| `active`     | `Boolean` | `default=True`    | `True`                  | Indicates whether the token is active. Defaults to `True`. |

### Notes

- **UUID Storage:** The `uuid` field is stored as a string with a length of 36 characters, assuming UUIDs are represented as strings. If you decide to use binary format for UUIDs, adjust the column type accordingly (e.g., `db.LargeBinary` or `db.Binary(16)`).

---

### Summary

The `User` model tracks user credentials and authentication status, while the `Token` model manages authentication tokens, including their validity and expiration. These models are designed to provide robust user and token management within the application.
