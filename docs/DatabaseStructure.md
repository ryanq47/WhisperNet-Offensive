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


