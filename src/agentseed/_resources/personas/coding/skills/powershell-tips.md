# PowerShell 语法要点 (PowerShell Tips)

> Windows 下 AI 跑终端命令时，优先用 PowerShell cmdlet；写脚本注意与 bash 的差异。

## 与 bash 的关键差异

| 场景 | bash | PowerShell |
|------|------|------------|
| 链式条件 | `A && B` | `A; if ($?) { B }` |
| 管道 | 传文本 | 传**对象**（用 `\| Select-Object` 取字段） |
| 变量 | `$var`（无前缀） | `$var`（有前缀 `$`） |
| 字符串插值 | `"$var"` | `"$var"` 或 `"$($obj.Prop)"` |
| 转义符 | `\` | **反引号** `` ` `` |
| 多行字符串 | heredoc `<<EOF` | **单引号 here-string** `@'...'@`（结束符必须顶格，位于行首） |

## 常用 cmdlet

- 列目录：`Get-ChildItem`（别名 `ls` / `dir`）
- 读文件：`Get-Content`（别名 `cat`）
- 写文件：优先用专用工具（Read / Edit / Write），脚本里用 `Set-Content`
- 创建目录：`New-Item -ItemType Directory -Path <path>`
- 删文件：`Remove-Item -Force -Confirm:$false`（危险操作前先想清楚；优先 `send2trash`）

## 调用原生 exe

路径含空格用调用运算符 `&`：

```powershell
& "C:\Program Files\App\app.exe" arg1 arg2
```

## 环境变量

- 读：`$env:NAME`
- 写（当前进程）：`$env:NAME = "value"`
- 不要写死密钥；敏感值从环境变量或 `.env` 注入。

## 注意事项

- 优先用 cmdlet 而非拼 shell 字符串；避免 `Invoke-Expression`（易注入）。
- 不写 `.ps1` 脚本让用户无脑运行；下载的脚本先隔离审查（见 `AGENTS.md` § Engineering Hygiene）。
