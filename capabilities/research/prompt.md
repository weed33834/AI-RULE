# DAR — Domain-Aware Retrieval

> 本文件由 `scripts/build_dar_md.py` 自动生成，聚合 4 域配置。禁止手工编辑。
> 加载后，在 enable_capabilities: [dar] 的 Profile 中生效，提供域感知源路由与打分策略。

## §1 源注册表

### 1.1 软件开发 (coding)

| Tier | 源 | 类型 |
|---|---|---|
| T1 | [Python Docs](https://docs.python.org/3/) | 官方文档 |
| T1 | [Node.js Docs](https://nodejs.org/docs/) | 官方文档 |
| T1 | [Rust Docs](https://doc.rust-lang.org/) | 官方文档 |
| T1 | [Go Docs](https://go.dev/doc/) | 官方文档 |
| T1 | [Java Docs](https://docs.oracle.com/en/java/) | 官方文档 |
| T1 | [Django Docs](https://docs.djangoproject.com/) | 框架文档 |
| T1 | [FastAPI Docs](https://fastapi.tiangolo.com/) | 框架文档 |
| T1 | [React Docs](https://react.dev/) | 框架文档 |
| T1 | [Next.js Docs](https://nextjs.org/docs) | 框架文档 |
| T1 | [Vue.js Docs](https://vuejs.org/guide/) | 框架文档 |
| T1 | [Spring Docs](https://docs.spring.io/spring-framework/reference/) | 框架文档 |
| T1 | [PyPI](https://pypi.org/) | 包仓库 |
| T1 | [npm](https://www.npmjs.com/) | 包仓库 |
| T1 | [crates.io](https://crates.io/) | 包仓库 |
| T1 | [Maven Central](https://central.sonatype.com/) | 包仓库 |
| T1 | [GitHub](https://github.com/) | 代码托管 |
| T1 | [GitLab](https://gitlab.com/) | 代码托管 |
| T1 | [MDN Web Docs](https://developer.mozilla.org/) | Web 标准 |
| T1 | [W3C](https://www.w3.org/) | Web 标准 |
| T1 | [WHATWG](https://whatwg.org/) | Web 标准 |
| T1 | [CVE](https://cve.mitre.org/) | 漏洞库 |
| T1 | [NVD](https://nvd.nist.gov/) | 漏洞库 |
| T1 | [Snyk Vulnerability DB](https://security.snyk.io/) | 漏洞库 |
| T1 | [GitHub Security Advisories](https://github.com/advisories) | 漏洞库 |
| T2 | [Stack Overflow](https://stackoverflow.com/) | 技术社区 |
| T2 | [DevDocs](https://devdocs.io/) | 文档聚合 |
| T2 | [Real Python](https://realpython.com/) | 教程 |
| T2 | [CSS-Tricks](https://css-tricks.com/) | 教程 |
| T2 | [Martin Fowler](https://martinfowler.com/) | 架构 |
| T2 | [Docker Docs](https://docs.docker.com/) | DevOps 文档 |
| T2 | [Kubernetes Docs](https://kubernetes.io/docs/) | DevOps 文档 |
| T2 | [Ansible Docs](https://docs.ansible.com/) | DevOps 文档 |
| T2 | [Terraform Docs](https://developer.hashicorp.com/terraform/docs) | DevOps 文档 |
| T2 | [AWS Docs](https://docs.aws.amazon.com/) | 云文档 |
| T2 | [Azure Docs](https://learn.microsoft.com/azure/) | 云文档 |
| T2 | [GCP Docs](https://cloud.google.com/docs) | 云文档 |
| T3 | [Reddit /r/programming](https://www.reddit.com/r/programming/) | 社区讨论 |
| T3 | [Hacker News](https://news.ycombinator.com/) | 社区讨论 |
| T3 | [Dev.to](https://dev.to/) | 技术博客 |
| T3 | [Medium](https://medium.com/) | 技术博客 |

### 1.2 通用对话 (conversation)

| Tier | 源 | 类型 |
|---|---|---|
| T1 | [中国政府网](https://www.gov.cn/) | 政府门户 |
| T1 | [WHO](https://www.who.int/) | 国际组织 |
| T1 | [CDC](https://www.cdc.gov/) | 卫生组织 |
| T1 | [World Bank](https://www.worldbank.org/) | 国际组织 |
| T1 | [IMF](https://www.imf.org/) | 国际组织 |
| T1 | [UN](https://www.un.org/) | 国际组织 |
| T1 | [Reuters](https://www.reuters.com/) | 通讯社 |
| T1 | [AP News](https://apnews.com/) | 通讯社 |
| T1 | [新华社](http://www.xinhuanet.com/) | 通讯社 |
| T1 | [Statista](https://www.statista.com/) | 统计数据 |
| T1 | [Snopes](https://www.snopes.com/) | 事实核查 |
| T1 | [FactCheck.org](https://www.factcheck.org/) | 事实核查 |
| T1 | [PolitiFact](https://www.politifact.com/) | 事实核查 |
| T2 | [Google Scholar](https://scholar.google.com/) | 学术索引 |
| T2 | [BBC](https://www.bbc.com/) | 权威媒体 |
| T2 | [NYT](https://www.nytimes.com/) | 权威媒体 |
| T2 | [Britannica](https://www.britannica.com/) | 百科 |
| T2 | [DevDocs](https://devdocs.io/) | 文档聚合 |
| T3 | [Wikipedia](https://www.wikipedia.org/) | 百科 |
| T3 | [百度百科](https://baike.baidu.com/) | 百科 |
| T4 | 自媒体平台 | 社交媒体 |

### 1.3 小说创作 (novel)

| Tier | 源 | 类型 |
|---|---|---|
| T1 | [Merriam-Webster](https://www.merriam-webster.com/) | 英语词典 |
| T1 | [Oxford English Dictionary (OED)](https://www.oed.com/) | 英语词典 |
| T1 | [Cambridge Dictionary](https://dictionary.cambridge.org/) | 英语词典 |
| T1 | [Zdic](https://www.zdic.net/) | 汉语词典 |
| T1 | [百度汉语](https://hanyu.baidu.com/) | 汉语词典 |
| T1 | [Etymonline](https://www.etymonline.com/) | 词源 |
| T1 | [Behind the Name](https://www.behindthename.com/) | 人名词源 |
| T1 | [Behind the Surname](https://surnames.behindthename.com/) | 姓氏词源 |
| T1 | [Purdue OWL](https://owl.purdue.edu/) | 写作规范 |
| T1 | [Chicago Manual of Style](https://www.chicagomanualofstyle.org/) | 写作规范 |
| T1 | [GeoNames](https://www.geonames.org/) | 地名 |
| T2 | [Power Thesaurus](https://www.powerthesaurus.org/) | 同义词 |
| T2 | [Thesaurus.com](https://www.thesaurus.com/) | 同义词 |
| T2 | [Free Dictionary Idioms](https://idioms.thefreedictionary.com/) | 习语 |
| T2 | [JSTOR](https://www.jstor.org/) | 历史资料 |
| T2 | [Britannica](https://www.britannica.com/) | 百科 |
| T2 | [Query Tracker](https://querytracker.net/) | 出版信息 |
| T2 | [Publishers Marketplace](https://www.publishersmarketplace.com/) | 出版信息 |

### 1.5 论文写作 (paper)

| Tier | 源 | 类型 |
|---|---|---|
| T1 | [Nature](https://www.nature.com/) |  |
| T1 | [Science](https://www.science.org/) |  |
| T1 | [The Lancet](https://www.thelancet.com/) |  |
| T1 | [JAMA](https://jamanetwork.com/) |  |
| T1 | [BMJ](https://www.bmj.com/) |  |
| T1 | [Cell](https://www.cell.com/cell) |  |
| T1 | [PNAS](https://www.pnas.org/) |  |
| T1 | [IEEE TPAMI](https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=34) |  |
| T1 | [JMLR](https://www.jmlr.org/) |  |
| T1 | [ACM Computing Surveys](https://dl.acm.org/journal/csur) |  |
| T1 | [Physical Review Letters](https://journals.aps.org/prl/) |  |
| T1 | [Chemical Reviews](https://pubs.acs.org/journal/chreay) |  |
| T1 | [Google Scholar](https://scholar.google.com/) | 索引 |
| T1 | [Semantic Scholar](https://www.semanticscholar.org/) | 索引 |
| T1 | [arXiv](https://arxiv.org/) | 预印本 |
| T1 | [JCR (Journal Citation Reports)](https://jcr.clarivate.com/) | 期刊评价 |
| T1 | [PubMed](https://pubmed.ncbi.nlm.nih.gov/) | 索引 |
| T1 | [DBLP](https://dblp.org/) | 索引 |
| T1 | [SSRN](https://www.ssrn.com/) | 预印本 |
| T1 | [JSTOR](https://www.jstor.org/) | 档案库 |
| T1 | [CrossRef](https://www.crossref.org/) | DOI 验证 |
| T1 | [Retraction Watch](https://retractionwatch.com/) | 撤稿检查 |
| T1 | [ORCID](https://orcid.org/) | 作者验证 |
| T2 | [Scopus](https://www.scopus.com/) | 索引 |
| T2 | [Web of Science](https://www.webofscience.com/) | 索引 |
| T2 | [Dimensions](https://app.dimensions.ai/) | 索引 |
| T2 | [Connected Papers](https://www.connectedpapers.com/) | 可视化 |
| T2 | [Inciteful](https://inciteful.xyz/) | 可视化 |
| T2 | [Zotero](https://www.zotero.org/) | 文献管理 |
| T2 | [Mendeley](https://www.mendeley.com/) | 文献管理 |
| T2 | [Citation Geany](https://citationgeany.com/) | 引用验证 |
| T3 | [ResearchGate](https://www.researchgate.net/) | 学术社交 |
| T3 | [Academia.edu](https://www.academia.edu/) | 学术社交 |

### 1.6 智能体构建 (agent-builder)

| Tier | 源 | 类型 |
|---|---|---|
| T1 | [Hugging Face](https://huggingface.co/) | 模型库 |
| T1 | [Papers with Code](https://paperswithcode.com/) | 论文+代码 |
| T1 | [LangChain Docs](https://python.langchain.com/docs/) | 框架文档 |
| T1 | [LlamaIndex Docs](https://docs.llamaindex.ai/) | 框架文档 |
| T1 | [AutoGen Docs](https://microsoft.github.io/autogen/) | 框架文档 |
| T1 | [CrewAI Docs](https://docs.crewai.com/) | 框架文档 |
| T1 | [OpenAI API Docs](https://platform.openai.com/docs/) | API 文档 |
| T1 | [Anthropic API Docs](https://docs.anthropic.com/) | API 文档 |
| T1 | [Google AI Docs](https://ai.google.dev/) | API 文档 |
| T1 | [MCP Spec](https://modelcontextprotocol.io/) | 协议规范 |
| T1 | [Open LLM Leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard) | 模型评测 |
| T1 | [LMSYS Chatbot Arena](https://chat.lmsys.org/) | 模型评测 |
| T2 | [Prompt Engineering Guide](https://www.promptingguide.ai/) | 提示词工程 |
| T2 | [Chroma Docs](https://docs.trychroma.com/) | 向量数据库 |
| T2 | [Pinecone Docs](https://docs.pinecone.io/) | 向量数据库 |
| T2 | [Weaviate Docs](https://weaviate.io/developers/weaviate) | 向量数据库 |
| T2 | [LangSmith](https://docs.smith.langchain.com/) | 可观测性 |
| T2 | [Phoenix (Arize)](https://phoenix.arize.com/) | 可观测性 |
| T2 | [tau-Bench](https://github.com/sierra-research/tau-bench) | Agent 评测 |

## §2 打分协议

| 领域 | R(相关性) | C(可信度) | F(时效) | S(共识) | 说明 |
|---|---|---|---|---|---|
| 软件开发 | 0.4 | 0.3 | 0.25 | 0.05 | 开发领域时效性权重高（API 变更频繁），共识性权重低（社区讨论质量参差） |
| 通用对话 | 0.45 | 0.25 | 0.1 | 0.2 | 通用问答相关性和共识度权重高，时效性要求因问题而异 |
| 小说创作 | 0.35 | 0.2 | 0.05 | 0.4 | 小说创作共识度权重最高（历史/文化事实需多源确认），时效性几乎不重要 |
| 互动小说 | 0.35 | 0.25 | 0.2 | 0.2 | 互动小说游戏引擎版本更新快，时效性权重较高 |
| 论文写作 | 0.3 | 0.4 | 0.15 | 0.15 | 学术论文以可信度（credibility）为最高权重，确保引用来源的权威性 |
| 智能体构建 | 0.35 | 0.3 | 0.25 | 0.1 | Agent 领域发展极快，时效性权重较高 |

## §3 时效表

| 域/类型 | 有效周期 | 衰减因子 | 备注 |
|---|---|---|---|
| [coding] API/SDK 版本 | 1-2 年 | 0.7 | 检查版本兼容性 |
| [coding] 框架版本 | 2 年 | 0.8 | 检查是否有 breaking change |
| [coding] 安全漏洞 | 3 个月 | 0.3 | 必须查最新状态 |
| [coding] 包/库版本 | 1 年 | 0.6 | 检查最新版本 |
| [coding] 语言语法 | 5 年 | 0.9 | 语法相对稳定 |
| [coding] 设计模式 | 10 年 | 1.0 | 设计模式稳定 |
| [conversation] 统计数据 | 1-3 年 | 0.7 | 查最新数据 |
| [conversation] 政策法规 | 5 年 | 0.8 | 检查修订 |
| [conversation] 历史事件 | 永不过期 | 1.0 | 事实不变 |
| [conversation] 新闻事件 | 1 个月 | 0.5 | 事件可能发展 |
| [conversation] 人物信息 | 1 年 | 0.8 | 可能变化 |
| [novel] 词源/词义 | 永不过期 | 1.0 | 语言历史不变 |
| [novel] 人名含义 | 永不过期 | 1.0 | 名字历史不变 |
| [novel] 历史背景 | 永不过期 | 1.0 | 历史事实不变 |
| [novel] 写作规范 | 10 年 | 0.9 | 规范偶尔修订 |
| [novel] 出版信息 | 1 年 | 0.8 | 出版界变化快 |
| [paper] 实证研究 | 5-10 年 | 0.8 | 检查是否有新研究推翻 |
| [paper] 理论研究 | 10-20 年 | 0.9 | 经典理论不降权 |
| [paper] 预印本 | 1 年 | 0.7 | 未同行评审，需标注 |
| [paper] 综述文章 | 5 年 | 0.8 | 检查是否有更新综述 |
| [paper] 基础公理 | 永不过期 | 1.0 | 无需时效检查 |
| [agent-builder] 模型 API | 6 个月 | 0.5 | API 变更频繁 |
| [agent-builder] 框架版本 | 1 年 | 0.6 | 框架迭代快 |
| [agent-builder] 模型评测 | 3 个月 | 0.3 | 新模型不断发布 |
| [agent-builder] 研究论文 | 2 年 | 0.7 | 领域发展快 |
| [agent-builder] 设计模式 | 3 年 | 0.8 | 模式相对稳定 |

## §4 路由规则

| 域/触发器 | 动作 | 优先源 | 回退源 |
|---|---|---|---|
| [coding] API 用法, API usage, how to use | prefer_official | 官方文档, MDN | Stack Overflow, Dev.to |
| [coding] 安装, install, pip install, npm install | check_latest_version | PyPI, npm, crates.io, Maven Central | Stack Overflow |
| [coding] 安全漏洞, CVE, vulnerability, security | must_verify | CVE, NVD, Snyk, GitHub Security Advisories | Stack Overflow |
| [coding] 部署, deploy, docker, kubernetes | prefer_official | Docker Docs, Kubernetes Docs, AWS/Azure/GCP Docs | Dev.to, Medium |
| [coding] 错误信息, error message, 报错 | check_version | 官方文档, Stack Overflow | GitHub Issues, Reddit |
| [coding] 性能优化, performance, benchmark | multi_source | 官方文档, Martin Fowler | Stack Overflow, Dev.to |
| [coding] 设计模式, design pattern, 架构 | prefer_authoritative | Martin Fowler, 官方文档 | Stack Overflow, Dev.to |
| [coding] 包对比, library comparison, vs | multi_source | PyPI, npm, GitHub | Stack Overflow, Reddit |
| [conversation] GDP, 经济数据, 统计数据, statistics | must_verify | World Bank, IMF, Statista | BBC, NYT |
| [conversation] 疫情, 健康, 疾病, health | must_verify | WHO, CDC | Reuters, BBC |
| [conversation] 谣言, 辟谣, fact check, 是真的吗 | must_verify | Snopes, FactCheck.org, PolitiFact | Reuters, AP News |
| [conversation] 政策, 法规, 法律 | must_verify | 中国政府网, 政府门户 | 新华社, BBC |
| [conversation] 历史事件, history, 什么时候发生 | cross_verify | Britannica, Wikipedia | BBC, NYT |
| [novel] 词义, 定义, definition, 什么意思 | prefer_authoritative | Merriam-Webster, OED, Cambridge Dictionary | Wikipedia |
| [novel] 词源, etymology, 词源学, 起源 | prefer_authoritative | Etymonline, OED | Merriam-Webster |
| [novel] 人名, 名字含义, name meaning, character name | prefer_authoritative | Behind the Name, Behind the Surname | Etymonline |
| [novel] 同义词, synonym, 近义词 | multi_source | Power Thesaurus, Thesaurus.com | Merriam-Webster |
| [novel] 历史背景, 历史事件, historical | cross_verify | Britannica, JSTOR | Wikipedia |
| [novel] 写作规范, 格式, style guide | prefer_authoritative | Purdue OWL, Chicago Manual of Style | Wikipedia |
| [paper] 文献综述, literature review, related work | must_cite | Google Scholar, Semantic Scholar, PubMed, DBLP | arXiv, SSRN, JSTOR |
| [paper] 引用验证, citation verification, 引用检查 | must_verify | CrossRef, Google Scholar, Semantic Scholar | ResearchGate, Academia.edu |
| [paper] 撤稿检查, retraction check, 撤稿 | must_check | Retraction Watch, CrossRef | Google Scholar |
| [paper] 方法对比, methodology comparison | multi_source | Google Scholar, Semantic Scholar | arXiv, PubMed |
| [paper] 影响因子, impact factor, 期刊排名 | must_verify | JCR, Scopus | Google Scholar |
| [paper] DOI 验证, DOI lookup | must_verify | CrossRef, DOI.org | Google Scholar |
| [paper] 作者验证, author verification, ORCID | must_verify | ORCID, Google Scholar | ResearchGate |
| [agent-builder] 模型选择, model selection, 哪个模型, best model | must_verify | Open LLM Leaderboard, LMSYS Chatbot Arena, Hugging Face | Papers with Code |
| [agent-builder] LangChain, langchain | prefer_official | LangChain Docs | Prompt Engineering Guide |
| [agent-builder] AutoGen, autogen, multi-agent | prefer_official | AutoGen Docs, CrewAI Docs | LangChain Docs |
| [agent-builder] 向量数据库, vector database, embedding | multi_source | Chroma Docs, Pinecone Docs, Weaviate Docs | LangChain Docs |
| [agent-builder] MCP, Model Context Protocol | prefer_official | MCP Spec | Anthropic API Docs |
| [agent-builder] Agent 评测, agent evaluation, benchmark | must_verify | tau-Bench, Open LLM Leaderboard | Papers with Code |

## §5 领域知识

### 5.1 软件开发 (coding)

**术语**：

- breaking change: 破坏性变更
- LTS: 长期支持版本
- semver: 语义化版本号 (major.minor.patch)
- deprecation: 弃用，即将移除
- polyfill: 兼容性填充代码
- tree shaking: 未使用代码剔除
- SSR/CSR/SSG: 服务端渲染/客户端渲染/静态站点生成
- CI/CD: 持续集成/持续部署
- CVE: 通用漏洞披露
- CWE: 通用弱点枚举

**常见陷阱**：

- 使用已废弃的 API——检查文档中的 deprecated 标记
- 版本不兼容——标注最低版本要求
- 混淆同步/异步 API——明确标注 async/await
- 忽略安全漏洞——必须检查 CVE/NVD
- 使用社区代码片段未验证——必须理解后再使用
- 参考过时教程——检查发布日期和版本号

### 5.2 通用对话 (conversation)

**术语**：

- GDP: 国内生产总值
- CPI: 消费者物价指数
- PMI: 采购经理指数
- GDP per capita: 人均 GDP
- mortality rate: 死亡率
- incidence rate: 发病率

**常见陷阱**：

- 混淆名义 GDP 和购买力平价 GDP
- 使用过时数据未标注日期
- 将媒体报道当作官方数据
- 忽略数据口径差异
- 混淆相关性和因果性

### 5.3 小说创作 (novel)

**术语**：

- etymology: 词源学
- onomastics: 专有名词研究
- denotation: 字面意义
- connotation: 隐含意义
- archaism: 古语/废词
- neologism: 新造词
- toponym: 地名
- anthroponym: 人名

**常见陷阱**：

- 使用现代词汇描写古代场景——检查词源年代
- 人名不符合文化背景——查 Behind the Name
- 混淆相似人名的文化来源
- 地名拼写错误——查 GeoNames
- 历史细节错误——交叉验证

### 5.5 论文写作 (paper)

**术语**：

- h-index: 作者学术影响力指标
- i10-index: Google Scholar 定义的指标
- IF (Impact Factor): 期刊影响因子
- Q1/Q2/Q3/Q4: JCR 分区
- CCF-A/B/C: 中国计算机学会推荐列表
- SCI/SSCI/EI: 索引收录类型
- DOI: 数字对象唯一标识符
- ORCID: 开放研究者与贡献者身份识别码
- preprint: 预印本，未经同行评审
- peer review: 同行评审
- double-blind: 双盲评审
- open access: 开放获取

**常见陷阱**：

- 引用了已撤稿的论文——必须检查 Retraction Watch
- 混淆预印本和正式发表——arXiv 不等于已发表
- 自引过多——学术自引率应 <20%
- 忽略负面结果——只引用支持自己观点的论文
- 引用过时综述——检查是否有更新版本
- 伪造引用——所有引用必须能通过 CrossRef 或 Google Scholar 找到原文

### 5.6 智能体构建 (agent-builder)

**术语**：

- LLM: 大语言模型
- RAG: 检索增强生成
- ReAct: Reasoning + Acting 模式
- CoT: Chain-of-Thought 思维链
- tool calling: 工具调用
- function calling: 函数调用
- embedding: 向量嵌入
- vector store: 向量数据库
- agent: 具有自主行动能力的 AI
- multi-agent: 多智能体协作

**常见陷阱**：

- 使用已废弃的 API（如旧的 OpenAI function calling）
- 混淆不同模型的 API 接口
- 忽略 token 限制——注意上下文窗口大小
- 未处理 API 错误和重试
- 评测结果过时——模型更新快

## §6 Adaptive Prefix Templates (v4)

### 6.1 软件开发 (coding)

**Standard**：`[DAR] coding/security 优先源：CVE/NVD/Snyk/GitHub Advisory/官方文档。关键术语：CVE/CVSS/CWE/semver。指引：引用CVE编号、标注包版本、检查NVD安全公告。
要求：①事实附URL+日期 ②来源冲突时呈现分歧 ③数据标注年份，>12月降权。`

**Extended**：`[DAR Routing] Priority sources (T1): CVE (cve.mitre.org), NVD (nvd.nist.gov), Snyk, GitHub Security Advisories, official docs, PyPI/npm.
[DAR Scoring] Score = 0.40×Relevance + 0.30×Credibility + 0.25×Freshness + 0.05×Consensus. T1 weight ×1.0, T3 ×0.5, T4 ×0.2.
[DAR Terms] CVE, CVSS, CWE, breaking change, semver. Cite CVE numbers, specify versions.`

### 6.2 通用对话 (conversation)

**Standard**：`[DAR] 通用对话/事实核查 优先源：World Bank/IMF/WHO/CDC/政府门户/Snopes。关键术语：GDP(名义/PPP)/CPI/PMI/事实核查。指引：标注数据年份和来源、区分名义GDP与PPP、区分相关性与因果性。
要求：①事实附URL+日期 ②来源冲突时呈现分歧 ③数据标注年份，>12月降权。`

**Extended**：`[DAR 路由] 优先源（T1）：World Bank (data.worldbank.org)、IMF、WHO、CDC、政府门户。事实核查：Snopes、FactCheck.org。
[DAR 打分] Score = 0.45×相关性 + 0.25×可信度 + 0.10×时效 + 0.20×共识。
[DAR 术语] GDP（名义/PPP）、CPI、PMI。标注年份和来源，区分名义GDP和PPP。`

### 6.3 小说创作 (novel)

**Standard**：`[DAR] novel/creative writing 优先源：Merriam-Webster/OED/Etymonline/Behind the Name/GeoNames。关键术语：etymology/anachronism/neologism/denotation。指引：查词源确认时代准确性、查人名库确认年代适宜性。
要求：①事实附URL+日期 ②来源冲突时呈现分歧 ③语言用法标注时代背景。`

**Extended**：`[DAR Routing] Priority sources (T1): Merriam-Webster, OED, Cambridge Dictionary, Etymonline, Behind the Name, GeoNames, Purdue OWL.
[DAR Scoring] Score = 0.35×Relevance + 0.20×Credibility + 0.05×Freshness + 0.40×Consensus. Consensus weighted highest.
[DAR Terms] etymology, denotation, connotation, archaism, neologism, anachronism. Check word etymology for period accuracy.`

### 6.5 论文写作 (paper)

**Standard**：`[DAR] academic paper 优先源：Google Scholar/Semantic Scholar/arXiv/PubMed/CrossRef/Retraction Watch。关键术语：DOI/h-index/IF/peer review/Q1。指引：通过CrossRef验证DOI、检查Retraction Watch撤稿记录。
要求：①事实附URL+日期 ②来源冲突时呈现分歧 ③研究标注年份，>5年降权。`

**Extended**：`[DAR Routing] Priority sources (T1): Google Scholar, Semantic Scholar, arXiv, PubMed, DBLP, CrossRef (doi.org), Retraction Watch, ORCID.
[DAR Scoring] Score = 0.30×Relevance + 0.40×Credibility + 0.15×Freshness + 0.15×Consensus. Credibility weighted highest. Check Retraction Watch.
[DAR Terms] h-index, IF, Q1/Q2/Q3/Q4, DOI, ORCID, peer review. Verify DOIs via CrossRef.`

### 6.6 智能体构建 (agent-builder)

**Standard**：`[DAR] AI agent 优先源：Hugging Face/Papers with Code/LangChain/LMSYS Arena。关键术语：LLM/RAG/ReAct/Elo/tool calling。指引：标注框架版本、使用完整模型名、区分pass@k与pass^k。
要求：①事实附URL+日期 ②来源冲突时呈现分歧 ③benchmark 标注日期，>3月降权。`

**Extended**：`[DAR Routing] Priority sources (T1): Hugging Face, Papers with Code, LangChain Docs, OpenAI/Anthropic Docs, MCP Spec, Open LLM Leaderboard, LMSYS Chatbot Arena (lmarena.ai).
[DAR Scoring] Score = 0.35×Relevance + 0.30×Credibility + 0.25×Freshness + 0.10×Consensus. Freshness weighted high.
[DAR Terms] LLM, RAG, ReAct, CoT, tool calling, embedding, Elo. Specify framework versions, full model names.`
