# AI Dev Environment 完整使用指南

本文介绍本项目提供的整套 macOS AI 开发环境，包括 Ghostty、tmux、Codex CLI、Claude Code、Git Worktree、LazyGit、Delta、GitHub CLI、Docker Compose，以及配套的安装、检查和恢复命令。

Git 工具的完整按键和命令说明另见 [LazyGit、Git Diff 与 GitHub CLI 使用指南](git-tools-guide.md)。

需要快速复制和查询命令时，使用 [AI Dev Environment 命令查询手册](command-reference.md)。

## 1. 环境组成

整套环境的关系如下：

```text
macOS
└── Ghostty：终端窗口、字体、主题、剪贴板和滚动历史
    └── tmux：持久会话、窗口、分屏和布局恢复
        └── dev：为每个项目创建标准工作区
            ├── codex：两个 Codex CLI 面板
            ├── codex-claude：Codex CLI + Claude Code
            ├── backend-frontend：后端 + 前端命令
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

在任意目录运行：

```bash
/Users/renyakun/work26/ai-dev-env-v1.0/install.sh
```

安装脚本会：

1. 检查 macOS 和 Homebrew。
2. 安装缺少的 Ghostty、tmux、Git、LazyGit、Delta 和 `gh`。
3. 安装 JetBrains Mono Nerd Font。
4. 备份已有 Ghostty、tmux、Shell 和辅助命令配置。
5. 安装 Ghostty 与 tmux 配置。
6. 将 `dev`、`newtask` 和 `ai-dev-doctor` 安装到 `~/.local/bin`。
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
- `dev` 与 `newtask` 是否位于 `PATH`。

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
| 辅助命令 | `~/.local/bin/` |
| TPM 与插件 | `~/.tmux/plugins/` |
| 安装状态和备份 | `~/.local/state/ai-dev-env/` |

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

### 基本用法

为当前目录启动工作区：

```bash
dev
```

指定项目或 Worktree：

```bash
dev /path/to/project
```

不自动启动三个 Codex Pane：

```bash
dev /path/to/project --no-codex
```

指定 tmux Session 名称：

```bash
dev /path/to/project --session my-project
```

查看帮助：

```bash
dev --help
```

同一个项目的默认 Session 名称为 `ai-<项目目录名>`。如果会话已经存在，再次运行 `dev` 只会 Attach 或切换到已有会话，不会重复创建窗口。

### 默认窗口布局

| 编号 | Window 名称 | 默认内容 |
|---|---|---|
| 1 | `codex` | 左右两个 Codex CLI |
| 2 | `codex-claude` | 左侧 Codex CLI，右侧 Claude Code |
| 3 | `backend-frontend` | 左侧后端目录，右侧前端目录 |
| 4 | `services` | 项目服务；发现 Compose 文件时执行 `docker compose ps` |
| 5 | `test` | 测试、Lint 和构建检查 Shell |
| 6 | `git` | Git 仓库中自动启动 LazyGit |

后端目录按以下顺序自动查找：

```text
backend → api → server → 项目根目录
```

前端目录按以下顺序自动查找：

```text
frontend → web → ui → 项目根目录
```

`--no-codex` 只禁止自动启动 Codex；如果已经安装 `claude`，`codex-claude` 的右侧 Pane 仍会启动 Claude Code。

### AI CLI 权限警告

默认 `dev` 使用以下命令启动 AI：

```bash
codex --model gpt-5.6-sol --config model_reasoning_effort=ultra --config service_tier=fast --enable multi_agent --enable fast_mode --dangerously-bypass-approvals-and-sandbox
claude --dangerously-skip-permissions
```

Codex 使用当前旗舰 `gpt-5.6-sol`、`ultra` 推理档位（最大推理并自动委派子代理）和 `fast` 服务层启动。Ultra 可能延长复杂任务的总处理时间，Fast 会加快模型输出；两者都会增加 Token/额度和并行任务用量。

这两个参数都会绕过重要的安全边界：

- Codex 的参数会跳过所有确认，并在没有 Codex 沙箱的情况下执行命令；它只适合已经由外部环境可靠隔离的场景。
- Claude 的参数会绕过全部权限检查；官方只建议在没有网络访问等严格隔离的沙箱中使用。

因此，“仓库可信”本身仍不足以消除风险。使用时还要确认运行环境、网络、凭据和可访问文件的范围，并避免让多个 AI Pane 同时编辑同一文件。

如需更严格的 Codex 确认流程，可以使用：

```bash
dev /path/to/project --no-codex
```

然后在 Codex Pane 中手动运行不带危险参数的命令：

```bash
codex
```

当前 `dev` 没有 `--no-claude` 选项，`--no-codex` 后 Claude 仍会带危险参数自动启动。若要使用普通权限模式，先在 `codex-claude` 右侧 Pane 中结束自动启动的 Claude，再手动运行不带危险参数的 `claude`。

另外，`--no-codex` 只在创建新 tmux Session 时影响启动流程。如果同名 Session 已存在，`dev` 会直接 Attach，参数不会停止其中已经运行的 Codex。需要严格模式时，应先检查现有 Session，或者用新的 Session 名创建工作区：

```bash
dev /path/to/project --session safe-project --no-codex
```

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

默认 `dev` 中的多个 AI Pane 位于同一个工作目录，它们会立即看到彼此的文件修改。适合的用法包括：

- 一个 AI 实现，另一个 AI 只读 Review；
- 一个处理后端，另一个处理前端，且文件范围不重叠；
- 一个编写代码，另一个运行测试和分析日志。

如果多个 AI 都要独立修改代码，优先使用 `newtask` 创建不同 Worktree，避免覆盖彼此的工作。

## 7. `newtask`：并行 Git Worktree

Git Worktree 可以让同一个仓库同时存在多个工作目录，每个目录使用独立分支，但共享 Git 对象和历史。

### 创建任务

完整命令结构是：

```text
newtask <TASK_NAME> [BASE_REF]
```

| 部分 | 全称 | 含义 |
|---|---|---|
| `TASK_NAME` | Task Name | 必填任务名；用于生成目录和 `feature/<任务名>` 分支 |
| `BASE_REF` | Base Reference | 可选基准引用；方括号表示可省略，默认是 `HEAD` |
| `auth` | authentication（示例助记） | 这里只是任务名示例，可以换成自己的任务名称 |
| `origin/main` | remote/branch | 远程 `origin` 的 `main` 分支所对应的本地远程跟踪引用 |

从当前提交创建：

```bash
newtask auth
```

从指定基准分支创建：

```bash
newtask pipeline origin/main
```

`origin/main` 是本地保存的 Remote-tracking Ref（远程跟踪引用），`newtask` 不会自动 Fetch。若任务必须基于远程最新的 `main`，先运行：

```bash
git fetch origin
newtask pipeline origin/main
```

命令会创建：

```text
分支：feature/<任务名>
目录：<主仓库>_worktrees/<任务名>
```

然后启动该 Worktree：

```bash
dev /path/to/repository_worktrees/auth
```

任务名只能包含字母、数字、点、下划线和连字符。

### 自定义 Worktree 根目录

临时指定：

```bash
AI_WORKTREE_ROOT=/path/to/worktrees newtask auth
```

长期指定时，把下面这一行加入 `~/.zshrc`：

```bash
export AI_WORKTREE_ROOT=/path/to/worktrees
```

然后运行 `source ~/.zshrc` 或打开新的 Ghostty 窗口。单独在当前终端执行 `export` 只持续到当前 Shell 结束，但会传递给它启动的子进程。

### 查看和清理 Worktree

查看：

```bash
git worktree list
```

确认工作已经提交后移除：

```bash
git worktree remove /exact/path/to/worktree
git branch -d feature/auth
```

`-d` 对应 `--delete`，只删除已经安全合并的分支；大写 `-D` 会强制删除，不适合作为日常默认操作。

如果 Worktree 中还有未提交修改，Git 通常会拒绝移除。一次 `git worktree remove --force <path>` 可以强制移除有修改或含 Submodule 的 Worktree；锁定的 Worktree 需要连续写两次 `--force --force`；主 Worktree 永远不能用该命令移除。强制操作可能丢失工作，不要把它当作日常默认操作。

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

`dev` 只创建标准工作目录和窗口，不会猜测并自动启动项目命令。应根据具体项目在对应 Pane 中运行命令。

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

### 单任务开发

```bash
cd /path/to/project
dev
```

1. 在 `codex` 或 `codex-claude` Window 中实现功能。
2. 在 `backend-frontend` Window 中运行应用。
3. 在 `services` Window 中观察 Docker 服务。
4. 在 `test` Window 中运行测试和 Lint。
5. 在 `git` Window 中使用 LazyGit 检查、提交和 Push。
6. 使用 `gh pr create --fill` 创建 PR。
7. 使用 `gh pr checks --watch` 等待 CI。

### 多任务并行开发

```bash
cd /path/to/project
newtask auth origin/main
newtask billing origin/main
dev /path/to/project_worktrees/auth
```

为另一个 Worktree 再运行一次 `dev`。每个 Worktree 会获得独立分支、目录和项目级 tmux Session。

### 离开和恢复

临时离开但保留进程：

```text
Ctrl+a d
```

恢复：

```bash
dev /path/to/project
```

如果 macOS 或 tmux 已经重启，可以尝试：

```text
Ctrl+a Ctrl+r
```

布局恢复后，按需重新启动 Codex、Claude、开发服务器或日志命令。

## 11. 卸载与恢复原配置

运行：

```bash
/Users/renyakun/work26/ai-dev-env-v1.0/uninstall.sh
```

卸载脚本会根据安装时记录的文件指纹恢复 Ghostty、tmux、Shell 和辅助命令配置。如果某个受管理文件在安装后被手动修改，脚本会保留它，避免覆盖用户改动。

卸载脚本不会删除：

- Homebrew 安装的软件；
- Ghostty、tmux 和 Git；
- 字体；
- TPM 与 tmux 插件；
- 历史备份。

## 12. 常见问题

### 找不到 `dev`、`newtask` 或 `ai-dev-doctor`

```bash
source ~/.zshrc
command -v dev
command -v newtask
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

同名 Session 已存在时，`dev` 会直接 Attach。先查看：

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

### Docker Window 只显示 Shell

只有项目根目录存在以下文件之一时，`dev` 才会自动运行 `docker compose ps`：

```text
compose.yml
compose.yaml
docker-compose.yml
docker-compose.yaml
```

同时确认 Docker Desktop 已经启动：

```bash
docker info
docker compose ps
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
| `dev` | `--no-codex` | No Codex | 不自动启动 Codex Pane |
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
