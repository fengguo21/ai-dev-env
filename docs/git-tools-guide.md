# LazyGit、Git Diff 与 GitHub CLI 使用指南

本文介绍 AI Dev Environment 中的三类 Git 工具：

需要按命令快速查询时，使用 [AI Dev Environment 命令查询手册](command-reference.md)。

| 工具 | 主要用途 | 操作范围 |
|---|---|---|
| `lazygit` | 在终端界面中执行常见 Git 操作 | 本地 Git，以及 push、pull 等远程操作 |
| `git diff` + Delta | 检查代码差异 | 只读比较，不修改文件 |
| `gh` | 管理 Pull Request、CI、Issue 和 GitHub 仓库 | GitHub 远程平台 |

它们不是相互替代的工具。日常开发中通常使用 `git diff` 检查修改，使用 LazyGit 暂存、提交和推送，再使用 `gh` 创建 Pull Request 并查看 CI。

## 如何阅读本文中的命令

一条命令通常由“工具 + 子命令 + 参数 + 参数值”组成：

```bash
gh pr create --fill
```

| 部分 | 全称或原词 | 含义与记忆方法 |
|---|---|---|
| `gh` | GitHub CLI | GitHub 命令行工具；可直接把 `g`、`h` 记成 GitHub |
| `pr` | Pull Request | Pull Request 子命令 |
| `create` | create | 创建 |
| `--fill` | fill | 从 Git Commit 自动“填充”PR 标题和正文 |

本文使用以下规则：

- `--word` 是长参数，英文单词通常直接说明功能；
- `-x` 是短参数，优先注明其官方长参数；
- 如果短参数没有正式全称，会标为“助记”，不把口诀写成官方定义；
- `<run-id>`、`<files>` 是占位符，使用时替换成真实值，不保留尖括号；
- 同一个短参数在不同命令中可能含义不同，必须连同命令一起记忆。

## 1. LazyGit

LazyGit 是 Git 的终端交互界面。它最终仍然调用 Git，但把文件、分支、提交和 Stash 等操作集中到了一个界面中。

### 启动方式

在 Git 仓库中启动：

```bash
lazygit
```

指定仓库目录：

```bash
lazygit -p /path/to/project
lazygit --path /path/to/project
```

`-p` 对应 `--path`，`p` 记作 **path（路径）**，用于指定仓库目录。

启动时直接聚焦指定面板：

```bash
lazygit status
lazygit branch
lazygit log
lazygit stash
```

这里的 `status`（状态）、`branch`（分支）、`log`（历史记录）和 `stash`（搁置记录）是启动时的面板位置参数，不是需要继续接子命令的独立功能入口。

使用本项目的 `dev` 命令创建 tmux 工作区时，如果当前目录是 Git 仓库并且已经安装 LazyGit，`git` 窗口会自动运行 `lazygit`。如果没有安装，窗口会退回执行：

```bash
git status --short --branch
```

`--short` 表示精简格式，`--branch` 表示同时显示分支和跟踪信息；它们可短写合并为 `git status -sb`，其中 `s` 记作 **short**、`b` 记作 **branch**。

### 基本导航

LazyGit 快捷键区分大小写。

| 按键 | 功能 |
|---|---|
| `1`～`5` | 跳转到对应面板 |
| `h/j/k/l` 或方向键 | 切换面板或选择项目 |
| `Enter` | 进入选中项目或查看详情 |
| `Esc` | Escape，返回上一级或取消 |
| `Tab` / `Shift+Tab` | 切换到下一个/上一个面板 |
| `[` / `]` | 切换标签页 |
| `/` | 搜索 |
| `?` | 打开当前上下文的操作菜单 |
| `R` | 通常刷新；Branches 面板中会被重定义为 Rename |
| `:` | 执行 Shell 命令 |
| `q` | 退出 |

如果不确定某个面板支持哪些操作，先按 `?` 查看当前上下文的准确按键。

LazyGit 的单字母按键是快捷键，并不都存在官方“全称”，而且同一字母会随面板改变。下面只把明确的“面板 + 按键 + 动作”组合用英文联想起来：

| 所在面板 | 按键 | 助记英文 | 记忆方法 |
|---|---|---|---|
| Files | `a` | all | 对全部文件操作 |
| Files | `c` | commit | 创建 Commit |
| Files | `A` | amend | 修订上一次 Commit |
| Files | `e` | edit | 编辑文件 |
| Files | `o` | open | 打开文件 |
| Files | `s` | stash | 搁置/收藏工作区修改；不要与 Stage 暂存区混淆 |
| Files | `f` | fetch | 获取远程数据 |
| Files | `p` / `P` | pull / push | 小写 Pull，大写 Push；注意大小写 |
| Branches | `n` | new | 新建分支 |
| Branches | `r` / `R` | rebase / rename | 小写 Rebase，大写 Rename |
| Branches | `M` | merge | 合并分支 |
| 全局 | `q` | quit | 退出 LazyGit |
| 全局 | `?` | help/options | 打开当前面板操作菜单 |

### 暂存、提交与推送

在 Files 面板中：

| 按键 | 功能 |
|---|---|
| `Space` | 暂存或取消暂存当前文件 |
| `a` | 暂存或取消暂存所有文件 |
| `c` | 提交已经暂存的修改 |
| `C` | 使用编辑器填写提交信息 |
| `A` | Amend 上一次提交 |
| `e` | 使用编辑器打开当前文件 |
| `x` | 丢弃当前修改，会要求确认 |
| `D` | 打开 Reset 选项 |
| `s` | Stash 全部修改 |
| `f` | Fetch |
| `p` | Pull |
| `P` | Push |

推荐操作顺序：

1. 在 Files 面板查看修改。
2. 使用 `Space` 暂存需要提交的文件。
3. 按 `c` 填写提交信息并提交。
4. 按 `P` 推送到远程仓库。

`x`、`D` 和 `A` 可能覆盖或重写已有工作。执行前应确认当前选中的文件和提交，并仔细阅读确认窗口。

### 分支操作

在 Branches 面板中：

| 按键 | 功能 |
|---|---|
| `n` | 创建新分支 |
| `Space` | Checkout 选中的分支 |
| `c` | 按名称 Checkout 分支 |
| `-` | 切换回上一个分支 |
| `d` | 删除选中的分支 |
| `R` | 重命名分支 |
| `M` | 将选中分支合并到当前分支 |
| `r` | Rebase 当前分支 |
| `o` | 创建 Pull Request |
| `G` | 在浏览器中打开 Pull Request |

删除、Merge 和 Rebase 都会改变分支或提交历史。操作前应确认当前分支，并在必要时先 Push 或创建备份分支。

### 提交历史与 Stash

在 Commits 面板中：

| 按键 | 功能 |
|---|---|
| `Space` | Checkout 选中的提交 |
| `r` | 修改提交说明 |
| `s` | 将提交向下 Squash |
| `f` | 标记为 Fixup |
| `t` | Revert 提交 |
| `C` | 复制提交以便 Cherry-pick |
| `V` | 粘贴已复制的提交 |
| `i` | 开始交互式 Rebase |
| `o` | 在浏览器中打开提交 |

在 Files 面板按 `s` 可以保存当前修改。进入 Stash 面板后，选择一条记录并按 `g` 可以 Pop Stash。

## 2. `git diff` 与 Delta

`git diff` 是标准 Git 比较命令。当前环境使用 Delta 作为 Git Pager，因此执行 `git diff` 时会获得语法高亮、行号和更清晰的布局。

当前环境使用的相关配置包括：

```ini
[core]
    pager = delta
[interactive]
    diffFilter = delta --color-only
[delta]
    navigate = true
    line-numbers = true
[merge]
    conflictstyle = zdiff3
```

配置项可以这样理解：

| 配置 | 全称或原词 | 作用与记忆方法 |
|---|---|---|
| `core.pager` | pager | 设置 Git 的分页显示器为 Delta |
| `interactive.diffFilter` | interactive diff filter | 让 `git add -p` 等交互操作也通过 Delta 着色 |
| `--color-only` | color only | 只增加颜色，不改写交互 Diff 的结构 |
| `delta.navigate` | navigate | 允许在 Delta 中按 `n` / `N` 跳到下一个/上一个文件 |
| `delta.line-numbers` | line numbers | 显示行号 |
| `merge.conflictstyle` | conflict style | 设置合并冲突的展示方式 |
| `zdiff3` | 名称；Zealous 只作助记 | 类似 `diff3`，显示共同祖先，并把冲突区首尾附近两侧相同的行移出冲突区域 |

这里的 `git add -p` 中，`-p` 对应 `--patch`，表示交互选择要加入暂存区的 Hunk（代码块）。它与 `lazygit -p` 的 `--path` 完全不同。

Delta 只负责显示，不会修改文件或提交历史。

### 工作区、暂存区和 HEAD

```text
工作区 -- git add --> 暂存区 -- git commit --> HEAD
   |                     |
   | git diff            | git diff --staged
```

查看尚未暂存的修改：

```bash
git diff
```

查看已经暂存、准备提交的修改：

```bash
git diff --staged
```

`--staged` 也可以写成 `--cached`：

```bash
git diff --cached
```

查看已跟踪文件相对于当前 `HEAD` 的已暂存和未暂存修改：

```bash
git diff HEAD
```

这条命令不显示未跟踪（untracked）文件，因为未跟踪文件还没有可供 Git 比较的历史版本。先用 `git status` 查看它们。

### 常用比较命令

只检查指定文件或目录：

```bash
git diff -- src/app.ts
git diff -- frontend/src/
```

只显示发生变化的文件名或修改统计：

```bash
git diff --name-only
git diff --stat
```

按单词显示变化：

```bash
git diff --word-diff
```

比较两个提交：

```bash
git diff HEAD~1 HEAD
git diff <old-commit> <new-commit>
```

比较两个分支当前指向的提交：

```bash
git diff main..feature/login
```

查看当前分支从 `main` 分叉后引入的修改：

```bash
git diff main...HEAD
```

三点形式特别适合在创建 Pull Request 前检查：它显示从共同祖先开始、当前 `HEAD` 已经提交的净改动。它不会包含工作区里尚未提交的修改；这部分应另外运行 `git diff` 和 `git diff --staged`。

筛选指定字符串出现次数发生变化的文件：

```bash
git diff -S'functionName'
```

`-S<string>` 没有对应的 `--string` 长参数。大写 `S` 只能联想为 **String（字符串）**：它默认区分大小写，比较字面字符串在前后文件中的出现次数。如果代码只是移动位置而次数不变，`-S` 可能不会命中。若要匹配新增或删除行中的正则表达式，可使用：

```bash
git diff -G'<regular-expression>'
```

临时跳过 Delta，不启动 Pager，直接把 Git Diff 写到终端：

```bash
git --no-pager diff
```

`pager` 是分页显示器；当前环境的 Pager 是 Delta。`--no-pager` 表示不启动 Pager，因此会绕过 Delta，由 Git 直接写入终端；Git 自身的颜色和格式配置仍可能生效。

### Git Diff 参数速记

| 写法 | 全称或原词 | 含义与记忆方法 |
|---|---|---|
| `diff` | difference | 查看“不同之处” |
| `--staged` | staged | 查看已经进入 Stage（暂存区）的修改 |
| `--cached` | cached | 与 `--staged` 等价；早期 Git 把暂存区称为 Cache |
| `--name-only` | name only | 只显示文件名 |
| `--stat` | statistics | 显示文件数和增删行统计 |
| `--word-diff` | word difference | 以单词粒度显示差异 |
| `--no-pager` | no pager | 禁用 Delta、less 等分页显示器 |
| `-S<string>` | String（助记，无官方长参数） | 筛选字面字符串出现次数发生变化的文件；Git 称为 Pickaxe 搜索 |
| `-G<regex>` | Regular Expression（助记） | 筛选新增或删除行能够匹配正则表达式的差异 |
| `-p`、`--patch` | patch | 输出补丁格式；普通 `git diff` 默认就是这种格式 |
| `-u` | `--patch` 的同义短写 | 在 Git Diff 中与 `-p` 相同，不是系统 `diff -u` 的 `--unified` |
| `-- <path>` | end of options | `--` 结束参数解析，后面明确作为文件路径处理 |

### Git 版本符号速记

| 写法 | 名称 | 含义与记忆方法 |
|---|---|---|
| `HEAD` | symbolic reference，不是缩写 | 当前检出的提交位置；可想成“当前头指针” |
| `HEAD~1` | first parent of HEAD | `~1` 表示沿第一父提交往回一步 |
| `A..B` | two-dot form | 对 `git diff` 来说比较 A 与 B 两个端点 |
| `A...B` | three-dot form | 比较 A、B 的 Merge Base（共同祖先）与 B |
| `main...HEAD` | three-dot branch diff | 查看共同祖先到当前 `HEAD` 已提交的修改，不包括未提交工作区内容 |
| `origin/main` | remote/branch | 远程 `origin` 上的 `main` 分支 |

> `..` 和 `...` 在 `git log` 等命令中的集合语义与 `git diff` 不完全相同；这里解释的是 `git diff`。

### `diff` 与 `git diff` 的区别

系统 `diff` 命令比较两个普通文件或目录，不会读取 Git 的暂存区和提交记录：

```bash
diff -u old.txt new.txt
diff -ru old-directory new-directory
```

| 参数 | 官方长参数 | 含义与记忆方法 |
|---|---|---|
| `-u` | `--unified` | Unified Diff（统一格式），把前后文和增删行放在一起 |
| `-r` | `--recursive` | Recursive（递归），进入子目录比较 |
| `-ru` | `-r -u` | 两个短参数的合并写法：递归 + 统一格式 |

在 Git 项目里检查代码修改时，通常应该使用 `git diff`。

## 3. GitHub CLI：`gh`

Git 负责本地版本历史和远程分支；`gh` 通过 GitHub API 管理 Pull Request、CI、Issue、Release 等 GitHub 平台功能。

这里的常见缩写是：

| 缩写/短词 | 英文全称 | 中文含义与记忆方法 |
|---|---|---|
| CLI | Command-Line Interface | 命令行界面；通过输入命令操作 GitHub |
| API | Application Programming Interface | 应用程序编程接口；`gh` 通过它与 GitHub 通信 |
| PR | Pull Request | 拉取请求；请求把一个分支合并到另一个分支 |
| CI | Continuous Integration | 持续集成；Push 后自动运行测试、Lint 和构建 |
| `auth` | authentication | 身份认证或登录 |
| `repo` | repository | GitHub 仓库 |
| `run` | workflow run | 一次 GitHub Actions 工作流运行 |
| `id` | identifier | 标识符；`<run-id>` 表示运行编号 |

### 登录和状态检查

```bash
gh auth login
gh auth status
gh auth switch
```

### 仓库操作

查看当前仓库，或者在浏览器中打开：

```bash
gh repo view
gh repo view --web
gh browse
```

克隆或 Fork 仓库：

```bash
gh repo clone owner/repository
gh repo fork owner/repository --clone
```

`clone` 是把远程仓库复制成本地工作副本；`fork` 是先在自己的 GitHub 账号下创建服务端副本。`--clone` 表示 Fork 完成后继续 Clone 到本地。

### Pull Request

列出、查看和比较 Pull Request：

```bash
gh pr list
gh pr view
gh pr diff
```

创建 Pull Request：

```bash
gh pr create
gh pr create --fill
gh pr create --draft --fill
```

检出编号为 `123` 的 Pull Request：

```bash
gh pr checkout 123
```

检查或持续等待 CI：

```bash
gh pr checks
gh pr checks --watch
```

合并 Pull Request：

```bash
gh pr merge
```

`gh pr create` 和 `gh pr merge` 会改变 GitHub 上的状态；`gh pr view`、`gh pr diff` 和 `gh pr checks` 主要用于读取信息。

### GitHub Actions

```bash
gh run list
gh run view <run-id>
gh run view <run-id> --log-failed
gh run watch <run-id>
gh run rerun <run-id> --failed
```

| 术语 | 英文原词 | 含义 |
|---|---|---|
| Workflow | workflow | 在仓库中定义的一套自动化流程 |
| Run | run | 某个 Workflow 的一次执行 |
| Job | job | Run 中的一组步骤或任务 |
| Check | check | PR 上显示的状态检查，不一定只来自 GitHub Actions |
| `--failed` | failed | 重新运行失败的 Job 及其依赖 |

### Issue

```bash
gh issue list
gh issue view 123
gh issue create
```

### 获取帮助

`gh` 的每一级命令都可以使用 `--help`：

```bash
gh --help
gh pr --help
gh pr create --help
gh run view --help
```

### `gh` 参数速记

| 参数 | 全称或原词 | 含义与记忆方法 |
|---|---|---|
| `--help` | help | 显示当前层级的帮助 |
| `--web` | web | 在 Web 浏览器中打开 |
| `--clone` | clone | Fork 后同时克隆到本地 |
| `--fill` | fill | 从 Commit 自动填充 PR 标题与正文 |
| `--draft` | draft | 创建 Draft PR（草稿拉取请求） |
| `--watch` | watch | 持续观察 CI，直到检查结束 |
| `--log-failed` | log failed | 只显示失败步骤的日志 |
| `--failed` | failed | 只重新运行失败的任务 |

这些参数也有部分短写，例如 `gh pr create -f` 等价于 `--fill`，但文档优先使用长参数，因为更容易读懂，也更不容易与其他命令的单字母参数混淆。

## 4. 推荐日常工作流

启动项目工作区：

```bash
dev /path/to/project
```

开发完成后先检查代码：

```bash
git status --short --branch
git diff
```

然后在 LazyGit 中：

1. 在 Files 面板选择文件。
2. 按 `Space` 暂存文件。
3. 按 `c` 提交。
4. 按 `P` 推送。

也可以完全使用 Git 命令完成相同操作：

```bash
git add <files>
git diff --staged
git commit -m "feat: describe the change"
git push -u origin HEAD
```

这组 Git 参数可以这样记：

| 参数/名称 | 官方长参数或原词 | 含义与记忆方法 |
|---|---|---|
| `-m` | `--message` | `m` 记作 Message，在命令行提供 Commit 信息 |
| `-u` | `--set-upstream` | `u` 记作 Upstream，设置当前分支的上游远程分支 |
| `origin` | origin | Git Clone 时常见的默认远程名称，可记作代码的远程“来源”；它不是保留字 |
| `HEAD` | symbolic reference | 当前检出的提交位置，不是英文缩写 |

整句的意思是：把当前检出分支推送到名为 `origin` 的远程，并把对应远程分支记录为当前分支的 Upstream；之后通常可以直接运行 `git push` 和 `git pull`。

提交信息中的 `feat` 是 **feature（功能）** 的缩写，属于 Conventional Commits（约定式提交）惯例，不是 Git 强制语法。

推送完成后创建 Pull Request，并等待 CI：

```bash
gh pr create --fill
gh pr checks --watch
```

合并前进行最后检查：

```bash
git diff main...HEAD
gh pr diff
gh pr checks
```

## 5. 常见问题

### LazyGit 提示当前目录不是 Git 仓库

```bash
cd /path/to/project
lazygit
lazygit -p /path/to/project
```

上面前两行是“先进入目录再启动”；最后一行是直接通过 `-p` 指定目录，实际使用时二选一即可。

### `git diff` 没有输出

可能是没有未暂存修改，或者修改已经进入暂存区。依次检查：

```bash
git status --short --branch
git diff
git diff --staged
git log --oneline -5
```

`--short` 表示紧凑输出，`--branch` 表示同时显示分支；`--oneline` 表示每个 Commit 一行，`-5` 是 `--max-count=5` 的短写，表示最多显示 5 条。

### `gh` 找不到当前仓库

确认当前目录位于 Git 仓库内，并且配置了 GitHub Remote：

```bash
git remote -v
gh repo view
```

这里 `remote` 是远程仓库，`-v` 对应 `--verbose`，表示显示更详细的 Fetch 和 Push 地址。不要把它与 `command -v` 或 tmux 的 `-v` 混为一谈。

如果尚未登录：

```bash
gh auth login
```

### 忘记快捷键或命令参数

在 LazyGit 中按 `?`；对于命令行工具使用：

```bash
git diff -h
gh <command> --help
lazygit --help
```

## 6. Git 术语与易混参数

### Git 动作英文速记

| 术语 | 英文原意 | 中文含义与记忆方法 |
|---|---|---|
| Working Tree | working tree | 工作区；当前磁盘上实际看到和编辑的文件 |
| Index / Stage | index / staging area | 暂存区；下一次 Commit 的“候选清单” |
| Commit | commit | 提交；把暂存区保存为历史快照 |
| Branch | branch | 分支；像树枝一样从历史中分出开发路线 |
| Remote | remote | 远程仓库配置 |
| Upstream | upstream | 当前本地分支跟踪的上游分支 |
| Fetch | fetch | 下载远程数据，但不自动合并 |
| Pull | pull | 拉取并整合；通常相当于 Fetch 后再 Merge/Rebase |
| Push | push | 把本地提交推送到远程 |
| Checkout | check out | 检出分支、提交或文件；直接检出 Commit 可能进入 Detached HEAD |
| Merge | merge | 合并两条开发历史 |
| Rebase | re-base | 更换提交的基础，把提交重新应用到新 Base 上，通常会改变 Commit Hash |
| Reset | reset | 把引用、暂存区或工作区重置到指定状态，影响范围取决于模式 |
| Revert | revert | 用一个新 Commit 反向撤销旧 Commit，不删除历史 |
| Stash | stash | 把未完成修改临时收藏起来；不要与 Stage（暂存区）混淆 |
| Amend | amend | 修订最近一次 Commit，并产生新的 Commit Hash |
| Squash | squash | 把多个 Commit 压成更少的 Commit |
| Fixup | fix up | 标记为修正某个旧 Commit，常在 Rebase 时并入目标并丢弃 Fixup 说明 |
| Cherry-pick | cherry-pick | 像挑樱桃一样，只挑选某个 Commit 应用到当前分支 |
| Delta | 希腊字母 Δ | 数学中表示“变化量”，因此很适合用来显示代码差异 |

### 同字母不同含义

短参数和快捷键不是跨工具通用语言，必须与命令一起记：

| 写法 | 所属工具 | 含义 |
|---|---|---|
| `lazygit -p` | LazyGit 命令行 | `--path`，指定仓库路径 |
| LazyGit 中按 `p` | LazyGit TUI | Pull |
| `git add -p` | Git | `--patch`，交互选择要暂存的 Hunk |
| `git diff -p` | Git | `--patch`，输出补丁格式 |
| `git push -u` | Git | `--set-upstream`，设置上游 |
| `diff -u` | 系统 diff | `--unified`，统一 Diff 格式 |
| `git remote -v` | Git | `--verbose`，详细显示 Remote 地址 |
| `command -v git` | Shell | 查询 Shell 如何找到 `git`；`v` 可用 Verify 助记，但不是官方展开 |
| `git branch -d` | Git | `--delete`，安全删除已合并分支 |
| `git branch -D` | Git | `--delete --force`，连未合并分支也强制删除，可能丢失提交 |
| `docker compose up -d` | Docker | `--detach`，后台运行 |
| `docker compose logs -f` | Docker | `--follow`，持续跟随日志 |
| `grep -F` | grep | `--fixed-strings`，固定字符串匹配；注意大写 `F` |

记忆时把整个短语一起读出来：

```text
git push -u       → push and set upstream
diff -u           → unified diff
docker logs -f    → follow logs
git branch -d     → delete merged branch
```

跨工具的完整缩写表见 [AI Dev Environment 完整使用指南](ai-dev-environment-guide.md#13-缩写参数与符号速查)。
