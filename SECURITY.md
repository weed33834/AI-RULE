# 安全政策

## 漏洞披露
如发现本仓库相关的安全漏洞（如规则导致密钥泄露风险、MCP 红线被绕过等），**请勿在公开 Issue 中附带漏洞详情**。

请先在 [GitHub Issues](https://github.com/weed33834/AI-RULE/issues) 或 [GitCode Issues](https://gitcode.com/badhope/AI-RULE/issues) 提交一个标题模糊的 issue（如"安全漏洞报告"），向维护者索取安全联系方式。维护者确认后会提供私密沟通渠道。

我们会尽快确认并修复。

## 密钥与 Token
- 本仓库绝不硬编码任何 API Key / Token / 密码；一律使用环境变量。
- 若你 Fork 后不慎提交了密钥，立即撤销该密钥，并清理提交历史（`git filter-repo` 或 BFG）。
- 报告漏洞时请勿在公开渠道附带真实密钥。

## MCP 红线
MCP 涉及常驻进程与权限，**AI 不得自下载、自安装、自启动、自配置**。任何涉及 MCP 自动化的 PR 将直接被拒。详见 `AGENTS.md` §5。

## 支持版本
仅最新 `main` 分支接收安全更新。
