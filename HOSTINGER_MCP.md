# Hostinger MCP — setup

This repo is wired to Hostinger's official MCP server (`hostinger-api-mcp`) via
`.mcp.json` at the repo root. Claude Code picks it up automatically for sessions
started from this folder.

## One-time setup

1. **Get an API token**
   Hostinger → hPanel → account menu → **API** → generate a token
   (https://hpanel.hostinger.com/profile/api). Copy it.

2. **Expose it as an environment variable** named `HOSTINGER_API_TOKEN`.
   The `.mcp.json` references `${HOSTINGER_API_TOKEN}` so the secret is never
   committed to git.

   - macOS/Linux — add to your shell profile (`~/.zshrc` / `~/.bashrc`):
     ```sh
     export HOSTINGER_API_TOKEN="paste-your-token-here"
     ```
     Then open a new terminal (or `source` the file).

3. **Start Claude Code from this folder.** On first run it will ask you to
   approve the new `hostinger` MCP server — approve it.

## Verify the connection

Inside Claude Code:

```
/mcp
```

`hostinger` should show as **connected**, and its tools (VPS, domains, DNS,
billing, etc.) become available.

## Notes

- The server runs on demand via `npx -y hostinger-api-mcp`, so Node.js must be
  installed. No global install is required.
- Never paste the token into `.mcp.json` or any committed file — keep it in the
  `HOSTINGER_API_TOKEN` environment variable only.
