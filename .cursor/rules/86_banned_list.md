# Banned Libraries and Tools

This file maintains a list of banned libraries and tools that must not be used in the project.
The security rule enforces these bans strictly.

## Package Managers
- pip (use rye instead)
- poetry (use rye instead)
- pipenv (use rye instead)

## Version Control
- svn (use git instead)
- mercurial (use git instead)

## Testing
- nose (use pytest instead)
- unittest (use pytest instead)

## Logging
- print statements for logging (use logfire instead)
- logging module directly (use logfire instead)

## Database
- sqlite3 for production (use supabase instead)
- raw sql queries (use sqlalchemy or postgrest instead)

## Security
- md5 for hashing (use argon2 instead)
- sha1 for hashing (use argon2 instead)
- pickle for serialization (use pydantic instead)

## Formatting
- autopep8 (use ruff instead)
- black (use ruff instead)
- pylint (use ruff instead)

## Documentation
- sphinx (use mkdocs instead)
- pdoc (use mkdocs instead)

Each banned library/tool includes the recommended alternative in parentheses. 