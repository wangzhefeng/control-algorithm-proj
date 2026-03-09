function pid_control_coupled_systems_demo()
    % Create a simple GUI
    f = figure('Name', 'PID Control Demo - Coupled Oscillatory Systems', 'NumberTitle', 'off', 'Position', [100, 100, 1000, 800]);
    
    % Position parameters
    left_margin = 20;
    top_margin = 760;
    spacing = 40;
    column_spacing = 200;
    
    % Display the system equations using LaTeX
    annotation('textbox', [0.05, 0.92, 0.9, 0.05], 'String', '$$\ddot{y}_1(t) + 2 \zeta_1 \omega_{n1} \dot{y}_1(t) + \omega_{n1}^2 y_1(t) = k_{11}u_1(t) + k_{12}u_2(t)$$', 'Interpreter', 'latex', 'EdgeColor', 'none', 'FontSize', 12);
    annotation('textbox', [0.05, 0.87, 0.9, 0.05], 'String', '$$\ddot{y}_2(t) + 2 \zeta_2 \omega_{n2} \dot{y}_2(t) + \omega_{n2}^2 y_2(t) = k_{21}u_1(t) + k_{22}u_2(t)$$', 'Interpreter', 'latex', 'EdgeColor', 'none', 'FontSize', 12);
    
    % Column 1: Parameters for System 1
    % PID parameters for system 1
    uicontrol('Style', 'text', 'Position', [left_margin, top_margin, 100, 20], 'String', 'Kp1');
    sliderKp1 = uicontrol('Style', 'slider', 'Position', [left_margin, top_margin-spacing, 100, 20], 'Min', 0, 'Max', 10, 'Value', 1);
    
    uicontrol('Style', 'text', 'Position', [left_margin, top_margin-2*spacing, 100, 20], 'String', 'Ki1');
    sliderKi1 = uicontrol('Style', 'slider', 'Position', [left_margin, top_margin-3*spacing, 100, 20], 'Min', 0, 'Max', 10, 'Value', 1);
    
    uicontrol('Style', 'text', 'Position', [left_margin, top_margin-4*spacing, 100, 20], 'String', 'Kd1');
    sliderKd1 = uicontrol('Style', 'slider', 'Position', [left_margin, top_margin-5*spacing, 100, 20], 'Min', 0, 'Max', 10, 'Value', 1);
    
    % System parameters for system 1
    uicontrol('Style', 'text', 'Position', [left_margin, top_margin-6*spacing, 100, 20], 'String', 'Damping 1');
    sliderDamping1 = uicontrol('Style', 'slider', 'Position', [left_margin, top_margin-7*spacing, 100, 20], 'Min', 0, 'Max', 2, 'Value', 0.5);
    
    uicontrol('Style', 'text', 'Position', [left_margin, top_margin-8*spacing, 100, 20], 'String', 'Frequency 1');
    sliderFrequency1 = uicontrol('Style', 'slider', 'Position', [left_margin, top_margin-9*spacing, 100, 20], 'Min', 0.1, 'Max', 5, 'Value', 1);
    
    % Initial state and target end point for system 1
    uicontrol('Style', 'text', 'Position', [left_margin, top_margin-10*spacing, 100, 20], 'String', 'Init State 1');
    sliderInitState1 = uicontrol('Style', 'slider', 'Position', [left_margin, top_margin-11*spacing, 100, 20], 'Min', -10, 'Max', 10, 'Value', 0);
    
    uicontrol('Style', 'text', 'Position', [left_margin, top_margin-12*spacing, 100, 20], 'String', 'Target End 1');
    sliderEndPoint1 = uicontrol('Style', 'slider', 'Position', [left_margin, top_margin-13*spacing, 100, 20], 'Min', -10, 'Max', 10, 'Value', 1);
    
    % Impact factors for system 1
    uicontrol('Style', 'text', 'Position', [left_margin, top_margin-14*spacing, 100, 20], 'String', 'k_{11}');
    sliderK11 = uicontrol('Style', 'slider', 'Position', [left_margin, top_margin-15*spacing, 100, 20], 'Min', 0, 'Max', 2, 'Value', 1);
    
    uicontrol('Style', 'text', 'Position', [left_margin, top_margin-16*spacing, 100, 20], 'String', 'k_{12}');
    sliderK12 = uicontrol('Style', 'slider', 'Position', [left_margin, top_margin-17*spacing, 100, 20], 'Min', 0, 'Max', 2, 'Value', 0.5);
    
    % Column 2: Parameters for System 2
    % PID parameters for system 2
    uicontrol('Style', 'text', 'Position', [left_margin+column_spacing, top_margin, 100, 20], 'String', 'Kp2');
    sliderKp2 = uicontrol('Style', 'slider', 'Position', [left_margin+column_spacing, top_margin-spacing, 100, 20], 'Min', 0, 'Max', 10, 'Value', 1);
    
    uicontrol('Style', 'text', 'Position', [left_margin+column_spacing, top_margin-2*spacing, 100, 20], 'String', 'Ki2');
    sliderKi2 = uicontrol('Style', 'slider', 'Position', [left_margin+column_spacing, top_margin-3*spacing, 100, 20], 'Min', 0, 'Max', 10, 'Value', 1);
    
    uicontrol('Style', 'text', 'Position', [left_margin+column_spacing, top_margin-4*spacing, 100, 20], 'String', 'Kd2');
    sliderKd2 = uicontrol('Style', 'slider', 'Position', [left_margin+column_spacing, top_margin-5*spacing, 100, 20], 'Min', 0, 'Max', 10, 'Value', 1);
    
    % System parameters for system 2
    uicontrol('Style', 'text', 'Position', [left_margin+column_spacing, top_margin-6*spacing, 100, 20], 'String', 'Damping 2');
    sliderDamping2 = uicontrol('Style', 'slider', 'Position', [left_margin+column_spacing, top_margin-7*spacing, 100, 20], 'Min', 0, 'Max', 2, 'Value', 0.5);
    
    uicontrol('Style', 'text', 'Position', [left_margin+column_spacing, top_margin-8*spacing, 100, 20], 'String', 'Frequency 2');
    sliderFrequency2 = uicontrol('Style', 'slider', 'Position', [left_margin+column_spacing, top_margin-9*spacing, 100, 20], 'Min', 0.1, 'Max', 5, 'Value', 1);
    
    % Initial state and target end point for system 2
    uicontrol('Style', 'text', 'Position', [left_margin+column_spacing, top_margin-10*spacing, 100, 20], 'String', 'Init State 2');
    sliderInitState2 = uicontrol('Style', 'slider', 'Position', [left_margin+column_spacing, top_margin-11*spacing, 100, 20], 'Min', -10, 'Max', 10, 'Value', 0);
    
    uicontrol('Style', 'text', 'Position', [left_margin+column_spacing, top_margin-12*spacing, 100, 20], 'String', 'Target End 2');
    sliderEndPoint2 = uicontrol('Style', 'slider', 'Position', [left_margin+column_spacing, top_margin-13*spacing, 100, 20], 'Min', -10, 'Max', 10, 'Value', 1);
    
    % Impact factors for system 2
    uicontrol('Style', 'text', 'Position', [left_margin+column_spacing, top_margin-14*spacing, 100, 20], 'String', 'k_{21}');
    sliderK21 = uicontrol('Style', 'slider', 'Position', [left_margin+column_spacing, top_margin-15*spacing, 100, 20], 'Min', 0, 'Max', 2, 'Value', 0.5);
    
    uicontrol('Style', 'text', 'Position', [left_margin+column_spacing, top_margin-16*spacing, 100, 20], 'String', 'k_{22}');
    sliderK22 = uicontrol('Style', 'slider', 'Position', [left_margin+column_spacing, top_margin-17*spacing, 100, 20], 'Min', 0, 'Max', 2, 'Value', 1);
    
    % Create a button to update the plot
    uicontrol('Style', 'pushbutton', 'Position', [left_margin, top_margin-18*spacing, 100, 30], 'String', 'Update', 'Callback', @updatePlot);
    
    % Axes for plotting the responses
    axResponse1 = axes('Position', [0.3, 0.55, 0.65, 0.4]);
    axResponse2 = axes('Position', [0.3, 0.1, 0.65, 0.4]);
    
    % Initial plot
    updatePlot();
    
    function updatePlot(~, ~)
        % Get the PID parameters for both systems
        Kp1 = sliderKp1.Value;
        Ki1 = sliderKi1.Value;
        Kd1 = sliderKd1.Value;
        Kp2 = sliderKp2.Value;
        Ki2 = sliderKi2.Value;
        Kd2 = sliderKd2.Value;
        
        % Get system parameters for both systems
        damping1 = sliderDamping1.Value;
        frequency1 = sliderFrequency1.Value;
        damping2 = sliderDamping2.Value;
        frequency2 = sliderFrequency2.Value;
        
        % Get initial states and target end points
        initialState1 = sliderInitState1.Value;
        targetEndPoint1 = sliderEndPoint1.Value;
        initialState2 = sliderInitState2.Value;
        targetEndPoint2 = sliderEndPoint2.Value;
        
        % Get impact factors
        k11 = sliderK11.Value;
        k12 = sliderK12.Value;
        k21 = sliderK21.Value;
        k22 = sliderK22.Value;
        
        % State-space representation for system 1
        A1 = [0 1; -frequency1^2 -2*damping1*frequency1];
        B1 = [0; 1];
        C1 = [1 0];
        
        % State-space representation for system 2
        A2 = [0 1; -frequency2^2 -2*damping2*frequency2];
        B2 = [0; 1];
        C2 = [1 0];
        
        % Time vector
        dt = 0.01;
        t = 0:dt:20;
        n = length(t);
        
        % Initial conditions
        x1 = [initialState1; 0];
        x2 = [initialState2; 0];
        y1 = zeros(1, n);
        y2 = zeros(1, n);
        u1 = zeros(1, n);
        u2 = zeros(1, n);
        
        % PID control variables for both systems
        integral1 = 0;
        integral2 = 0;
        previous_error1 = 0;
        previous_error2 = 0;
        
        % Simulation loop
        for k = 1:n
            % Calculate the error for both systems
            error1 = targetEndPoint1 - C1*x1;
            error2 = targetEndPoint2 - C2*x2;
            
            % Proportional terms
            P1 = Kp1 * error1;
            P2 = Kp2 * error2;
            
            % Integral terms
            integral1 = integral1 + error1 * dt;
            integral2 = integral2 + error2 * dt;
            I1 = Ki1 * integral1;
            I2 = Ki2 * integral2;
            
            % Derivative terms
            derivative1 = (error1 - previous_error1) / dt;
            derivative2 = (error2 - previous_error2) / dt;
            D1 = Kd1 * derivative1;
            D2 = Kd2 * derivative2;
            
            % Control signals
            u1(k) = P1 + I1 + D1;
            u2(k) = P2 + I2 + D2;
            
            % System dynamics with coupling
            x1 = x1 + dt * (A1*x1 + B1*(k11*u1(k) + k12*u2(k)));
            x2 = x2 + dt * (A2*x2 + B2*(k21*u1(k) + k22*u2(k)));
            y1(k) = C1*x1;
            y2(k) = C2*x2;
            
            % Update previous errors
            previous_error1 = error1;
            previous_error2 = error2;
        end
        
        % Plot the responses
        plot(axResponse1, t, y1);
        title(axResponse1, 'Response of System 1');
        xlabel(axResponse1, 'Time (s)');
        ylabel(axResponse1, 'Output');
        grid(axResponse1, 'on');
        
        plot(axResponse2, t, y2);
        title(axResponse2, 'Response of System 2');
        xlabel(axResponse2, 'Time (s)');
        ylabel(axResponse2, 'Output');
        grid(axResponse2, 'on');
    end
end
