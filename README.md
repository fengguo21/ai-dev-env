# AI Dev Environment for macOS v1.2

Ghostty + tmux + Git worktree 工作台。用一个入口创建任务、切换工作区、启动项目、检查环境和收尾；默认以一个 AI 窗格开始，按需选择协作布局。

## 安装与升级

在本仓库目录运行：

~~~bash
./install.sh
source ~/.zshrc
ai-dev-doctor
~~~

安装器先验证候选 Ghostty/tmux 配置，再备份和替换；应用失败会回滚受管理文件和安装状态。已有安装指纹的文件若被手动修改，默认拒绝覆盖；先把个人修改移到覆盖层，或检查差异后使用 ./install.sh --replace-modified。首次安装会备份现有配置。

个人配置不会被安装器覆盖：

| 文件 | 用途 |
|---|---|
| ~/.tmux.local.conf | 自定义 tmux 按键、配色、插件 |
| ~/.config/ghostty/config.local | 字体、字号、Ghostty 偏好 |

~~~bash
./install.sh --skip-deps --no-reload
~~~

该选项使用已有依赖、跳过软件和插件安装，不重载正在运行的 tmux。普通安装会补装缺失的 tmux、Git、Ghostty、字体及可选 LazyGit、Delta、GitHub CLI、fzf；AI CLI 需自行安装和登录。安装 fzf 失败不影响文本任务命令。

## 日常使用

~~~bash
dev /path/to/project
task new auth
task list
task pick
task open auth
task open auth --resume
~~~

task 命令在对应 Git 仓库或其 worktree 内运行。task new 默认从当前 HEAD 创建 feature/auth 和独立 worktree，然后打开工作区；只创建不打开时加 --no-open。远程基准不会自动更新，需要时先 git fetch，再指定 origin/main。

~~~bash
task new auth origin/main --layout pair
task new billing --no-open
task open billing --start
~~~

每个 worktree 的 tmux 会话使用规范化完整路径的短哈希，连接前核对记录的目录。从仓库子目录运行 dev 会回到该 worktree 的同一个会话。界面显示可读的“仓库 / 任务”，中文名称保留。

newtask 仍兼容原来的创建方式：

~~~bash
newtask auth
newtask --print-path billing
AI_WORKTREE_ROOT=/path/to/worktrees newtask search
~~~

默认目录为主仓库旁的 <repository>_worktrees/<task>。设置 AI_WORKTREE_ROOT 后使用 <root>/<repository-id>/<task>，不同仓库的同名任务互不冲突；相对根目录按调用位置解析并输出绝对路径。已有旧路径的任务仍按 Git 的 worktree 登记查找。

## 布局与 AI 档位

| 选项 | 行为 |
|---|---|
| --layout focus | 默认：一个实现窗格，另有 app、services、test、git 窗口 |
| --layout pair | 实现与 Claude plan 模式审查并排 |
| --layout full | pair 基础上增加独立 Codex read-only 探索窗口 |
| --profile standard | 默认：尊重 Codex CLI 自身的模型和推理配置 |
| --profile deep | 按当前 CLI 模型目录的可见优先级及支持档位选择；保留原最强档工作流 |
| --no-ai | 所有 AI 窗格留在 Shell |
| --no-codex / --no-claude | 禁用对应 CLI 的自动启动 |
| --resume | 新工作区打开 AI 历史选择器，或恢复配置中指定的会话 ID |
| --unsafe | 仅显式启用时，为实现用 Codex 加权限绕过参数 |
| --detached | 创建但不附着，适合自动化 |

~~~bash
dev --layout pair
dev --profile deep
dev --layout full --profile deep
dev --no-ai
~~~

deep 沿用实验性 codex debug models 接口：实时查询最多约 5 秒，随后尝试 CLI 内置目录；失败时使用 CLI 默认配置，不再硬编码可能不可用的模型。目录优先级只是选择规则，不是跨模型质量基准。支持 Fast 时可以启用；codex_model、codex_effort、codex_fast 可在项目配置中覆盖。

默认不添加权限绕过参数，实际权限遵循 CLI 配置。Claude 的 plan 模式是协作约定的一部分；独立写代码的任务仍应使用不同 worktree。full 的探索会话不复用实现会话 ID。

已有 tmux 会话只重新连接，不会因 --start、--resume 或布局参数重复启动进程。tmux 恢复布局不等于恢复 AI 对话；--resume 不使用 --last 猜测会话。需要精确恢复可配置 codex_session / claude_session。旧版未记录目录身份的会话不会自动接管，可先从 Ctrl+a s 找回旧会话，或指定新的 --session 名称。

## 项目配置与启动

将 [配置示例](config/project.example.conf) 复制为项目根目录的 .ai-dev.conf，并按真实项目调整。它是纯 key=value 数据：不写 export、不在整个值外加引号，只支持整行注释，不执行 source 或 eval。

~~~ini
layout=pair
profile=standard
backend_dir=backend
frontend_dir=frontend
backend_cmd=uv run uvicorn app.main:app --reload --port "$BACKEND_PORT"
frontend_cmd=pnpm dev --port "$FRONTEND_PORT"
test_cmd=git diff --check
services_cmd=docker compose up
~~~

~~~bash
dev --plan
dev --check
dev --start
ai-dev-doctor --project /path/to/project
~~~

--plan 显示目录、布局、端口和命令，不启动程序，也不查询模型目录。--check 检查配置、目录、Shell 语法、简单命令的可执行文件和端口占用。只有 --start 执行配置中的服务/测试命令，命令使用 Bash 语法。

端口默认按 worktree 路径生成，也可用 backend_port、frontend_port 覆盖；所有新窗格获得 BACKEND_PORT、FRONTEND_PORT 和独立 COMPOSE_PROJECT_NAME。应用和 Compose 文件需要实际引用这些变量。检测冲突会提示修改配置；端口检查不提供原子租约，也不自动隔离数据库或缓存。

配置优先级：显式命令行选项 > .ai-dev.conf > 默认值。服务目录必须在当前 worktree 内。不会自动复制 .env、依赖目录或凭据。可以提交适合团队共享的配置；个人 AI 会话 ID 不应提交。

## 任务收尾

~~~bash
task done auth
task done auth --apply
~~~

默认只展示清理预览。执行清理要求任务目录干净、分支已合并到主 worktree 当前 HEAD（或 --base 指定提交）、提交可从本地远程跟踪引用到达，且没有关联 tmux 会话。先保存并结束相关会话，必要时 git fetch 更新远程引用。

被忽略的文件也会阻止清理，避免误删本地 .env 等文件。只有明确不需要它们时才加 --allow-ignored；本地未发布的任务可显式 --allow-unpushed；--keep-branch 保留分支，其余检查仍然有效。不会自动提交、推送、创建 PR、强制删除或终止工作中的会话。分支安全删除被 Git 拒绝时会保留分支并明确报告。

## 终端 UI

保留 Tokyo Night、等宽字体、不透明背景和 Ctrl+a 前缀。主要改进是稳定的角色标签、任务上下文、易读的非活动窗口文字及可发现的切换入口。角色标签不会被应用标题覆盖。

| 操作 | 快捷键 |
|---|---|
| 任务选择器 | Ctrl+a t |
| 会话/窗口树 | Ctrl+a s |
| 任务帮助 | Ctrl+a ? |
| 移动窗格 | Ctrl+a h/j/k/l |
| 放大当前窗格 | Ctrl+a z |
| 新窗口 / 拆分 | Ctrl+a c / \| / - |
| 分离会话 | Ctrl+a d |
| 重载配置 | Ctrl+a r |
| 保存 / 恢复布局 | Ctrl+a Ctrl+s / Ctrl+r |

task pick 有 fzf 时支持搜索；没有 fzf 时使用编号选择，非交互环境输出文本列表。命令输出保持纯文本，状态使用 clean/dirty 等文字。tmux 的颜色主题独立于 NO_COLOR；研究报告说明了这一区别。

[GitHub 与 UI 最佳实践调研](docs/research-best-practices.md) 实际比较了 tmux、fzf、sesh、tmuxinator、git-worktree-runner、zoxide、LazyGit、Gum，并交叉核对 Git、CLI Guidelines、NO_COLOR 与 W3C。建议和本轮落地、后续候选已分开记录。

## 验证与维护

~~~bash
python3 -m unittest discover -s tests -v
git diff --check
~~~

测试使用临时 Git 仓库、独立 tmux socket 和临时安装目标，不启动真实 AI、不改用户配置。覆盖同名任务、相对路径、配置执行边界、角色标签、半成品会话清理、安装回滚、体检误报和任务删除约束。真实 Ghostty 校验测试在该程序可用时运行。

~~~bash
./uninstall.sh
~~~

卸载按指纹恢复最近一次安装前的文件，保留后续修改、个人覆盖层、软件、插件和历史备份。它不是逐层回退全部历史安装。

更多：[环境指南](docs/ai-dev-environment-guide.md) · [命令参考](docs/command-reference.md) · [Git 工具指南](docs/git-tools-guide.md)。
