function pid_control_state_space_demo()
    % Create a simple GUI
    f = figure('Name', 'PID Control Demo - State Space System', 'NumberTitle', 'off', 'Position', [100, 100, 1000, 800]);
    
    % Position parameters
    left_margin = 20;
    top_margin = 700;
    spacing = 30;
    
    % Display the system equation using LaTeX
    annotation('textbox', [0.05, 0.92, 0.9, 0.05], 'String', '$$\ddot{y}(t) + 2 \zeta \omega_n \dot{y}(t) + \omega_n^2 y(t) = u(t)$$', 'Interpreter', 'latex', 'EdgeColor', 'none', 'FontSize', 12);
    
    % Create sliders for PID parameters
    uicontrol('Style', 'text', 'Position', [left_margin, top_margin, 100, 20], 'String', 'Kp');
    sliderKp = uicontrol('Style', 'slider', 'Position', [left_margin, top_margin-spacing, 100, 20], 'Min', 0, 'Max', 10, 'Value', 1);
    
    uicontrol('Style', 'text', 'Position', [left_margin, top_margin-2*spacing, 100, 20], 'String', 'Ki');
    sliderKi = uicontrol('Style', 'slider', 'Position', [left_margin, top_margin-3*spacing, 100, 20], 'Min', 0, 'Max', 10, 'Value', 1);
    
    uicontrol('Style', 'text', 'Position', [left_margin, top_margin-4*spacing, 100, 20], 'String', 'Kd');
    sliderKd = uicontrol('Style', 'slider', 'Position', [left_margin, top_margin-5*spacing, 100, 20], 'Min', 0, 'Max', 10, 'Value', 1);
    
    % Create sliders for noise parameters
    uicontrol('Style', 'text', 'Position', [left_margin, top_margin-6*spacing, 100, 20], 'String', 'Noise Amplitude');
    sliderNoiseAmp = uicontrol('Style', 'slider', 'Position', [left_margin, top_margin-7*spacing, 100, 20], 'Min', 0, 'Max', 0.5, 'Value', 0.1);
    
    uicontrol('Style', 'text', 'Position', [left_margin, top_margin-8*spacing, 100, 20], 'String', 'Correlation Factor');
    sliderCorrFactor = uicontrol('Style', 'slider', 'Position', [left_margin, top_margin-9*spacing, 100, 20], 'Min', 0, 'Max', 1, 'Value', 0.5);
    
    % Create sliders for initial state and target end point
    uicontrol('Style', 'text', 'Position', [left_margin, top_margin-10*spacing, 100, 20], 'String', 'Initial State');
    sliderInitState = uicontrol('Style', 'slider', 'Position', [left_margin, top_margin-11*spacing, 100, 20], 'Min', -10, 'Max', 10, 'Value', 0);
    
    uicontrol('Style', 'text', 'Position', [left_margin, top_margin-12*spacing, 100, 20], 'String', 'Target End Point');
    sliderEndPoint = uicontrol('Style', 'slider', 'Position', [left_margin, top_margin-13*spacing, 100, 20], 'Min', -10, 'Max', 10, 'Value', 1);
    
    % Create sliders for system parameters
    uicontrol('Style', 'text', 'Position', [left_margin, top_margin-14*spacing, 100, 20], 'String', 'Damping Coefficient');
    sliderDamping = uicontrol('Style', 'slider', 'Position', [left_margin, top_margin-15*spacing, 100, 20], 'Min', 0, 'Max', 2, 'Value', 0.5);
    
    uicontrol('Style', 'text', 'Position', [left_margin, top_margin-16*spacing, 100, 20], 'String', 'Natural Frequency');
    sliderFrequency = uicontrol('Style', 'slider', 'Position', [left_margin, top_margin-17*spacing, 100, 20], 'Min', 0.1, 'Max', 5, 'Value', 1);
    
    % Create a slider for time delay
    uicontrol('Style', 'text', 'Position', [left_margin, top_margin-18*spacing, 100, 20], 'String', 'Time Delay (s)');
    sliderTimeDelay = uicontrol('Style', 'slider', 'Position', [left_margin, top_margin-19*spacing, 100, 20], 'Min', 0, 'Max', 5, 'Value', 0);
    
    % Create a button to update the plot
    uicontrol('Style', 'pushbutton', 'Position', [left_margin, top_margin-20*spacing, 100, 30], 'String', 'Update', 'Callback', @updatePlot);
    
    % Axes for plotting the response
    axResponse = axes('Position', [0.3, 0.55, 0.65, 0.4]);
    % Axes for the cartoon
    axCartoon = axes('Position', [0.3, 0.1, 0.65, 0.3]);
    
    % Initial plot
    updatePlot();
    
    function updatePlot(~, ~)
        % Get the PID parameters from sliders
        Kp = sliderKp.Value;
        Ki = sliderKi.Value;
        Kd = sliderKd.Value;
        
        % Get noise parameters from sliders
        noiseAmp = sliderNoiseAmp.Value;
        corrFactor = sliderCorrFactor.Value;
        
        % Get initial state and target end point from sliders
        initialState = sliderInitState.Value;
        targetEndPoint = sliderEndPoint.Value;
        
        % Get system parameters from sliders
        damping = sliderDamping.Value;
        frequency = sliderFrequency.Value;
        
        % Get time delay from slider
        timeDelay = sliderTimeDelay.Value;
        
        % State-space representation
        A = [0 1; -frequency^2 -2*damping*frequency];
        B = [0; 1];
        C = [1 0];
        D = 0;
        
        % Time vector
        dt = 0.01;
        t = 0:dt:20;
        n = length(t);
        
        % Initial conditions
        x = [initialState; 0];
        y = zeros(1, n);
        u = zeros(1, n);
        
        % PID control variables
        integral = 0;
        previous_error = 0;
        
        % Simulation loop
        for k = 1:n
            % Calculate the error
            error = targetEndPoint - C*x;
            
            % Proportional term
            P = Kp * error;
            
            % Integral term
            integral = integral + error * dt;
            I = Ki * integral;
            
            % Derivative term
            derivative = (error - previous_error) / dt;
            D = Kd * derivative;
            
            % Control signal
            u(k) = P + I + D;
            u_delayed = 0;
            if k - round(timeDelay/dt) > 0
                u_delayed = u(k - round(timeDelay/dt));
            end
            
            % System dynamics
            x = x + dt * (A*x + B*u_delayed);
            y(k) = C*x;
            
            % Update previous error
            previous_error = error;
        end
        
        % Generate self-correlated noise
        noise = zeros(size(y));
        noise(1) = noiseAmp * randn;
        for i = 2:length(noise)
            noise(i) = corrFactor * noise(i-1) + noiseAmp * randn;
        end
        
        % Add noise to the response
        y = y + noise;
        
        % Plot the response
        plot(axResponse, t, y);
        title(axResponse, 'Step Response of the State-Space System with Self-Correlated Noise');
        xlabel(axResponse, 'Time (s)');
        ylabel(axResponse, 'Output');
        grid(axResponse, 'on');
        
        % Update cartoon
        plotCartoon(y);
    end

    function plotCartoon(y)
        % Clear previous cartoon
        cla(axCartoon);
        
        % Plot cartoon (a simple moving ball)
        hold(axCartoon, 'on');
        axis(axCartoon, [0 10 0 1]);
        for i = 1:length(y)
            cla(axCartoon);
            rectangle('Position', [mod(y(i), 10), 0.5, 0.2, 0.2], 'Curvature', [1, 1], 'FaceColor', 'b');
            pause(0.01);
        end
        hold(axCartoon, 'off');
    end
end
