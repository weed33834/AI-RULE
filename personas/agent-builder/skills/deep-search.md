# Deep Search / 深度搜索技能

## One-line Description / 一句话描述

> 让智能体通过多步循环（分解→搜索→提取→验证→反思→标注→综合）找到高质量、可溯源的网络信息，而非单次泛搜索。
>
> Enables agents to find high-quality, source-traceable web information through a multi-step loop (decompose → search → extract → verify → reflect → cite → synthesize), rather than a single shallow search.

---

## When to Use / 适用场景

- 智能体需要回答事实性问题，且信息时效性重要 / Factual questions where freshness matters
- 需要多源交叉验证才能确认的事实 / Facts requiring multi-source cross-verification
- 研究型任务（竞品分析、技术调研、学术文献） / Research tasks (competitive analysis, tech evaluation, academic literature)
- 单次搜索返回的结果过于泛泛、缺乏深度 / Single-search results are too shallow
- 需要生成带引用来源的结构化报告 / Need to generate a structured report with citations

---

## Core Methodology / 核心方法论

### The Seven-Step Deep Search Loop / 七步深度搜索循环

```
┌─────────────────────────────────────────────────┐
│              用户问题 / User Query                │
└──────────────────────┬──────────────────────────┘
                       ▼
              ┌────────────────┐
              │ 1. 问题分解     │ 将复杂问题拆为可独立搜索的子问题
              │ Decompose      │ Break complex question into sub-questions
              └───────┬────────┘
                      ▼
              ┌────────────────┐
              │ 2. 多源搜索     │ 每个子问题并行搜索 ≥2 个来源
              │ Search         │ Parallel search across ≥2 sources per sub-question
              └───────┬────────┘
                      ▼
              ┌────────────────┐
              │ 3. 内容提取     │ 抓取全文，提取关键信息（非仅摘要）
              │ Extract        │ Fetch full content, extract key info (not just snippets)
              └───────┬────────┘
                      ▼
              ┌────────────────┐
              │ 4. 交叉验证     │ 多来源交叉验证同一事实
              │ Verify         │ Cross-verify same fact across sources
              └───────┬────────┘
                      ▼
              ┌────────────────┐
              │ 5. 反思判断     │ 信息是否充分？不足则回到步骤 1
              │ Reflect        │ Is info sufficient? If not, loop back to step 1
              └───────┬────────┘
                      ▼
              ┌────────────────┐
              │ 6. 来源标注     │ 每个结论附带来源 URL + 时效
              │ Cite           │ Attach source URL + freshness to each conclusion
              └───────┬────────┘
                      ▼
              ┌────────────────┐
              │ 7. 综合报告     │ 结构化输出，区分事实与推测
              │ Synthesize     │ Structured output, separate facts from speculation
              └────────────────┘
```

**推理模式**：Plan-and-Execute + Reflection 组合（参见 AGENTS.md §4）。步骤 1-2 是规划与执行，步骤 5 是反思迭代。

**循环上限**：最多 3 轮反思迭代。超过 3 轮仍信息不足时，停止搜索，明确告知用户"当前可获取的信息不足以得出确定结论"，并附上已找到的部分信息。不得编造信息填补空白（AGENTS.md §1 真实性铁律）。

---

## Search API Selection Decision Tree / 搜索 API 选型决策树

```
需要搜索？
├─ 预算为零 / 开发测试？
│  └─ DuckDuckGo（免费无限制，但结果质量和深度有限）
│
├─ 需要 RAG 就绪的结果（带相关性评分、引用 URL）？
│  └─ Tavily（1000 次/月免费，AI 优化，内置注入防御）
│     https://docs.tavily.com/documentation/about
│
├─ 需要复杂语义查询 / 多跳检索 / 学术研究？
│  └─ Exa（自建索引，语义+关键词混合，多跳准确率 81%）
│     https://exa.ai/docs/reference/search-api-guide
│
├─ 需要完整网页内容提取 / JS 渲染 / 批量爬取？
│  └─ Firecrawl（自动 JS 渲染，输出 clean markdown，有 MCP Server）
│     https://www.firecrawl.dev
│
├─ 需要原始 Google SERP（含 featured snippet、knowledge panel）？
│  └─ SerpAPI（100 次/月免费，Google 结果代理）
│     https://serpapi.com
│
└─ 需要自主深度研究（端到端，生成带引用报告）？
   └─ GPT Researcher（开源，MIT，Plan-and-Solve + RAG）
      https://github.com/assafelovic/gpt-researcher
```

### API 横向对比 / API Comparison

| API | 类型 | 免费额度 | 核心优势 | 局限 | 推荐场景 |
|-----|------|---------|---------|------|---------|
| Tavily | AI 搜索 | 1000 次/月 | 相关性评分(0-1)、引用 URL、注入防御、RAG 就绪 | 语义理解弱于 Exa | RAG 管线、需要引用的智能体 |
| Exa | 语义搜索 | 有免费额度 | 自建索引、语义+关键词混合、多跳检索强 | 无 JS 渲染 | 学术研究、复杂查询 |
| Firecrawl | 爬取+提取 | 500 次/月 | JS 渲染、clean markdown、MCP Server | 搜索能力弱于专用搜索 API | 内容提取、批量爬取 |
| SerpAPI | Google 代理 | 100 次/月 | 完整 SERP JSON、featured snippet | 最贵、非 AI 优化 | SEO 分析、需要 Google 原始结果 |
| DuckDuckGo | 免费搜索 | 无限制 | 无需 Key、零成本 | 结果质量有限、无评分 | 开发测试、低预算 |
| GPT Researcher | 研究框架 | 开源(MIT) | 端到端自主研究、带引用报告 | 需要配置 LLM API | 深度研究任务 |

> **组合策略**：Tavily/Exa 做搜索 + Firecrawl 做内容提取 = 覆盖大部分深度搜索需求。
>
> **Combination strategy**: Tavily/Exa for search + Firecrawl for content extraction = covers most deep-search needs.

---

## Source Quality Rating / 来源质量评级

搜索结果必须按来源权威性分级，低级别来源的结论需要更高级别来源确认：

| 级别 | 来源类型 | 示例 | 可信度 | 单独使用 |
|------|---------|------|--------|---------|
| S | 官方文档/标准 | RFC、W3C、MDN、官方 API 文档 | 最高 | 可单独作为事实 |
| A | 学术论文/权威期刊 | arXiv、IEEE、ACM、Nature | 高 | 可单独作为事实 |
| B | 权威媒体/行业报告 | TechCrunch、Gartner、McKinsey | 较高 | 需交叉验证 |
| C | 技术博客/社区 | Medium、Dev.to、Stack Overflow | 中 | 必须交叉验证 |
| D | 社交媒体/论坛 | Twitter、Reddit、Hacker News | 低 | 仅作为线索，不作事实来源 |

### 交叉验证规则 / Cross-Verification Rules

- **S/A 级来源**：1 个即可作为事实陈述。
- **B 级来源**：需要 ≥2 个独立 B 级来源确认，或 1 个 B + 1 个 S/A 级确认。
- **C 级来源**：需要 ≥2 个独立 C 级 + 1 个 B 级以上确认。
- **D 级来源**：仅作为搜索线索，不得直接作为事实来源。
- **冲突处理**：当来源间出现矛盾时，以高级别来源为准；若同级来源矛盾，标注分歧并交由用户判断（AGENTS.md §7 知识冲突裁决）。

---

## Search Query Optimization / 搜索查询优化

### 从宽泛到具体的三步聚焦 / Three-Step Funneling

```
第 1 轮：宽泛搜索（了解全局）
  query = "LangGraph 多智能体协作"
  → 目标：获取概览、识别关键术语和权威来源

第 2 轮：聚焦搜索（深入特定方面）
  query = "LangGraph StateGraph conditional edges multi-agent 2026"
  → 目标：找到具体技术细节和实现方案

第 3 轮：验证搜索（确认关键事实）
  query = "LangGraph add_conditional_edges 官方文档 site:langchain-ai.github.io"
  → 目标：在官方来源中验证第 2 轮发现的关键信息
```

### 查询构造技巧 / Query Construction Tips

- **加时间限定**：`"2026"` / `"latest"` / `"updated"` 确保时效性
- **加站点限定**：`site:arxiv.org` / `site:github.com` / `site:docs.python.org` 聚焦权威源
- **加文件类型**：`filetype:pdf` 找学术论文；`filetype:md` 找技术文档
- **去噪关键词**：`-site:pinterest.com -site:medium.com` 排除低质量来源
- **中英文双搜**：技术类问题用英文搜索质量更高，国内政策类用中文搜索

---

## Tool Definition (OpenAI Function Calling) / 工具定义

### `deep_search` 工具

```json
{
  "type": "function",
  "function": {
    "name": "deep_search",
    "description": "Perform a multi-step deep web search: decompose the query into sub-questions, search multiple sources, extract full content, cross-verify findings, and return structured results with source citations and freshness timestamps. Use this when a single web_search call is insufficient for the question's complexity.",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "The research question to investigate deeply. Should be a specific question, not a keyword string. Example: 'What are the latest benchmark results for LangGraph vs CrewAI on multi-agent tasks?'"
        },
        "depth": {
          "type": "string",
          "enum": ["quick", "standard", "thorough"],
          "description": "Search depth. 'quick' = 1 round, 2-3 sources. 'standard' = 2 rounds, 4-6 sources. 'thorough' = 3 rounds, 8+ sources with cross-verification. Default: 'standard'."
        },
        "source_preference": {
          "type": "array",
          "items": {
            "type": "string",
            "enum": ["official_docs", "academic", "tech_blog", "news", "github", "any"]
          },
          "description": "Preferred source types to prioritize in results. Example: ['official_docs', 'academic'] for technical accuracy.",
          "default": ["any"]
        },
        "max_results_per_subquery": {
          "type": "integer",
          "description": "Maximum results to fetch per sub-query. Default: 5.",
          "default": 5
        },
        "freshness_filter": {
          "type": "string",
          "description": "Only return results newer than this date (ISO 8601). Example: '2026-01-01'. Omit for no filter.",
          "default": null
        }
      },
      "required": ["query"]
    }
  }
}
```

**副作用标注**：`[side-effect:network]` — 发起网络请求，可能泄露查询内容（AGENTS.md §5 副作用五级标注 L4）。

### `extract_webpage` 工具

```json
{
  "type": "function",
  "function": {
    "name": "extract_webpage",
    "description": "Fetch and extract the full text content of a web page as clean markdown. Use after deep_search to get complete content from promising URLs.",
    "parameters": {
      "type": "object",
      "properties": {
        "url": {
          "type": "string",
          "description": "The URL to extract content from. Must be a valid http(s) URL."
        },
        "output_format": {
          "type": "string",
          "enum": ["markdown", "text", "structured"],
          "description": "Output format. 'markdown' preserves headings and links. 'text' is plain text. 'structured' returns sections as JSON. Default: 'markdown'.",
          "default": "markdown"
        }
      },
      "required": ["url"]
    }
  }
}
```

**副作用标注**：`[side-effect:network]` — 发起网络请求（AGENTS.md §5 副作用五级标注 L4）。

---

## Output Format / 输出格式

深度搜索的输出必须包含以下字段：

```json
{
  "query": "原始问题",
  "sub_questions": ["拆解后的子问题1", "子问题2", "..."],
  "findings": [
    {
      "sub_question": "子问题1",
      "answer": "基于搜索结果的回答",
      "confidence": "high | medium | low",
      "sources": [
        {
          "url": "https://...",
          "title": "来源标题",
          "source_level": "S | A | B | C | D",
          "freshness": "2026-07-12",
          "snippet": "来源中的关键原文片段"
        }
      ],
      "cross_verified": true,
      "conflicts": null
    }
  ],
  "summary": "综合结论（区分事实与推测）",
  "gaps": ["未能找到可靠信息的问题点"],
  "iterations_used": 2,
  "search_apis_used": ["tavily", "exa"]
}
```

---

## Common Pitfalls / 常见陷阱

| 陷阱 | 后果 | 解决方案 |
|------|------|---------|
| 只用搜索摘要，不提取全文 | 信息浅薄、遗漏关键细节 | 对高价值结果必须调用 `extract_webpage` 获取全文 |
| 单来源即作为事实 | 信息可能有误或偏见 | B 级及以下来源必须交叉验证（见来源质量评级） |
| 不标注来源 URL | 用户无法验证真实性 | 每个结论必须附带来源 URL 和时效 |
| 搜索查询太宽泛 | 返回大量低质量结果 | 用三步聚焦法逐步缩小查询范围 |
| 不做反思判断 | 信息不充分就仓促回答 | 必须执行步骤 5 反思，不足则补搜 |
| 搜索轮次无上限 | 浪费 token、拖延响应 | 最多 3 轮反思迭代，超限即停并告知用户 |
| 忽略时效性 | 引用过时信息 | 每条信息标注获取日期，过期信息标注"待更新" |
| 将 D 级来源作为事实 | 传播谣言或错误信息 | D 级来源仅作线索，必须找到 B 级以上来源确认 |

---

## Truthfulness Requirements / 真实性要求（对应 AGENTS.md §1）

- **禁止编造来源**：所有引用的 URL 必须是搜索 API 实际返回的，不得自行构造看似真实的 URL。
- **禁止拼接内容**：不得将不同来源的片段拼接成看似连贯但实际不存在的原文。
- **区分事实与推测**：搜索结果明确支持的内容用陈述句；搜索结果部分支持或推断的内容必须标注"推测："。
- **信息不足即停**：当搜索 3 轮后仍无可靠来源时，必须明确告知用户"当前搜索无法找到可靠信息"，不得编造答案。
- **来源可追溯**：每个事实陈述必须附带至少一个可访问的来源 URL。
- **时效标注**：信息可能随时间变化时，必须标注搜索日期，提示用户"此信息截至 [日期]，可能有更新"。

---

## Checklist / 检查清单

- [ ] 问题已拆解为可独立搜索的子问题
- [ ] 每个子问题搜索了 ≥2 个来源
- [ ] 对高价值结果提取了全文（非仅摘要）
- [ ] B 级及以下来源已交叉验证
- [ ] 执行了反思判断，确认信息充分或已达到 3 轮上限
- [ ] 每个结论附带了来源 URL 和时效
- [ ] 来源按 S/A/B/C/D 分级标注
- [ ] 区分了事实陈述和推测性内容
- [ ] 未找到可靠信息的问题点已明确列出
- [ ] 未编造任何来源、数据或结论
