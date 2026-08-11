# AI Dev Environment 命令查询手册

本文是整套开发环境的命令速查手册。内容根据本项目脚本、当前已安装 CLI 的 `--help`，以及各工具官方文档核验，核验日期为 **2026-08-08**。

详细概念说明见：

- [AI Dev Environment 完整使用指南](ai-dev-environment-guide.md)
- [LazyGit、Git Diff 与 GitHub CLI 使用指南](git-tools-guide.md)

## 1. 使用说明

### 行尾注释

每条命令后面的 `# ...` 都是中文注释。

当前交互式 zsh 可能没有启用行尾注释。默认复制执行时，只复制 `#` 左侧的命令。如果想整行复制，先只复制并执行 `setopt interactivecomments`，不要带它后面的注释：

```zsh
setopt interactivecomments  # [Shell 设置] 让当前交互式 zsh 把 # 后面的内容当作注释；仅持续到当前 Shell 结束
```

### 风险标签

| 标签 | 含义 |
|---|---|
| `[只读]` | 查询信息，正常情况下不改变项目或远程状态 |
| `[启动]` | 启动交互程序、服务或长期运行进程 |
| `[本地修改]` | 修改本地文件、配置、分支、依赖或进程状态 |
| `[远程修改]` | 修改 GitHub、远程 Git 仓库或远程 CI 状态 |
| `[危险]` | 可能丢失未提交工作、停止进程或删除数据 |
| `[极高风险]` | 绕过安全边界，必须在外部严格隔离环境中使用 |

尖括号是占位符。例如 `<run-id>` 必须替换成真实运行编号，输入时不能保留 `<` 和 `>`。

### 常见缩写和符号

| 写法 | 全称或来源 | 记忆说明 |
|---|---|---|
| CLI | Command-Line Interface | 命令行界面，例如 `gh`、`codex` |
| TUI | Text-based User Interface / Terminal UI | 文本式终端交互界面，例如 LazyGit、Codex TUI |
| PR | Pull Request | 请求把一个分支的修改合并到另一个分支 |
| CI | Continuous Integration | 持续集成；自动执行测试、检查和构建 |
| MCP | Model Context Protocol | 模型上下文协议；让 AI 客户端连接工具和数据源 |
| TPM | Tmux Plugin Manager | tmux 插件管理器 |
| SSH | Secure Shell | 安全连接远程主机的协议和命令 |
| ASGI | Asynchronous Server Gateway Interface | Python 异步 Web Server 与应用之间的接口规范 |
| RGB | Red, Green, Blue | 红、绿、蓝三通道真彩色 |
| PATH | Path 环境变量；不是正式缩写 | Shell 查找可执行命令的目录列表 |
| HEAD | Git 的当前检出位置 | 不是缩写；通常指向当前分支的最新 Commit |
| `origin/main` | Remote-Tracking Branch | 本地保存的远程跟踪引用；运行 Fetch 后才会更新 |
| `--` | End of Options | 结束参数解析；Git 中常用来分隔 Revision 与文件路径 |
| `|` | Pipe | 把左侧命令的输出交给右侧命令处理 |

## 2. 最常用工作流

### 启动项目

```zsh
cd /path/to/project  # [Shell 状态] Change Directory，进入项目目录；替换为真实路径
dev  # [启动] Development，为当前目录创建或连接标准 tmux 工作区
dev /path/to/project  # [启动] 为指定项目或 Git Worktree 创建或连接工作区
```

### 检查、提交和创建 Pull Request

```zsh
git status --short --branch  # [只读] 紧凑显示分支、暂存区、工作区和未跟踪文件状态
git diff  # [只读] 查看已跟踪文件中尚未暂存的修改
git diff --staged  # [只读] 查看已经进入暂存区、准备提交的修改
lazygit  # [交互] 启动 Git TUI；启动本身不修改仓库，界面操作可能修改
gh pr create --fill  # [远程修改] 创建 PR；--fill 从 Commit 自动填充标题和正文
gh pr checks --watch  # [只读/等待] 持续观察当前 PR 的 CI 检查直到结束
```

### 创建并行任务

```zsh
git fetch origin  # [本地修改] 更新 origin 的远程跟踪引用；不会自动合并当前分支
newtask auth origin/main  # [本地修改] 从本地 origin/main 引用创建 feature/auth 分支和 Worktree
dev /path/to/repository_worktrees/auth  # [启动] 为新 Worktree 创建或连接独立 tmux 工作区
```

## 3. 安装、升级、检查和卸载

### 推荐安装方式

```zsh
/Users/renyakun/work26/ai-dev-env-v1.0/install.sh  # [本地修改/联网] 安装或升级本项目配置；操作前备份受管理文件，并补装缺失工具
source ~/.zshrc  # [Shell 状态] 在当前 Shell 重新执行 zsh 配置，使新增 PATH 立即生效
ai-dev-doctor  # [只读/诊断] 检查 Ghostty、tmux、Git、字体、主题、插件和辅助命令
```

该脚本会更新本项目管理的配置并安装缺失软件，但不会对已经安装的 CLI 自动执行 `brew upgrade`。如果本机还没有 Homebrew，脚本会调用 Homebrew 官方联网安装器。

### 可选的手工安装

优先使用上面的项目安装脚本。只有需要单独修复缺失软件时才使用下面命令。

```zsh
brew install --cask ghostty font-jetbrains-mono-nerd-font  # [本地修改/联网] Cask 安装 Ghostty 和 JetBrains Mono Nerd Font
brew install tmux git lazygit git-delta gh  # [本地修改/联网] 安装 tmux、Git、LazyGit、Delta 和 GitHub CLI
```

### 手工查询和升级 Homebrew 软件

项目脚本不会自动升级已经安装的软件。需要升级时先预览，再按工具类型执行：

```zsh
brew outdated --verbose  # [只读/联网] 查询有新版本的 Formula 和 Cask；-v = --verbose，显示版本详情
brew upgrade --dry-run tmux git lazygit git-delta gh  # [只读/联网] 预览 Formula 升级；-n = --dry-run，不实际安装
brew upgrade tmux git lazygit git-delta gh  # [本地修改/联网] 升级这组命令行 Formula；可能同时升级依赖
brew upgrade --cask ghostty font-jetbrains-mono-nerd-font  # [本地修改/联网] 升级 Ghostty 和字体 Cask
```

### 查询命令位置

```zsh
command -v dev  # [只读] 显示 Shell 实际会执行的 dev 路径；这里 -v 无长参数，不是 Version
command -v newtask  # [只读] 显示 newtask 的命令解析结果；-v 用于查询 Shell 将执行什么
command -v ai-dev-doctor  # [只读] 显示环境诊断命令的解析结果；PATH 中找不到时返回非零状态
command -v lazygit  # [只读] 显示 Shell 实际会执行的 LazyGit 路径、Alias 或 Function
command -v codex  # [只读] 显示 Shell 实际会执行的 Codex CLI 路径、Alias 或 Function
command -v claude  # [只读] 显示 Shell 实际会执行的 Claude Code 路径、Alias 或 Function
```

### 查询版本

```zsh
ghostty +version  # [只读] 显示 Ghostty 版本；+version 是 Ghostty Action
tmux -V  # [只读] 显示 tmux 版本；-V = Version，注意是大写 V
git --version  # [只读] 显示 Git 版本
lazygit --version  # [只读] 显示 LazyGit 版本
delta --version  # [只读] 显示 Delta 版本
gh --version  # [只读] 显示 GitHub CLI 版本
codex -V  # [只读] 显示 Codex CLI 版本；-V = --version
claude -v  # [只读] 显示 Claude Code 版本；-v = --version
docker --version  # [只读] 显示 Docker CLI 版本；不代表 Docker Daemon 已启动
docker compose version  # [只读] 显示 Docker Compose 插件版本
uv --version  # [只读] 显示 uv 版本；uv 是工具名称，不是正式缩写
python3 --version  # [只读] 显示当前 PATH 中的 Python 3 版本
node --version  # [只读] 显示当前 PATH 中的 Node.js 版本
pnpm --version  # [只读] 显示 pnpm 版本；pnpm 常解释为 performant npm
```

### 卸载配置

```zsh
/Users/renyakun/work26/ai-dev-env-v1.0/uninstall.sh  # [本地修改] 恢复安装前配置；保留软件、字体、插件和历史备份
```

## 4. Ghostty

macOS 上 Ghostty CLI 主要运行 `+action` 辅助动作。新开 GUI 应使用 macOS 的 `open`。

```zsh
open -na Ghostty.app  # [启动] macOS 新开 Ghostty 实例；-n = New Instance，-a = Application
ghostty +help  # [只读] 列出 Ghostty CLI 支持的 Action 和基本用法
ghostty +version  # [只读] 显示 Ghostty 版本和构建信息
ghostty +validate-config --config-file="$HOME/.config/ghostty/config"  # [只读] 验证指定 Ghostty 配置；config = Configuration
ghostty +show-config --changes-only  # [只读] 显示相对默认值发生变化的有效配置
ghostty +show-config --default --docs | less  # [只读] 显示全部默认配置及说明；Pipe 将输出交给 less 分页
ghostty +list-fonts | grep -F "JetBrainsMono Nerd Font Mono"  # [只读] 按固定字符串确认目标字体存在；-F = --fixed-strings
ghostty +list-themes | grep -F "TokyoNight Night"  # [只读] 确认 TokyoNight Night 主题存在
ghostty +list-keybinds --plain | less  # [只读] 以纯文本列出 Ghostty 快捷键并分页查看
ghostty +list-actions --docs | less  # [只读] 列出可绑定到按键的 Ghostty Action 及说明；不同于 CLI 的 +action
ghostty +list-colors --plain | less  # [只读] 列出 Ghostty 支持的命名 RGB 颜色；--plain 输出纯文本
ghostty +show-face --string="→"  # [只读] 查询 Ghostty 会用哪个 Font Face 渲染指定字符，可排查图标或字形问题
ghostty +ssh-cache  # [只读] 列出 SSH Terminfo 自动安装的缓存主机；Terminfo = Terminal Information 数据库
ghostty +edit-config  # [启动/可能修改] 用 VISUAL 或 EDITOR 指定的编辑器打开配置；保存后仍需手动 Reload
printf '\033[38;2;122;162;247mtruecolor sample\033[0m\n'  # [只读] 输出 RGB True Color 测试文字；RGB = Red/Green/Blue
```

官方参考：[Ghostty Configuration Reference](https://ghostty.org/docs/config/reference)。CLI Action 以当前安装版本的 `ghostty +help` 为准。

当前 macOS 安装虽然会在 `ghostty +help` 的通用 Action 列表中看到 `+new-window`，但执行 `ghostty +new-window --help` 会返回“不支持此平台”；新开实例仍使用 `open -na Ghostty.app`。

## 5. tmux

### Session 命令

```zsh
tmux list-sessions  # [只读] 列出全部 Session；tmux = Terminal Multiplexer
tmux new-session -d -s ai-demo -c /path/to/project  # [启动] 创建后台 Session；-d = Detached，-s = Session，-c = Starting Directory
tmux attach-session -t '=ai-demo'  # [启动] Attach 到指定 Session；-t = Target，前导 = 要求名称精确匹配
tmux switch-client -t '=ai-demo'  # [Shell 状态] 在 tmux 内把当前 Client 切换到指定 Session
tmux detach-client  # [Shell 状态] Detach 当前 Client，但保留 Session 中的进程
tmux rename-session -t '=ai-demo' ai-new  # [本地修改] 重命名指定 Session
tmux list-windows -t '=ai-demo'  # [只读] 列出指定 Session 的 Window
tmux list-panes -a  # [只读] 列出全部 Pane；-a = All
tmux display-message -p '#{pane_current_path}'  # [只读] 输出当前 Pane 的工作目录；-p = Print
tmux source-file "$HOME/.tmux.conf"  # [本地修改] 重新读取 tmux 配置并影响当前 Server
tmux list-keys | less  # [只读] 列出全部 tmux 按键绑定并分页查看
tmux show-options -gqv default-terminal  # [只读] 显示全局终端类型；-gqv = Global + Quiet + Value
tmux show-options -sqv terminal-features  # [只读] 显示服务器终端能力；-sqv = Server + Quiet + Value
tmux kill-session -t '=ai-demo'  # [危险] 结束指定 Session 以及其中全部 Pane 进程
tmux kill-server  # [极高风险] 结束整个 tmux Server、全部 Session 和其中进程
```

### tmux 快捷键

Prefix 是 `Ctrl+a`：按下并松开 `Ctrl+a`，再按后续按键。

```text
Ctrl+a c        # [本地修改] Create，新建 Window
Ctrl+a p        # [Shell 状态] Previous，切换到上一个 Window
Ctrl+a n        # [Shell 状态] Next，切换到下一个 Window
Ctrl+a 1～9     # [Shell 状态] 按编号切换 Window
Ctrl+a w        # [只读] Windows，打开 Window 列表
Ctrl+a |        # [本地修改] 左右分屏；当前配置调用 horizontal split
Ctrl+a -        # [本地修改] 上下分屏；当前配置调用 vertical split
Ctrl+a h/j/k/l  # [Shell 状态] 按 Vi 的左/下/上/右布局切换 Pane
Ctrl+a H/J/K/L  # [本地修改] 向左/下/上/右调整 Pane，每次 5 个终端单元格
Ctrl+a z        # [Shell 状态] Zoom，最大化或还原当前 Pane
Ctrl+a q        # [只读] 显示 Pane 编号
Ctrl+a [        # [只读] 进入 Copy Mode
Ctrl+a d        # [Shell 状态] Detach，离开 Session 但保留其中进程
Ctrl+a r        # [本地修改] Reload，重新加载 ~/.tmux.conf
Ctrl+a $        # [本地修改] 重命名当前 Session
Ctrl+a ?        # [只读] 查看 tmux 快捷键帮助
Ctrl+a I        # [本地修改/联网] TPM（Tmux Plugin Manager）安装配置中声明的插件；I 可记作 Install
Ctrl+a U        # [本地修改/联网] TPM 更新已安装插件；U = Update
Ctrl+a Alt+u    # [本地修改] TPM 移除配置中已经不再声明的插件；u = uninstall
Ctrl+a Ctrl+s   # [本地修改] tmux-resurrect 保存 Session、Window、Pane 和目录
Ctrl+a Ctrl+r   # [本地修改] tmux-resurrect 恢复之前保存的布局
```

Copy Mode 使用 Vi 按键：

```text
h/j/k/l  # [只读] 移动光标：左/下/上/右
v        # [只读] 开始选择
Ctrl+v   # [只读] 切换矩形选择
y        # [本地修改] Yank，把选中内容复制到剪贴板并退出 Copy Mode
```

```zsh
exit  # [本地修改] 退出当前 Shell；该 Shell 所在 Pane 通常会随之关闭
```

官方参考：[tmux(1) Manual](https://man.openbsd.org/tmux.1)、[tmux Wiki](https://github.com/tmux/tmux/wiki)、[TPM](https://github.com/tmux-plugins/tpm)、[tmux-resurrect](https://github.com/tmux-plugins/tmux-resurrect)。

## 6. `dev` 项目工作区

```zsh
dev  # [启动] Development，为当前目录创建或连接项目级 tmux 工作区
dev /path/to/project  # [启动] 为指定项目或 Worktree 创建或连接工作区
dev /path/to/project --session ai-demo  # [启动] 使用指定 Session 名；只允许字母、数字、下划线和连字符
dev /path/to/project --no-codex  # [启动] 新 Session 不启动三个 Codex Pane；Claude 仍会以危险权限启动
dev /path/to/project --session safe-demo --no-codex  # [启动] 用新 Session 名创建不自动启动 Codex 的工作区；仍不禁用 Claude
dev --help  # [只读] 显示 dev 用法和参数
```

注意：

- 默认新 Session 会启动三个 `codex --model gpt-5.6-sol --config model_reasoning_effort=ultra --config service_tier=fast --enable multi_agent --enable fast_mode --dangerously-bypass-approvals-and-sandbox` 和一个 `claude --dangerously-skip-permissions`。Codex 因此使用旗舰模型、最大推理与自动子代理委派，并选择更快但用量更高的 Fast 服务层。
- `--no-codex` 不等于 `--no-claude`；当前脚本没有后者。
- 同名 Session 已存在时，`dev` 直接 Attach，创建参数不会停止或改变已有进程。
- 需要普通 Claude 权限时，先结束右侧 Pane 中自动启动的 Claude，再手动运行不带危险参数的命令。

该命令的权威定义是本项目的 [dev 脚本](../dev)。

## 7. Codex CLI

### 启动、权限和会话

```zsh
codex  # [启动] 使用当前目录和默认配置启动交互式 Codex TUI
codex --model gpt-5.6-sol --config model_reasoning_effort=ultra --config service_tier=fast --enable multi_agent --enable fast_mode  # [启动/高用量] 使用旗舰模型、Ultra 自动委派和 Fast 服务层
codex -C /path/to/project  # [启动] 在指定工作根目录启动；-C = --cd = Change Directory
codex --sandbox read-only --ask-for-approval on-request  # [启动] 使用只读沙箱并按需批准；-s = --sandbox，-a = --ask-for-approval
codex --sandbox workspace-write --ask-for-approval on-request  # [启动] 允许工作区写入并按需批准；可短写为 -s workspace-write -a on-request
codex --no-alt-screen  # [启动] 禁用 Alternate Screen，让普通终端滚动历史保留输出
codex resume  # [启动] 打开当前目录的历史 Session 选择器
codex resume --last  # [启动] 直接继续当前目录最近一次 Session
codex resume --all  # [启动] 在选择器中显示所有目录的 Session
codex fork --last  # [启动/本地修改] 从最近 Session 分叉出独立对话
codex review --uncommitted  # [只读/AI] Review 当前未提交修改，不要求写代码
codex exec "检查当前项目并总结风险"  # [启动/非交互] 执行一次非交互任务后退出；实际权限遵循 Codex 配置
```

### 登录、诊断和帮助

```zsh
codex login  # [本地修改] 登录 OpenAI/Codex 并保存认证信息
codex login status  # [只读] 检查 Codex 登录状态
codex logout  # [本地修改] 删除本地保存的 Codex 登录凭据
codex doctor  # [只读/诊断] 检查 Codex 安装、配置、认证、Git、终端和运行环境
codex --help  # [只读] 显示 Codex CLI 帮助
codex -V  # [只读] 显示 Codex CLI 版本；-V = --version
codex update  # [本地修改/联网] 检查并更新支持自更新的 Codex CLI 版本
codex --dangerously-bypass-approvals-and-sandbox  # [极高风险] 跳过全部确认并关闭 Codex 沙箱；仅用于外部严格沙箱环境
```

### Codex TUI 斜杠命令

下面命令输入在 Codex 会话内部，不是 Shell 命令。

```text
/status       # [只读] 查看模型、权限、可写目录、Token 使用和 Session 状态
/permissions  # [Shell 状态] 调整当前会话的批准与权限预设
/model        # [Shell 状态] 切换当前会话模型
/diff         # [只读] 查看已暂存、未暂存和未跟踪文件变化
/review       # [只读/AI] 启动工作树代码 Review
/compact      # [本地修改] 总结较早对话以释放上下文空间
/resume       # [启动] 从选择器恢复已保存对话
/fork         # [本地修改] 把当前对话分叉成新的独立 Session
/new          # [本地修改] 在同一 CLI 中开始新对话
/clear        # [本地修改] 清除当前显示并开始新对话；不同于仅清屏
/init         # [本地修改] 在当前目录生成 AGENTS.md 模板
/mcp          # [只读] 查看 Model Context Protocol Server 和工具状态
/agent        # [Shell 状态] 查看并切换 Subagent 线程
/copy         # [本地修改] 复制最近一条已完成的 Codex 输出
/exit         # [Shell 状态] 退出 Codex CLI
```

官方参考：[OpenAI Codex Developer Commands](https://learn.chatgpt.com/docs/developer-commands)、[Agent Approvals & Security](https://learn.chatgpt.com/docs/agent-approvals-security)。危险参数即使在可信仓库中也可能暴露凭据和其他可访问文件。

## 8. Claude Code

```zsh
claude  # [启动] 使用当前目录和默认权限配置启动交互式 Claude Code
claude -c  # [启动] Continue，继续当前目录最近一次对话；-c = --continue
claude -r  # [启动] Resume，打开历史对话选择器；-r = --resume
claude -r <session-id>  # [启动] 按 Session ID 恢复指定对话；必须替换占位符
claude -r <session-id> --fork-session  # [启动/本地修改] 恢复后创建新 Session ID，保留原对话分支
claude --worktree auth  # [启动/本地修改] 为本次 Claude Session 创建名为 auth 的 Git Worktree；-w = --worktree
claude auth login  # [本地修改] 登录 Anthropic 账户
claude auth status --text  # [只读] 以可读文本显示认证状态
claude auth logout  # [本地修改] 退出账户并删除本地认证状态
claude doctor  # [只读/诊断] 检查 Claude Code 安装和配置
claude --safe-mode  # [启动] 禁用自定义指令、插件、Hook、MCP 等；它不是文件权限沙箱
claude -p "解释当前项目"  # [启动/非交互] Print 一次回答后退出；会跳过工作区信任对话，只在可信目录使用
claude --help  # [只读] 显示 Claude Code 帮助；-h = --help
claude -v  # [只读] 显示 Claude Code 版本；-v = --version
claude --dangerously-skip-permissions  # [极高风险] 绕过全部权限检查；官方只建议在无网络等严格隔离沙箱中使用
```

官方参考：[Claude Code CLI Reference](https://code.claude.com/docs/en/cli-reference)。命令同时与当前安装版本的 `claude --help` 核验。

## 9. `newtask` 与 Git Worktree

`newtask` 格式是 `newtask TASK_NAME [BASE_REF]`。`BASE_REF` 可省略，默认是 `HEAD`。

### 项目辅助命令

```zsh
newtask auth  # [本地修改] 从当前 HEAD 创建 feature/auth 分支和 auth Worktree
git fetch origin  # [本地修改] 更新 origin 的远程跟踪引用，但不合并当前分支
newtask pipeline origin/main  # [本地修改] 从本地 origin/main 引用创建 feature/pipeline 和 Worktree；需要最新基线时先 Fetch
AI_WORKTREE_ROOT=/path/to/worktrees newtask auth  # [本地修改] 只为本次命令临时指定 Worktree 根目录
export AI_WORKTREE_ROOT=/path/to/worktrees  # [Shell 状态] 为当前 Shell 及其子进程导出 Worktree 根目录
dev /path/to/repository_worktrees/auth  # [启动] 为创建出的 Worktree 启动独立项目工作区
```

### 原生 Git Worktree 命令

```zsh
git worktree list  # [只读] 列出主 Worktree 和全部关联 Worktree
git worktree list --verbose  # [只读] 显示 Worktree 路径、分支、锁定原因等详细信息；-v = --verbose
git worktree add ../project-auth feature/auth  # [本地修改] 在指定目录检出已经存在的 feature/auth 分支
git worktree add -b feature/auth ../project-auth origin/main  # [本地修改] 从 origin/main 创建新分支并建立 Worktree；-b 可记作 Branch
git worktree lock --reason "长期保留" ../project-auth  # [本地修改] 锁定 Worktree，防止被自动清理
git worktree unlock ../project-auth  # [本地修改] 解除 Worktree 锁定
git worktree move ../project-auth ../worktrees/auth  # [本地修改] 移动 Worktree 目录并更新 Git 管理信息
git worktree remove ../project-auth  # [危险] 删除干净的关联 Worktree 目录；对应分支不会自动删除
git worktree remove --force ../project-auth  # [危险] 强制删除有未提交修改或含 Submodule 的 Worktree；-f = --force
git worktree remove --force --force ../project-auth  # [极高风险] 强制删除锁定 Worktree；可能永久丢失未提交内容
git worktree prune --dry-run  # [只读] 预览将清理的失效 Worktree 管理记录；-n 是 --dry-run 的短写
git worktree prune --verbose  # [本地修改] 清理目录已不存在的失效 Worktree 管理记录并显示详情；-v = --verbose
git worktree repair ../project-auth  # [本地修改] 修复移动或损坏后的 Worktree 管理信息
```

### 删除任务分支

```zsh
git branch -d feature/auth  # [本地修改] -d = --delete，仅删除 Git 判断已合并的分支
git branch -D feature/auth  # [危险] -D = --delete --force，即使未合并也强制删除分支
```

主 Worktree 不能用 `git worktree remove` 删除。该辅助命令的权威定义是本项目的 [newtask 脚本](../newtask)，原生命令见 [Git Worktree 官方文档](https://git-scm.com/docs/git-worktree)。

## 10. LazyGit

### 启动命令

```zsh
lazygit  # [交互] 在当前 Git 仓库启动 LazyGit
lazygit --path /path/to/project  # [交互] 在指定仓库启动；--path 的短写是 -p
lazygit -p /path/to/project  # [交互] 与上一条等价；这里 -p = Path
lazygit status  # [交互] 启动后聚焦 Status/Files 面板；status 是位置参数
lazygit branch  # [交互] 启动后聚焦 Branches 面板；branch 是位置参数
lazygit log  # [交互] 启动后聚焦 Commits/Log 面板；log 是位置参数
lazygit stash  # [交互] 启动后聚焦 Stash 面板；stash 是位置参数
lazygit --config  # [只读] 输出 LazyGit 默认配置；--config 的短写是 -c
lazygit --print-config-dir  # [只读] 输出 LazyGit 配置目录；当前版本的短写是 -cd
lazygit --help  # [只读] 显示 LazyGit 参数和用法；-h = --help
lazygit --version  # [只读] 显示 LazyGit 版本；-v = --version
```

### 常用按键

同一按键会随面板改变。按 `?` 查看当前版本、当前面板的准确绑定。

```text
?      # [只读/全局] 打开当前面板按键菜单
Space  # [本地修改/Files] Stage 或 Unstage 选中文件
a      # [本地修改/Files] 暂存或取消暂存全部文件；a 可记作 All
c      # [本地修改/Files] Commit 已暂存内容
A      # [危险/Files] Amend 最近 Commit，并改变 Commit Hash
x      # [危险/Files] Discard 选中文件修改；确认目标后执行
D      # [危险/Files] 打开 Reset 选项；风险取决于随后选择的模式
s      # [本地修改/Files] Stash 工作区修改；不要与 Stage 暂存区混淆
f      # [本地修改/Files] Fetch 远程引用但不自动合并
p      # [本地修改/全局] Pull 当前分支并整合远程提交
P      # [远程修改/全局] Push 当前分支到 Upstream
n      # [本地修改/Branches] New，新建分支
Space  # [本地修改/Branches] Checkout，切换到选中分支
d      # [本地修改/Branches] Delete，删除选中分支
R      # [本地修改/Branches] Rename，重命名分支；其他面板的 R 可能是 Refresh/Reword
M      # [本地修改/Branches] Merge，把选中分支合并到当前分支
r      # [危险/Branches] Rebase，可能重写 Commit Hash
o      # [远程修改/Branches] 创建 Pull Request
G      # [只读/Branches] 在浏览器中打开 Pull Request
q      # [只读/全局] Quit，退出 LazyGit
```

官方参考：[LazyGit 官方仓库](https://github.com/jesseduffield/lazygit)、[官方 Keybindings](https://github.com/jesseduffield/lazygit/blob/master/docs/keybindings/Keybindings_en.md)。

## 11. Git 基础操作

### 状态和历史

```zsh
git status  # [只读] 查看分支、暂存区、工作区和未跟踪文件状态
git status --short  # [只读] 使用紧凑格式；--short 的短写是 -s
git status --branch  # [只读] 同时显示分支与跟踪信息；--branch 的短写是 -b
git status -sb  # [只读] -s = Short，-b = Branch；等价于 --short --branch
git log --oneline -5  # [只读] 每个 Commit 显示一行，最多显示 5 条；-5 = --max-count=5
git remote -v  # [只读] 显示 Remote 的 Fetch/Push 地址；-v = --verbose
git branch  # [只读] 列出本地分支；星号标记当前分支
git branch --all  # [只读] 列出本地和远程跟踪分支；-a = --all
git branch --show-current  # [只读] 显示当前分支名；Detached HEAD 时输出为空
git branch -vv  # [只读] 两次 Verbose，显示分支、Commit 和 Upstream 信息
```

### 暂存、提交和同步

```zsh
git add <files>  # [本地修改] 把指定文件当前内容加入 Index/暂存区；替换占位符
git add -p  # [本地修改/交互] -p = --patch，按 Hunk 选择要暂存的代码块
git diff --staged  # [只读] 提交前复查暂存区相对 HEAD 的修改
git commit -m "feat: describe the change"  # [本地修改] 创建 Commit；-m = --message，feat = Feature
git fetch origin  # [本地修改] 获取 origin 对象和引用，不自动合并当前分支
git pull  # [本地修改] Fetch 后再 Merge/Rebase；可能产生冲突
git push -u origin HEAD  # [远程修改] 推送当前分支，并用 -u/--set-upstream 建立上游跟踪
```

### 分支查询和修改

```zsh
git branch --remotes  # [只读] 只列出远程跟踪分支；-r = --remotes
git branch --merged main  # [只读] 列出已经合并进 main 的分支
git branch --no-merged main  # [只读] 列出尚未合并进 main 的分支
git branch --contains <commit>  # [只读] 列出包含指定 Commit 的分支；替换占位符
git switch feature/auth  # [本地修改] 切换到已有分支并更新工作区
git switch --create feature/auth origin/main  # [本地修改] 从 origin/main 创建并切换新分支；-c = --create
git branch --move feature/new-name  # [本地修改] 重命名当前分支；-m = --move
git branch --set-upstream-to=origin/main  # [本地修改] 设置当前分支的 Upstream；短写是 -u
git branch --unset-upstream  # [本地修改] 移除当前分支的 Upstream 配置
git branch -d feature/auth  # [本地修改] 安全删除已合并分支；-d = --delete
git branch -D feature/auth  # [危险] 强制删除未合并分支；-D = --delete --force
```

官方参考：[Git Status](https://git-scm.com/docs/git-status)、[Git Branch](https://git-scm.com/docs/git-branch)、[Git Push](https://git-scm.com/docs/git-push)。

## 12. Git Diff 与 Delta

### 工作区、暂存区和 Commit 比较

```zsh
git diff  # [只读] Difference，查看已跟踪文件中尚未暂存的修改；不显示未跟踪文件内容
git diff --staged  # [只读] 查看暂存区相对 HEAD 的修改
git diff --cached  # [只读] 与 --staged 等价；Cache/Index 在这里都指暂存区
git diff HEAD  # [只读] 查看已跟踪文件中已暂存和未暂存的全部修改
git diff -- src/app.ts  # [只读] 只比较指定文件；-- 结束参数解析，后面按路径处理
git diff -- frontend/src/  # [只读] 只比较指定目录
git diff --name-only  # [只读] 只列出发生变化的文件名
git diff --stat  # [只读] Statistics，显示文件数与增删行摘要
git diff --word-diff  # [只读] 按单词粒度显示差异
```

### Commit 和分支比较

```zsh
git diff HEAD~1 HEAD  # [只读] 比较 HEAD 的第一父提交与当前提交；~1 表示沿第一父提交后退一步
git diff <old-commit> <new-commit>  # [只读] 比较两个 Commit；必须替换两个占位符
git diff main..feature/login  # [只读] 对 git diff 而言，双点比较两个端点快照
git diff main...HEAD  # [只读] 三点比较共同祖先到 HEAD 的已提交修改；不含工作区未提交内容
git diff origin/main...HEAD  # [只读] 与本地远程跟踪引用比较；需要最新结果时先 git fetch origin
git diff -S'functionName'  # [只读] 筛选字面字符串出现次数发生变化的文件；-S 没有官方长参数
git diff -G'<regular-expression>'  # [只读] 筛选新增/删除行可匹配正则表达式的差异；-G 没有官方长参数
git diff --patch  # [只读] 输出 Patch 格式；短写 -p，普通 git diff 默认如此
git --no-pager diff  # [只读] 不启动 Pager，因此绕过 Delta/less 并直接输出到终端
```

### 系统 `diff`

```zsh
diff -u old.txt new.txt  # [只读] Unified 格式比较两个普通文件；这里 -u = --unified
diff -ru old-directory new-directory  # [只读] Recursive + Unified，递归比较两个普通目录
```

### Delta 查询

```zsh
delta --help  # [只读] 显示 Delta 完整手册
git config --global --get core.pager  # [只读] 查询 Git 全局 Pager，当前配置应显示 delta
git config --global --get interactive.diffFilter  # [只读] 查询交互式 Diff Filter
git config --global --get delta.navigate  # [只读] 查询 Delta 文件间导航配置
git config --global --get delta.line-numbers  # [只读] 查询 Delta 行号配置
```

Delta 只改变显示，不修改 Git 数据。官方参考：[Git Diff](https://git-scm.com/docs/git-diff)、[Delta User Manual](https://dandavison.github.io/delta/)。

## 13. GitHub CLI：`gh`

### 认证和仓库

```zsh
gh auth status  # [只读] Authentication，查看当前 GitHub 登录状态
gh auth login  # [本地修改] 登录 GitHub 并保存认证信息
gh auth switch  # [本地修改] 交互切换当前使用的 GitHub 账户
gh repo view  # [只读] Repository，查看当前 GitHub 仓库
gh repo view --web  # [启动] 在浏览器中打开当前仓库
gh browse  # [启动] 在浏览器中打开当前仓库页面
gh repo clone owner/repository  # [本地修改] Clone GitHub 仓库到本地新目录
gh repo fork owner/repository --clone  # [远程+本地修改] 创建账户下的远程 Fork，并 Clone 到本地
```

### Pull Request

```zsh
gh pr list  # [只读] PR = Pull Request，列出 Pull Request
gh pr view  # [只读] 查看当前分支对应的 Pull Request
gh pr diff  # [只读] 查看当前 Pull Request 的代码差异
gh pr create  # [远程修改] 交互创建 Pull Request；分支未 Push 时可能提示推送或 Fork
gh pr create --fill  # [远程修改] 从 Commit 自动填充 PR 标题和正文；-f = --fill
gh pr create --draft --fill  # [远程修改] 创建 Draft PR 并自动填充内容；-d = --draft
gh pr checkout 123  # [本地修改] 获取编号 123 的 PR 并切换本地分支
gh pr checks  # [只读] 查看当前 PR 的 CI（Continuous Integration，持续集成）和状态检查
gh pr checks --watch  # [只读/等待] 持续刷新检查状态直到全部结束
gh pr merge  # [危险/远程修改] 合并当前 Pull Request，改变目标分支和 GitHub 状态
```

### GitHub Actions

```zsh
gh run list  # [只读] 列出 GitHub Actions Workflow Run
gh run view <run-id>  # [只读] 查看指定 Run；run-id = Run Identifier
gh run view <run-id> --log-failed  # [只读] 只显示失败步骤的日志
gh run watch <run-id>  # [只读/等待] 持续显示指定 Run 的状态
gh run rerun <run-id> --failed  # [远程修改] 重新运行失败 Job 及其依赖
```

### Issue 和帮助

```zsh
gh issue list  # [只读] 列出仓库 Issue
gh issue view 123  # [只读] 查看编号 123 的 Issue
gh issue create  # [远程修改] 交互创建新的 GitHub Issue
gh --help  # [只读] 显示 GitHub CLI 顶层帮助
gh pr --help  # [只读] 显示 Pull Request 子命令帮助
gh pr create --help  # [只读] 显示创建 Pull Request 的全部参数
gh run view --help  # [只读] 显示查看 Actions Run 的全部参数
```

官方参考：[GitHub CLI Manual](https://cli.github.com/manual/)。

## 14. Docker 与 Docker Compose

```zsh
docker --version  # [只读] 显示 Docker CLI 版本；不检查 Daemon 是否已经运行
docker compose version  # [只读] 显示 Docker Compose 插件版本
docker info  # [只读] 显示 Docker Client/Daemon 信息，也可检查 Docker Desktop 是否启动
docker compose config  # [只读] 解析并显示合并后的 Compose 配置，可用于语法检查
docker compose ps  # [只读] 显示当前 Compose 项目的服务和容器状态；ps = Process Status
docker compose pull  # [本地修改/联网] 拉取 Compose 服务镜像，但不启动容器
docker compose up -d  # [本地修改] 创建或重建并启动服务；-d = --detach，在后台运行
docker compose logs -f  # [只读/等待] 持续跟随服务日志；-f = --follow，Ctrl+C 不会停止容器
docker compose restart  # [本地修改] 重启当前 Compose 项目的服务容器
docker compose down  # [本地修改] 停止并移除项目容器与网络；默认保留数据卷
docker compose down -v  # [危险] 同时删除 Compose 命名卷和容器匿名卷；-v = --volumes，数据可能不可恢复
```

这些命令通常应在包含 `compose.yml`、`compose.yaml`、`docker-compose.yml` 或 `docker-compose.yaml` 的项目目录运行。

官方参考：[Docker Compose CLI Reference](https://docs.docker.com/reference/cli/docker/compose/)、[docker compose up](https://docs.docker.com/reference/cli/docker/compose/up/)、[docker compose down](https://docs.docker.com/reference/cli/docker/compose/down/)。

## 15. Python、uv、Uvicorn 和 pytest

```zsh
uv --version  # [只读] 显示 uv 版本；uv 是工具品牌名，没有需要展开的官方全称
python3 --version  # [只读] 显示当前 PATH 中 Python 3 的版本
uv run python --version  # [只读/可能同步] 显示项目环境 Python 版本；uv run 可能先调整项目环境
uv sync  # [本地修改] 按 pyproject.toml 和 uv.lock 同步项目环境，可能更新 uv.lock 和 .venv
uv run pytest  # [测试/可能同步] 在 uv 项目环境运行 pytest；测试副作用取决于项目
uv run uvicorn <module>:<app> --reload  # [启动/长期运行] 启动 ASGI（Asynchronous Server Gateway Interface）服务；代码变化后自动 Reload
```

例如，项目入口是 `app/main.py` 中的 `app` 对象时，把占位符换成 `app.main:app`。

官方参考：[uv CLI Reference](https://docs.astral.sh/uv/reference/cli/)、[Uvicorn Settings](https://www.uvicorn.org/settings/)、[pytest Reference](https://docs.pytest.org/en/stable/reference/reference.html)。

## 16. Node.js 与 pnpm

```zsh
node --version  # [只读] 显示当前 PATH 中 Node.js 版本
pnpm --version  # [只读] 显示 pnpm 版本；pnpm 常解释为 performant npm
pnpm install  # [本地修改/供应链注意] 安装依赖，修改 node_modules，可能更新 Lockfile 并运行依赖脚本
pnpm dev  # [启动/项目脚本] 执行 package.json 的 dev 脚本；等价于 pnpm run dev
pnpm test  # [测试/项目脚本] 执行 package.json 的 test 脚本；具体工具和副作用由项目定义
pnpm lint  # [检查/可能修改] 执行 lint 脚本；如果脚本包含 Fix 选项，可能修改源码
pnpm build  # [本地修改] 执行 build 脚本，通常生成 dist、build 等构建产物
```

官方参考：[pnpm CLI](https://pnpm.io/pnpm-cli)、[pnpm run](https://pnpm.io/cli/run)。

## 17. 故障排查命令

```zsh
ai-dev-doctor  # [只读/诊断] 执行整套环境检查，优先处理输出中的 FAIL
ghostty +validate-config --config-file="$HOME/.config/ghostty/config"  # [只读] 验证 Ghostty 配置语法
ghostty +list-fonts | grep -F "JetBrainsMono Nerd Font Mono"  # [只读] 检查 Nerd Font 是否可见
tmux show-options -gqv default-terminal  # [只读] 检查 tmux 默认终端类型
tmux show-options -sqv terminal-features  # [只读] 检查 tmux Server 的终端能力
tmux list-sessions  # [只读] 检查 dev 对应 Session 是否已经存在
git rev-parse --is-inside-work-tree  # [只读] 判断当前目录是否位于 Git Worktree 中
git status --short --branch  # [只读] 快速检查 Git 分支和文件状态
git remote -v  # [只读] 检查 Git Remote 地址
gh auth status  # [只读] 检查 GitHub CLI 登录状态
docker info  # [只读] 检查 Docker Daemon 是否运行
docker compose ps  # [只读] 检查 Compose 服务状态
codex doctor  # [只读/诊断] 检查 Codex 安装、配置、认证和运行环境
claude doctor  # [只读/诊断] 检查 Claude Code 安装和配置
tmux kill-session -t '=exact-session-name'  # [危险] 结束准确匹配的 Session 及其中全部进程；先确认名称
```

## 18. 官方资料索引

以下资料在 2026-08-08 用于核对本手册。项目辅助命令以本仓库脚本为准；外部工具以当前安装版本的 `--help` 和官方文档共同为准。

| 工具 | 官方资料 |
|---|---|
| 本项目 | [README](../README.md)、[install.sh](../install.sh)、[doctor](../doctor)、[dev](../dev)、[newtask](../newtask)、[uninstall.sh](../uninstall.sh) |
| zsh / Shell | [Builtin Commands](https://zsh.sourceforge.io/Doc/Release/Shell-Builtin-Commands.html)、[Options](https://zsh.sourceforge.io/Doc/Release/Options.html)、本机 `man open` / `man grep` / `man less` |
| Homebrew | [Manpage](https://docs.brew.sh/Manpage) |
| Ghostty | [Configuration Reference](https://ghostty.org/docs/config/reference)、本机 `ghostty +help` |
| tmux | [tmux(1) Manual](https://man.openbsd.org/tmux.1)、[Official Wiki](https://github.com/tmux/tmux/wiki) |
| tmux 插件 | [TPM](https://github.com/tmux-plugins/tpm)、[tmux-resurrect](https://github.com/tmux-plugins/tmux-resurrect)、[tmux-continuum](https://github.com/tmux-plugins/tmux-continuum)、[tmux-yank](https://github.com/tmux-plugins/tmux-yank) |
| Codex | [Developer Commands](https://learn.chatgpt.com/docs/developer-commands)、[Agent Approvals & Security](https://learn.chatgpt.com/docs/agent-approvals-security) |
| Claude Code | [CLI Reference](https://code.claude.com/docs/en/cli-reference)、本机 `claude --help` |
| Git | [Git Reference](https://git-scm.com/docs)、[git-diff](https://git-scm.com/docs/git-diff)、[git-worktree](https://git-scm.com/docs/git-worktree) |
| LazyGit | [Official Repository](https://github.com/jesseduffield/lazygit)、[Keybindings](https://github.com/jesseduffield/lazygit/blob/master/docs/keybindings/Keybindings_en.md) |
| Delta | [User Manual](https://dandavison.github.io/delta/)、[Official Repository](https://github.com/dandavison/delta) |
| GitHub CLI | [Official Manual](https://cli.github.com/manual/) |
| Docker Compose | [CLI Reference](https://docs.docker.com/reference/cli/docker/compose/) |
| Python | [Command Line and Environment](https://docs.python.org/3/using/cmdline.html) |
| uv | [CLI Reference](https://docs.astral.sh/uv/reference/cli/) |
| Uvicorn | [Settings](https://www.uvicorn.org/settings/) |
| pytest | [Reference](https://docs.pytest.org/en/stable/reference/reference.html) |
| Node.js | [Command-line API](https://nodejs.org/api/cli.html) |
| pnpm | [CLI](https://pnpm.io/pnpm-cli)、[Run Scripts](https://pnpm.io/cli/run) |

官方文档会随版本变化。如果手册与当前安装工具不一致，先运行该工具的 `--help`，再对照上面的官方链接。
