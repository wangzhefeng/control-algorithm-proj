"""Incremental LQR tracking demo with piecewise reference signal."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
import numpy as np
from scipy.linalg import solve_discrete_are


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Incremental LQR tracking demo")
    parser.add_argument("--sim-steps", type=int, default=150, help="Closed-loop simulation steps")
    parser.add_argument("--q-pos", type=float, default=30.0, help="Weight for position error")
    parser.add_argument("--q-vel", type=float, default=3.0, help="Weight for velocity error")
    parser.add_argument("--q-du-state", type=float, default=0.2, help="Weight for previous input state")
    parser.add_argument("--r-du", type=float, default=2.0, help="Weight for delta-u")
    parser.add_argument("--u-max", type=float, default=2.4, help="Absolute input limit")
    parser.add_argument("--du-max", type=float, default=0.9, help="Absolute delta-u limit")
    parser.add_argument("--save-fig", action="store_true", help="Save figure to src/lqr/figures")
    parser.add_argument("--no-show", action="store_true", help="Do not show figure window")
    return parser


def reference_signal(step: int, dt: float) -> float:
    t = step * dt
    if t < 4.0:
        return 0.0
    if t < 9.0:
        return 1.2
    if t < 13.0:
        return -0.8
    return 0.6


def dlqr_gain(A: np.ndarray, B: np.ndarray, Q: np.ndarray, R: np.ndarray) -> np.ndarray:
    P = solve_discrete_are(A, B, Q, R)
    K = np.linalg.solve(B.T @ P @ B + R, B.T @ P @ A)
    return K


def main() -> None:
    args = build_parser().parse_args()
    if args.no_show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    dt = 0.1
    A = np.array([[1.0, dt], [0.0, 1.0]], dtype=float)
    B = np.array([[0.5 * dt**2], [dt]], dtype=float)

    # Augmented incremental model: z = [e_pos, e_vel, u_prev]
    A_aug = np.array(
        [[1.0, dt, 0.5 * dt**2], [0.0, 1.0, dt], [0.0, 0.0, 1.0]],
        dtype=float,
    )
    B_aug = np.array([[0.5 * dt**2], [dt], [1.0]], dtype=float)

    Q = np.diag([args.q_pos, args.q_vel, args.q_du_state])
    R = np.array([[args.r_du]], dtype=float)
    K = dlqr_gain(A_aug, B_aug, Q, R)

    x = np.array([0.0, 0.0], dtype=float)
    u_prev = 0.0

    xs = [x.copy()]
    us = []
    refs = []
    du_hist = []
    clip_count = 0

    for k in range(args.sim_steps):
        ref_k = reference_signal(k, dt=dt)

        e = np.array([x[0] - ref_k, x[1]], dtype=float)
        z = np.array([e[0], e[1], u_prev], dtype=float)

        du_raw = float(-(K @ z)[0])
        du = float(np.clip(du_raw, -args.du_max, args.du_max))
        if abs(du_raw - du) > 1e-9:
            clip_count += 1

        u = float(np.clip(u_prev + du, -args.u_max, args.u_max))
        if abs((u_prev + du) - u) > 1e-9:
            clip_count += 1

        disturbance = np.array([0.0, 0.012 * np.sin(0.2 * k * dt)], dtype=float)
        x = A @ x + B.flatten() * u + disturbance

        refs.append(ref_k)
        us.append(u)
        du_hist.append(du)
        xs.append(x.copy())
        u_prev = u

    x_arr = np.array(xs)
    u_arr = np.array(us)
    ref_arr = np.array(refs)
    du_arr = np.array(du_hist)

    t_x = np.arange(x_arr.shape[0]) * dt
    t_u = np.arange(u_arr.shape[0]) * dt

    tracking_mse = float(np.mean((x_arr[:-1, 0] - ref_arr) ** 2))
    control_energy = float(np.sum(u_arr**2) * dt)
    delta_u_energy = float(np.sum(du_arr**2) * dt)

    print("LQR demo: incremental tracking")
    print(f"tracking_mse={tracking_mse:.6f}")
    print(f"control_energy={control_energy:.6f}")
    print(f"delta_u_energy={delta_u_energy:.6f}")
    print(f"constraint_violations={clip_count}")

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(9, 9), sharex=True)
    ax1.plot(t_x[:-1], x_arr[:-1, 0], label="position")
    ax1.plot(t_x[:-1], ref_arr, "--", label="reference")
    ax1.set_ylabel("position")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="best")

    ax2.step(t_u, u_arr, where="post", label="u")
    ax2.axhline(args.u_max, color="r", linestyle="--", linewidth=1.0, label="u limits")
    ax2.axhline(-args.u_max, color="r", linestyle="--", linewidth=1.0)
    ax2.set_ylabel("u")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="best")

    ax3.step(t_u, du_arr, where="post", label="delta_u")
    ax3.axhline(args.du_max, color="g", linestyle="--", linewidth=1.0, label="du limits")
    ax3.axhline(-args.du_max, color="g", linestyle="--", linewidth=1.0)
    ax3.set_xlabel("time (s)")
    ax3.set_ylabel("delta_u")
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc="best")

    fig.suptitle("Incremental LQR Tracking Demo")
    fig.tight_layout()

    if args.save_fig:
        fig_dir = Path(__file__).resolve().parent / "figures"
        fig_dir.mkdir(parents=True, exist_ok=True)
        out = fig_dir / "lqr_tracking_incremental_demo.png"
        fig.savefig(out, dpi=140)
        print(f"saved_figure={out}")

    if not args.no_show:
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    main()

