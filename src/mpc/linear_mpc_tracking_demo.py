"""Linear MPC tracking demo with piecewise reference and disturbance."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import cvxpy as cp
import matplotlib
import numpy as np


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Linear MPC tracking demo")
    parser.add_argument("--horizon", type=int, default=18, help="Prediction horizon N")
    parser.add_argument("--sim-steps", type=int, default=120, help="Closed-loop simulation steps")
    parser.add_argument("--save-fig", action="store_true", help="Save figure to src/mpc/figures")
    parser.add_argument("--no-show", action="store_true", help="Do not display figure window")
    return parser


def reference_signal(k: int, dt: float) -> float:
    t = k * dt
    if t < 4.0:
        return 0.0
    if t < 8.0:
        return 1.0
    if t < 12.0:
        return -0.7
    return 0.5


def solve_tracking_mpc(
    A: np.ndarray,
    B: np.ndarray,
    x0: np.ndarray,
    ref_seq: np.ndarray,
    horizon: int,
    q: np.ndarray,
    r: np.ndarray,
    x_min: np.ndarray,
    x_max: np.ndarray,
    u_min: float,
    u_max: float,
) -> tuple[float, str]:
    n_x = A.shape[0]
    x = cp.Variable((n_x, horizon + 1))
    u = cp.Variable((1, horizon))
    cost = 0
    constraints = [x[:, 0] == x0]

    for i in range(horizon):
        x_ref = np.array([ref_seq[i], 0.0])
        cost += cp.quad_form(x[:, i] - x_ref, q) + cp.quad_form(u[:, i], r)
        constraints += [
            x[:, i + 1] == A @ x[:, i] + B @ u[:, i],
            x_min <= x[:, i],
            x[:, i] <= x_max,
            u_min <= u[:, i],
            u[:, i] <= u_max,
        ]

    x_ref_terminal = np.array([ref_seq[-1], 0.0])
    cost += cp.quad_form(x[:, horizon] - x_ref_terminal, q)
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
    q = np.diag([30.0, 1.0])
    r = np.diag([0.4])
    x_min = np.array([-2.2, -2.5])
    x_max = np.array([2.2, 2.5])
    u_min, u_max = -1.3, 1.3

    x = np.array([0.3, 0.0])
    xs = [x.copy()]
    us = []
    refs = []
    solve_times = []
    infeasible_count = 0
    violation_count = 0

    for k in range(args.sim_steps):
        ref_seq = np.array(
            [reference_signal(k + i, dt=dt) for i in range(args.horizon + 1)],
            dtype=float,
        )
        refs.append(reference_signal(k, dt=dt))
        t0 = time.perf_counter()
        u, status = solve_tracking_mpc(
            A=A,
            B=B,
            x0=x,
            ref_seq=ref_seq,
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

        disturbance = 0.06 * np.sin(0.5 * k * dt)
        x = A @ x + B.flatten() * u + np.array([0.0, disturbance])
        xs.append(x.copy())
        us.append(u)
        if (x < x_min - 1e-6).any() or (x > x_max + 1e-6).any() or u < u_min - 1e-6 or u > u_max + 1e-6:
            violation_count += 1

    x_arr = np.array(xs)
    u_arr = np.array(us)
    refs_arr = np.array(refs)
    t_x = np.arange(x_arr.shape[0]) * dt
    t_u = np.arange(u_arr.shape[0]) * dt

    tracking_mse = float(np.mean((x_arr[:-1, 0] - refs_arr) ** 2))
    avg_solve_ms = float(np.mean(solve_times) * 1000.0)

    print("MPC demo: linear tracking with changing reference")
    print(f"tracking_mse={tracking_mse:.6f}")
    print(f"constraint_violations={violation_count}")
    print(f"infeasible_steps={infeasible_count}")
    print(f"avg_solve_time_ms={avg_solve_ms:.3f}")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
    ax1.plot(t_x[:-1], x_arr[:-1, 0], label="position")
    ax1.plot(t_x[:-1], refs_arr, "--", label="reference")
    ax1.set_ylabel("position")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="best")

    ax2.step(t_u, u_arr, where="post", label="u")
    ax2.axhline(u_min, color="r", linestyle="--", linewidth=1.0, label="u bounds")
    ax2.axhline(u_max, color="r", linestyle="--", linewidth=1.0)
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("input")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="best")

    fig.suptitle("Linear MPC Tracking Demo")
    fig.tight_layout()

    if args.save_fig:
        fig_dir = Path(__file__).resolve().parent / "figures"
        fig_dir.mkdir(parents=True, exist_ok=True)
        out = fig_dir / "linear_mpc_tracking_demo.png"
        fig.savefig(out, dpi=140)
        print(f"saved_figure={out}")

    if not args.no_show:
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    main()
