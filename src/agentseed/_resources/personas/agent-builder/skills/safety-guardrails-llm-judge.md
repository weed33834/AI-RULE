---
# Skills 四元组（S = C, π, T, R；悉尼科大 + CSIRO Data61 2026 形式化）
applicable_when: C    # 用户要落地 LLM-as-Judge 双层审查或配置 NeMo Guardrails self_check_input/output
terminates_when: T    # 双层审查流程已接入、NeMo 自检模板已配置并通过测试
provides: π           # LLM-as-Judge 双层审查方法、NeMo self_check_input/output YAML 模板、最小集成 config.yml
interface: R          # 输入=智能体安全审查需求；输出=审查模型配置 + NeMo YAML 模板 + 集成配置
---

# LLM-as-Judge 双层审查与 NeMo 自检模板 (LLM-as-Judge & NeMo Self-Check)

> 本文件是 `safety-guardrails-core.md` 的子文件，专门覆盖 LLM-as-Judge 双层审查与 NeMo Guardrails 自检流程的可落地配置。

---

## LLM-as-Judge Dual-Layer Review (LLM-as-Judge 双层审查)

对应 AGENTS.md §8 新增规则。

使用一个廉价快速模型作为安全审查层：
1. 主模型输出后、交付用户前，审查层模型检查输入和输出
2. 审查内容：有害内容、提示注入、越权请求
3. 审查模型配置：高约束、低温度、仅做通过/拒绝判断
4. 推荐模型：Gemini Flash / GPT-4o-mini 等廉价快速模型
5. 拒绝时返回拒绝原因，不直接交付用户

---

## NeMo Guardrails Self-Check Templates (NeMo 自检模板)

NVIDIA NeMo Guardrails 提供了 `self_check_input` 和 `self_check_output` 两个自检流程，可在输入到达模型之前和输出交付用户之前进行拦截。以下是可直接复用的配置模板。

### self_check_input 模板（输入自检）

```yaml
# self_check_input — 在用户输入到达 LLM 之前执行
self_check_input:
  enabled: true

  # 1. 指令注入检测
  injection_detection:
    patterns:
      - regex: "忽略.*(以上|之前|所有).*(指令|规则|提示)"
        action: block
      - regex: "you are (now|a) "
        action: flag
      - regex: "(ignore|disregard).*(previous|above|all).*(instructions?|rules?)"
        action: block
      - regex: "(output|show|print).*(system|your).*(prompt|instructions?)"
        action: block
    on_block: "检测到潜在的指令注入，输入已被拦截。"
    on_flag: "输入包含可疑模式，已标记为降级处理。"

  # 2. 越狱检测（启发式）
  jailbreak_detection:
    methods:
      - length_per_perplexity       # 长度与困惑度比值
      - prefix_suffix_perplexity    # 前缀后缀困惑度
    threshold: default              # 使用 NeMo 默认阈值
    on_detect: degrade             # degrade（限制输出范围）| block

  # 3. PII 检测
  pii_detection:
    enabled: true
    patterns:
      - phone_number
      - email_address
      - id_card_number
      - bank_account
    on_detect: mask                # mask（脱敏）| block | flag

  # 4. 内容安全分类
  content_safety:
    model: nvidia-nemotron-content-safety  # 或 meta-llama-guard-3 / google-shieldgemma
    categories:
      - violence
      - hate_speech
      - sexual_content
      - self_harm
      - illegal_activity
    on_detect: block_and_log

  # 通过后的输出
  on_pass: allow
```

### self_check_output 模板（输出自检）

```yaml
# self_check_output — 在 LLM 输出交付用户之前执行
self_check_output:
  enabled: true

  # 1. 系统提示词泄露检测
  prompt_leak_detection:
    patterns:
      - regex: "(system|系统).*(prompt|提示|指令|规则)"
        action: flag
      - regex: "<language_mediation>"
        action: block
      - regex: "behavior_boundary|tier_[123]"
        action: block
    on_block: "检测到系统提示词泄露，输出已拦截。"
    on_flag: "输出包含可疑的系统配置信息，已标记为脱敏处理。"

  # 2. 敏感数据泄露检测
  sensitive_data_detection:
    patterns:
      - api_key
      - password
      - token
      - connection_string
    on_detect: mask                # 脱敏后输出

  # 3. 未授权高风险操作检测
  unauthorized_action_detection:
    check_for:
      - git_push_without_confirmation
      - file_deletion_without_confirmation
      - email_send_without_confirmation
      - payment_without_confirmation
      - config_modification_without_confirmation
    on_detect: block               # 拦截输出，返回确认请求

  # 4. 内容安全分类（与输入侧一致）
  content_safety:
    model: nvidia-nemotron-content-safety
    categories:
      - violence
      - hate_speech
      - sexual_content
      - self_harm
      - illegal_activity
    on_detect: block_and_log

  # 通过后的输出
  on_pass: allow
```

### 集成方式

NeMo Guardrails 通过 `config.yml` 声明护栏流程。以下是最小集成配置：

```yaml
# config.yml — NeMo Guardrails 最小集成
rails:
  input:
    flows:
      - self check input
  output:
    flows:
      - self check output
  dialog:
    single_call:
      enabled: true
```

> **注意**：NeMo Guardrails 的具体 API 和配置格式可能随版本更新而变化。以上模板基于 NeMo Guardrails 0.x 系列的公开文档。生产部署前请查阅 [NeMo Guardrails 官方文档](https://github.com/NVIDIA/NeMo-Guardrails) 确认最新配置语法。
