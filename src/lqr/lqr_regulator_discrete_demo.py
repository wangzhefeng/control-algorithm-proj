"""Discrete LQR regulator demo on a double-integrator system."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
import numpy as np
from scipy.linalg import solve_discrete_are


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Discrete LQR regulator demo")
    parser.add_argument("--sim-steps", type=int, default=120, help="Closed-loop simulation steps")
    parser.add_argument("--q-pos", type=float, default=18.0, help="State weight for position")
    parser.add_argument("--q-vel", type=float, default=2.0, help="State weight for velocity")
    parser.add_argument("--r-u", type=float, default=0.6, help="Input weight")
    parser.add_argument("--u-max", type=float, default=2.0, help="Absolute input limit")
    parser.add_argument("--save-fig", action="store_true", help="Save figure to src/lqr/figures")
    parser.add_argument("--no-show", action="store_true", help="Do not show figure window")
    return parser


def dlqr_gain(A: np.ndarray, B: np.ndarray, Q: np.ndarray, R: np.ndarray) -> np.ndarray:
    P = solve_discrete_are(A, B, Q, R)
    K = np.linalg.solve(B.T @ P @ B + R, B.T @ P @ A)
    return K


def compute_settling_time(error: np.ndarray, dt: float, tol: float = 0.02) -> tuple[float, bool]:
    within = np.abs(error) <= tol
    for i in range(len(error)):
        if within[i:].all():
            return float(i * dt), True
    return float((len(error) - 1) * dt), False


def main() -> None:
    args = build_parser().parse_args()
    if args.no_show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    dt = 0.1
    A = np.array([[1.0, dt], [0.0, 1.0]], dtype=float)
    B = np.array([[0.5 * dt**2], [dt]], dtype=float)

    Q = np.diag([args.q_pos, args.q_vel])
    R = np.array([[args.r_u]], dtype=float)
    K = dlqr_gain(A, B, Q, R)

    x = np.array([1.4, -0.3], dtype=float)
    xs = [x.copy()]
    us = []
    clipped_count = 0

    for k in range(args.sim_steps):
        u_raw = float(-(K @ x)[0])
        u = float(np.clip(u_raw, -args.u_max, args.u_max))
        if abs(u_raw - u) > 1e-9:
            clipped_count += 1

        disturbance = np.array([0.0, 0.02 * np.sin(0.15 * k)], dtype=float)
        x = A @ x + B.flatten() * u + disturbance

        xs.append(x.copy())
        us.append(u)

    x_arr = np.array(xs)
    u_arr = np.array(us)
    t_x = np.arange(x_arr.shape[0]) * dt
    t_u = np.arange(u_arr.shape[0]) * dt

    state_mse = float(np.mean(np.sum(x_arr[:-1] ** 2, axis=1)))
    control_energy = float(np.sum(u_arr**2) * dt)
    settling_time, settled = compute_settling_time(x_arr[:, 0], dt=dt)

    print("LQR demo: discrete regulator")
    print(f"state_mse={state_mse:.6f}")
    print(f"control_energy={control_energy:.6f}")
    print(f"settling_time_s={settling_time:.3f}")
    print(f"settled={int(settled)}")
    print(f"constraint_violations={clipped_count}")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
    ax1.plot(t_x, x_arr[:, 0], label="position")
    ax1.plot(t_x, x_arr[:, 1], label="velocity")
    ax1.axhline(0.0, color="k", linestyle="--", linewidth=1.0)
    ax1.set_ylabel("state")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="best")

    ax2.step(t_u, u_arr, where="post", label="u")
    ax2.axhline(args.u_max, color="r", linestyle="--", linewidth=1.0, label="u limits")
    ax2.axhline(-args.u_max, color="r", linestyle="--", linewidth=1.0)
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("input")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="best")

    fig.suptitle("Discrete LQR Regulator")
    fig.tight_layout()

    if args.save_fig:
        fig_dir = Path(__file__).resolve().parent / "figures"
        fig_dir.mkdir(parents=True, exist_ok=True)
        out = fig_dir / "lqr_regulator_discrete_demo.png"
        fig.savefig(out, dpi=140)
        print(f"saved_figure={out}")

    if not args.no_show:
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    main()
