# Connect Revit MCP Server to GitHub Copilot

## 1. Start the Revit bridge (pyRevit Routes)

In Revit, enable pyRevit Routes and verify the endpoint responds:

```text
http://localhost:48884/revit_mcp/status/
```

## 2. Start the MCP server for Copilot

Use this exact developer flow in Windows PowerShell:

1. Open a new terminal window in the repository root.
2. Activate the virtual environment:

```powershell
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& C:\Users\<your-username>\path\to\mcp-server-for-revit-python.extension\.venv\Scripts\Activate.ps1)
```

3. Wait until the prompt shows the env prefix, for example:

```text
(mcp-server-for-revit-python) PS C:\Users\<your-username>\path\to\mcp-server-for-revit-python.extension>
```

4. Start the MCP server with the streamable HTTP protocol:

```powershell
python main.py --streamable-http
```

You can also start with other protocols:

```powershell
python main.py --sse
python main.py --combined
```

Expected startup logs:

```text
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
```

With `--streamable-http`, Copilot should use this endpoint:

```text
http://localhost:8000/mcp
```

Optional alternative command (also valid):

```powershell
uv run --with "mcp[cli]" main.py --combined
```

## 3. Configure MCP in VS Code

Add this configuration to `.vscode/mcp.json`:

```json
{
  "servers": {
    "revit-mcp": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## 4. Enable and trust the server

In VS Code:

1. Run `MCP: List Servers` and ensure `revit-mcp` is running.
2. Accept the trust prompt if shown.
3. In Copilot Chat, open Configure Tools and enable the server tools.

## 5. Validate end-to-end

In Copilot Chat, run `get_revit_status`.

Expected values:

- `status`: `active`
- `health`: `healthy`
- `revit_available`: `true`
