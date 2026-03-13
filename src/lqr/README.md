# LQR 学习模块

本目录提供 3 个可运行的 LQR 系列示例，目标是用最短路径理解：

1. 线性系统稳态调节（LQR）
2. 参考轨迹跟踪（增量 LQR）
3. 非线性系统迭代优化控制（iLQR）

## 1. 学习路线

建议按下面顺序学习：

1. `lqr_regulator_discrete_demo.py`
2. `lqr_tracking_incremental_demo.py`
3. `ilqr_unicycle_demo.py`

学习目标：

- 掌握离散 LQR 的建模与 DARE 求解
- 理解“调节问题”如何扩展为“跟踪问题”
- 理解 iLQR 如何通过线性化 + 二次近似处理非线性系统

## 2. 示例说明（问题 + 逻辑 + 算法）

### 2.1 `lqr_regulator_discrete_demo.py`

- 要解决的问题：
  将偏离平衡点的双积分系统（位置、速度）稳定回原点。
- 问题基本逻辑：
  系统离散动力学为 `x_{k+1} = A x_k + B u_k`，目标是状态小、控制输入不过大。
- 算法基本逻辑：
  最小化二次代价
  `J = sum(x_k^T Q x_k + u_k^T R u_k)`，
  通过离散 Riccati 方程（DARE）得到 `K`，使用 `u_k = -K x_k` 闭环控制。
- 关注指标：
  `state_mse`、`control_energy`、`settling_time_s`、`constraint_violations`。

### 2.2 `lqr_tracking_incremental_demo.py`

- 要解决的问题：
  对分段变化参考信号进行跟踪，同时保持控制变化平滑。
- 问题基本逻辑：
  跟踪不是纯稳态调节。示例使用增量输入 `delta_u`，把控制器重点放在“误差收敛 + 控制变化抑制”。
- 算法基本逻辑：
  构建增广状态 `z = [e_pos, e_vel, u_prev]`，控制量为 `delta_u`，
  对增广线性系统应用离散 LQR，得到 `delta_u = -K z`，再由 `u = u_prev + delta_u` 更新输入。
- 关注指标：
  `tracking_mse`、`control_energy`、`delta_u_energy`、`constraint_violations`。

### 2.3 `ilqr_unicycle_demo.py`

- 要解决的问题：
  非线性单车模型（`x, y, theta`）跟踪二维参考轨迹。
- 问题基本逻辑：
  非线性动力学无法直接用一次离散 LQR 全局解决，需要迭代优化控制序列。
- 算法基本逻辑：
  iLQR 在当前轨迹上迭代：
  1. forward rollout 得到状态轨迹
  2. 局部线性化动力学、二次近似代价
  3. backward pass 求前馈项和反馈增益
  4. line-search 更新控制并重复
- 关注指标：
  `tracking_mse_xy`、`tracking_mse_heading`、`control_energy`、`avg_solve_time_ms`。

## 3. 关键公式最小集

### 3.1 离散 LQR

- 动力学：`x_{k+1} = A x_k + B u_k`
- 代价：`J = sum_{k=0}^{N-1}(x_k^T Q x_k + u_k^T R u_k) + x_N^T Q_f x_N`
- Riccati 递推稳态解（DARE）得到 `P`，反馈增益：
  `K = (B^T P B + R)^(-1) B^T P A`
- 控制律：`u_k = -K x_k`

### 3.2 增量 LQR 跟踪

- 增广状态：`z_k = [e_k; u_{k-1}]`
- 控制变量：`delta_u_k`
- 更新：`u_k = u_{k-1} + delta_u_k`
- 在增广系统上求解 LQR：
  `delta_u_k = -K z_k`

### 3.3 iLQR

- 在名义轨迹附近做局部近似：
  `delta_x_{k+1} ~= A_k delta_x_k + B_k delta_u_k`
- 反向递推得到：
  `delta_u_k = k_k + K_k delta_x_k`
- 通过 line-search 选择步长更新控制序列，迭代到收敛。

## 4. 运行方式

在项目根目录执行：

```powershell
uv run python src/lqr/lqr_regulator_discrete_demo.py --no-show --save-fig
uv run python src/lqr/lqr_tracking_incremental_demo.py --no-show --save-fig
uv run python src/lqr/ilqr_unicycle_demo.py --no-show --save-fig
```

常用参数：

- `--sim-steps`：闭环仿真步数
- `--save-fig`：保存图像到 `src/lqr/figures/`
- `--no-show`：无界面环境下关闭图窗
- `--q-*` / `--r-*`：状态/输入代价权重

## 5. 指标解读

- `state_mse` / `tracking_mse`：越小表示跟踪或稳定效果越好
- `control_energy`：越小表示控制动作更节省
- `settling_time_s`：越小表示收敛越快
- `avg_solve_time_ms`：越小表示更适合实时控制
- `constraint_violations`：大于 0 说明触发了输入限幅，通常需要重新调权重或放宽约束

## 6. 业内常用 LQR 系列算法调研（工程评估版）

### 6.1 常见算法族

- LQR：线性模型 + 全状态反馈，适合调节问题
- LQI：在 LQR 中加入积分状态，降低稳态偏差
- LQG：LQR + Kalman Filter，适合状态不可全测场景
- TVLQR：时变线性化模型上的 LQR，常用于参考轨迹稳定
- iLQR / DDP：非线性最优控制常用迭代方法，适合机器人运动规划与跟踪

### 6.2 典型应用场景

- 机器人：机械臂关节控制、移动机器人姿态稳定
- 自动驾驶：横纵向轨迹跟踪与局部稳定
- 无人机：姿态/位置回路设计
- 伺服系统：电机速度和位置控制

### 6.3 选型维度（工程视角）

- 实时性：
  LQR/LQI 通常最快，iLQR 受迭代次数影响较大
- 模型依赖：
  模型越准，性能越好；iLQR 对模型和初始化更敏感
- 鲁棒性：
  LQI 对常值扰动更友好；LQG 处理噪声更系统
- 调参与部署复杂度：
  LQR 最低，LQG 次之，iLQR 更高
- 可解释性：
  LQR/LQI 参数解释最直观，便于工程落地与维护

### 6.4 常用工具链

- Python 科研原型：`numpy` + `scipy`
- 控制分析增强：`python-control`（可选）
- 工业/教学标准：MATLAB Control System Toolbox
- 嵌入式注意点：
  固定点精度、采样周期、执行时延、输入限幅与 anti-windup 协同

## 7. 学习建议

1. 先固定 `R`，扫描 `Q`，观察收敛速度和输入幅值的权衡。
2. 在跟踪示例里重点观察 `r-du` 对控制平滑性的影响。
3. 在 iLQR 示例里调 `--horizon` 和 `--ilqr-iters`，体会实时性与性能折中。
4. 若后续做工程落地，可在本目录基础上扩展 LQI 与 LQG 对比实验。
