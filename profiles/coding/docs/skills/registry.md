# 技能注册表 (Skills Registry)

> 经审核的 AI 开发工具白名单。**日常开发必须优先从此表选取工具。**
> 读取方式：AI 在选工具时先检索本表；无匹配项才走「受限自主搜索」协议（见 AGENTS.md §8 技能获取协议）。

## 0. 标准库优先

任何任务首先评估 Python 标准库是否可解：
`os` `sys` `pathlib` `re` `json` `csv` `sqlite3` `subprocess` `urllib` `http` `asyncio` `argparse` `logging` `tempfile` `zipfile` `hashlib` `collections` `itertools` `functools` `dataclasses` `typing` `decimal` `enum` `io`

**标准库能解决的不引入第三方依赖。**

## 0.5 优先厂商官方仓库（Trusted Vendor Orgs）

注册表（上方分类）无匹配时，**先在这些国内外大厂的官方仓库里搜**，再考虑其他高星仓库。
大厂仓库代码经审阅、Star 普遍数万、维护活跃，质量与安全性远优于野生高星仓库。

| 厂商 | 官方 GitHub Org | 代表仓库（示例） |
|------|----------------|------------------|
| 阿里巴巴 | https://github.com/alibaba · https://github.com/QwenLM | alibaba/nacos、alibaba/arthas、QwenLM/Qwen |
| 腾讯 | https://github.com/Tencent · https://github.com/Tencent-Hunyuan | Tencent/ncnn、Tencent/mmkv、Tencent-Hunyuan/Hunyuan |
| 字节跳动 | https://github.com/bytedance | bytedance/sonic、bytedance/lightseq |
| 百度 | https://github.com/baidu | baidu/amis、baidu/Paddle (PaddlePaddle) |
| 谷歌 | https://github.com/google | google/jax、google/mediapipe、google/flatbuffers |
| 微软 | https://github.com/microsoft | microsoft/playwright、microsoft/autogen、microsoft/semantic-kernel |
| Meta | https://github.com/facebookresearch · https://github.com/facebook | facebookresearch/llama、facebook/react |
| OpenAI | https://github.com/openai | openai/openai-python、openai/whisper、openai/gpt-oss |
| Anthropic | https://github.com/anthropics | anthropics/anthropic-sdk-python、anthropics/claude-code |
| Hugging Face | https://github.com/huggingface | huggingface/transformers、huggingface/diffusers |
| DeepSeek | https://github.com/deepseek-ai | deepseek-ai/DeepSeek-R1 |
| Mistral AI | https://github.com/mistralai | mistralai/mistral-src |
| AWS | https://github.com/aws | aws/aws-cli、aws/aws-cdk |
| NVIDIA | https://github.com/NVIDIA | NVIDIA/cuda-samples、NVIDIA/TensorRT |
| 苹果 | https://github.com/apple | apple/swift、apple/foundationdb |
| Netflix | https://github.com/Netflix | Netflix/conductor、Netflix/dispatch |
| Airbnb | https://github.com/airbnb | airbnb/lottie-android、airbnb/javascript |
| Uber | https://github.com/uber | uber-go/makisu |
| Stripe | https://github.com/stripe | stripe/stripe-python、stripe/stripe-node |
| Cloudflare | https://github.com/cloudflare | cloudflare/workers-sdk、cloudflare/wrangler |
| Databricks | https://github.com/databricks | databricks/databricks-cli |
| Redis | https://github.com/redis | redis/redis-py |
| MongoDB | https://github.com/mongodb | mongodb/mongo-python-driver |
| Elastic | https://github.com/elastic | elastic/elasticsearch-py |

## 1. 网页与 API

| 工具 | 安装 | 适用场景 |
|------|------|----------|
| httpx | `pip install httpx` | 异步 HTTP 客户端，优先于 requests |
| requests | `pip install requests` | 同步 HTTP（仅 httpx 不适用的老旧项目中） |
| playwright | `pip install playwright && playwright install` | 浏览器自动化，优先于 selenium |
| beautifulsoup4 | `pip install beautifulsoup4` | HTML 解析，配合 lxml 使用 |
| lxml | `pip install lxml` | 高性能 XML/HTML 解析 |
| scrapy | `pip install scrapy` | 大规模爬虫框架 |
| fastapi | `pip install fastapi` | REST API 开发 |
| uvicorn | `pip install uvicorn` | ASGI 服务器 |

## 2. 文档处理

| 工具 | 安装 | 适用场景 |
|------|------|----------|
| python-docx | `pip install python-docx` | Word .docx 读写 |
| openpyxl | `pip install openpyxl` | Excel .xlsx 读写 |
| pandas | `pip install pandas` | 表格数据/CSV/Excel |
| pypdf | `pip install pypdf` | PDF 读取、合并、拆分 |
| reportlab | `pip install reportlab` | PDF 生成 |
| python-pptx | `pip install python-pptx` | PowerPoint .pptx |
| markdown | `pip install markdown` | Markdown ↔ HTML 互转 |

## 3. 数据处理

| 工具 | 安装 | 适用场景 |
|------|------|----------|
| pandas | `pip install pandas` | 数据分析核心 |
| numpy | `pip install numpy` | 数值计算 |
| polars | `pip install polars` | 高性能 DataFrame，百万行以上优先 |
| pydantic | `pip install pydantic` | 数据校验、序列化 |
| pendulum | `pip install pendulum` | 日期时间处理，优先于 datetime |
| orjson | `pip install orjson` | 高速 JSON 序列化 |

## 4. Windows 系统操作

| 工具 | 安装 | 适用场景 |
|------|------|----------|
| psutil | `pip install psutil` | 进程管理、系统监控 |
| pywin32 | `pip install pywin32` | Windows API（COM、注册表等） |
| pyautogui | `pip install pyautogui` | GUI 自动化（鼠标/键盘模拟） |
| send2trash | `pip install send2trash` | 文件安全删除（送入回收站） |

## 5. Web 开发

| 工具 | 安装 | 适用场景 |
|------|------|----------|
| fastapi | `pip install fastapi` | 后端 API 框架 |
| jinja2 | `pip install jinja2` | HTML 模板引擎 |
| starlette | `pip install starlette` | 轻量 ASGI 框架 |
| python-multipart | `pip install python-multipart` | 文件上传 |

## 6. 测试

| 工具 | 安装 | 适用场景 |
|------|------|----------|
| pytest | `pip install pytest` | 测试框架（优先于 unittest） |
| pytest-asyncio | `pip install pytest-asyncio` | 异步测试 |
| pytest-cov | `pip install pytest-cov` | 测试覆盖率 |
| ruff | `pip install ruff` | Linter + Formatter（优先于 flake8/black） |
| mypy | `pip install mypy` | 静态类型检查 |

## 7. AI / 智能体开发

| 工具 | 安装 | 适用场景 |
|------|------|----------|
| openai | `pip install openai` | OpenAI API 客户端 |
| anthropic | `pip install anthropic` | Claude API 客户端 |
| httpx | `pip install httpx` | 自建 LLM API 调用（轻量替代方案） |

## 8. CLI 工具与终端

| 工具 | 安装 | 适用场景 |
|------|------|----------|
| typer | `pip install typer` | CLI 框架，优先于 argparse |
| rich | `pip install rich` | 终端美化输出（表格、进度条、颜色） |
| click | `pip install click` | CLI 框架（typer 底层依赖） |

## 9. 数据库

| 工具 | 安装 | 适用场景 |
|------|------|----------|
| sqlite3 | stdlib（内置） | 轻量本地数据库 |
| sqlalchemy | `pip install sqlalchemy` | ORM，多数据库兼容 |
| asyncpg | `pip install asyncpg` | PostgreSQL 异步驱动 |

## 10. 安全与加密

| 工具 | 安装 | 适用场景 |
|------|------|----------|
| hashlib | stdlib（内置） | 哈希计算 |
| secrets | stdlib（内置） | 安全随机数/令牌 |
| cryptography | `pip install cryptography` | 加密/解密、证书操作 |
| python-dotenv | `pip install python-dotenv` | 环境变量加载（.env 文件） |

## 11. DevOps / 运维

| 工具 | 安装 | 适用场景 |
|------|------|----------|
| docker | `pip install docker` | Docker 容器管理 API |
| ansible | `pip install ansible` | 自动化运维 |
| fabric | `pip install fabric` | SSH 远程执行 |

## 12. 参考与灵感仓库（Awesome 系列 & 知名 Agent/Skill 框架）

> 以下不是「直接安装的工具」，而是**学习 / 选型灵感来源**。需要落地某框架时，仍走 §8 技能获取协议的受限搜索协议评估，优先厂商官方仓库与高星可信源。

| 仓库 | Star（约） | 用途 |
|------|-----------|------|
| sindresorhus/awesome | 475k★ | 一切 awesome 清单的总入口 |
| vinta/awesome-python | 302k★ | Python 生态权威清单 |
| langchain-ai/langchain | 100k+★ | LLM 应用框架 |
| Significant-Gravitas/AutoGPT | 169k★ | 自主 Agent 早期代表 |
| n8n-io/n8n | 164k★ | 工作流自动化 |
| microsoft/autogen | 46k★ | 多 Agent 协作框架 |
| run-llama/llama_index | 42k★ | RAG / 数据框架 |
| crewAIInc/crewAI | 33k★ | 角色化多 Agent 框架 |
| All-Hands-AI/OpenHands | 30k★ | 自主编程 Agent |
| microsoft/semantic-kernel | 高星 | 微软 Agent SDK |
| anthropics/claude-code | 高星 | Claude Code 官方 |
| openai/openai-python | 高星 | OpenAI 官方 SDK |

---

## 受限自主搜索协议摘要

当注册表与优先厂商官方仓库都无匹配时，按以下约束在 GitHub 自主搜索（详见 AGENTS.md）：

| 条件 | 要求 |
|------|------|
| 搜索优先级 | ① 优先厂商官方仓库（见 §0.5）→ ② 其他 Star > 1000 的仓库 → ③ 更低 Star 作最后兜底 |
| 仓库质量 | 优先厂商官方仓库免审 Star 门槛；普通仓库须 Star > 1000 或近 3 个月有提交 |
| 用户确认 | 展示 URL / Star 数 / 简介，等待明确确认后才能下载 |
| 脚本安全 | **禁止**未经审查直接执行 `.ps1` `.py` `.sh` |
| 下载隔离 | 先放入 `/tmp` 或 `%TEMP%` 审查，确认无误后移入正式目录 |
| 包优先 | 仍优先检查 PyPI/npm 是否有同名包，而非直接克隆仓库 |
