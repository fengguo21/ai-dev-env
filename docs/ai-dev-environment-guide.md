# AI Dev Environment v1.2 完整使用指南

本文介绍本项目提供的整套 macOS AI 开发环境，包括 Ghostty、tmux、Codex CLI、Claude Code、Git Worktree、LazyGit、Delta、GitHub CLI、Docker Compose，以及配套的安装、检查和恢复命令。

Git 工具的完整按键和命令说明另见 [LazyGit、Git Diff 与 GitHub CLI 使用指南](git-tools-guide.md)。

需要快速复制和查询命令时，使用 [AI Dev Environment 命令查询手册](command-reference.md)。v1.2 的设计依据见 [工作流调研与最佳实践](research-best-practices.md)。

## 1. 环境组成

整套环境的关系如下：

```text
macOS
└── Ghostty：终端窗口、字体、主题、剪贴板和滚动历史
    └── tmux：持久会话、窗口、分屏和布局恢复
        └── dev：按项目目录创建与复用工作区
            ├── codex：左右两个 Codex
            ├── codex-claude：Codex + 普通模式 Claude
            ├── backend-frontend：后端 + 前端 Shell
            ├── services：Docker Compose 和其他服务
            ├── test：测试、Lint 和构建检查
            └── git：LazyGit、Delta 和 GitHub CLI
```

| 组件 | 用途 | 是否由 `install.sh` 安装或配置 |
|---|---|---|
| Ghostty | macOS 终端模拟器 | 是 |
| JetBrains Mono Nerd Font | 终端等宽字体与图标字符 | 是 |
| tmux | 持久会话、窗口和分屏 | 是 |
| TPM 与 tmux 插件 | 布局保存、自动恢复和复制增强 | 是 |
| Git | 版本管理与 Worktree | 是 |
| LazyGit | Git 终端交互界面 | 是 |
| Delta | 美化 Git Diff | 是 |
| GitHub CLI `gh` | PR、CI、Issue 和仓库管理 | 是 |
| `dev` | 创建项目 tmux 工作区 | 是 |
| `newtask` | 创建并行 Git Worktree | 是 |
| `task` | 新建、切换、查看和清理任务 | 是 |
| `ai-dev-doctor` | 检查环境状态 | 是 |
| Codex CLI | AI 编码终端客户端 | 否，需要单独安装 |
| Claude Code | AI 编码终端客户端 | 否，需要单独安装 |
| Docker Desktop / Compose | 启动项目依赖服务 | 否，需要单独安装 |
| Python、uv、Node、pnpm 等 | 项目运行时与包管理器 | 否，按项目需要安装 |

### 阅读命令时的约定

为了方便记忆，本文按下面的方式解释命令：

- **命令（command）**：第一个单词，例如 `git`、`tmux`、`gh`。
- **子命令（subcommand）**：说明要做什么，例如 `gh pr create` 中的 `pr` 和 `create`。
- **长参数（long option）**：以 `--` 开头，名称通常就是含义，例如 `--version` 表示“显示版本”。
- **短参数（short option）**：以 `-` 开头，例如 `-v`。同一个字母在不同命令中可能含义不同。
- **占位符（placeholder）**：`<project>`、`<run-id>` 等尖括号内容需要替换成真实值，输入命令时不要保留尖括号。
- **环境变量（environment variable）**：`$HOME`、`$PATH` 等以 `$` 开头的名称由 Shell 展开成实际值。

例如：

```bash
git push -u origin HEAD
```

可以拆成：

| 部分 | 全称或含义 | 记忆方法 |
|---|---|---|
| `git` | Git 版本管理工具 | 所有 Git 操作的入口 |
| `push` | 推送 | 把本地提交“推”到远程 |
| `-u` | `--set-upstream` | `u` 记作 **upstream**，建立上游跟踪关系 |
| `origin` | 默认远程仓库名称 | 代码最初的远程“来源” |
| `HEAD` | 当前检出的提交位置 | 想成你当前站立位置的“头部指针” |

> 注意：并非每个短参数都有官方英文全称。本文优先写官方长参数；如果没有，就明确标注为“助记含义”，不会把口诀当作正式定义。

## 2. 安装、升级与检查

### 安装或升级

在本工具的仓库根目录运行：

```bash
./install.sh
```

已装好依赖时可以使用 `./install.sh --skip-deps --no-reload`，只更新配置与辅助命令，并保留正在运行的 tmux 会话。完整安装参数和升级说明见 [README](../README.md) 与 `./install.sh --help`。

升级会检查受管理文件是否被手动修改；有改动时默认停止覆盖。可以先把个人设置移到 local 配置，或检查差异后使用 `--replace-modified`，备份并替换这些文件。

安装脚本会：

1. 检查 macOS 和 Homebrew。
2. 安装缺少的 Ghostty、tmux、Git、LazyGit、Delta 和 `gh`。
3. 安装 JetBrains Mono Nerd Font。
4. 备份已有 Ghostty、tmux、Shell 和辅助命令配置。
5. 安装 Ghostty 与 tmux 配置。
6. 将 `dev`、`newtask`、`task` 和 `ai-dev-doctor` 安装到 `~/.local/bin`，共享辅助文件安装到 `~/.local/share/ai-dev-env/`。
7. 安装 TPM、tmux-resurrect、tmux-continuum 和 tmux-yank。
8. 验证 Ghostty 和 tmux 配置。

安装结束后，打开新的 Ghostty 窗口，或者重新加载 Shell：

```bash
source ~/.zshrc
```

### 检查环境

运行完整检查：

```bash
ai-dev-doctor
```

它会检查：

- Ghostty、tmux 和 Git 是否可用；
- LazyGit、Delta 和 `gh` 是否安装；
- Ghostty 配置、字体和主题是否有效；
- tmux 配置和插件是否正常；
- `dev`、`newtask` 与 `task` 是否位于 `PATH`。

查看常用工具版本：

```bash
ghostty +version
tmux -V
git --version
lazygit --version
delta --version
gh --version
codex --version
claude --version
docker --version
docker compose version
```

tmux 使用大写 `-V` 表示 **Version（版本）**；其余示例使用可读性更高的 `--version`。

### 配置和备份位置

| 内容 | 安装位置 |
|---|---|
| Ghostty 配置 | `~/.config/ghostty/config` |
| tmux 配置 | `~/.tmux.conf` |
| tmux 个人覆盖配置 | `~/.tmux.local.conf` |
| Ghostty 个人覆盖配置 | `~/.config/ghostty/config.local` |
| 项目启动配置 | `<项目>/.ai-dev.conf` |
| 辅助命令 | `~/.local/bin/` |
| TPM 与插件 | `~/.tmux/plugins/` |
| 安装状态和备份 | `~/.local/state/ai-dev-env/` |

主题、字号、按键等个人调整放在对应的 local 文件中，避免和受管理的基础配置混在一起。项目配置格式见 [模板](../config/project.example.conf)。

每次安装或升级前的配置会备份到：

```text
~/.local/state/ai-dev-env/backups/<时间戳>/
```

## 3. Ghostty

Ghostty 是整套环境最外层的终端应用。它负责显示 Shell 和 tmux，但不负责项目会话管理；持久会话和窗口布局由 tmux 管理。

### 当前视觉与交互配置

- 主题：`TokyoNight Night`；
- 字体：`JetBrainsMono Nerd Font Mono`，15 pt；
- 关闭字体连字，使 Diff、日志和运算符保持字面显示；
- 不透明背景，降低长时间阅读疲劳；
- 50 MB 滚动历史；
- 块状、不闪烁光标；
- 选中文字时自动复制；
- 写入剪贴板允许，读取剪贴板需要确认；
- 启用粘贴保护；
- 关闭仍有运行进程的窗口时要求确认；
- 左 Option 作为 `Alt`，右 Option 保留 macOS 默认行为；
- SSH 时尽可能传播环境与 Ghostty terminfo，保留 True Color。

本项目没有覆盖 Ghostty 的全局快捷键，因此窗口、标签页和原生分屏仍使用 Ghostty/macOS 自身的快捷键。项目工作区优先使用 tmux 分屏，便于保存和恢复布局。

### 验证 Ghostty

检查配置语法：

```bash
ghostty +validate-config --config-file="$HOME/.config/ghostty/config"
```

其中 `validate` 表示“验证”，`config` 是 **configuration（配置）** 的缩写，`--config-file` 表示指定配置文件。

确认字体存在：

```bash
ghostty +list-fonts | grep -F "JetBrainsMono Nerd Font Mono"
```

这里 `|` 是 Pipe（管道），把左侧输出交给右侧；`grep` 名称源自 **Global Regular Expression Print**，用于筛选文本；`-F` 是 `--fixed-strings`，表示按固定字符串而不是正则表达式匹配。

确认主题存在：

```bash
ghostty +list-themes | grep -F "TokyoNight Night"
```

Ghostty 命令里的 `+version`、`+validate-config`、`+list-fonts` 和 `+list-themes` 都是 Ghostty Action（动作），前导 `+` 不是普通的单字母短参数。修改配置后，最稳妥的生效方式是打开一个新的 Ghostty 窗口。

## 4. tmux

tmux 用三个层级组织终端：

```text
Session（一个项目工作区）
└── Window（codex、test、git 等工作窗口）
    └── Pane（一个窗口中的分屏）
```

关闭 Ghostty 或从 tmux Detach 后，tmux 中的进程通常仍会继续运行。重新 Attach 即可回到原来的终端状态。

### Prefix 的使用方式

默认 tmux Prefix 已从 `Ctrl+b` 修改为 `Ctrl+a`。

例如 `Ctrl+a c` 的含义是：

1. 按下 `Ctrl+a`；
2. 松开；
3. 再按 `c`。

### 窗口与分屏快捷键

| 操作 | 快捷键 |
|---|---|
| 新建窗口 | `Ctrl+a c` |
| 上一个/下一个窗口 | `Ctrl+a p` / `Ctrl+a n` |
| 按编号切换窗口 | `Ctrl+a 1`～`Ctrl+a 9` |
| 查看窗口列表 | `Ctrl+a w` |
| 选择并打开任务 | `Ctrl+a t` |
| 浏览项目会话树 | `Ctrl+a s` |
| 查看任务命令帮助 | `Ctrl+a ?` |
| 左右分屏 | `Ctrl+a \|` |
| 上下分屏 | `Ctrl+a -` |
| 切换 Pane | `Ctrl+a h/j/k/l` |
| 调整 Pane 大小 | `Ctrl+a H/J/K/L` |
| 最大化/还原当前 Pane | `Ctrl+a z` |
| 显示 Pane 编号 | `Ctrl+a q` |
| 关闭当前 Pane | 在 Pane 中运行 `exit` |
| Detach 当前 Session | `Ctrl+a d` |
| 重新加载配置 | `Ctrl+a r` |

大写 `H/J/K/L` 支持连续重复，每次调整 5 个终端单元格：左右方向改变列数，上下方向改变行数。

这些按键是快捷键助记，不是严格的参数全称：

| 按键 | 英文联想 | 记忆方法 |
|---|---|---|
| `c` | create | 创建新 Window |
| `p` / `n` | previous / next | 上一个/下一个 Window |
| `w` | windows | 打开 Window 列表 |
| `h/j/k/l` | Vi navigation | 左/下/上/右；沿用 Vi 的方向键布局 |
| `z` | zoom | 最大化当前 Pane，再按一次还原 |
| `q` | query（助记） | 显示 Pane 编号供选择 |
| `d` | detach | 离开 Session，但不结束其中进程 |
| `r` | reload | 重新加载配置 |

新窗口和新 Pane 会继承当前 Pane 的工作目录，因此在 Worktree 中创建分屏时不会跳回主仓库。

### Copy Mode

进入复制模式：

```text
Ctrl+a [
```

Copy Mode 使用 Vi 按键：

| 按键 | 功能 |
|---|---|
| `h/j/k/l` | 移动光标 |
| `v` | 开始选择 |
| `Ctrl+v` | 矩形选择 |
| `y` | 复制并退出 Copy Mode |
| 鼠标拖选 | 复制并退出 Copy Mode |

### Session 命令

在 tmux 外查看会话：

```bash
tmux list-sessions
```

Attach 到指定会话：

```bash
tmux attach-session -t <session-name>
```

`attach` 表示“连接回去”，`-t` 是 `target（目标）` 的助记，后面填写目标 Session 名称。

重命名当前会话：

```text
Ctrl+a $
```

结束指定会话：

```bash
tmux kill-session -t <session-name>
```

`kill` 表示结束，`-t` 仍然表示目标 Session。

`kill-session` 会结束会话中的所有进程。执行前先使用 `tmux list-sessions` 确认名称。

### tmux 插件

| 插件 | 功能 |
|---|---|
| TPM | Tmux Plugin Manager，管理 tmux 插件 |
| tmux-resurrect | `resurrect` 意为“复活”，保存和恢复 Session、Window、Pane 与目录 |
| tmux-continuum | `continuum` 意为“连续体”，每 15 分钟自动保存并在启动时尝试恢复 |
| tmux-yank | `yank` 是 Vi 中的“复制”，增强 tmux 与系统剪贴板的复制 |

常用插件快捷键：

| 操作 | 快捷键 |
|---|---|
| 安装配置中声明的插件 | `Ctrl+a I` |
| 保存 tmux 状态 | `Ctrl+a Ctrl+s` |
| 恢复 tmux 状态 | `Ctrl+a Ctrl+r` |

注意区分：`Ctrl+a r` 是重新加载当前配置，`Ctrl+a Ctrl+r` 是由 tmux-resurrect 恢复之前保存的布局。

tmux-resurrect 能恢复布局、Pane 目录和部分程序，但不能保证重建所有 Codex 或 Claude 交互进程。AI 会话应同时使用各自 CLI 的会话恢复功能。

## 5. `dev`：创建项目工作区

### 默认启动与会话复用

在项目根目录或任意子目录启动：

```bash
dev
dev /path/to/project
```

默认使用 `classic` 布局和 `deep` 配置，恢复原来的六窗口、九窗格：三个 Codex、一个普通模式 Claude，以及后端、前端、服务、测试和 Git 窗格。Deep 按可见模型目录选择高优先级模型及最高支持推理档位，支持时启用 Fast，并启用 `multi_agent`。所有 Codex 默认使用最高 CLI 权限，跳过审批并关闭 Codex 沙箱。

Session 名称为 `ai-<目录名>-<规范绝对路径的哈希>`。因此，不同仓库中都叫 `auth` 的任务有不同会话；从同一 Worktree 的子目录启动会回到同一会话。复用前还会核对记录的项目目录及初始化状态，避免进入别的项目或半完成的工作区。

```bash
dev --session my-project
dev --detached
dev --help
```

`--session` 覆盖名称，但不会绕过目录归属检查。`--detached` 创建或检查会话后返回 Shell，不切换当前界面。已有会话会被复用；布局、启动、恢复等选项只在新建会话时生效，不会自动重启已有进程。模型和权限的新默认值只对新启动的 Codex 生效。

如果当前工作区是此前创建且未经改动的 focus 布局，显式恢复原版：

```bash
dev --restore-layout
task open auth --restore-layout --detached
```

`--restore-layout` 选择 classic，核对会话属于当前目录、初始化完成且五窗口结构未被改动，保留所有已有窗格和进程，只补齐缺少的窗格。classic 会话无需转换；被改过的 focus 和 pair/full 会话会拒绝转换。已有 AI 保持原设置，新窗格使用本次配置，默认 deep；不带该参数时只连接原有布局。

### 布局与 AI 分工

| 布局 | AI 内容 | 适合的任务 |
|---|---|---|
| `classic`（默认） | 三个 Codex + 一个普通模式 Claude | 原来的多 AI 工作台 |
| `focus` | 一个 Codex 实现 Pane | 希望减少同时打开的 AI 时 |
| `pair` | Codex 实现 + Claude Plan 模式审查 | 实现与方案/代码 Review |
| `full` | Pair，再增加独立 Codex 探索窗口，同样使用最高 CLI 权限 | 需要独立代码探索的复杂任务 |

```bash
dev --layout classic --profile deep
dev --layout focus --profile standard
dev --layout pair
dev --layout full --profile deep
dev --no-ai
dev --layout pair --no-claude
dev --layout pair --no-codex
```

默认 classic 的六个窗口与原版一致，共九个窗格：

| Window 名称 | 内容 |
|---|---|
| `codex` | 左右两个 Codex CLI |
| `codex-claude` | 左侧 Codex，右侧普通模式 Claude |
| `backend-frontend` | 左侧后端 Shell，右侧前端 Shell |
| `services` | 服务 Shell |
| `test` | 测试 Shell |
| `git` | LazyGit；未安装时显示 Git 状态 |

可选的 focus/pair/full 布局使用 `ai`、`app`、`services`、`test`、`git` 窗口；`app` 分为后端和前端，`full` 另有 `explore`。pair/full 中 Claude 审查 Pane 使用 `--permission-mode plan`。full 的 Codex 探索 Pane 与实现 Pane 一样跳过审批并关闭 Codex 沙箱，始终独立新建会话。多个独立实现任务应分别创建 Worktree。

`--no-ai` 禁止自动启动所有 AI；`--no-codex` 和 `--no-claude` 分别禁用对应 CLI，Pane 保持普通 Shell。这些参数不会终止已经存在的 AI 会话。

### 普通与深度配置

默认 `deep` 在启动时尝试读取可见模型目录，选择高优先级模型及其最高支持推理档位；支持时启用 Fast，并启用 `multi_agent`。查询有超时限制，失败时退回 CLI 默认配置，不固定到某个未来可能失效的模型名称。目录优先级是选择规则，不是跨模型质量基准。可选的 `standard` 使用已有 Codex CLI 的模型与推理配置。

```bash
dev --profile standard
dev --profile deep
```

Deep 可能增加调用用量；需要沿用个人模型配置时显式选择 `--profile standard`。目录接口属于实验性接口，具体模型能力与可用参数取决于安装的 CLI。

所有布局和配置档位中的 Codex 均默认添加 `--dangerously-bypass-approvals-and-sandbox`，跳过审批并关闭 Codex 沙箱，包括 full 的探索 Pane。`--unsafe` 仅额外为 classic 中的 Claude 启用权限绕过；pair/full 中的 Claude 保持 Plan 模式。

### 预览、检查和恢复

```bash
dev --plan
dev --check
dev --start
dev --resume
```

`--plan` 显示目录、会话、布局、端口和已配置命令，不启动工作区或项目命令。`--check` 检查项目配置、可执行命令和端口。`--start` 才会执行 `.ai-dev.conf` 中的后端、前端、服务与测试命令。

`--resume` 在新建工作区时打开 AI 的历史会话选择器；项目配置可选填写 `codex_session`、`claude_session` 指定会话。classic 只让第一个 Codex 恢复历史，另外两个 Codex 新开对话，避免并发使用同一会话 ID。已有 tmux Session 直接连接，不会再次打开选择器。tmux 重启后的布局恢复与 AI 对话恢复是两件事。

## 6. Codex CLI 与 Claude Code

### 手动启动

```bash
codex
claude
```

查看可用参数：

```bash
codex --help
claude --help
```

如果 AI 进程退出，Pane 本身仍然存在，可以在原 Pane 中重新运行命令。需要恢复之前的对话时，使用对应 CLI 帮助中提供的 Resume/Continue 功能；CLI 的具体恢复选项可能随版本变化。

### 并行工作的原则

同一 Worktree 中的 AI Pane 会立即看到彼此的文件修改。classic 保留多个 AI Pane，需要自行明确分工；pair/full 则预设实现、审查和独立探索角色，Codex 探索 Pane 也拥有写入权限。适合的用法包括：

- 一个 AI 实现，另一个 AI 只读 Review；
- 一个处理后端，另一个处理前端，且文件范围不重叠；
- 一个编写代码，另一个运行测试和分析日志。

如果多个 AI 都要独立修改代码，使用 `task new` 创建不同 Worktree，并明确各任务的交付范围。

## 7. `task` 与 `newtask`：任务生命周期

Git Worktree 让同一仓库同时拥有多个工作目录，各自使用独立分支，共享对象与历史。`task` 把创建、打开、查询和收尾串起来；`newtask` 仍可单独使用。

### 创建并打开

```bash
task new auth
git fetch origin
task new billing origin/main --layout pair
task new docs --no-open
```

`task new NAME [BASE_REF]` 创建 `feature/NAME`，默认基于当前 `HEAD`，随后打开该 Worktree 的 `dev` 工作区。`--no-open` 只创建。`origin/main` 是本地远程跟踪引用，需要最新基线时先 Fetch。

只创建目录时也可以使用：

```bash
newtask auth
newtask pipeline origin/main
newtask --print-path sandbox
```

`--print-path` 只在标准输出中返回绝对路径。任务名只允许字母、数字、点、下划线和连字符，并须通过 Git 分支名称检查。

目标路径已经存在，或分支已经在某个 Worktree 中检出时，命令会报错并提示如何继续；创建失败会尝试撤销本次创建且未被其他操作改变的分支。未检出的已有分支可以复用，但必须省略 `BASE_REF`，避免悄悄忽略指定基线。

### 查找与切换

```bash
task list
task pick
task open auth
task open auth --resume
```

`list` 显示任务、分支、工作区修改状态、关联 tmux Session 与目录。`open` 按 Git 实际登记的分支查找，旧目录结构无需搬迁。`pick` 在交互终端使用可选的 fzf；没有 fzf 时用编号选择，没有终端时只输出列表。tmux 中可以按 `Ctrl+a t` 打开选择器。

`task new/open/pick` 可传递 `dev` 的布局、配置、恢复、启动与禁用 AI 等选项，也可用 `--` 分隔。`task new` 总会先创建 Worktree；若只想预览已有目录，使用 `dev --plan` 或 `task open NAME --plan`。

### Worktree 目录

默认目录仍为主仓库旁的 `<主仓库>_worktrees/<任务名>`。自定义共享目录：

```bash
AI_WORKTREE_ROOT=/path/to/worktrees task new auth
```

使用全局根目录时，实际路径为 `<根目录>/<仓库名-路径哈希>/<任务名>`，不同项目可以使用相同任务名。相对根目录以调用命令时的目录解析，输出始终为绝对路径。从已有 Worktree 创建任务时，仓库标识仍来自主仓库。

### 预览和完成任务

```bash
task done auth
task done auth --apply
task done auth --base origin/main --keep-branch
```

`done` 默认只预览。只有 `--apply` 才尝试删除已登记的关联 Worktree。应用前必须同时满足：

- 工作区没有未提交或未跟踪内容。
- 任务分支已合并到指定 `--base`；未指定时使用主 Worktree 的当前 `HEAD`。
- 有本地远程跟踪引用包含任务提交；若缺失，可先 Fetch。
- 没有关联的 tmux Session，且不是主 Worktree。

忽略文件也会被 Git 删除，因此存在 `.env` 等忽略文件时默认阻止清理。`--allow-ignored` 明确允许删除这些文件；`--allow-unpushed` 明确跳过远程包含检查。两者都不会跳过未提交内容和合并检查。

`--keep-branch` 保留分支，其他检查照常执行。不带它时使用 Git 的安全分支删除；若 Git 因其上游/当前分支规则拒绝，Worktree 已移除而分支会保留，并输出说明。命令不会强制删除锁定 Worktree、未合并分支，也不会自动结束 tmux 进程。

原生查看、修复、移动等命令仍见 [命令查询手册](command-reference.md#9-tasknewtask-与-git-worktree)。完整参数以 `task help` 为准。

## 8. Git 工具

### LazyGit

启动：

```bash
lazygit
```

最常用操作。按键会随面板改变，因此应把面板一起记住：

| 面板 | 按键 | 操作 |
|---|---|---|
| Files | `Space` | 暂存/取消暂存当前文件 |
| Files | `a` | 暂存/取消暂存所有文件 |
| Files | `c` | Commit |
| Files | `p` / `P` | Pull / Push |
| Files | `x` | 丢弃文件修改，会要求确认 |
| Branches | `n` | 创建分支 |
| 全局 | `?` | 查看当前面板操作 |
| 全局 | `q` | 退出 |

### Git Diff 与 Delta

```bash
git diff
git diff --staged
git diff HEAD
git diff main...HEAD
git diff --stat
git diff --name-only
```

按顺序分别表示：未暂存差异、已暂存差异、已跟踪文件相对 `HEAD` 的全部差异、共同祖先到当前已提交 `HEAD` 的差异、统计摘要、只显示文件名。

Delta 只改变显示效果，不修改 Git 数据。

### GitHub CLI

```bash
gh auth status
gh pr create --fill
gh pr view
gh pr diff
gh pr checks --watch
gh run list
gh run view --log-failed
```

其中 `auth` 是 Authentication（认证），`pr` 是 Pull Request，`--fill` 自动填充 PR 内容，`--watch` 持续观察 CI，`--log-failed` 只显示失败步骤日志。

完整说明见 [Git 工具指南](git-tools-guide.md)。

## 9. 后端、前端、服务与测试窗口

默认只创建窗口；项目命令需要写入 `.ai-dev.conf`，再使用 `dev --start` 执行。可以参考 [项目配置模板](../config/project.example.conf)，按自己的目录修改，例如：

```ini
layout=classic
profile=deep
backend_dir=backend
frontend_dir=frontend
backend_cmd=uv run uvicorn app.main:app --reload --port "$BACKEND_PORT"
frontend_cmd=pnpm dev --port "$FRONTEND_PORT"
test_cmd=git diff --check
services_cmd=docker compose up
```

配置按字面 `key=value` 读取，不是 Shell 脚本：不要添加 `export`，不要给整个值包一层引号，只使用独立整行注释。命令值本身可以包含正常的 Shell 引号；这些命令仅在显式 `--start` 时执行。

每个 Worktree 按规范绝对路径生成默认 `BACKEND_PORT`、`FRONTEND_PORT` 和 `COMPOSE_PROJECT_NAME`。应用命令需要实际使用这些变量；固定端口、固定 Compose 容器名或共享数据卷不会因创建 Worktree 自动隔离。端口占用时，调整配置中的 `backend_port`、`frontend_port`，再运行 `dev --check`。

未指定目录时，后端按 `backend → api → server → 项目根目录` 查找，前端按 `frontend → web → ui → 项目根目录` 查找。依赖安装、未跟踪的本地环境文件仍需按项目说明准备。以下是手动启动的常见命令。

### Backend Pane 示例

Python/uv 项目：

```bash
uv sync
uv run pytest
uv run uvicorn <module>:<app> --reload
```

`sync` 表示同步依赖，`run` 表示在项目环境中运行命令，`--reload` 表示源代码变化后自动重启服务。`<module>:<app>` 是“Python 模块:应用对象”的占位格式。

具体的 Uvicorn 模块名由项目决定，例如 `app.main:app`。

### Frontend Pane 示例

Node/pnpm 项目：

```bash
pnpm install
pnpm dev
```

`pnpm` 通常解释为 **performant npm**；`dev` 是 **development（开发）** 的缩写。`install` 安装依赖，`dev` 启动开发模式。

也可以根据锁文件和项目说明使用 `npm`、`yarn` 或其他包管理器。

### Services Window

```bash
docker compose ps
docker compose up -d
docker compose logs -f
docker compose down
```

`ps` 是 Process Status（服务状态），`-d` 是 `--detach`（后台启动），`-f` 是 `--follow`（持续跟随日志）。

`up -d` 会创建或启动容器；`down` 会停止并移除 Compose 容器和网络。是否同时删除数据卷取决于参数，不要在不确认数据用途时添加 `-v`。

### Test Window

根据项目类型运行：

```bash
uv run pytest
pnpm test
pnpm lint
pnpm build
```

长时间运行的测试和日志适合放在独立 Window，避免打断 AI 对话 Pane。

## 10. 推荐日常工作流

### 从任务到交付

```bash
cd /path/to/project
git fetch origin
task new auth origin/main
```

在 `codex` 与 `codex-claude` 窗口安排实现和审查，在 `backend-frontend` 窗口运行应用，在 `test` 窗口执行测试和 Lint。已配置项目启动命令时，可在新建任务时追加 `--start`。

交付前检查修改并提交：

```bash
git status --short --branch
git diff
git diff --staged
lazygit
```

确认要推送和创建 PR 后，按项目流程运行：

```bash
git push -u origin HEAD
gh pr create --fill
gh pr checks --watch
```

本工具不会代替用户自动执行这些远程操作。PR 完成后，保存工作、结束对应 tmux Session，再从主仓库 Fetch 并预览清理：

```bash
git fetch origin
task done auth --base origin/main
```

确认预览内容后，用同样参数追加 `--apply`。Squash Merge 不一定保留祖先关系，此时安全合并检查可能拒绝删除；不要把强制删除当作默认收尾方式。

### 多任务与恢复

```bash
task new billing origin/main --no-open
task list
task pick
task open billing
```

临时离开使用 `Ctrl+a d`，保留 Session 及进程。再次运行 `task open NAME` 连接回去。

macOS 或 tmux 重启后，可用 `Ctrl+a Ctrl+r` 恢复插件保存的布局。创建新会话并恢复 AI 历史时，使用 `task open NAME --resume`；若布局已恢复且 Session 仍存在，在对应 Pane 中手动运行 `codex resume` 或 `claude --resume`。

## 11. 卸载与恢复原配置

在本工具的仓库根目录运行：

```bash
./uninstall.sh
```

卸载脚本会根据安装时记录的文件指纹恢复 Ghostty、tmux、Shell 和辅助命令配置。如果某个受管理文件在安装后被手动修改，脚本会保留它，避免覆盖用户改动。

卸载脚本不会删除：

- Homebrew 安装的软件；
- Ghostty、tmux 和 Git；
- 字体；
- TPM 与 tmux 插件；
- 历史备份。

## 12. 常见问题

### 找不到 `dev`、`newtask`、`task` 或 `ai-dev-doctor`

```bash
source ~/.zshrc
command -v dev
command -v newtask
command -v task
command -v ai-dev-doctor
```

如果仍找不到，确认 `~/.local/bin` 位于 `PATH`，然后重新运行安装脚本。

### tmux 颜色或字体不正确

```bash
ghostty +validate-config --config-file="$HOME/.config/ghostty/config"
ghostty +list-fonts | grep -F "JetBrainsMono Nerd Font Mono"
tmux show-options -gqv default-terminal
tmux show-options -sqv terminal-features
```

修改 tmux 配置后按 `Ctrl+a r` 重新加载；修改 Ghostty 配置后打开新窗口。

### `dev` 没有重新创建窗口

属于同一目录且初始化完成的 Session 已存在时，`dev` 会直接连接；布局和启动选项不会重建窗口。先查看：

```bash
tmux list-sessions
```

如果确实需要重建，先保存工作并结束准确的目标会话：

```bash
tmux kill-session -t <exact-session-name>
dev /path/to/project
```

### `git` Window 没有启动 LazyGit

确认项目是 Git 仓库且命令可用：

```bash
git rev-parse --is-inside-work-tree
command -v lazygit
```

`rev-parse` 是 **revision parse（解析版本引用）**；`--is-inside-work-tree` 会判断当前目录是否位于 Git 工作树内。`command -v` 用于确认命令能否被 Shell 找到，这里的 `v` 可记作 **verify（验证）**，但它是助记而非该选项的官方展开。

也可以在该 Window 中手动运行：

```bash
lazygit
```

### Services 窗口只显示 Shell

默认不会自动启动 Docker 或项目服务。先在 `.ai-dev.conf` 设置 `services_cmd`，再用 `dev --start` 创建新工作区；已有 Session 中按需手动执行命令。确认 Docker 可用：

```bash
docker info
docker compose ps
dev --check
```

### 一键诊断

```bash
ai-dev-doctor
```

如果检查失败，优先处理输出中的 `FAIL` 行。

## 13. 缩写、参数与符号速查

### 常见技术缩写

| 缩写 | 英文全称 | 中文含义与记忆提示 |
|---|---|---|
| AI | Artificial Intelligence | 人工智能；Codex 和 Claude 属于 AI 编码工具 |
| API | Application Programming Interface | 应用程序编程接口；程序之间交互的“接口” |
| ASGI | Asynchronous Server Gateway Interface | 异步服务器网关接口；FastAPI 常用的 Python 服务接口标准 |
| CI | Continuous Integration | 持续集成；代码 Push 后自动测试、Lint 和构建 |
| CLI | Command-Line Interface | 命令行界面；通过输入命令操作，例如 `gh`、`codex` |
| TUI | Text-based User Interface | 文本式用户界面，也常称 Terminal UI；例如 LazyGit |
| GUI | Graphical User Interface | 图形用户界面；普通桌面应用窗口 |
| PR | Pull Request | 拉取请求；请求把一个分支的修改合并到另一个分支 |
| SSH | Secure Shell | 安全 Shell；常用于登录远程服务器或访问 Git 远程仓库 |
| TPM | Tmux Plugin Manager | tmux 插件管理器；类比包管理器 |
| UI | User Interface | 用户界面；`ui` 目录通常是前端目录 |
| URL | Uniform Resource Locator | 统一资源定位符；通常就是网页或资源地址 |
| ID | Identifier | 标识符；例如 `<run-id>` 是某次 CI 运行的编号 |
| RGB | Red, Green, Blue | 红、绿、蓝三色通道；终端 True Color 的基础 |
| MB | Megabyte | 兆字节；本文的滚动历史容量单位 |
| pt | point | 排版字号单位“点”；15 pt 表示 15 点字号 |
| YAML | YAML Ain't Markup Language | 配置文件格式；`.yml` 是 `.yaml` 的短扩展名 |

### 命令和名称缩写

| 写法 | 全称或来源 | 含义与记忆提示 |
|---|---|---|
| `tmux` | Terminal Multiplexer | 终端多路复用器；一个终端里管理多个 Session、Window 和 Pane |
| `zsh` | Z Shell | 当前 Shell；`.zshrc` 是它的运行配置文件 |
| `rc` | run commands | 配置文件名中的历史缩写；`.zshrc` 可记作 Z Shell Run Commands |
| `.sh` | Shell Script | Shell 脚本扩展名，例如 `install.sh` |
| `bin` | binaries | 存放可执行命令的目录名，例如 `~/.local/bin` |
| `gh` | GitHub CLI 的命令名 | `g` + `h` 可直接记成 GitHub |
| `git diff` | difference | 查看差异；`diff` 记作“不同之处” |
| Delta | 希腊字母 Δ | 数学中表示“变化量”，用于美化代码变化显示 |
| `auth` | authentication | 认证或登录，例如 `gh auth login` |
| `repo` | repository | 仓库，例如 `gh repo view` |
| `pr` | Pull Request | Pull Request 子命令，例如 `gh pr create` |
| `rev` | revision | 版本或修订，例如 `git rev-parse` |
| `config` | configuration | 配置，例如 `--config-file` |
| `env` | environment | 环境，例如项目名 `ai-dev-env` |
| `dev` | development | 开发；`dev` 创建开发工作区，`pnpm dev` 启动开发服务器 |
| `cd` | change directory | 切换目录；`cd /path/to/project` |
| `ps` | process status | 进程/服务状态；`docker compose ps` |
| `grep` | Global Regular Expression Print | 从文本中筛选匹配行；名称来自早期 Unix 编辑器命令 |
| `source` | source file | 在当前 Shell 中读取并执行配置文件 |
| `export` | export variable | 把变量导出给当前 Shell 后续启动的子进程 |
| `command -v` | command lookup | 查询 Shell 会执行哪个命令；`v` 可用 Verify 助记，但不是官方展开 |
| `pnpm` | performant npm | 强调高性能和磁盘复用的 Node 包管理器 |
| `uv` | 工具专有名称，无需展开 | Python 项目与包管理工具；不要为它强行编造全称 |
| `pytest` | 工具名称，不是正式缩写 | Python 测试框架；可把 `py` + `test` 当作记忆联想 |
| `lint` | 不是缩写 | 静态检查代码风格和潜在错误；名称来自早期 Unix `lint` 工具 |

### 常用参数

同一个短参数必须结合前面的命令理解。例如 `-d` 在 Docker 中是后台运行，在 Git Branch 中却是删除。

| 命令场景 | 短参数/长参数 | 全称或助记 | 实际含义 |
|---|---|---|---|
| tmux | `-V` | Version | 显示 tmux 版本；这里是大写 V |
| Git、LazyGit、`gh` 等 | `--version` | Version | 显示版本；是否支持短写应查看具体命令帮助 |
| 多数本文工具 | `--help` | Help | 显示帮助；不要假设所有工具的 `-h` 都表示 Help |
| Git Diff | `-h` | Help | 显示 `git diff` 的简短帮助；此含义只适用于对应命令 |
| Ghostty | `+validate-config` | Validate Configuration | 验证配置；`+` 表示 Ghostty CLI Action |
| Ghostty | `+list-fonts` | List Fonts | 列出可用字体 |
| Ghostty | `+list-themes` | List Themes | 列出可用主题 |
| Ghostty | `--config-file` | Configuration File | 指定配置文件路径 |
| `grep` | `-F`、`--fixed-strings` | Fixed Strings | 把搜索内容当作固定字符串 |
| LazyGit | `-p`、`--path` | Path | 指定 Git 仓库路径 |
| tmux Attach/Kill | `-t` | Target | 指定目标 Session；其他 tmux 子命令也常用它指定目标 |
| `tmux show-options` | `-g` | Global | 读取全局选项 |
| `tmux show-options` | `-q` | Quiet | 选项不存在时保持安静，不输出错误 |
| `tmux show-options` | `-v` | Value | 只输出选项值 |
| `tmux show-options` | `-s` | Server | 读取服务器级选项 |
| `dev` | `--session` | Session | 指定 tmux Session 名称 |
| `dev` | `--no-ai` | No AI | 新会话不启动 AI |
| `dev` | `--no-codex` / `--no-claude` | No Codex / No Claude | 分别禁用对应 CLI |
| `dev` | `--layout` / `--profile` | Layout / Profile | 选择窗口布局与模型配置 |
| `dev` | `--plan` / `--check` | Plan / Check | 预览启动方案或检查项目配置 |
| `dev` | `--start` / `--resume` | Start / Resume | 执行配置的项目命令或恢复 AI 历史 |
| `dev` | `--restore-layout` | Restore Layout | 保留原窗格与进程，将未改动的 focus 会话恢复为 classic |
| `task done` | `--apply` | Apply | 通过检查后执行预览的清理 |
| Codex | `--dangerously-bypass-approvals-and-sandbox` | Bypass Approvals and Sandbox | 跳过全部确认且不使用 Codex 沙箱；只适合外部已可靠隔离的环境 |
| Claude | `--dangerously-skip-permissions` | Skip Permissions | 绕过全部权限检查；只适合无网络等严格隔离的沙箱 |
| Docker | `-d`、`--detach` | Detached | 在后台启动容器，不占住当前终端 |
| Docker Logs | `-f`、`--follow` | Follow | 持续跟随新日志 |
| Git Branch | `-d`、`--delete` | Delete | 安全删除已合并分支 |
| Git Branch | `-D` | `--delete --force` | 强制删除分支，即使尚未合并；可能丢失提交 |
| `git worktree remove` | `--force` | Force | 一次可移除有修改/含 Submodule 的 Worktree；锁定项要写两次；主 Worktree 不可移除 |
| Git Add | `-p`、`--patch` | Patch | 交互选择要加入暂存区的 Hunk；不要与 LazyGit 的 `-p/--path` 混淆 |
| Git Commit | `-m`、`--message` | Message | 在命令行直接提供提交信息 |
| Git Push | `-u`、`--set-upstream` | Upstream | 建立本地分支与远程分支的跟踪关系 |
| Git Remote | `-v`、`--verbose` | Verbose | 显示更详细的远程地址 |
| Git Diff | `-S<string>` | String（助记，无官方长参数） | 筛选字面字符串出现次数发生变化的文件，也称 Pickaxe 搜索 |
| Git Diff | `-p`、`--patch` | Patch | 输出补丁格式；普通 `git diff` 默认使用该格式 |
| Git Diff | `-u` | `--patch` 的同义短写 | 在 Git 中等同 `-p`，不要与系统 `diff -u` 的 Unified 混淆 |
| 系统 `diff` | `-u`、`--unified` | Unified | 使用统一 Diff 格式 |
| 系统 `diff` | `-r`、`--recursive` | Recursive | 递归比较目录；`-ru` 是 `-r -u` 的合并写法 |
| Git Status | `--short` | Short | 使用紧凑状态格式 |
| Git Status | `--branch` | Branch | 同时显示分支信息 |
| Git Log | `--oneline` | One Line | 每个提交显示一行 |
| Git Diff | `--staged`、`--cached` | Staged / Cached | 查看暂存区与 `HEAD` 的差异；两者等价 |
| Git Diff | `--stat` | Statistics | 只显示文件与增删行统计 |
| Git Diff | `--name-only` | Name Only | 只显示发生变化的文件名 |
| Git Diff | `--word-diff` | Word Difference | 按单词而不是整行展示差异 |
| Git | `--no-pager` | No Pager | 不经过 Delta、less 等分页显示器 |
| Git | `--is-inside-work-tree` | Is Inside Work Tree | 判断当前位置是否位于 Git 工作树内 |
| `gh pr create` | `--fill` | Fill | 从 Commit 自动填充 PR 标题与正文 |
| `gh pr create` | `--draft` | Draft | 创建草稿 PR |
| `gh repo view` | `--web` | Web | 在浏览器打开 |
| `gh pr checks` | `--watch` | Watch | 持续刷新，直到检查结束 |
| `gh run view` | `--log-failed` | Log Failed | 只显示失败步骤的日志 |
| `gh run rerun` | `--failed` | Failed | 重新运行失败的 Job 及其依赖 |
| `gh repo fork` | `--clone` | Clone | Fork 后同时克隆到本地 |
| Uvicorn | `--reload` | Reload | 代码变化后自动重启开发服务器 |
| `docker compose down` | `-v`、`--volumes` | Volumes | 同时删除 Compose 声明的命名卷和容器匿名卷，可能删除持久化数据 |

组合短参数按字母拆开理解：

```bash
tmux show-options -gqv default-terminal
tmux show-options -sqv terminal-features
diff -ru old-directory new-directory
```

这里 `-gqv` 是 Global + Quiet + Value，`-sqv` 是 Server + Quiet + Value，`-ru` 是 Recursive + Unified。

### Shell、Git 与快捷键符号

| 符号 | 名称 | 含义与记忆提示 |
|---|---|---|
| `~` | Tilde / Home shorthand | 当前用户主目录，例如 `~/.tmux.conf` |
| `$HOME` | Home environment variable | 当前用户主目录的环境变量形式 |
| `$PATH` | Command search path | Shell 搜索可执行命令的目录列表 |
| `$NAME` | Variable expansion | 取出名为 `NAME` 的环境变量值 |
| `NAME=value command` | Temporary environment assignment | 只为后面的这一条命令临时设置环境变量，例如 `AI_WORKTREE_ROOT=/tmp/wt newtask auth` |
| `|` | Pipe | 把左侧命令的输出“输送”给右侧命令 |
| `#` | Comment | Shell 脚本中表示注释；交互式 zsh 可能未启用 `interactivecomments`，所以本文可复制命令块不放行尾 `#` 注释 |
| `--` | End of options | 结束参数解析；Git 中常用来分隔版本参数和文件路径 |
| `<name>` | Placeholder | 替换成真实值，不要输入 `<` 和 `>` |
| `.` | Current directory | 当前目录；单独使用时不是 Git 的点范围语法 |
| `..` | Parent / two-dot range | 路径中表示父目录；`git diff A..B` 中比较 A 与 B 的端点 |
| `...` | Three-dot range | `git diff A...B` 比较 A、B 的共同祖先与 B |
| `HEAD` | Symbolic reference，不是缩写 | 当前检出的提交位置 |
| `HEAD~1` | First parent of HEAD | 当前提交的第一代父提交；`~1` 可记为“往回一步” |
| `origin/main` | Remote-tracking reference | 本地保存的远程跟踪引用，代表最近一次 Fetch 得知的 `origin` 上 `main` 状态 |
| `<module>:<app>` | Module/object separator | Uvicorn 中冒号左边是模块，右边是应用对象 |
| `Ctrl` | Control | 控制键；`Ctrl+a` 表示按住 Control 再按 a |
| `Alt` | Alternate | 备用修饰键；本配置中左 Option 被映射为 Alt |
| `Esc` | Escape | 退出当前模式或返回上一级 |

记忆短参数时，不要只背字母：把“命令 + 参数 + 动作”一起记。例如 `docker logs -f = follow logs`，`git push -u = set upstream`，比单独记忆 `-f` 或 `-u` 更不容易混淆。
