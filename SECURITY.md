# Security Policy

## Reporting a Vulnerability

If you discover a security issue related to this repository (e.g., rules that
could leak secrets, MCP red-line bypasses), **do not include vulnerability
details in a public issue**.

Instead, open a vaguely-titled issue (e.g., "Security report") on
[GitHub Issues](https://github.com/weed33834/agentseed/issues) or
[GitCode Issues](https://gitcode.com/badhope/agentseed/issues) and ask the
maintainers for a secure contact channel. We will confirm and provide a
private channel, then fix the issue as soon as possible.

## Secrets & Tokens

- This repository never hardcodes API keys, tokens, or passwords; always use environment variables.
- If you accidentally commit a secret in a fork, revoke it immediately and scrub the history (`git filter-repo` or BFG).
- Never attach real secrets to public reports.

## MCP Red Line

MCP involves long-running processes and permissions. **AI must not
self-download, self-install, self-start, or self-configure MCP servers.**
Any PR that automates MCP setup will be rejected outright. See `AGENTS.md` §5.

## Supported Versions

Only the latest `main` branch receives security updates.
