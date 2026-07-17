# fine-tuning-guide.md — 微调 vs 提示词工程决策指南 / Fine-tuning vs Prompt Engineering Decision Guide

---

## 1. 一句话描述 / One-sentence Description

**中文：** 在"改提示词"成本极低且往往足够的前提下，通过一套基于任务表现缺口与能力边界的决策树，判断何时该继续优化提示词、何时该转向微调（全量/LoRA/QLoRA/RLHF/DPO），并给出数据准备、成本估算与评估的完整落地路径。

**English:** Given that prompt engineering is cheap and often sufficient, this guide uses a decision tree based on performance gaps and capability boundaries to determine when to keep improving prompts versus when to invest in fine-tuning (full / LoRA / QLoRA / RLHF / DPO), with a complete path covering data preparation, cost estimation, and evaluation.

---

## 2. 适用场景 / Applicable Scenarios

| 场景 / Scenario | 说明 / Description |
|---|---|
| 提示词已达瓶颈 / Prompt hit ceiling | 系统提示词与 few-shot 已反复迭代，但特定任务的表现仍不达标 |
| 风格/格式一致性 / Style & format consistency | 模型输出风格、语气、格式难以仅靠提示词稳定约束（如品牌口吻、严格 JSON） |
| 领域知识注入 / Domain knowledge injection | 需要让模型内化大量领域术语/规则，RAG 检索成本高或时延不可接受 |
| 对齐人类偏好 / Align to human preference | 需要让输出更符合人类偏好排序（更安全、更有用、更简洁），从偏好数据学习 |
| 降低推理成本 / Inference cost reduction | 将大模型能力"蒸馏"到更小的开源模型上自托管，替代昂贵的 API 调用 |

**不适用 / Not applicable：** 任务可被一条清晰的提示词 + few-shot 解决；事实性知识可通过 RAG 动态注入；调用频率低、API 成本不敏感——此时微调属于过度工程。

---

## 3. 核心方法论 / Core Methodology

### 3.1 优先级原则：先穷尽提示词，再考虑微调

提示词迭代成本通常以"分钟/小时"计，而微调以"天/周"计。遵循阶梯式投入：

```
zero-shot prompt → few-shot prompt → RAG / 工具增强 → 提示词压缩与结构化优化
    →（仍不满足）→ 微调
```

只有当前四步均已穷尽且仍有明确、可量化的表现缺口时，才进入微调评估。

### 3.2 微调方法对比 / Fine-tuning Methods Comparison

| 方法 / Method | 训练参数量 / Trainable Params | 显存需求 / VRAM | 核心思想 / Core Idea | 适用场景 / Best For |
|---|---|---|---|---|
| **全量微调 / Full FT** | 100% | 最高（需多卡） | 更新模型全部权重 | 领域迁移大、有充足数据与算力 |
| **LoRA** | <1%（低秩矩阵 A·B） | 中（基模 fp16） | 冻结基模，仅训练注入的低秩适配矩阵；推理时可合并 | 通用首选，性价比最高 |
| **QLoRA** | <1%（4-bit 基模 + LoRA） | 低（单卡可跑大模型） | 基模 4-bit NF4 量化 + LoRA 适配器 + 分页优化器 | 显存有限、想在大模型上微调 |
| **RLHF** | 多阶段（SFT + RM + PPO） | 高 | 监督微调 → 训练奖励模型 → PPO 强化学习对齐 | 需要复杂的人类偏好对齐，有标注预算 |
| **DPO** | 仅策略模型（<1% with LoRA） | 中 | 直接从偏好对 (chosen, rejected) 优化，跳过奖励模型与 PPO | 想做偏好对齐但嫌 RLHF 太复杂 |

> **关键事实：** LoRA 原论文为 Hu et al. (Microsoft, 2021)；QLoRA 原论文为 Dettmers et al. (2023)，引入 NF4 量化、双重量化与分页优化器；DPO 原论文为 Rafailov et al. (2023)，证明可省去奖励模型直接从偏好数据优化。RLHF 是 InstructGPT/ChatGPT 早期采用的三阶段对齐范式（SFT → RM → PPO）。

### 3.3 推荐工具 / Recommended Tools

| 工具 / Tool | 维护方 / Maintainer | 定位 / Positioning | 核心优势 / Key Strength | 许可证 / License |
|---|---|---|---|---|
| **Hugging Face PEFT** | Hugging Face | 参数高效微调库 | 支持 LoRA / QLoRA / Prefix Tuning / Prompt Tuning / AdaLoRA / IA³；与 `transformers` Trainer 无缝集成；生态最广 | Apache-2.0 |
| **Unsloth** | Unsloth AI (Daniel Han) | 极致效率微调 | 自研 CUDA/Triton kernel，LoRA/QLoRA 训练速度提升约 2×、显存降低约 50–70%；支持单卡训练大模型；上手简单 | Apache-2.0（部分模型有额外限制，以仓库为准） |
| **Axolotl** | OpenAccess AI Collective | 高度可配置微调工具链 | YAML 配置驱动；支持 LoRA/QLoRA/全量/RLHF/DPO/ORPO 等多种方法；多卡 FSDP/DeepSpeed；配置灵活、可复现 | Apache-2.0 |

> **选型速查：** 个人开发者/单卡优先试 Unsloth；需要深度自定义与多方法实验选 Axolotl；需要在自有训练管线中嵌入 PEFT 能力用 Hugging Face PEFT。三者可组合使用（如 Axolotl 底层也调用 PEFT）。

### 3.4 数据准备要求 / Data Preparation Requirements

| 维度 / Dimension | 要求 / Requirement |
|---|---|
| **最少样本量** | 监督微调（SFT）建议 **500–1000 条**高质量样本起步；效果稳定通常需数千至数万条。DPO 需要偏好对（prompt + chosen + rejected），数量级类似 |
| **质量 > 数量** | 1000 条人工精标的样本往往优于 10000 条噪声样本；低质量数据会"教会"模型错误模式 |
| **多样性** | 覆盖真实输入分布，避免分布偏窄导致过拟合到窄场景 |
| **格式一致性** | 统一 instruction/input/output 结构（如 Alpaca 格式、ChatML 对话格式），与推理时格式严格对齐 |
| **数据清洗** | 去重、去噪、长度过滤、去除敏感信息；建议保留 5–10% 作为留出评估集 |
| **偏好数据（DPO/RLHF）** | chosen 与 rejected 应针对同一 prompt 构成对比，差异需有明确的偏好信号（非随机标注） |

---

## 4. 决策树 / 流程图 — Decision Tree

```
任务表现不达标 / Performance gap identified
   │
   ▼
Q1: 是否已穷尽提示词优化？(zero-shot → few-shot → 结构化 → 压缩)
   ├─ 否 ──► 继续提示词优化，回到迭代
   └─ 是 ──► Q2
   │
   ▼
Q2: 缺口类型是什么？
   ├─ 事实性知识缺失 ──► 优先 RAG / 工具增强（知识应外挂而非内化）
   ├─ 推理能力不足 ──► 换更强模型或加 ReAct/思维链；微调难补推理短板
   ├─ 风格/格式/口吻不稳定 ──► Q3（微调候选）
   └─ 领域术语/规则需内化 ──► Q3（微调候选）
   │
   ▼
Q3: 是否有 ≥500 条高质量标注数据（或可获取）？
   ├─ 否 ──► 先做数据采集/合成/人工标注，数据未就绪前不微调
   └─ 是 ──► Q4
   │
   ▼
Q4: 目标是"对齐人类偏好"还是"指令/风格学习"？
   ├─ 指令/风格学习 ──► Q5（SFT 路线）
   └─ 对齐人类偏好 ──► 有偏好对数据？
        ├─ 是 ──► DPO（比 RLHF 简单，先试 DPO）
        └─ 否 ──► RLHF（需先标注偏好、训练奖励模型；成本高）
   │
   ▼
Q5(SFT): 显存预算如何？
   ├─ 单卡 / 消费级 GPU（如 RTX 3090/4090 24GB）──► QLoRA（Unsloth）
   ├─ 单卡 A100/H100 80GB ──► LoRA 或 QLoRA
   └─ 多卡集群 ──► LoRA（Axolotl + FSDP/DeepSpeed）；数据极充足可考虑全量微调
   │
   ▼
执行微调 → 评估（见第 6 节）→ 是否达标？
   ├─ 是 ──► 合并适配器 → 灰度上线 → 监控
   └─ 否 ──► 回到数据/方法/超参排查（数据质量 > 超参 > 方法）
```

---

## 5. 模板示例 — Template Example

### 5.1 SFT 数据格式（Alpaca 风格）

```jsonl
{"instruction": "将以下句子改为礼貌的客服口吻", "input": "你这个退款太慢了", "output": "非常抱歉给您带来不便，您的退款我们正在加急处理，预计 1-3 个工作日到账，感谢您的耐心等待。"}
{"instruction": "判断用户意图并归类", "input": "我想取消昨天下的单", "output": "{\"intent\": \"cancel_order\", \"confidence\": 0.95}"}
```

### 5.2 DPO 偏好数据格式

```jsonl
{"prompt": "解释什么是量子纠缠", "chosen": "量子纠缠是指两个或多个粒子……（准确、通俗、带类比的解释）", "rejected": "量子纠缠就是魔法，科学家也不懂。（错误且敷衍）"}
```

### 5.3 Axolotl 配置示例（QLoRA）

```yaml
# axolotl_config.yaml — QLoRA 微调配置示例（概念示意，字段以 Axolotl 官方文档为准）
base_model: meta-llama/Llama-3.1-8B-Instruct
model_type: LlamaForCausalLM
tokenizer_type: AutoTokenizer

# 微调方法
adapter: qlora
lora_r: 16
lora_alpha: 32
lora_dropout: 0.05
lora_target_modules:
  - q_proj
  - v_proj
  - k_proj
  - o_proj

# 数据
datasets:
  - path: ./data/sft_train.jsonl
    type: alpaca

# 量化（QLoRA）
load_in_4bit: true
bnb_4bit_compute_dtype: bfloat16
bnb_4bit_quant_type: nf4
bnb_4bit_use_double_quant: true

# 训练超参
sequence_len: 2048
micro_batch_size: 2
gradient_accumulation_steps: 4
num_epochs: 3
learning_rate: 2e-4
warmup_steps: 50
optimizer: paged_adamw_8bit

# 输出
output_dir: ./outputs/llama31-8b-qlora
save_steps: 200
eval_steps: 200
```

### 5.4 Unsloth 训练片段（概念示意）

```python
# unsloth_train.py — 概念示意，API 以 Unsloth 官方文档为准
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-3-8b-bnb-4bit",
    max_seq_length=2048,
    load_in_4bit=True,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha=32,
    lora_dropout=0.05,
)

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,            # 已格式化的 datasets.Dataset
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        num_train_epochs=3,
        learning_rate=2e-4,
        output_dir="outputs",
    ),
)
trainer.train()
model.save_pretrained("outputs/llama3-lora")
```

---

## 6. 评估方法 / Evaluation Methods

| 评估方式 / Method | 说明 / Description |
|---|---|
| **留出集 loss** | 在未参与训练的留出集上监控 loss，判断是否过拟合 |
| **任务准确率** | 针对目标任务构造评测集，计算准确率/F1/通过率 |
| **公开基准** | 用 MMLU（综合知识）、HumanEval/MBPP（代码）、GSM8K（数学）等评测能力保持情况（避免灾难性遗忘） |
| **LLM-as-Judge** | 用更强的模型按 rubric 评分，对比微调前后；需校准裁判偏差 |
| **人工评估** | 抽样盲评，对比基线与微调版本，最可信但成本高 |
| **回归测试** | 复用智能体测试用例集（见 `agent-testing-automation.md`），确认未引入退化 |
| **A/B 测试** | 灰度分流对比线上效果与用户反馈 |

---

## 7. 常见陷阱 / Common Pitfalls

1. **数据不足就上微调 / Fine-tuning with too little data**
   - 危害：少于约 500 条样本极易过拟合，泛化差。
   - 纠正：数据未达门槛先做数据采集/合成；优先补 few-shot。

2. **格式训练/推理不一致 / Train-inference format mismatch**
   - 危害：训练用 Alpaca 格式、推理用 ChatML，模型表现骤降。
   - 纠正：训练数据格式必须与推理时 prompt 模板严格对齐。

3. **灾难性遗忘 / Catastrophic forgetting**
   - 危害：微调后模型在通用能力上退化（MMLU 掉分）。
   - 纠正：混入通用数据；降低学习率与 epoch；用 LoRA（影响小于全量）；用公开基准做回归。

4. **用微调补推理能力 / Fine-tuning to fix reasoning**
   - 危害：微调擅长风格/格式/领域术语，难补纯推理短板，投入产出比差。
   - 纠正：推理不足优先换更强模型或加 ReAct/思维链。

5. **忽视评估导致无法判断收益 / No eval means no signal**
   - 危害：没有基线对比，无法证明微调有效。
   - 纠正：微调前先冻结基线评测集，微调后严格对比。

6. **把 RLHF 当默认选项 / Defaulting to RLHF**
   - 危害：RLHF 三阶段成本高、调参难、不稳定。
   - 纠正：偏好对齐优先试 DPO，简单且稳定；确有需要再上 RLHF。

7. **QLoRA 量化未校准精度损失 / Ignoring quantization quality loss**
   - 危害：4-bit 量化对部分模型/任务有精度损失。
   - 纠正：QLoRA 后需评估精度是否可接受；敏感任务考虑 LoRA（fp16 基模）。

---

## 8. 检查清单 / Checklist

微调启动前逐项确认 / Confirm before starting：

- [ ] 提示词优化（zero-shot → few-shot → 结构化 → 压缩）已穷尽 / prompt optimization exhausted
- [ ] 已明确表现缺口类型，确认微调是正确手段（非知识检索/非纯推理短板） / gap type confirmed, fine-tuning is right lever
- [ ] 高质量训练数据 ≥ 500–1000 条，已去重去噪脱敏 / high-quality data ≥ 500–1000, cleaned
- [ ] 训练数据格式与推理时 prompt 模板严格一致 / train-inference format aligned
- [ ] 已选对方法（SFT 用 LoRA/QLoRA；偏好对齐优先 DPO） / method selected correctly
- [ ] 已选对工具（单卡 Unsloth / 多方法 Axolotl / 嵌入管线 PEFT） / tool selected
- [ ] 已划分留出评估集 / held-out eval set prepared
- [ ] 已冻结基线评测结果便于对比 / baseline eval frozen for comparison
- [ ] 训练后已跑公开基准确认无灾难性遗忘 / public benchmark run, no catastrophic forgetting
- [ ] 已跑回归测试集确认无退化 / regression suite passed
- [ ] 适配器已合并并可推理 / adapter merged and inference-ready
- [ ] 已制定灰度上线与监控方案 / rollout and monitoring plan in place

---

## 真实性要求 / Authenticity Requirements

- 本文档所述方法（LoRA / QLoRA / RLHF / DPO）均源自公开发表的学术论文，原理描述忠实于原论文。论文作者与发表年份已标注，使用前可检索原文核实。
- 推荐工具（Hugging Face PEFT、Unsloth、Axolotl）均为真实存在的开源项目，其维护方、定位与许可证基于公开仓库信息核实。**具体 API 字段、配置项、许可证条款可能随版本演进**——动手前务必以各项目 GitHub 仓库根目录的 LICENSE 文件与官方文档为准。
- 数据量建议（≥500–1000 条）为业界广泛引用的经验门槛，非绝对值；实际需求因任务与模型而异，应以留出集表现为准。
- 配置与代码示例为**概念示意**，标注了"以官方文档为准"；实际使用前需对照目标工具的当前版本文档校准字段名与参数。
- 任何标注"需验证"的信息，使用前必须通过官方文档二次确认，不得直接用于生产决策。
