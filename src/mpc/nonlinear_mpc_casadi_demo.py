"""Nonlinear MPC demo using CasADi and direct multiple shooting."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import casadi as ca
import matplotlib
import numpy as np


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Nonlinear MPC (CasADi) demo")
    parser.add_argument("--horizon", type=int, default=25, help="Prediction horizon N")
    parser.add_argument("--sim-steps", type=int, default=90, help="Closed-loop simulation steps")
    parser.add_argument("--save-fig", action="store_true", help="Save figure to src/mpc/figures")
    parser.add_argument("--no-show", action="store_true", help="Do not show figure")
    return parser


def build_nmpc_solver(dt: float, horizon: int):
    opti = ca.Opti()

    x = opti.variable(2, horizon + 1)  # [position, velocity]
    u = opti.variable(1, horizon)
    x0 = opti.parameter(2, 1)
    x_ref = opti.parameter(1, horizon + 1)

    q_pos, q_vel, r_u = 45.0, 2.0, 0.2
    total_cost = 0
    opti.subject_to(x[:, 0] == x0)

    for k in range(horizon):
        pos_k = x[0, k]
        vel_k = x[1, k]
        uk = u[0, k]

        # Nonlinear dynamics: damped pendulum-like surrogate.
        pos_next = pos_k + dt * vel_k
        vel_next = vel_k + dt * (-0.4 * vel_k - ca.sin(pos_k) + uk)
        opti.subject_to(x[0, k + 1] == pos_next)
        opti.subject_to(x[1, k + 1] == vel_next)

        total_cost += q_pos * (pos_k - x_ref[0, k]) ** 2 + q_vel * vel_k**2 + r_u * uk**2

        opti.subject_to(opti.bounded(-2.4, pos_k, 2.4))
        opti.subject_to(opti.bounded(-3.0, vel_k, 3.0))
        opti.subject_to(opti.bounded(-2.0, uk, 2.0))

    total_cost += q_pos * (x[0, horizon] - x_ref[0, horizon]) ** 2 + q_vel * x[1, horizon] ** 2
    opti.subject_to(opti.bounded(-2.4, x[0, horizon], 2.4))
    opti.subject_to(opti.bounded(-3.0, x[1, horizon], 3.0))
    opti.minimize(total_cost)

    opts = {"ipopt.print_level": 0, "print_time": 0}
    opti.solver("ipopt", opts)
    return opti, (x, u, x0, x_ref)


def reference_signal(k: int, dt: float) -> float:
    t = k * dt
    if t < 3.0:
        return 0.0
    if t < 7.0:
        return 0.8
    if t < 11.0:
        return -0.9
    return 0.4


def main() -> None:
    args = build_parser().parse_args()
    if args.no_show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    dt = 0.08
    opti, (x_var, u_var, x0_par, xref_par) = build_nmpc_solver(dt=dt, horizon=args.horizon)

    xk = np.array([-1.0, 0.0], dtype=float)
    xs = [xk.copy()]
    us = []
    refs = []
    solve_times = []
    infeasible_count = 0
    violation_count = 0

    u_guess = np.zeros((1, args.horizon))
    x_guess = np.tile(xk.reshape(-1, 1), (1, args.horizon + 1))

    for k in range(args.sim_steps):
        ref_seq = np.array(
            [reference_signal(k + i, dt=dt) for i in range(args.horizon + 1)],
            dtype=float,
        ).reshape(1, -1)

        refs.append(reference_signal(k, dt=dt))
        opti.set_value(x0_par, xk.reshape(2, 1))
        opti.set_value(xref_par, ref_seq)
        opti.set_initial(u_var, u_guess)
        opti.set_initial(x_var, x_guess)

        t0 = time.perf_counter()
        status_ok = True
        try:
            sol = opti.solve()
            u_opt = float(sol.value(u_var[0, 0]))
            u_guess = np.asarray(sol.value(u_var), dtype=float).reshape(1, args.horizon)
            x_guess = np.asarray(sol.value(x_var), dtype=float).reshape(2, args.horizon + 1)
        except RuntimeError:
            status_ok = False
            u_opt = 0.0
        solve_times.append(time.perf_counter() - t0)

        if not status_ok:
            infeasible_count += 1

        pos, vel = xk
        pos_next = pos + dt * vel
        vel_next = vel + dt * (-0.4 * vel - np.sin(pos) + u_opt)
        xk = np.array([pos_next, vel_next], dtype=float)

        us.append(u_opt)
        xs.append(xk.copy())

        if abs(xk[0]) > 2.4 + 1e-6 or abs(xk[1]) > 3.0 + 1e-6 or abs(u_opt) > 2.0 + 1e-6:
            violation_count += 1

        # Shift initial guess for the next NMPC iteration.
        u_guess = np.hstack([u_guess[:, 1:], u_guess[:, -1:]])
        x_guess = np.hstack([x_guess[:, 1:], x_guess[:, -1:]])

    x_arr = np.array(xs)
    u_arr = np.array(us)
    refs_arr = np.array(refs)
    t_x = np.arange(x_arr.shape[0]) * dt
    t_u = np.arange(u_arr.shape[0]) * dt

    tracking_mse = float(np.mean((x_arr[:-1, 0] - refs_arr) ** 2))
    avg_solve_ms = float(np.mean(solve_times) * 1000.0)

    print("MPC demo: nonlinear MPC with CasADi")
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
    ax2.axhline(-2.0, color="r", linestyle="--", linewidth=1.0, label="u bounds")
    ax2.axhline(2.0, color="r", linestyle="--", linewidth=1.0)
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("input")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="best")

    fig.suptitle("Nonlinear MPC Demo (CasADi)")
    fig.tight_layout()

    if args.save_fig:
        fig_dir = Path(__file__).resolve().parent / "figures"
        fig_dir.mkdir(parents=True, exist_ok=True)
        out = fig_dir / "nonlinear_mpc_casadi_demo.png"
        fig.savefig(out, dpi=140)
        print(f"saved_figure={out}")

    if not args.no_show:
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    main()
