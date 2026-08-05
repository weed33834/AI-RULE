# SEO & Discoverability Guide for AgentSeed Maintainers

## GitHub Topics (Most Important for Search)

GitHub Topics are the #1 discovery mechanism. Set them via:

**Web UI:** Repository page → gear icon next to "About" → Topics

**CLI (requires `gh` + write token):**
```bash
gh api repos/weed33834/agentseed/topics \
  -X PUT \
  -H "Accept: application/vnd.github.mercy-preview+json" \
  -f names='["ai-agent","agent-framework","mcp","model-context-protocol","persona","governance","ai-rules","system-prompt","prompt-engineering","claude-code","cursor","copilot","trae","gemini","windsurf","cline","continue","amazon-q","coding-assistant","developer-tools","automation","workflow","cli","python","open-source"]'
```

**Recommended topics** (from `.github/topics.yml`):
`ai-agent` `agent-framework` `mcp` `model-context-protocol` `persona` `governance` `ai-rules` `system-prompt` `prompt-engineering` `claude-code` `cursor` `copilot` `trae` `gemini` `windsurf` `cline` `continue` `amazon-q` `coding-assistant` `developer-tools` `automation` `workflow` `cli` `python` `open-source`

## Repository Settings for SEO

1. **Description** (under repo name): Use the full tagline:
   > One command to give your AI agent a brain. Persona-Governance Platform with safety rules, swappable personalities, and 13-platform sync.

2. **Website** (optional): Link to a docs site or GitHub Pages

3. **Social Preview** (Settings → Social preview): Upload a 1280×640px image with:
   - Project name + logo
   - Key value prop ("One command → full agent brain")
   - Platform badges (Claude, Cursor, Copilot, etc.)

## Release SEO

- **Tag names**: Use `v{major}.{minor}.{patch}` (e.g., `v2.4.1`)
- **Release titles**: Include keywords: "AgentSeed v2.4.1 — MCP Server, 13-Platform Sync, Self-Evolution"
- **Release notes**: First 160 chars appear in Google snippets — lead with value prop

## Cross-Platform SEO

| Platform | SEO Action |
|----------|-----------|
| **GitHub** | Topics + Description + Releases + README keywords |
| **Gitee** | 设置标签（开源/AI/开发工具）+ 项目描述 |
| **GitCode** | 添加标签 + 完善项目简介 |
| **PyPI** (future) | Classifiers + Keywords + Long description |
| **Google** | JSON-LD in README + CITATION.cff + codemeta.json |
| **Awesome Lists** | Submit to `awesome-ai-agents`, `awesome-mcp`, `awesome-cursor` |

## Content Marketing

- Blog posts: "How I stopped re-teaching my AI assistant every project"
- Reddit: r/ClaudeAI, r/CursorAI, r/LocalLLaMA, r/MachineLearning
- Hacker News: "Show HN: One command to give your AI agent a brain"
- Twitter/X: Threads about persona governance, MCP, blank-agent problem
- Dev.to / Medium: "Building a Constitution for AI Agents"

## Metrics to Track

- GitHub stars / forks / watchers
- Release download counts (GitHub API)
- `pip install` from Release URL (track via server logs if self-hosted)
- Issue/PR velocity (community health)
- Search ranking: "ai agent framework", "mcp server", "cursor rules"
