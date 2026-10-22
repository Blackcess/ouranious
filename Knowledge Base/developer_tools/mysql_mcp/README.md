# Ouranious MySQL MCP (read-only)

A local STDIO MCP server that lets Codex inspect the configured MySQL database without manual copy/paste. It exposes:

- `list_tables`
- `describe_table`
- `read_query` (single `SELECT` only, bounded results)
- `get_table_counts` (metadata estimates)

## Security model

**Use a dedicated MySQL account with only `SELECT` and `SHOW VIEW` grants.** The server's query checks are defense in depth, not a substitute for database permissions. Use a local development database with non-sensitive data. Do not use production credentials. The server does not expose write tools.

## Windows setup

1. Copy this directory into a stable location, for example:
   `C:\Users\Thomas\Documents\Ouranious Project\Knowledge Base\developer_tools\mysql_mcp`
2. Open PowerShell in that directory.
3. Create and activate a virtual environment:

   ```powershell
   py -3 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   Copy-Item .env.example .env
   notepad .env
   ```

4. Edit `.env` with the actual local database name, user, and password. Do not share `.env` or commit it to Git.
5. Create a dedicated read-only MySQL user (adjust database name as necessary):

   ```sql
   CREATE USER 'ouranious_inspector'@'localhost'
     IDENTIFIED BY 'USE_A_LONG_RANDOM_PASSWORD_HERE';
   GRANT SELECT, SHOW VIEW ON ouranious_kb.*
     TO 'ouranious_inspector'@'localhost';
   SHOW GRANTS FOR 'ouranious_inspector'@'localhost';
   ```

   If MySQL is listening on TCP and the `localhost` account does not match your connection, configure the account host appropriately for your local setup. Do not expose MySQL to the public internet.

6. Smoke-test the server by starting it from the activated environment:

   ```powershell
   python .\server.py
   ```

   It should wait silently for MCP messages. Stop with `Ctrl+C`. No output is expected because stdout is reserved for the MCP protocol.

## Connect the VS Code Codex extension

Codex's IDE extension uses `%USERPROFILE%\.codex\config.toml`. Open the Codex gear menu and choose its MCP/configuration option, or edit the file directly. Merge the section in `config.toml.example`, updating both absolute paths to your actual location. Do not overwrite other existing configuration.

Example shape:

```toml
[mcp_servers.ouranious_mysql]
command = "C:\\absolute\\path\\to\\mysql_mcp\\.venv\\Scripts\\python.exe"
args = ["C:\\absolute\\path\\to\\mysql_mcp\\server.py"]
```

Restart the Codex extension. Check its MCP server list. Then ask Codex to call `list_tables`, followed by `describe_table` on a known table.

## Suggested first prompt in Codex

> Use `ouranious_mysql` to list the tables in the configured database, then inspect `identities`, `relationships`, and the relationship-property tables. Summarise the schema and foreign keys. Do not modify the database. If a table name is missing, report that rather than guessing.

## Notes and limitations

- This is a conservative starter implementation, not a general-purpose SQL sandbox. The database account is the principal safety boundary.
- `read_query` accepts one `SELECT` statement only, blocks comments and several unsafe keywords/functions, limits result rows, and sets MySQL's `max_execution_time` for supported server versions. Keep the account restricted even if query validation is improved later.
- Use only trusted local repositories and reviewed MCP servers. Returned database data is passed to the model as tool output; avoid sensitive personal or production data.
- Package versions are bounded to MCP SDK v1 because this code uses its `FastMCP` API. Upgrade to SDK v2 only after updating the imports and testing against the new API.
