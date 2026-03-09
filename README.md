# Control Algorithm Project

用于学习控制算法（当前聚焦 PID、状态空间与耦合系统示例）的实验仓库。

## 项目目标

- 梳理并运行 `src` 中的 PID 控制算法示例代码。
- 修复示例中的可运行性问题，沉淀可复现的实验步骤。
- 建立清晰的项目结构，方便后续持续扩展。

## 目录结构

```text
control-algorithm-proj
|- .codex/                   # Codex 协作开发配置与模板
|- .venv/                    # uv 管理的虚拟环境
|- docs/                     # 学习资料（不在本轮处理范围）
|- src/                      # 控制算法示例代码（重点）
|- .python-version           # Python 版本
|- AGENTS.md                 # 仓库协作要求
|- pyproject.toml            # 依赖与项目配置
|- uv.lock                   # 依赖锁定文件
`- README.md                 # 项目唯一维护说明文档
```

## 环境准备

1. 安装 `uv`。
2. 在仓库根目录执行：

```powershell
uv sync
```

3. 运行脚本时，优先使用：

```powershell
uv run python <script.py>
```

## 依赖说明

根据 `src` 的实际导入情况，当前关键依赖为：

- `numpy`
- `matplotlib`
- `scipy`

依赖定义见 [pyproject.toml](E:\control-algorithm-proj\pyproject.toml) 与 [uv.lock](E:\control-algorithm-proj\uv.lock)。

## 源码说明

`src/` 已按“算法类型 + 算法功能”完成分类。

### 分类结构

```text
src
`- pid
   |- basic
   |  `- pid_demo.py
   |- state_space
   |  |- pid_state_space_demo.py
   |  `- pid_control_state_space_demo.m
   `- coupled_systems
      |- pid_coupled_systems_demo.py
      `- pid_control_coupled_systems_demo.m
```

### 分类说明

- `src/pid/basic`
  - PID 基础算法示例。
- `src/pid/state_space`
  - 状态空间建模与 PID 控制示例（Python + Matlab）。
- `src/pid/coupled_systems`
  - 耦合系统 PID 控制示例（Python + Matlab）。

### 运行建议

- 优先运行示例脚本进行环境验证：
  - `uv run python src/pid/basic/pid_demo.py`
  - `uv run python src/pid/state_space/pid_state_space_demo.py`
  - `uv run python src/pid/coupled_systems/pid_coupled_systems_demo.py`

### 已知问题

- GUI 示例依赖 Tkinter 图形环境，部分无界面环境下无法直接显示窗口。
- 目前缺少面向数值结果的自动化回归测试。

## 与 Codex 协作

已提供 `.codex` 目录用于任务模板与工作流约束：

- [context.md](E:\control-algorithm-proj\.codex\context.md)
- [workflow.md](E:\control-algorithm-proj\.codex\workflow.md)
- [task.md](E:\control-algorithm-proj\.codex\templates\task.md)

## 当前状态与后续建议

- 当前已完成项目结构层面的基础整理（目录、说明、依赖、算法分类）。
- 后续建议优先补充 `src/pid` 目录下示例的自动化测试（非 GUI 部分）。
- 今后项目内容更新统一维护在根目录 `README.md`。
