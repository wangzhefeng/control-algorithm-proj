# MPC 学习模块

本目录包含 4 个可运行的 MPC 示例，目标是让你从线性 MPC 逐步过渡到非线性 MPC，并理解每个示例“要解决什么问题、问题本身的逻辑、算法如何解决问题”。

## 1. 推荐学习顺序

1. `linear_mpc_qp_demo.py`
2. `linear_mpc_tracking_demo.py`
3. `nonlinear_mpc_casadi_demo.py`
4. `nmpc_unicycle_tracking_demo.py`

---

## 2. 统一运行方式

在项目根目录执行：

```powershell
uv run python src/mpc/linear_mpc_qp_demo.py --no-show --save-fig
uv run python src/mpc/linear_mpc_tracking_demo.py --no-show --save-fig
uv run python src/mpc/nonlinear_mpc_casadi_demo.py --no-show --save-fig
uv run python src/mpc/nmpc_unicycle_tracking_demo.py --no-show --save-fig
```

常用参数：

- `--horizon`：预测时域长度
- `--sim-steps`：闭环仿真步数
- `--save-fig`：保存图像到 `src/mpc/figures/`
- `--no-show`：不弹出图窗，适合无桌面环境

`nmpc_unicycle_tracking_demo.py` 额外参数：

- `--q-pos`：位置误差权重
- `--q-theta`：航向角误差权重
- `--r-v`：线速度输入惩罚
- `--r-omega`：角速度输入惩罚
- `--v-min` / `--v-max`：线速度约束
- `--omega-max`：角速度绝对值上限

输出指标（不同脚本略有差异）：

- `tracking_mse` / `tracking_mse_xy` / `tracking_mse_heading`
- `constraint_violations`
- `infeasible_steps`
- `avg_solve_time_ms`

---

## 3. 示例详解（问题 + 逻辑 + 算法）

### 3.1 `linear_mpc_qp_demo.py`

要解决什么问题：
将系统状态（位置、速度）从初始值稳定地拉到目标值，同时满足输入和状态约束。

问题的基本逻辑：
系统是离散线性模型（双积分器）。每一步都需要在“跟踪快”和“控制平滑”之间折中，且不能超出约束。

算法的基本逻辑：

- 在每个采样时刻，构造长度为 `N` 的预测优化问题。
- 目标函数由状态误差项 + 控制输入项组成（二次型）。
- 约束包含系统动力学、状态上下界、输入上下界。
- 问题是标准 QP，用 `cvxpy + OSQP` 求解。
- 只执行第一个控制量（滚动优化），下一时刻重新求解。

---

### 3.2 `linear_mpc_tracking_demo.py`

要解决什么问题：
在参考轨迹分段变化且系统有小扰动时，持续跟踪目标并保持约束可行。

问题的基本逻辑：
真实工程里参考值会变（比如工艺设定点切换），扰动也会存在。控制器要在“快速跟踪”和“避免过激输入”之间动态平衡。

算法的基本逻辑：

- 每个时刻生成未来参考序列（不是固定单点参考）。
- 将“对参考轨迹的跟踪误差”写入滚动优化代价。
- 保留状态/输入约束，在线求解 QP。
- 对系统施加扰动后继续闭环优化，观察鲁棒跟踪性能。

---

### 3.3 `nonlinear_mpc_casadi_demo.py`

要解决什么问题：
在线性模型不够准确时，直接利用非线性动力学进行约束跟踪控制。

问题的基本逻辑：
系统动力学含有非线性项 `sin(x)`，线性 MPC 可能在较大状态范围内误差变大，需要 NMPC 在预测中保留非线性关系。

算法的基本逻辑：

- 用 CasADi 的 `Opti` 构建非线性优化问题（NLP）。
- 采用 multiple shooting 思路：把未来状态和输入都作为决策变量。
- 通过非线性动力学等式连接相邻时刻状态。
- 在代价中惩罚状态偏差和输入能量，并施加状态/输入边界。
- 使用 IPOPT 求解，每次仅执行第一步输入并滚动更新。

---

### 3.4 `nmpc_unicycle_tracking_demo.py`

要解决什么问题：
让二维单车模型（移动机器人）跟踪给定路径（圆轨迹），同时满足速度和角速度约束。

问题的基本逻辑：
机器人状态是 `(x, y, theta)`，控制输入是线速度 `v` 和角速度 `omega`。目标不是单变量稳态，而是“时变路径跟踪 + 姿态协调 + 约束可行”。

算法的基本逻辑：

- 在预测时域内同时优化位置与航向误差。
- 代价函数由 `x/y/theta` 误差项和输入惩罚项构成（均可调参数化）。
- 动力学使用单车模型非线性方程：
  - `x_{k+1} = x_k + dt * v_k * cos(theta_k)`
  - `y_{k+1} = y_k + dt * v_k * sin(theta_k)`
  - `theta_{k+1} = theta_k + dt * omega_k`
- 施加 `v` 与 `omega` 约束，NLP 由 IPOPT 在线求解。
- 执行首个控制量并滚动，形成闭环 NMPC。

调参建议：

- 先调 `q_pos / r_v`，决定“跟踪积极程度 vs 控制平滑程度”。
- 再调 `q_theta / r_omega`，改善转向精度和角速度抖动。

---

## 4. 常见 MPC 算法（调研摘要）

### 4.1 线性 MPC（LMPC）

- 核心：线性模型 + 二次代价 + 线性约束（QP）
- 优点：成熟、实时性好、工业部署广
- 局限：依赖线性化质量

### 4.2 非线性 MPC（NMPC）

- 核心：非线性模型 + 非线性约束（NLP）
- 优点：对强非线性对象更准确
- 局限：计算量大、求解器敏感

### 4.3 鲁棒 MPC（Robust MPC）

- 核心：显式考虑模型不确定性与最坏情形
- 优点：安全裕度高
- 局限：更保守，计算更重

### 4.4 随机 MPC（Stochastic MPC）

- 核心：考虑随机扰动与概率约束
- 优点：风险-性能可平衡
- 局限：建模和实现复杂

### 4.5 经济型 MPC（Economic MPC）

- 核心：直接优化经济目标（能耗、成本、产率）
- 优点：直接对业务 KPI 负责
- 局限：稳定性分析与调参更难

### 4.6 显式 MPC（Explicit MPC）

- 核心：离线求解多参数 QP，在线查表
- 优点：在线计算极快
- 局限：高维下可能分区爆炸

### 4.7 分布式 / 分散式 MPC

- 核心：多子系统协同优化
- 优点：适合大规模系统
- 局限：通信与收敛问题复杂

---

## 5. 工具生态

开源：

- `CVXPY + OSQP`：线性 MPC/QP 入门与原型友好
- `CasADi + IPOPT`：NMPC 常用组合，自动微分能力强
- `do-mpc`：CasADi 上层框架，快速实验友好
- `acados`：偏实时场景的高性能 NMPC/MHE 框架

工业：

- MATLAB Model Predictive Control Toolbox
- AspenTech / Honeywell / Emerson 等 APC 工具链

---

## 6. 参考资料

- Rawlings, Mayne, Diehl, *Model Predictive Control: Theory, Computation, and Design*  
  <https://sites.engineering.ucsb.edu/~jbraw/mpc/>
- CVXPY 文档  
  <https://www.cvxpy.org/>
- OSQP 文档  
  <https://osqp.org/>
- CasADi 文档  
  <https://web.casadi.org/docs/>
- do-mpc 文档  
  <https://www.do-mpc.com/>
- acados 文档  
  <https://docs.acados.org/>
- MathWorks MPC Toolbox  
  <https://www.mathworks.com/products/model-predictive-control.html>
