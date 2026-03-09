import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def pid_control_coupled_systems_demo():
    # Function to simulate the coupled systems
    def simulate_systems():
        # Get parameters from sliders
        Kp1 = sliderKp1.get()
        Ki1 = sliderKi1.get()
        Kd1 = sliderKd1.get()
        damping1 = sliderDamping1.get()
        frequency1 = sliderFrequency1.get()
        initialState1 = sliderInitState1.get()
        targetEndPoint1 = sliderEndPoint1.get()
        k11 = sliderK11.get()
        k12 = sliderK12.get()

        Kp2 = sliderKp2.get()
        Ki2 = sliderKi2.get()
        Kd2 = sliderKd2.get()
        damping2 = sliderDamping2.get()
        frequency2 = sliderFrequency2.get()
        initialState2 = sliderInitState2.get()
        targetEndPoint2 = sliderEndPoint2.get()
        k21 = sliderK21.get()
        k22 = sliderK22.get()

        # State-space matrices
        A1 = np.array([[0, 1], [-frequency1**2, -2*damping1*frequency1]])
        B1 = np.array([0, 1])
        C1 = np.array([1, 0])

        A2 = np.array([[0, 1], [-frequency2**2, -2*damping2*frequency2]])
        B2 = np.array([0, 1])
        C2 = np.array([1, 0])

        # Time vector
        dt = 0.01
        t = np.arange(0, 20, dt)
        n = len(t)

        # Initial conditions
        x1 = np.array([initialState1, 0])
        x2 = np.array([initialState2, 0])
        y1 = np.zeros(n)
        y2 = np.zeros(n)
        u1 = np.zeros(n)
        u2 = np.zeros(n)

        # PID control variables
        integral1 = 0
        integral2 = 0
        previous_error1 = 0
        previous_error2 = 0

        # Simulation loop
        for k in range(n):
            error1 = targetEndPoint1 - C1 @ x1
            error2 = targetEndPoint2 - C2 @ x2

            P1 = Kp1 * error1
            P2 = Kp2 * error2

            integral1 += error1 * dt
            integral2 += error2 * dt
            I1 = Ki1 * integral1
            I2 = Ki2 * integral2

            derivative1 = (error1 - previous_error1) / dt
            derivative2 = (error2 - previous_error2) / dt
            D1 = Kd1 * derivative1
            D2 = Kd2 * derivative2

            u1[k] = P1 + I1 + D1
            u2[k] = P2 + I2 + D2

            x1 = x1 + dt * (A1 @ x1 + B1 * (k11 * u1[k] + k12 * u2[k]))
            x2 = x2 + dt * (A2 @ x2 + B2 * (k21 * u1[k] + k22 * u2[k]))
            y1[k] = C1 @ x1
            y2[k] = C2 @ x2

            previous_error1 = error1
            previous_error2 = error2

        # Plot the responses
        ax1.clear()
        ax2.clear()
        ax1.plot(t, y1)
        ax1.set_title('Response of System 1')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Output')
        ax1.grid(True)

        ax2.plot(t, y2)
        ax2.set_title('Response of System 2')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Output')
        ax2.grid(True)

        canvas.draw()

    # Create main window
    root = tk.Tk()
    root.title('PID Control Demo - Coupled Oscillatory Systems')

    # Create figure for plotting
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Control panel
    control_frame = tk.Frame(root)
    control_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)

    # Column 1: Parameters for System 1
    tk.Label(control_frame, text='System 1').grid(row=0, column=0, columnspan=2)

    tk.Label(control_frame, text='Kp1').grid(row=1, column=0)
    sliderKp1 = tk.Scale(control_frame, from_=0, to=10, resolution=0.1, orient=tk.HORIZONTAL)
    sliderKp1.set(1)
    sliderKp1.grid(row=1, column=1)

    tk.Label(control_frame, text='Ki1').grid(row=2, column=0)
    sliderKi1 = tk.Scale(control_frame, from_=0, to=10, resolution=0.1, orient=tk.HORIZONTAL)
    sliderKi1.set(1)
    sliderKi1.grid(row=2, column=1)

    tk.Label(control_frame, text='Kd1').grid(row=3, column=0)
    sliderKd1 = tk.Scale(control_frame, from_=0, to=10, resolution=0.1, orient=tk.HORIZONTAL)
    sliderKd1.set(1)
    sliderKd1.grid(row=3, column=1)

    tk.Label(control_frame, text='Damping 1').grid(row=4, column=0)
    sliderDamping1 = tk.Scale(control_frame, from_=0, to=2, resolution=0.1, orient=tk.HORIZONTAL)
    sliderDamping1.set(0.5)
    sliderDamping1.grid(row=4, column=1)

    tk.Label(control_frame, text='Frequency 1').grid(row=5, column=0)
    sliderFrequency1 = tk.Scale(control_frame, from_=0.1, to=5, resolution=0.1, orient=tk.HORIZONTAL)
    sliderFrequency1.set(1)
    sliderFrequency1.grid(row=5, column=1)

    tk.Label(control_frame, text='Init State 1').grid(row=6, column=0)
    sliderInitState1 = tk.Scale(control_frame, from_=-10, to=10, resolution=0.1, orient=tk.HORIZONTAL)
    sliderInitState1.set(0)
    sliderInitState1.grid(row=6, column=1)

    tk.Label(control_frame, text='Target End 1').grid(row=7, column=0)
    sliderEndPoint1 = tk.Scale(control_frame, from_=-10, to=10, resolution=0.1, orient=tk.HORIZONTAL)
    sliderEndPoint1.set(1)
    sliderEndPoint1.grid(row=7, column=1)

    tk.Label(control_frame, text='k11').grid(row=8, column=0)
    sliderK11 = tk.Scale(control_frame, from_=0, to=2, resolution=0.1, orient=tk.HORIZONTAL)
    sliderK11.set(1)
    sliderK11.grid(row=8, column=1)

    tk.Label(control_frame, text='k12').grid(row=9, column=0)
    sliderK12 = tk.Scale(control_frame, from_=0, to=2, resolution=0.1, orient=tk.HORIZONTAL)
    sliderK12.set(0.5)
    sliderK12.grid(row=9, column=1)

    # Column 2: Parameters for System 2
    tk.Label(control_frame, text='System 2').grid(row=0, column=2, columnspan=2)

    tk.Label(control_frame, text='Kp2').grid(row=1, column=2)
    sliderKp2 = tk.Scale(control_frame, from_=0, to=10, resolution=0.1, orient=tk.HORIZONTAL)
    sliderKp2.set(1)
    sliderKp2.grid(row=1, column=3)

    tk.Label(control_frame, text='Ki2').grid(row=2, column=2)
    sliderKi2 = tk.Scale(control_frame, from_=0, to=10, resolution=0.1, orient=tk.HORIZONTAL)
    sliderKi2.set(1)
    sliderKi2.grid(row=2, column=3)

    tk.Label(control_frame, text='Kd2').grid(row=3, column=2)
    sliderKd2 = tk.Scale(control_frame, from_=0, to=10, resolution=0.1, orient=tk.HORIZONTAL)
    sliderKd2.set(1)
    sliderKd2.grid(row=3, column=3)

    tk.Label(control_frame, text='Damping 2').grid(row=4, column=2)
    sliderDamping2 = tk.Scale(control_frame, from_=0, to=2, resolution=0.1, orient=tk.HORIZONTAL)
    sliderDamping2.set(0.5)
    sliderDamping2.grid(row=4, column=3)

    tk.Label(control_frame, text='Frequency 2').grid(row=5, column=2)
    sliderFrequency2 = tk.Scale(control_frame, from_=0.1, to=5, resolution=0.1, orient=tk.HORIZONTAL)
    sliderFrequency2.set(1)
    sliderFrequency2.grid(row=5, column=3)

    tk.Label(control_frame, text='Init State 2').grid(row=6, column=2)
    sliderInitState2 = tk.Scale(control_frame, from_=-10, to=10, resolution=0.1, orient=tk.HORIZONTAL)
    sliderInitState2.set(0)
    sliderInitState2.grid(row=6, column=3)

    tk.Label(control_frame, text='Target End 2').grid(row=7, column=2)
    sliderEndPoint2 = tk.Scale(control_frame, from_=-10, to=10, resolution=0.1, orient=tk.HORIZONTAL)
    sliderEndPoint2.set(1)
    sliderEndPoint2.grid(row=7, column=3)

    tk.Label(control_frame, text='k21').grid(row=8, column=2)
    sliderK21 = tk.Scale(control_frame, from_=0, to=2, resolution=0.1, orient=tk.HORIZONTAL)
    sliderK21.set(0.5)
    sliderK21.grid(row=8, column=3)

    tk.Label(control_frame, text='k22').grid(row=9, column=2)
    sliderK22 = tk.Scale(control_frame, from_=0, to=2, resolution=0.1, orient=tk.HORIZONTAL)
    sliderK22.set(1)
    sliderK22.grid(row=9, column=3)

    # Button to run the simulation
    run_button = ttk.Button(control_frame, text='Run Simulation', command=simulate_systems)
    run_button.grid(row=10, column=0, columnspan=4, pady=20)

    # Start GUI loop
    root.mainloop()

# Call the function to run the simulation with GUI
pid_control_coupled_systems_demo()
