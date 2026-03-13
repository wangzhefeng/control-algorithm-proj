"""NMPC demo: unicycle path tracking with CasADi."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import casadi as ca
import matplotlib
import numpy as np


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NMPC unicycle tracking demo")
    parser.add_argument("--horizon", type=int, default=20, help="Prediction horizon N")
    parser.add_argument("--sim-steps", type=int, default=100, help="Closed-loop simulation steps")
    parser.add_argument("--q-pos", type=float, default=70.0, help="State weight for x/y tracking")
    parser.add_argument("--q-theta", type=float, default=3.0, help="State weight for heading tracking")
    parser.add_argument("--r-v", type=float, default=0.6, help="Input weight for linear velocity")
    parser.add_argument("--r-omega", type=float, default=0.2, help="Input weight for angular velocity")
    parser.add_argument("--v-min", type=float, default=0.0, help="Lower bound of v")
    parser.add_argument("--v-max", type=float, default=1.0, help="Upper bound of v")
    parser.add_argument("--omega-max", type=float, default=1.2, help="Absolute bound of omega")
    parser.add_argument("--save-fig", action="store_true", help="Save figure to src/mpc/figures")
    parser.add_argument("--no-show", action="store_true", help="Do not show figure")
    return parser


def reference_state(k: int, dt: float) -> np.ndarray:
    t = k * dt
    radius = 1.2
    omega = 0.18
    x_ref = radius * np.cos(omega * t)
    y_ref = radius * np.sin(omega * t)
    theta_ref = omega * t + np.pi / 2.0
    return np.array([x_ref, y_ref, theta_ref], dtype=float)


def build_solver(
    dt: float,
    horizon: int,
    q_pos: float,
    q_theta: float,
    r_v: float,
    r_omega: float,
    v_min: float,
    v_max: float,
    omega_max: float,
):
    opti = ca.Opti()
    x = opti.variable(3, horizon + 1)  # [x, y, theta]
    u = opti.variable(2, horizon)  # [v, omega]
    x0 = opti.parameter(3, 1)
    x_ref = opti.parameter(3, horizon + 1)

    q = np.diag([q_pos, q_pos, q_theta])
    r = np.diag([r_v, r_omega])
    q_ca = ca.DM(q)
    r_ca = ca.DM(r)

    opti.subject_to(x[:, 0] == x0)
    total_cost = 0

    for k in range(horizon):
        px = x[0, k]
        py = x[1, k]
        th = x[2, k]
        v = u[0, k]
        w = u[1, k]

        px_next = px + dt * v * ca.cos(th)
        py_next = py + dt * v * ca.sin(th)
        th_next = th + dt * w
        opti.subject_to(x[0, k + 1] == px_next)
        opti.subject_to(x[1, k + 1] == py_next)
        opti.subject_to(x[2, k + 1] == th_next)

        e_x = x[:, k] - x_ref[:, k]
        total_cost += ca.mtimes([e_x.T, q_ca, e_x]) + ca.mtimes([u[:, k].T, r_ca, u[:, k]])

        opti.subject_to(opti.bounded(-2.5, px, 2.5))
        opti.subject_to(opti.bounded(-2.5, py, 2.5))
        opti.subject_to(opti.bounded(-3.2, th, 3.2))
        opti.subject_to(opti.bounded(v_min, v, v_max))
        opti.subject_to(opti.bounded(-omega_max, w, omega_max))

    e_terminal = x[:, horizon] - x_ref[:, horizon]
    total_cost += ca.mtimes([e_terminal.T, q_ca, e_terminal])
    opti.minimize(total_cost)

    opts = {"ipopt.print_level": 0, "print_time": 0}
    opti.solver("ipopt", opts)
    return opti, (x, u, x0, x_ref)


def wrap_to_pi(angle: float) -> float:
    return (angle + np.pi) % (2.0 * np.pi) - np.pi


def main() -> None:
    args = build_parser().parse_args()
    if args.no_show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    dt = 0.1
    opti, (x_var, u_var, x0_par, xref_par) = build_solver(
        dt=dt,
        horizon=args.horizon,
        q_pos=args.q_pos,
        q_theta=args.q_theta,
        r_v=args.r_v,
        r_omega=args.r_omega,
        v_min=args.v_min,
        v_max=args.v_max,
        omega_max=args.omega_max,
    )

    xk = np.array([1.6, -0.8, 0.2], dtype=float)
    u_guess = np.zeros((2, args.horizon))
    x_guess = np.tile(xk.reshape(3, 1), (1, args.horizon + 1))

    states = [xk.copy()]
    controls = []
    refs = []
    solve_times = []
    infeasible_count = 0
    violation_count = 0

    for k in range(args.sim_steps):
        ref_seq = np.column_stack(
            [reference_state(k + i, dt=dt) for i in range(args.horizon + 1)]
        ).astype(float)
        refs.append(reference_state(k, dt=dt))

        opti.set_value(x0_par, xk.reshape(3, 1))
        opti.set_value(xref_par, ref_seq)
        opti.set_initial(u_var, u_guess)
        opti.set_initial(x_var, x_guess)

        t0 = time.perf_counter()
        ok = True
        try:
            sol = opti.solve()
            uk = np.asarray(sol.value(u_var[:, 0]), dtype=float).reshape(2)
            u_guess = np.asarray(sol.value(u_var), dtype=float).reshape(2, args.horizon)
            x_guess = np.asarray(sol.value(x_var), dtype=float).reshape(3, args.horizon + 1)
        except RuntimeError:
            ok = False
            uk = np.array([0.0, 0.0], dtype=float)
        solve_times.append(time.perf_counter() - t0)

        if not ok:
            infeasible_count += 1

        px, py, th = xk
        v, w = uk
        px_next = px + dt * v * np.cos(th)
        py_next = py + dt * v * np.sin(th)
        th_next = wrap_to_pi(th + dt * w)
        xk = np.array([px_next, py_next, th_next], dtype=float)

        states.append(xk.copy())
        controls.append(uk.copy())

        if (
            abs(px_next) > 2.5 + 1e-6
            or abs(py_next) > 2.5 + 1e-6
            or not (args.v_min - 1e-6 <= v <= args.v_max + 1e-6)
            or abs(w) > args.omega_max + 1e-6
        ):
            violation_count += 1

        u_guess = np.hstack([u_guess[:, 1:], u_guess[:, -1:]])
        x_guess = np.hstack([x_guess[:, 1:], x_guess[:, -1:]])

    x_arr = np.array(states)
    u_arr = np.array(controls)
    r_arr = np.array(refs)

    xy_mse = float(np.mean((x_arr[:-1, :2] - r_arr[:, :2]) ** 2))
    heading_err = np.array([wrap_to_pi(a - b) for a, b in zip(x_arr[:-1, 2], r_arr[:, 2])], dtype=float)
    heading_mse = float(np.mean(heading_err**2))
    avg_solve_ms = float(np.mean(solve_times) * 1000.0)

    print("MPC demo: unicycle NMPC path tracking")
    print(f"tracking_mse_xy={xy_mse:.6f}")
    print(f"tracking_mse_heading={heading_mse:.6f}")
    print(f"constraint_violations={violation_count}")
    print(f"infeasible_steps={infeasible_count}")
    print(f"avg_solve_time_ms={avg_solve_ms:.3f}")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 8))
    ax1.plot(x_arr[:, 0], x_arr[:, 1], label="nmpc trajectory")
    ax1.plot(r_arr[:, 0], r_arr[:, 1], "--", label="reference")
    ax1.set_xlabel("x")
    ax1.set_ylabel("y")
    ax1.set_title("Unicycle XY Tracking")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="best")

    t_u = np.arange(u_arr.shape[0]) * dt
    ax2.step(t_u, u_arr[:, 0], where="post", label="v")
    ax2.step(t_u, u_arr[:, 1], where="post", label="omega")
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("control")
    ax2.set_title("Control Inputs")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="best")
    fig.tight_layout()

    if args.save_fig:
        fig_dir = Path(__file__).resolve().parent / "figures"
        fig_dir.mkdir(parents=True, exist_ok=True)
        out = fig_dir / "nmpc_unicycle_tracking_demo.png"
        fig.savefig(out, dpi=140)
        print(f"saved_figure={out}")

    if not args.no_show:
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    main()
