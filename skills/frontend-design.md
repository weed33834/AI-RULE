---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 98adaa6f98486df4666888a6691e7607_c0cce340883611f18108525400287e28
    ReservedCode1: CL0bm9tSPAo8RdOzCA7zxgxQeaZbEtFrJxA2uQHv9Xm61Jy7icNrh69YC/nixFpmyUEk8t2BM+gGmHo/LT8+bfXqBzTlX3WNuykqEeds0exvI8U+J6QQK4f6j/nV/iDxZvdnHpX3xYedPpktW2LA6YMkhj5jTvTXqCWdFNJHM/AfU6O4SwB0vdGQ4BY=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 98adaa6f98486df4666888a6691e7607_c0cce340883611f18108525400287e28
    ReservedCode2: CL0bm9tSPAo8RdOzCA7zxgxQeaZbEtFrJxA2uQHv9Xm61Jy7icNrh69YC/nixFpmyUEk8t2BM+gGmHo/LT8+bfXqBzTlX3WNuykqEeds0exvI8U+J6QQK4f6j/nV/iDxZvdnHpX3xYedPpktW2LA6YMkhj5jTvTXqCWdFNJHM/AfU6O4SwB0vdGQ4BY=
---

# Frontend Design — 前端组件设计参考系统

> **触发条件**：需要设计 UI 组件、页面布局、CSS 样式时。
> **加载时机**：Architect 设计前端方案、Engineer 编写前端组件时。
> **优先级**：P2 — 确保 UI 质量、一致性、无障碍合规。

---

## 设计流程

```text
需求分析 → 参考研究 → 设计模式提取 → 代码生成 → 质量校验
```

---

## Step 1: 需求分析

### 输入契约

| 字段 | 必需 | 说明 |
|------|------|------|
| 组件类型 | ✅ | Button / Modal / Form / Table / Card / Navbar / Dashboard / Landing Page 等 |
| 交互模式 | ✅ | 点击、悬停、拖拽、表单提交、实时搜索、无限滚动等 |
| 设计风格 | 推荐 | Minimal / Material / Glassmorphism / Neumorphism / Brutalist / Corporate |
| 技术栈 | ✅ | React / Vue / Svelte + CSS 方案（Tailwind / SCSS / CSS-in-JS） |
| 响应式要求 | 推荐 | Mobile-first / Desktop-first / 断点定义 |
| 无障碍级别 | 推荐 | WCAG AA（默认） / WCAG AAA |

### 输出：需求摘要

```markdown
### 组件需求摘要
- **类型**: Modal Dialog
- **交互**: 点击触发 → 弹出 → 点击遮罩关闭 / ESC 关闭 / 确认按钮
- **风格**: Minimal, clean
- **技术栈**: React 18 + Tailwind CSS 3
- **响应式**: Mobile-first（< 640px 全屏，≥ 640px 居中 480px 宽）
- **无障碍**: WCAG AA（focus trap, aria-modal, ESC key）
```

---

## Step 2: 参考研究

### 2.1 搜索优秀同类 UI 仓库

按技术栈匹配的参考仓库：

| 技术栈 | 参考仓库 | 用途 |
|--------|----------|------|
| React | shadcn/ui | 组件设计模式、可访问性 |
| React | radix-ui/primitives | 无头组件基元 |
| React | ant-design | 企业级组件库参考 |
| React | nextui-org/nextui | 现代简约风格 |
| Vue | element-plus | Vue 3 组件库 |
| Vue | primevue | 丰富的组件集合 |
| 通用 CSS | tailwindlabs/tailwindui | 商业级 Tailwind 设计 |
| 通用 CSS | tailwindlabs/headlessui | 无头 UI 基元 |
| 通用 | chakra-ui | 无障碍优先 |

### 2.2 提取设计模式

从参考仓库中提取（不照抄）：

| 提取维度 | 关注点 |
|----------|--------|
| 布局结构 | 组件如何分块（header / body / footer） |
| 状态管理 | loading / empty / error / success 状态处理 |
| 动画过渡 | enter / exit 动画实现方式 |
| 无障碍 | aria 属性、键盘导航、focus management |
| 可组合性 | props 设计、slot / children 约定 |
| 主题系统 | CSS 变量、暗色模式切换 |

---

## Step 3: 设计模式提取

### 输出模板

```markdown
### 设计模式分析

**参考来源**: shadcn/ui Dialog (Radix UI)
**提取模式**:

1. **组合式架构**: 使用 compound components 模式
   - `Dialog.Root` → `Dialog.Trigger` → `Dialog.Content` → `Dialog.Close`
2. **Portal 渲染**: 使用 `ReactDOM.createPortal` 将内容挂载到 body
3. **Focus Trap**: 弹窗内 Tab 循环、打开时自动聚焦第一个可聚焦元素
4. **ESC 关闭**: 键盘事件监听
5. **动画**: CSS transition + data-state 属性驱动
```

---

## Step 4: 代码生成

### 生成要求

1. **完整可运行**：组件代码可直接放入项目运行（含必要的类型定义）
2. **状态覆盖**：至少包含 loading / empty / error / success 四种状态中的适用项
3. **响应式**：至少两组断点（mobile < 640px / desktop ≥ 640px）
4. **暗色模式**：使用 CSS 变量或 Tailwind `dark:` 前缀
5. **无障碍**：ARIA 属性完整、键盘可操作

### 代码输出格式

```typescript
// ============================================================
// Component: Modal
// Tech Stack: React 18 + Tailwind CSS 3
// Reference: shadcn/ui Dialog pattern (Radix UI primitives)
// ============================================================

import { useState, useEffect, useCallback } from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export function Modal({ isOpen, onClose, title, children }: ModalProps) {
  // ... implementation
}
```

### 安全红线（core/governance.md §1）

```text
❌ 禁止在组件中硬编码任何密钥、Token、密码
❌ 禁止在客户端代码中暴露数据库连接字符串
✅ 敏感配置一律通过环境变量或后端 API 获取
```

---

## Step 5: 质量校验

### 自检清单

| 检查项 | 标准 |
|--------|------|
| Tab 键可以完成所有交互 | Y/N |
| 屏幕阅读器可理解内容 | Y/N |
| 颜色对比度 ≥ 4.5:1（正文） | Y/N |
| 暗色模式下可读 | Y/N |
| 无 layout shift（CLS） | Y/N |
| < 640px 可用 | Y/N |
| 无硬编码密钥 | Y/N |
| 无 `any` 类型（TypeScript） | Y/N |

---

## 设计 Token 规范

生成的组件应使用以下 CSS 变量命名约定（方便主题切换）：

```css
:root {
  /* Colors */
  --color-primary: #3B82F6;
  --color-primary-hover: #2563EB;
  --color-surface: #FFFFFF;
  --color-surface-alt: #F9FAFB;
  --color-border: #E5E7EB;
  --color-text: #111827;
  --color-text-muted: #6B7280;

  /* Dark mode */
  --dark-color-surface: #1F2937;
  --dark-color-surface-alt: #111827;
  --dark-color-border: #374151;
  --dark-color-text: #F9FAFB;
  --dark-color-text-muted: #9CA3AF;

  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;

  /* Typography */
  --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  /* Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;

  /* Shadow */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
}
```

---

## 输出总结

每次完成前端组件设计后输出：

```markdown
## 组件设计交付

**组件**: `<Modal />`
**技术栈**: React 18 + Tailwind CSS 3
**参考**: shadcn/ui Dialog (Radix UI primitives)
**设计模式**: Compound Components + Portal + Focus Trap

**文件**:
- `src/components/Modal.tsx` — 组件实现
- `src/components/Modal.test.tsx` — 测试（含键盘和无障碍测试）

**检查结果**: 8/8 ✅
```

---

## 禁止行为

| 禁止 | 原因 |
|------|------|
| 不搜索参考仓库直接凭空设计 | 缺少设计模式依据，质量不可控 |
| 照抄参考仓库代码 | 需提取模式而非复制（尊重许可证 + 适配项目） |
| 跳过无障碍检查 | 违反 WCAG 标准 |
| 硬编码密钥在前端代码 | P0 安全违规 |
| 不生成测试 | 组件复杂时无测试保证行为正确 |

---

## 交叉引用

| 引用 | 内容 |
|------|------|
| `core/governance.md §1` | 安全与保密：不硬编码密钥 |
| `core/governance.md §2` | 真实性：设计依据来自真实参考仓库 |
| `core/governance.md §4` | 变更范围：只生成指定组件文件 |
| `skills/deep-search-first.md` | 搜索优先：不确定 API 时先搜索 |
| `skills/workflow-five-roles.md` | 五子角色：Architect 设计 → Engineer 实现 → Critic 审查 |
*（内容由AI生成，仅供参考）*
