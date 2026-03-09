import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.integrate import odeint
import tkinter as tk
from tkinter import ttk

def state_space_system(x, t, u, omega_n, zeta):
    dxdt = [x[1], u - 2 * zeta * omega_n * x[1] - omega_n**2 * x[0]]
    return dxdt

def pid_control_demo():
    root = tk.Tk()
    root.title("PID Control Demo - State Space System")

    # Create figure and axes for response
    fig, axResponse = plt.subplots(figsize=(8, 4))
    
    # Embed the plot into the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().grid(row=0, column=2, rowspan=10)
    
    def update_plot():
        # Retrieve the current values from the sliders
        Kp = sliderKp.get()
        Ki = sliderKi.get()
        Kd = sliderKd.get()

        noiseAmp = sliderNoiseAmp.get()
        corrFactor = sliderCorrFactor.get()

        initialState = sliderInitState.get()
        targetEndPoint = sliderEndPoint.get()

        damping = sliderDamping.get()
        frequency = sliderFrequency.get()

        timeDelay = sliderTimeDelay.get()

        # Time vector
        dt = 0.01
        t = np.arange(0, 20, dt)
        n = len(t)

        # Initial conditions
        x = [initialState, 0]
        y = np.zeros(n)
        u = np.zeros(n)

        # PID control variables
        integral = 0
        previous_error = 0

        # Simulation loop
        for k in range(n):
            # Calculate the error
            error = targetEndPoint - x[0]

            # Proportional term
            P = Kp * error

            # Integral term
            integral += error * dt
            I = Ki * integral

            # Derivative term
            derivative = (error - previous_error) / dt
            D = Kd * derivative

            # Control signal
            u[k] = P + I + D

            # Apply time delay
            if k - int(timeDelay / dt) > 0:
                u_delayed = u[k - int(timeDelay / dt)]
            else:
                u_delayed = 0

            # Solve the state-space equation
            x = odeint(state_space_system, x, [t[k], t[k] + dt], args=(u_delayed, frequency, damping))[1]
            y[k] = x[0]

            # Update previous error
            previous_error = error

        # Generate self-correlated noise
        noise = np.zeros_like(y)
        noise[0] = noiseAmp * np.random.randn()
        for i in range(1, len(noise)):
            noise[i] = corrFactor * noise[i - 1] + noiseAmp * np.random.randn()

        # Add noise to the response
        y += noise

        # Clear previous plot
        axResponse.clear()

        # Plot the response
        axResponse.plot(t, y)
        axResponse.set_title('Step Response of the State-Space System with Self-Correlated Noise')
        axResponse.set_xlabel('Time (s)')
        axResponse.set_ylabel('Output')
        axResponse.grid(True)

        # Redraw the plot
        canvas.draw()

    # Tkinter sliders and labels
    tk.Label(root, text="Kp").grid(row=0, column=0)
    sliderKp = tk.Scale(root, from_=0, to=10, resolution=0.1, orient=tk.HORIZONTAL)
    sliderKp.set(1)
    sliderKp.grid(row=0, column=1)

    tk.Label(root, text="Ki").grid(row=1, column=0)
    sliderKi = tk.Scale(root, from_=0, to=10, resolution=0.1, orient=tk.HORIZONTAL)
    sliderKi.set(1)
    sliderKi.grid(row=1, column=1)

    tk.Label(root, text="Kd").grid(row=2, column=0)
    sliderKd = tk.Scale(root, from_=0, to=10, resolution=0.1, orient=tk.HORIZONTAL)
    sliderKd.set(1)
    sliderKd.grid(row=2, column=1)

    tk.Label(root, text="Noise Amplitude").grid(row=3, column=0)
    sliderNoiseAmp = tk.Scale(root, from_=0, to=0.5, resolution=0.01, orient=tk.HORIZONTAL)
    sliderNoiseAmp.set(0.1)
    sliderNoiseAmp.grid(row=3, column=1)

    tk.Label(root, text="Correlation Factor").grid(row=4, column=0)
    sliderCorrFactor = tk.Scale(root, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL)
    sliderCorrFactor.set(0.5)
    sliderCorrFactor.grid(row=4, column=1)

    tk.Label(root, text="Initial State").grid(row=5, column=0)
    sliderInitState = tk.Scale(root, from_=-10, to=10, resolution=0.1, orient=tk.HORIZONTAL)
    sliderInitState.set(0)
    sliderInitState.grid(row=5, column=1)

    tk.Label(root, text="Target End Point").grid(row=6, column=0)
    sliderEndPoint = tk.Scale(root, from_=-10, to=10, resolution=0.1, orient=tk.HORIZONTAL)
    sliderEndPoint.set(1)
    sliderEndPoint.grid(row=6, column=1)

    tk.Label(root, text="Damping Coefficient").grid(row=7, column=0)
    sliderDamping = tk.Scale(root, from_=0, to=2, resolution=0.1, orient=tk.HORIZONTAL)
    sliderDamping.set(0.5)
    sliderDamping.grid(row=7, column=1)

    tk.Label(root, text="Natural Frequency").grid(row=8, column=0)
    sliderFrequency = tk.Scale(root, from_=0.1, to=5, resolution=0.1, orient=tk.HORIZONTAL)
    sliderFrequency.set(1)
    sliderFrequency.grid(row=8, column=1)

    tk.Label(root, text="Time Delay (s)").grid(row=9, column=0)
    sliderTimeDelay = tk.Scale(root, from_=0, to=5, resolution=0.1, orient=tk.HORIZONTAL)
    sliderTimeDelay.set(0)
    sliderTimeDelay.grid(row=9, column=1)

    # Update button
    update_button = ttk.Button(root, text="Update", command=update_plot)
    update_button.grid(row=10, column=0, columnspan=2)

    root.mainloop()

# Run the PID control demo
pid_control_demo()
