# Hostinger MCP servers for Claude Code

Adds three Hostinger MCP servers — hosting, domains, and DNS — so Claude Code can
manage the website's hosting, domain, and DNS records directly.

## Config

Add this to your Claude config file, merging it into any existing `mcpServers`
block (don't overwrite one that's already there):

- **Windows:** `%USERPROFILE%\.claude.json`  (e.g. `C:\Users\<you>\.claude.json`)
- **macOS / Linux:** `~/.claude.json`

```json
{
  "mcpServers": {
    "hostinger-hosting": {
      "command": "npx.cmd",
      "args": ["--package=hostinger-api-mcp@latest", "hostinger-hosting-mcp"],
      "env": { "HOSTINGER_API_TOKEN": "your-token-here" }
    },
    "hostinger-domains": {
      "command": "npx.cmd",
      "args": ["--package=hostinger-api-mcp@latest", "hostinger-domains-mcp"],
      "env": { "HOSTINGER_API_TOKEN": "your-token-here" }
    },
    "hostinger-dns": {
      "command": "npx.cmd",
      "args": ["--package=hostinger-api-mcp@latest", "hostinger-dns-mcp"],
      "env": { "HOSTINGER_API_TOKEN": "your-token-here" }
    }
  }
}
```

## Steps

1. Get a Hostinger API token from **hPanel → Account → API** and copy it.
2. Open `%USERPROFILE%\.claude.json` (Windows) or `~/.claude.json` (Mac/Linux).
   If the file already has an `mcpServers` object, add the three entries above
   inside it rather than replacing it.
3. Replace **every** `"your-token-here"` with your real token.
4. Save, then fully restart Claude Code.
5. Verify with `/mcp` — the three `hostinger-*` servers should be listed.

## Notes

- `npx.cmd` is the Windows executable. On **macOS / Linux** change each
  `"command": "npx.cmd"` to `"command": "npx"`.
- The token is a live credential. Keep it out of the repo — this file uses the
  `your-token-here` placeholder on purpose. Never commit the real token.
