"""iLQR unicycle tracking demo with receding-horizon replanning."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import matplotlib
import numpy as np


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="iLQR unicycle tracking demo")
    parser.add_argument("--sim-steps", type=int, default=90, help="Closed-loop simulation steps")
    parser.add_argument("--horizon", type=int, default=30, help="Planning horizon")
    parser.add_argument("--ilqr-iters", type=int, default=18, help="Max iLQR iterations per step")
    parser.add_argument("--q-pos", type=float, default=18.0, help="Weight for x/y tracking")
    parser.add_argument("--q-theta", type=float, default=2.5, help="Weight for heading tracking")
    parser.add_argument("--r-v", type=float, default=0.5, help="Weight for linear velocity")
    parser.add_argument("--r-omega", type=float, default=0.2, help="Weight for angular velocity")
    parser.add_argument("--v-max", type=float, default=1.2, help="Absolute v limit")
    parser.add_argument("--omega-max", type=float, default=1.5, help="Absolute omega limit")
    parser.add_argument("--save-fig", action="store_true", help="Save figure to src/lqr/figures")
    parser.add_argument("--no-show", action="store_true", help="Do not show figure window")
    return parser


def wrap_to_pi(angle: float) -> float:
    return (angle + np.pi) % (2.0 * np.pi) - np.pi


def reference_state(step: int, dt: float) -> np.ndarray:
    t = step * dt
    radius = 1.3
    omega = 0.16
    x = radius * np.cos(omega * t)
    y = radius * np.sin(omega * t)
    theta = wrap_to_pi(omega * t + np.pi / 2.0)
    return np.array([x, y, theta], dtype=float)


def dynamics(x: np.ndarray, u: np.ndarray, dt: float) -> np.ndarray:
    px, py, th = x
    v, w = u
    return np.array(
        [
            px + dt * v * np.cos(th),
            py + dt * v * np.sin(th),
            wrap_to_pi(th + dt * w),
        ],
        dtype=float,
    )


def linearize_dynamics(x: np.ndarray, u: np.ndarray, dt: float) -> tuple[np.ndarray, np.ndarray]:
    _, _, th = x
    v, _ = u
    A = np.eye(3, dtype=float)
    A[0, 2] = -dt * v * np.sin(th)
    A[1, 2] = dt * v * np.cos(th)

    B = np.zeros((3, 2), dtype=float)
    B[0, 0] = dt * np.cos(th)
    B[1, 0] = dt * np.sin(th)
    B[2, 1] = dt
    return A, B


def rollout(x0: np.ndarray, u_seq: np.ndarray, dt: float) -> np.ndarray:
    xs = np.zeros((u_seq.shape[0] + 1, 3), dtype=float)
    xs[0] = x0
    for k in range(u_seq.shape[0]):
        xs[k + 1] = dynamics(xs[k], u_seq[k], dt)
    return xs


def stage_cost(x: np.ndarray, u: np.ndarray, x_ref: np.ndarray, Q: np.ndarray, R: np.ndarray) -> float:
    e = x - x_ref
    e[2] = wrap_to_pi(e[2])
    return float(e.T @ Q @ e + u.T @ R @ u)


def terminal_cost(x: np.ndarray, x_ref: np.ndarray, Qf: np.ndarray) -> float:
    e = x - x_ref
    e[2] = wrap_to_pi(e[2])
    return float(e.T @ Qf @ e)


def total_cost(x_seq: np.ndarray, u_seq: np.ndarray, refs: np.ndarray, Q: np.ndarray, R: np.ndarray, Qf: np.ndarray) -> float:
    cost = 0.0
    for k in range(u_seq.shape[0]):
        cost += stage_cost(x_seq[k], u_seq[k], refs[k], Q, R)
    cost += terminal_cost(x_seq[-1], refs[-1], Qf)
    return cost


def ilqr_solve(
    x0: np.ndarray,
    u_init: np.ndarray,
    refs: np.ndarray,
    dt: float,
    Q: np.ndarray,
    R: np.ndarray,
    Qf: np.ndarray,
    max_iters: int,
    v_max: float,
    omega_max: float,
) -> tuple[np.ndarray, np.ndarray, bool]:
    n_horizon = u_init.shape[0]
    u_seq = np.array(u_init, dtype=float)
    x_seq = rollout(x0, u_seq, dt)
    base_cost = total_cost(x_seq, u_seq, refs, Q, R, Qf)
    reg = 1e-4

    for _ in range(max_iters):
        A_list = []
        B_list = []
        l_x = []
        l_u = []
        l_xx = []
        l_uu = []

        for k in range(n_horizon):
            A_k, B_k = linearize_dynamics(x_seq[k], u_seq[k], dt)
            e = x_seq[k] - refs[k]
            e[2] = wrap_to_pi(e[2])

            A_list.append(A_k)
            B_list.append(B_k)
            l_x.append(2.0 * Q @ e)
            l_u.append(2.0 * R @ u_seq[k])
            l_xx.append(2.0 * Q)
            l_uu.append(2.0 * R)

        e_terminal = x_seq[-1] - refs[-1]
        e_terminal[2] = wrap_to_pi(e_terminal[2])
        V_x = 2.0 * Qf @ e_terminal
        V_xx = 2.0 * Qf

        k_ff = np.zeros((n_horizon, 2), dtype=float)
        K_fb = np.zeros((n_horizon, 2, 3), dtype=float)
        ok = True

        for k in range(n_horizon - 1, -1, -1):
            A_k = A_list[k]
            B_k = B_list[k]

            Q_x = l_x[k] + A_k.T @ V_x
            Q_u = l_u[k] + B_k.T @ V_x
            Q_xx = l_xx[k] + A_k.T @ V_xx @ A_k
            Q_ux = B_k.T @ V_xx @ A_k
            Q_uu = l_uu[k] + B_k.T @ V_xx @ B_k + reg * np.eye(2)

            try:
                Q_uu_inv = np.linalg.inv(Q_uu)
            except np.linalg.LinAlgError:
                ok = False
                break

            k_k = -Q_uu_inv @ Q_u
            K_k = -Q_uu_inv @ Q_ux

            k_ff[k] = k_k
            K_fb[k] = K_k

            V_x = Q_x + K_k.T @ Q_uu @ k_k + K_k.T @ Q_u + Q_ux.T @ k_k
            V_xx = Q_xx + K_k.T @ Q_uu @ K_k + K_k.T @ Q_ux + Q_ux.T @ K_k
            V_xx = 0.5 * (V_xx + V_xx.T)

        if not ok:
            reg = min(reg * 10.0, 1e6)
            continue

        improved = False
        for alpha in [1.0, 0.5, 0.25, 0.1, 0.05]:
            x_new = np.zeros_like(x_seq)
            u_new = np.zeros_like(u_seq)
            x_new[0] = x0

            for k in range(n_horizon):
                dx = x_new[k] - x_seq[k]
                dx[2] = wrap_to_pi(dx[2])
                du = alpha * k_ff[k] + K_fb[k] @ dx
                u_trial = u_seq[k] + du
                u_trial[0] = np.clip(u_trial[0], -v_max, v_max)
                u_trial[1] = np.clip(u_trial[1], -omega_max, omega_max)
                u_new[k] = u_trial
                x_new[k + 1] = dynamics(x_new[k], u_new[k], dt)

            new_cost = total_cost(x_new, u_new, refs, Q, R, Qf)
            if new_cost < base_cost:
                u_seq = u_new
                x_seq = x_new
                base_cost = new_cost
                reg = max(reg / 2.0, 1e-6)
                improved = True
                break

        if not improved:
            reg = min(reg * 5.0, 1e6)
            if reg > 1e5:
                break

        if np.max(np.abs(k_ff)) < 1e-3:
            break

    return x_seq, u_seq, True


def main() -> None:
    args = build_parser().parse_args()
    if args.no_show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    dt = 0.1
    Q = np.diag([args.q_pos, args.q_pos, args.q_theta])
    R = np.diag([args.r_v, args.r_omega])
    Qf = np.diag([args.q_pos * 2.0, args.q_pos * 2.0, args.q_theta * 2.0])

    xk = np.array([1.8, -0.8, 0.2], dtype=float)
    u_guess = np.zeros((args.horizon, 2), dtype=float)

    states = [xk.copy()]
    controls = []
    refs_log = []
    solve_times = []
    clip_count = 0

    for k in range(args.sim_steps):
        refs = np.array([reference_state(k + i, dt=dt) for i in range(args.horizon + 1)], dtype=float)
        refs_log.append(refs[0].copy())

        t0 = time.perf_counter()
        _, u_plan, _ = ilqr_solve(
            x0=xk,
            u_init=u_guess,
            refs=refs,
            dt=dt,
            Q=Q,
            R=R,
            Qf=Qf,
            max_iters=args.ilqr_iters,
            v_max=args.v_max,
            omega_max=args.omega_max,
        )
        solve_times.append(time.perf_counter() - t0)

        uk = u_plan[0].copy()
        clipped_v = float(np.clip(uk[0], -args.v_max, args.v_max))
        clipped_w = float(np.clip(uk[1], -args.omega_max, args.omega_max))
        if abs(clipped_v - uk[0]) > 1e-9 or abs(clipped_w - uk[1]) > 1e-9:
            clip_count += 1
        uk = np.array([clipped_v, clipped_w], dtype=float)

        xk = dynamics(xk, uk, dt)

        states.append(xk.copy())
        controls.append(uk.copy())

        u_guess = np.vstack([u_plan[1:], u_plan[-1:]])

    x_arr = np.array(states)
    u_arr = np.array(controls)
    r_arr = np.array(refs_log)

    t_u = np.arange(u_arr.shape[0]) * dt
    xy_mse = float(np.mean((x_arr[:-1, :2] - r_arr[:, :2]) ** 2))
    heading_err = np.array([wrap_to_pi(a - b) for a, b in zip(x_arr[:-1, 2], r_arr[:, 2])], dtype=float)
    heading_mse = float(np.mean(heading_err**2))
    control_energy = float(np.sum(np.sum(u_arr**2, axis=1)) * dt)
    avg_solve_ms = float(np.mean(solve_times) * 1000.0)

    print("LQR demo: iLQR unicycle tracking")
    print(f"tracking_mse_xy={xy_mse:.6f}")
    print(f"tracking_mse_heading={heading_mse:.6f}")
    print(f"control_energy={control_energy:.6f}")
    print(f"constraint_violations={clip_count}")
    print(f"avg_solve_time_ms={avg_solve_ms:.3f}")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 8))
    ax1.plot(x_arr[:, 0], x_arr[:, 1], label="iLQR trajectory")
    ax1.plot(r_arr[:, 0], r_arr[:, 1], "--", label="reference")
    ax1.set_xlabel("x")
    ax1.set_ylabel("y")
    ax1.set_title("Unicycle Tracking")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="best")

    ax2.step(t_u, u_arr[:, 0], where="post", label="v")
    ax2.step(t_u, u_arr[:, 1], where="post", label="omega")
    ax2.axhline(args.v_max, color="r", linestyle="--", linewidth=1.0, label="v limits")
    ax2.axhline(-args.v_max, color="r", linestyle="--", linewidth=1.0)
    ax2.axhline(args.omega_max, color="g", linestyle="--", linewidth=1.0, label="omega limits")
    ax2.axhline(-args.omega_max, color="g", linestyle="--", linewidth=1.0)
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("input")
    ax2.set_title("Control Inputs")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="best")

    fig.tight_layout()

    if args.save_fig:
        fig_dir = Path(__file__).resolve().parent / "figures"
        fig_dir.mkdir(parents=True, exist_ok=True)
        out = fig_dir / "ilqr_unicycle_demo.png"
        fig.savefig(out, dpi=140)
        print(f"saved_figure={out}")

    if not args.no_show:
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    main()
