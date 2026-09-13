# 终端开发工作台最佳实践调研

调研日期：2026-09-08。适用环境：macOS、Ghostty、tmux、Git worktree，以及 Codex / Claude Code 等终端 AI 工具。

2026-09-09 修正：按用户要求，默认恢复 `classic + deep`，即原来的 `codex`、`codex-claude`、`backend-frontend`、`services`、`test`、`git` 六窗口、九窗格，包含三个 Codex 和一个普通模式 Claude。`focus`、`pair`、`full` 与 `standard` 保留为显式选项。下文保留 2026-09-08 的调研和设计建议，不再将精简布局视为用户的默认选择。

这套工具最值得投入的方向是：让用户随时知道正在操作哪个任务，让创建、切换、检查、收尾形成连续工作流，再用可选的模糊选择和清楚的窗格标签减少记忆成本。项目配置应让环境可重复启动；更复杂的会话管理器和完整 TUI 框架可以等实际需求出现后再引入。

本文是调研结论和设计依据；“本轮采用”表示适合本次实现的方向，具体已实现命令、默认值和限制以 [README](../README.md) 与 [命令参考](command-reference.md) 为准。文中标为“后续”的能力不应理解为已经实现。

## 调研方法与范围

实际访问 GitHub Search API，先以 `tmux worktree session in:readme` 广泛检索，再以以下查询缩小到工具本身：

- [`tmux session manager in:description`](https://api.github.com/search/repositories?q=tmux+session+manager+in%3Adescription&sort=stars&order=desc&per_page=6)
- [`git worktree manager in:description`](https://api.github.com/search/repositories?q=git+worktree+manager+in%3Adescription&sort=stars&order=desc&per_page=6)

检索结果包括 sesh、tmuxp、tmux-sessionx、git-worktree-runner、gwq 等。随后阅读与本仓库最相关的 8 个项目的官方 README 或手册，并用 Git 官方文档、Command Line Interface Guidelines、NO_COLOR 和 W3C 对照具体行为。选择依据是工作流相关性、集成成本和可验证的功能，排序只用于发现候选，不把 Star 数当作效果证据。

读取 GitHub 文档主要使用 `api.github.com/repos/<owner>/<repo>/readme` 或 `contents/<path>`，请求 `application/vnd.github.raw+json`。最初访问 `raw.githubusercontent.com` 有两次超时，改用 GitHub API 后取得所需正文；这不影响后续报告，但说明当前网络路径存在差异。

本次没有安装或运行所有第三方工具，没有做耗时、内存、费用或任务成功率的横向基准，也没有将项目 README 的营销描述当作独立验证。页面来自检索当日的默认分支，内容以后可能变化。终端配色借用 WCAG 对比度作为设计参考，不能据此宣称整个终端或本工具通过了完整无障碍认证。

Codex 参数核对另尝试了官方开发者站 CLI reference/features 页面，返回 HTTP 403；官方域名搜索超时，Platform 页面返回访问限制。本轮未据此宣称最新模型或价格已经在线验证。实现使用本机 `codex --help`、`codex resume --help` 与 `claude --help` 核对启动、恢复和权限参数；模型目录继续视为实验性接口，查询失败回到 CLI 默认配置。

## 候选工具与采用决策

| 来源 | 文档中确认的能力 | 对本工具的决定 | 原因与边界 |
|---|---|---|---|
| [tmux](https://github.com/tmux/tmux/blob/master/tmux.1) | `choose-tree`、窗格标题、路径和进程格式变量、`remain-on-exit` / `respawn-pane` | 本轮采用原生导航、角色标签、明确的活动窗格；失败恢复按需使用原生命令 | 已有核心依赖，能覆盖大量 UI 需求；不同版本选项有差异，需要本机验证 |
| [fzf](https://github.com/junegunn/fzf#readme) | 模糊筛选、局部高度、键盘选择、预览、可组合的文本输入输出 | 本轮采用可选 `task pick`，保留 `task list` / `task open` | 把任务路径记忆转为识别；不应成为创建和打开任务的硬依赖 |
| [sesh](https://github.com/joshmedeski/sesh#readme) | 会话选择、zoxide 集成、项目启动命令、last/root navigation、可配置窗口和预览 | 本轮借鉴快速切换与项目上下文；后续再评估完整集成 | 其会话管理与本工具重叠；同时维护两个入口会增加命名和配置来源的不确定性 |
| [tmuxinator](https://github.com/tmuxinator/tmuxinator#readme) | 项目 YAML、窗口与窗格配置、独立工作目录、启动焦点、`debug` / `doctor` | 本轮借鉴声明式项目配置及体检；暂不添加 Ruby 管理器 | 当前少量稳定布局可用现有脚本实现；任意窗口拓扑成为真实需求时再考虑替换 |
| [git-worktree-runner](https://github.com/coderabbitai/git-worktree-runner#readme) | 仓库范围的任务、创建与打开、PR worktree、hooks、可解析输出、配置复制 | 本轮借鉴任务生命周期和仓库范围；PR 导入、hooks 和配置复制后续单独设计 | 与当前 Bash + macOS 结构接近；hooks 和复制 `.env` 带来明确的代码执行与机密边界 |
| [zoxide](https://github.com/ajeetdsouza/zoxide#readme) | 根据常用目录快速跳转，`zi` 使用 fzf 选择 | 后续作为个人可选增强 | 目录历史不等于 Git 任务清单；不能替代 `git worktree list` 的事实来源 |
| [LazyGit](https://github.com/jesseduffield/lazygit#readme) | 文件和行级暂存、差异审查、分支、worktree、过滤 | 保留现有 Git 窗口和文本回退 | 已经有成熟 Git UI，任务工具只需要提供入口和任务状态，无需再造 Git 操作界面 |
| [Gum](https://github.com/charmbracelet/gum#readme) | 选择、过滤、输入、确认、表格、进度显示 | 暂缓引入 | 现阶段 fzf 加原生 tmux 足够；出现多步初始化表单后再评估，避免仅为装饰增加依赖 |

这不是要求同时安装表中所有工具。当前最合适的组合仍是 Ghostty + tmux + 本仓库任务命令 + LazyGit，fzf 提供可选选择界面。

## UI：首先解决位置、焦点和操作入口

### 信息架构

界面应该以“项目 → 任务 / worktree → 角色窗格”组织。状态栏显示简短项目和任务，窗格边框显示 `implement`、`review`、`backend`、`frontend`、`test` 等角色。AI CLI 的名称可以保留，但只写三个相同的 `codex` 很难说明分工。

人看到的名称与程序使用的身份应分开。界面使用可读短名；tmux 会话 ID 使用规范化路径对应的稳定短哈希，连接前核对会话保存的工作目录。两个不同仓库的 `auth` 任务不能因为显示名相同而连接到同一会话。同样，共用 worktree 根目录时应先按仓库标识分组。

任务列表优先显示任务、分支、修改状态和会话是否存在。完整路径可放在末列或按需显示；状态不应只用颜色表达。任务名称中含空格等特殊字符时，应保留原始路径作为内部数据，不能把屏幕上按空格对齐的文本拆回路径。

### 默认布局与渐进展示

2026-09-08 的调研建议是提供少量语义明确的布局。以下是当时的布局方向；当前默认按用户要求恢复 classic，精简与角色协作布局供显式选择：

| 布局方向 | 适用工作 | 主要视图 |
|---|---|---|
| focused | 日常单项实现、笔记本屏幕 | 一个主要 AI 工作区，其余服务与 Git 按窗口切换 |
| review | 需要实现与审查协作 | 实现与审查角色并排；在开始时明确谁可以修改哪些文件 |
| full | 已经明确分工的高并行工作 | 保留原先多 AI 能力，窗口和窗格各有稳定角色标签 |

布局本身不会隔离文件系统，也不会把标为 `review` 的 AI 自动变成只读。独立写代码的任务应在不同 worktree 执行；同一任务内的多个 AI 必须明确修改范围。并排窗格适合比较，阅读长 diff 或长推理输出时使用 tmux zoom。

笔记本上先检验正文宽度是否足够；窄终端优先收起路径、时钟等次要信息，保留项目、任务和活动窗口。不要在状态栏每秒执行多个昂贵 Git / 网络查询。分支等动态信息如果缓存，应注明更新边界，避免把启动时的分支名误当成实时状态。

### 键盘导航与可发现性

保留现有 `Ctrl+a` 前缀和 `h/j/k/l` 习惯，结合 tmux 原生会话 / 窗口树与一个任务选择入口。帮助页应该列出少量高频操作，并提供 `--help` 完整说明。后续增加 shell completion，比再增加一套自定义全局快捷键更容易学习。

fzf 官方 README 明确列出 Enter 选择、Esc / Ctrl+C 取消，以及 Ctrl+J / Ctrl+K 等导航键。任务选择器应在界面上显示这些键，取消时退出，不执行默认任务。没有 fzf 或没有交互终端时，用户仍可使用文本列表和明确的任务参数。

选择器用局部参数配置，例如 `--height`、`--layout reverse`、`--border`。预览适合展示所选任务的路径与 `git status`，应保持只读。fzf 文档提醒不要把文件专用预览写入全局 `FZF_DEFAULT_OPTS`，因为其他调用的输入可能是任务名、历史或进程。

### 可读性与无障碍

保留不透明背景和稳定等宽字体；高亮只用于活动项、选中项和必要的状态。用 `dirty`、`clean`、`open` 等文字表达状态，Nerd Font 图标作为可选补充，普通字体或远程终端仍应能看懂。避免用一组红绿圆点承载全部意义。

[WCAG Contrast Minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) 对一般文字提供 4.5:1 的对比度参考；终端状态栏和次要文字也应测量，不能只确认主题正文。它是本项目配色的工程参考，不是终端专用认证要求。

普通 CLI 输出在非 TTY、`TERM=dumb` 或非空 `NO_COLOR` 时应保持纯文本；没有添加颜色的命令天然满足这部分要求。`NO_COLOR` 是输出约定，不代表 tmux 主题会自动切换，也不代表所有子程序都已经支持。不要在重定向输出或 CI 日志中加入动画；详细错误应能复制为文本。

### 输出与错误措辞

[Command Line Interface Guidelines](https://clig.dev/#output) 建议主体结果写 stdout，进度与错误写 stderr；成功信息简短，状态变化明确。给人看的表格和给脚本的稳定格式不能互相污染。后续 `--json` 或 `--porcelain` 应承诺字段和退出码，而不是让调用方解析带边框的界面。

错误至少解释“哪一步失败、哪个对象、下一步怎么处理”。例如：

```text
无法打开任务 auth：worktree 目录不存在。
目录：/path/to/repo_worktrees/auth
运行 task list 查看当前仓库的任务。
```

删除前检查失败时应指出未提交文件、未发布提交或运行中的会话等具体原因。避免仅返回 `failed` 或完整内部调用栈；调试细节可以另设详细模式。向用户展示可执行的下一步，并不意味着自动执行提交、推送或删除。

## 工作流与配置的最佳实践

### 一条任务生命周期

创建任务时创建分支和 worktree，然后打开对应工作台；再次打开时复用同一会话。列表只从当前 Git 仓库的 worktree 记录确定真实任务，再关联 tmux 状态。可提供路径输出，方便编辑器和其他命令复用。

`task done` 的含义应明确为本地收尾。它不应默默提交、推送、合并 PR，或强制删除尚未保存的内容。删除前核对目标属于当前仓库、不是主 worktree，检查已跟踪和未跟踪内容、必要的被忽略文件、提交是否已有可保留的引用，以及会话是否仍有工作。

[Git 官方手册](https://git-scm.com/docs/git-worktree) 说明 `git worktree remove` 默认只处理干净 worktree；不要用 `rm -rf` 绕过 Git 的登记和检查。worktree 清理与分支删除是不同操作，保留分支能保留提交，但不能找回未提交文件。锁定 worktree 或带子模块的情况应交给 Git 报告限制。

脚本读取 worktree 列表优先使用 `git worktree list --porcelain -z`；Git 明确保证 porcelain 格式稳定，并推荐 NUL 分隔以处理路径中的换行。不能只因为路径“通常没有空格”就使用未经约定的文本切割。

### 声明式项目配置

把服务目录、启动命令、测试命令、布局和端口写进项目配置，降低每次启动手工输入的成本。参考 tmuxinator 的按项目 root、窗口和 pane 的配置思路；当前需求不必立刻支持任意脚本钩子和复杂模板语言。

配置加载阶段只解析数据，拒绝未知字段或错误类型，不应通过 `source` 或 `eval` 执行整个配置文件。字段里允许服务命令，意味着运行项目时仍会执行项目代码；命令入口与自动运行行为必须明确。能够查看解析后的配置和启动计划，会让排错更直接。

项目共享配置与机器个人配置分层。升级安装的默认 Ghostty / tmux 文件时保留个人覆盖层，使个人字体、快捷键和本机路径不会反复与工具升级冲突。配置优先级必须在帮助中写清，并对目录不存在和端口非法给出明确错误。

不默认批量复制 `.env`、凭据、`node_modules` 或整个主仓库到每个 worktree。确需复制或链接时，使用明确白名单和项目约定。git-worktree-runner 提供配置复制和 hooks 是功能事实，不代表在本项目自动启用它们就是合适的默认值。

### 端口与资源隔离

不同 worktree 需要独立的应用端口；后台服务命令从明确的环境变量取值。稳定的任务标识可以生成候选端口，但哈希不能保证无冲突，启动前还需要检查占用，并显示实际使用的地址。检查到启动之间存在竞争窗口，服务最终监听失败仍需保留错误输出。

应用不读取分配的端口变量时，自动分配没有效果；固定写死的命令要改为读取配置。Docker Compose 的项目名、数据库名、缓存前缀和临时目录也可能冲突，端口隔离不能代替这些资源的独立配置。完整端口租约、反向代理域名和数据库生命周期暂列后续需求。

### AI 上下文与安全边界

worktree 隔离的是工作目录与部分 Git 状态。Git 手册说明许多 refs 和默认 repository config 在 worktree 间共享；它不是操作系统沙箱。终端 AI 仍可能访问本机网络、其他目录和凭据，具体能力由 CLI 权限和运行环境决定。

模型、推理档位、布局、自动启动数量和权限策略应分别可配置。恢复 tmux 布局不等于恢复 AI 对话；对话恢复使用相应 CLI 的正式恢复功能，必要时保留用户选择。项目内的任务说明、已完成工作和测试命令应该简短、可复用，避免每开一个窗格重复灌入大量无关上下文。

git-worktree-runner 的 [AI Agent Usage](https://github.com/coderabbitai/git-worktree-runner/blob/main/docs/agent-usage.md) 值得借鉴的是：直接用稳定 CLI 即可完成生命周期，输出包含路径和状态，并明确 hooks 的执行边界。本项目没有必要为了这些本地操作额外引入 MCP 服务。

### 验证、安装和恢复

tmux 官方手册说明，启动时的配置错误会在第一个会话中展示，解析还会继续；因此“能创建 tmux 会话”不是“配置完全正确”的证据。体检应在隔离 socket 显式执行 `source-file` 并检查错误，再检查所需版本和关键能力。

安装先在暂存位置验证完整配置，再替换受管理文件，失败时恢复备份。检查范围不仅是 `bash -n`：会话名称碰撞、相同任务名、已有修改的 worktree、不正确配置和不可用命令，都需要针对实际风险验证。插件恢复应明确只能恢复哪些状态，不宣称任意长时间运行的 AI 进程能无损重启。

## 本轮优先级与后续验证

| 优先级 | 应交付的结果 | 验证重点 |
|---|---|---|
| 本轮 | 会话与 worktree 按仓库 / 路径区分 | 不同仓库同名目录、同名任务不会串会话；路径身份与会话记录一致 |
| 本轮 | 创建、列表、打开、选择、收尾组成任务命令 | 取消选择无副作用；未提交或未发布内容保留；路径正确引用 |
| 本轮 | 项目配置、清楚的布局与角色标题 | 配置错误提前失败；启动目录与命令一致；新旧布局均可理解 |
| 本轮 | 真实配置体检、安装回滚和个人覆盖层 | 无效 tmux 选项会报错；失败安装可恢复；用户修改不被覆盖 |
| 后续 | 任务详情预览、补全、稳定结构化输出 | 不解析显示文本；非交互环境可运行；预览保持只读 |
| 后续 | PR 导入、可选 setup hooks、资源租约 | 明确网络 / 执行边界；配置可信来源；并行创建时不碰撞 |
| 后续 | 完整 Gum / Bubble Tea UI 或 sesh 集成 | 先证明现有命令的真实使用瓶颈；只保留一个任务和会话的事实来源 |

UI 回归建议覆盖窄终端、普通字体、长项目名、中文路径、无 fzf、无 LazyGit、无 AI CLI、非交互输出，以及两个任务同时运行。可以记录“打开已知任务需要几步”“定位当前 worktree 是否需要额外命令”“首次启动失败是否能直接知道原因”等指标；本次没有采集用户使用数据，不给出未经测量的效率百分比。

## 来源与访问记录

以下来源均在 2026-09-08 实际请求和阅读了与本文相关的正文；GitHub 条目通过 README / Contents API 读取，链接指向便于复查的项目页面或文件。

| 来源 | 主要核对内容 |
|---|---|
| [tmux 官方手册](https://github.com/tmux/tmux/blob/master/tmux.1) | 配置加载错误、`source-file`、选择树、标题、窗格状态和恢复 |
| [fzf README](https://github.com/junegunn/fzf#readme) | 键盘导航、局部展示、预览执行、全局预览配置限制 |
| [sesh README](https://github.com/joshmedeski/sesh#readme) | 会话创建、选择器、项目配置、返回上个会话、目录跳转 |
| [tmuxinator README](https://github.com/tmuxinator/tmuxinator#readme) | 项目配置、按窗格目录、命名与启动焦点、doctor/debug |
| [git-worktree-runner README](https://github.com/coderabbitai/git-worktree-runner#readme) / [AI Agent Usage](https://github.com/coderabbitai/git-worktree-runner/blob/main/docs/agent-usage.md) | 任务命令、可解析输出、配置复制、hooks 信任和清理边界 |
| [zoxide README](https://github.com/ajeetdsouza/zoxide#readme) | 常用目录排序、`zi` 与 fzf 集成 |
| [LazyGit README](https://github.com/jesseduffield/lazygit#readme) | 行级暂存、过滤、worktree、Git 审查界面 |
| [Gum README](https://github.com/charmbracelet/gum#readme) | shell 选择、输入、确认、表格和进度组件 |
| [Git worktree 官方文档](https://git-scm.com/docs/git-worktree) / [源码文档](https://github.com/git/git/blob/master/Documentation/git-worktree.adoc) | 删除约束、共享状态、porcelain 与 NUL 分隔 |
| [Command Line Interface Guidelines](https://clig.dev/) | 帮助、输出、退出码、TTY、颜色、错误和下一步提示 |
| [NO_COLOR](https://no-color.org/) | 非空环境变量禁用默认 ANSI 颜色的约定 |
| [W3C Contrast Minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) | 一般文字 4.5:1 对比度设计参考及适用限制 |
