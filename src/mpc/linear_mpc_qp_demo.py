"""Linear constrained MPC demo solved as a QP with CVXPY.

This script shows the classic receding-horizon MPC loop on a discrete
double-integrator system with state and input constraints.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import cvxpy as cp
import matplotlib
import numpy as np


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Linear MPC QP demo")
    parser.add_argument("--horizon", type=int, default=20, help="Prediction horizon N")
    parser.add_argument("--sim-steps", type=int, default=80, help="Closed-loop simulation steps")
    parser.add_argument(
        "--save-fig",
        action="store_true",
        help="Save the simulation figure to src/mpc/figures",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Do not open a GUI window for the figure",
    )
    return parser


def solve_linear_mpc(
    A: np.ndarray,
    B: np.ndarray,
    x0: np.ndarray,
    x_ref: np.ndarray,
    horizon: int,
    q: np.ndarray,
    r: np.ndarray,
    x_min: np.ndarray,
    x_max: np.ndarray,
    u_min: float,
    u_max: float,
) -> tuple[float, str]:
    n_x = A.shape[0]
    n_u = B.shape[1]

    x = cp.Variable((n_x, horizon + 1))
    u = cp.Variable((n_u, horizon))

    cost = 0
    constraints = [x[:, 0] == x0]
    for k in range(horizon):
        cost += cp.quad_form(x[:, k] - x_ref, q) + cp.quad_form(u[:, k], r)
        constraints += [
            x[:, k + 1] == A @ x[:, k] + B @ u[:, k],
            x_min <= x[:, k],
            x[:, k] <= x_max,
            u_min <= u[:, k],
            u[:, k] <= u_max,
        ]
    cost += cp.quad_form(x[:, horizon] - x_ref, q)
    constraints += [x_min <= x[:, horizon], x[:, horizon] <= x_max]

    problem = cp.Problem(cp.Minimize(cost), constraints)
    problem.solve(solver=cp.OSQP, warm_start=True, verbose=False)

    if u.value is None:
        return 0.0, problem.status
    return float(u.value[0, 0]), problem.status


def main() -> None:
    args = build_parser().parse_args()
    if args.no_show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    dt = 0.1
    A = np.array([[1.0, dt], [0.0, 1.0]])
    B = np.array([[0.5 * dt**2], [dt]])

    q = np.diag([20.0, 2.0])
    r = np.diag([0.5])
    x_ref = np.array([1.0, 0.0])

    x_min = np.array([-2.0, -3.0])
    x_max = np.array([2.0, 3.0])
    u_min, u_max = -1.2, 1.2

    x = np.array([-1.5, 0.5])
    xs = [x.copy()]
    us = []
    solve_times = []
    infeasible_count = 0
    violation_count = 0

    for _ in range(args.sim_steps):
        t0 = time.perf_counter()
        u, status = solve_linear_mpc(
            A=A,
            B=B,
            x0=x,
            x_ref=x_ref,
            horizon=args.horizon,
            q=q,
            r=r,
            x_min=x_min,
            x_max=x_max,
            u_min=u_min,
            u_max=u_max,
        )
        solve_times.append(time.perf_counter() - t0)
        if status not in ("optimal", "optimal_inaccurate"):
            infeasible_count += 1
            u = 0.0

        x = A @ x + B.flatten() * u
        us.append(u)
        xs.append(x.copy())

        if (x < x_min - 1e-6).any() or (x > x_max + 1e-6).any() or u < u_min - 1e-6 or u > u_max + 1e-6:
            violation_count += 1

    x_arr = np.array(xs)
    u_arr = np.array(us)
    t_x = np.arange(x_arr.shape[0]) * dt
    t_u = np.arange(u_arr.shape[0]) * dt

    tracking_mse = float(np.mean((x_arr[:, 0] - x_ref[0]) ** 2))
    avg_solve_ms = float(np.mean(solve_times) * 1000.0)

    print(f"MPC demo: linear constrained QP")
    print(f"tracking_mse={tracking_mse:.6f}")
    print(f"constraint_violations={violation_count}")
    print(f"infeasible_steps={infeasible_count}")
    print(f"avg_solve_time_ms={avg_solve_ms:.3f}")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
    ax1.plot(t_x, x_arr[:, 0], label="position")
    ax1.plot(t_x, x_arr[:, 1], label="velocity")
    ax1.axhline(x_ref[0], color="k", linestyle="--", linewidth=1.0, label="position ref")
    ax1.set_ylabel("state")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="best")

    ax2.step(t_u, u_arr, where="post", label="u")
    ax2.axhline(u_min, color="r", linestyle="--", linewidth=1.0, label="u bounds")
    ax2.axhline(u_max, color="r", linestyle="--", linewidth=1.0)
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("input")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="best")

    fig.suptitle("Linear MPC (QP) on Double Integrator")
    fig.tight_layout()

    if args.save_fig:
        fig_dir = Path(__file__).resolve().parent / "figures"
        fig_dir.mkdir(parents=True, exist_ok=True)
        out = fig_dir / "linear_mpc_qp_demo.png"
        fig.savefig(out, dpi=140)
        print(f"saved_figure={out}")
    if not args.no_show:
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    main()
