# DAR 测试场景与题目清单

> 6 个测试场景覆盖：多语种（en/zh/ja）、全领域（coding/conversation/paper/novel/agent-builder）、复杂推理与工程任务。
> 每个场景同时执行基准测试（无 DAR 提示词）和增强测试（含 DAR 路由/打分/领域知识提示词），共 120 次 API 调用。

## §1 测试场景

### S1-CVE：安全漏洞调查（English / coding）

**测试重点**：CVE/CVSS/CWE 精确数据获取，版本号与补丁追溯

**题目**：
> Our FastAPI service uses python-multipart. Investigate CVE-2024-24762: what is the CVSS score, affected versions, CWE classification, and fix version? Provide verified data with sources.

**预期术语**：CVSS, CWE, 7.5, 0.0.7, ReDoS, python-multipart
**预期来源**：NVD, CVE, Snyk, GitHub

---

### S2-GDP：GDP 事实核查（中文 / conversation）

**测试重点**：名义 GDP vs PPP GDP 区分，权威数据源定位

**题目**：
> 有人声称"2024年中国GDP已超过美国成为全球第一"。请验证这个说法是否准确，区分名义GDP和PPP GDP，提供World Bank或IMF的权威数据，标注数据年份和来源。

**预期术语**：名义GDP, PPP, World Bank, current US$, 万亿
**预期来源**：World Bank, IMF, Statista

---

### S3-ACADEMIC：学术文献综述（English / paper）

**测试重点**：学术方法论（CrossRef/Retraction Watch），引用验证流程

**题目**：
> For a literature review on 'LLMs in medical diagnosis', explain the methodology to: (1) search Google Scholar and Semantic Scholar, (2) verify citations via CrossRef, (3) check retractions via Retraction Watch, (4) assess source authority. What are the key terminology and conventions?

**预期术语**：DOI, CrossRef, Retraction Watch, peer review, h-index, Q1
**预期来源**：Google Scholar, Semantic Scholar, CrossRef, PubMed

---

### S4-NOVEL：历史小说背景研究（English / novel）

**测试重点**：词源验证、人名时代准确性、历史一致性

**题目**：
> I'm writing a novel set in Victorian London (1860s). How would I verify: (1) character names like Eleanor and Reginald are period-appropriate, (2) the word 'gaslight' existed then (but not 'gaslighting' as psychological manipulation), (3) place names like Whitechapel? What authoritative sources should I use?

**预期术语**：etymology, Behind the Name, Etymonline, anachronism, OED
**预期来源**：Behind the Name, Etymonline, OED, GeoNames

---

### S5-JP：多语言技术问答（日本語 / conversation）

**测试重点**：日语技术准确性，ASGI/WSGI 概念辨析

**题目**：
> FastAPIとDjangoの非同期処理の違いを説明してください。公式ドキュメントに基づいて、ASGIとWSGIの違い、async/awaitの使い方、パフォーマンスの違いを含めて回答してください。情報源を明記してください。

**预期术语**：ASGI, WSGI, async, await, FastAPI, Django
**预期来源**：FastAPI Docs, Django Docs, MDN

---

### S6-AGENT：模型选型与 Benchmark（English / agent-builder）

**测试重点**：模型对比方法论，Benchmark 数据引用，Elo 评分

**题目**：
> Compare GPT-4o vs Claude-3.5-Sonnet vs Llama-3.1-70B for a customer service agent. Evaluate on: reasoning, tool-calling, cost, latency, multilingual support. Which benchmarks (LMSYS Arena, Open LLM Leaderboard) should you check? Provide a structured comparison with data sources.

**预期术语**：Elo, benchmark, tool calling, function calling, LMSYS, token
**预期来源**：LMSYS, Open LLM Leaderboard, Hugging Face

---

## §2 DAR 增强提示词（按领域）

基准测试使用通用系统提示词：
> You are a helpful AI assistant. Answer accurately and cite sources.

增强测试在用户问题前注入 DAR 提示词，包含三个部分：
1. **[DAR 路由]** — 优先源名录（T1-T4 分级）
2. **[DAR 打分]** — 打分公式与权重
3. **[DAR 领域知识]** — 关键术语、规范、常见陷阱

### coding 领域 DAR 前缀
```
[DAR Routing] For coding/security queries, priority sources (T1): Python/Node.js docs,
PyPI/npm, CVE (cve.mitre.org), NVD (nvd.nist.gov), Snyk (security.snyk.io),
GitHub Security Advisories, MDN, Docker/K8s docs.
[DAR Scoring] Final Score = 0.40×Relevance + 0.30×Credibility + 0.25×Freshness + 0.05×Consensus.
T1 sources get ×1.0 weight; T3 (blogs) get ×0.5; T4 (social media) get ×0.2.
[DAR Domain Knowledge] Key terms: CVE, CVSS, CWE, breaking change, semver, deprecation.
Conventions: cite CVE numbers, specify package versions. Pitfalls: ignoring CVE, version incompatibility.
```

### conversation 领域 DAR 前缀
```
[DAR 路由] 事实核查类问题，优先源（T1）：World Bank、IMF、WHO、CDC、政府门户网站。
事实核查（T1）：Snopes、FactCheck.org、PolitiFact。
[DAR 打分] Final Score = 0.45×相关性 + 0.25×可信度 + 0.10×时效 + 0.20×共识。
[DAR 领域知识] 关键术语：GDP（名义/PPP）、CPI、PMI。
规范：统计数据标注年份和来源，区分名义GDP和PPP。陷阱：混淆口径，使用过时数据。
```

### paper 领域 DAR 前缀
```
[DAR Routing] For academic queries, priority sources (T1): Google Scholar, Semantic Scholar,
arXiv, PubMed, DBLP, CrossRef, Retraction Watch, ORCID.
Top journals: Nature, Science, PNAS, Cell, Lancet, IEEE TPAMI, JMLR.
[DAR Scoring] Final Score = 0.30×Relevance + 0.40×Credibility + 0.15×Freshness + 0.15×Consensus.
Academic credibility weighted highest. Preprints need "Preprint" label.
[DAR Domain Knowledge] Terms: h-index, IF, Q1/Q2/Q3/Q4, DOI, ORCID, peer review.
Conventions: verify all DOIs via CrossRef, check Retraction Watch. Pitfalls: citing retracted papers.
```

### novel 领域 DAR 前缀
```
[DAR Routing] For creative writing research, priority sources (T1): Merriam-Webster,
Oxford English Dictionary, Etymonline, Behind the Name, GeoNames, Purdue OWL.
[DAR Scoring] Final Score = 0.35×Relevance + 0.20×Credibility + 0.05×Freshness + 0.40×Consensus.
Consensus weighted highest for historical/cultural facts.
[DAR Domain Knowledge] Terms: etymology, archaism, neologism, anachronism.
Conventions: check word etymology for period accuracy. Pitfalls: using modern words in historical settings.
```

### agent-builder 领域 DAR 前缀
```
[DAR Routing] For AI agent queries, priority sources (T1): Hugging Face, Papers with Code,
LangChain Docs, LlamaIndex Docs, OpenAI/Anthropic/Google AI Docs, MCP Spec,
Open LLM Leaderboard, LMSYS Chatbot Arena.
[DAR Scoring] Final Score = 0.35×Relevance + 0.30×Credibility + 0.25×Freshness + 0.10×Consensus.
Freshness weighted high (API changes fast). Model benchmarks expire in 3 months.
[DAR Domain Knowledge] Terms: LLM, RAG, ReAct, CoT, tool calling, Elo rating.
Conventions: specify framework versions, full model names. Pitfalls: deprecated APIs, confusing versions.
```

---

## §3 评分标准（6 维度 × 0-5 分）

| 维度 | 说明 | 评分标准 |
|------|------|----------|
| **Source Quality** | 来源是否权威、是否覆盖 T1/T2 | 0=无来源, 5=全部 T1/T2 |
| **Citation Fidelity** | 引用信息是否准确可验证 | 0=无引用, 5=全部可追溯+URL |
| **Routing Accuracy** | 是否按 DAR 路由优先查权威源 | 0=全网乱搜, 5=完全按路由 |
| **Conflict Handling** | 来源冲突是否正确处理 | 0=忽略冲突, 5=呈现分歧+标注 |
| **Freshness Awareness** | 是否标注时效性 | 0=无时效意识, 5=完整时效标注 |
| **Domain Knowledge** | 是否使用领域专业术语 | 0=无术语, 5=正确使用+避坑 |

单场景总分 /30。评分基于客观关键词匹配，不因期望结果调整分数。

---

## §4 API 渠道

| 渠道 | 地址 | 密钥 | 可用模型 |
|------|------|------|---------|
| 主接口 | https://api.587.lol/v1 | 任意值 | moonweaver-4.8 |
| 备用接口 | https://api.hcnsec.cn/v1 | sk-j4TEjj...（已配置） | 25 个文本模型 |

> 注：主接口穷尽所有调试方案后仅 1 个模型可用，按预案切换至备用接口完成全覆盖测试。
