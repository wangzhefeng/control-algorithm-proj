#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 11:04:56 2024

@author: suntie
"""

# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 19:50:20 2024

@author: suntie shuang liang V5.0
"""

import json
import numpy as np
from bisect import bisect_right
import pandas as pd
import os


def interpolation(left, right, x):
    diff = right - left
    add_value = diff * x / 60

    y = left + add_value
    return y


def interpolation_10min(left, right, x):
    diff = right - left
    add_value = diff * x / 10
    y = left + add_value
    return y


# 根据料表 做线性插值，得到每分钟的量
def look_table(time, dl_time, time_table, H2_table, TCS_table, A1_I_table, A2_I_table, B1_I_table, B2_I_table,
               C1_I_table, C2_I_table):
    if time == 0:
        H2_LL_base = H2_table[0]
        TCS_LL_base = TCS_table[0]

        # H2_TCS_ratio = H2_LL_base/TCS_LL_base
        # H2_change_max = 0.05*TCS_LL_base


    else:
        index = bisect_right(time_table, time / 60)  # time = 0 会报错，��个要单独做
        time_mod = time % 60

        H2_left = H2_table[index - 1]
        H2_right = H2_table[index]
        H2_LL_base = interpolation(H2_left, H2_right, time_mod)

        TCS_left = TCS_table[index - 1]
        TCS_right = TCS_table[index]

        TCS_LL_base = interpolation(TCS_left, TCS_right, time_mod)

    if time <= 0:

        A1_I_base = A1_I_table[0]
        A2_I_base = A2_I_table[0]
        B1_I_base = B1_I_table[0]
        B2_I_base = B2_I_table[0]
        C1_I_base = C1_I_table[0]
        C2_I_base = C2_I_table[0]
        Current_base = [A1_I_base, A2_I_base, B1_I_base, B2_I_base, C1_I_base, C2_I_base]

    else:
        index = bisect_right(time_table, dl_time / 60)  # time = 0 会报错，这个要单独做
        time_mod = dl_time % 60

        A1_I_left = A1_I_table[index - 1]
        A1_I_right = A1_I_table[index]
        A1_I_base = interpolation(A1_I_left, A1_I_right, time_mod)

        A2_I_left = A2_I_table[index - 1]
        A2_I_right = A2_I_table[index]
        A2_I_base = interpolation(A2_I_left, A2_I_right, time_mod)

        B1_I_left = B1_I_table[index - 1]
        B1_I_right = B1_I_table[index]
        B1_I_base = interpolation(B1_I_left, B1_I_right, time_mod)

        B2_I_left = B2_I_table[index - 1]
        B2_I_right = B2_I_table[index]
        B2_I_base = interpolation(B2_I_left, B2_I_right, time_mod)

        C1_I_left = C1_I_table[index - 1]
        C1_I_right = C1_I_table[index]
        C1_I_base = interpolation(C1_I_left, C1_I_right, time_mod)

        C2_I_left = C2_I_table[index - 1]
        C2_I_right = C2_I_table[index]
        C2_I_base = interpolation(C2_I_left, C2_I_right, time_mod)

        # H2_TCS_ratio = H2_LL_base/TCS_LL_base
        # H2_change_max = 0.05*TCS_LL_base

        Current_base = [A1_I_base, A2_I_base, B1_I_base, B2_I_base, C1_I_base, C2_I_base]

    return H2_LL_base, TCS_LL_base, Current_base


def get_ref(time, time_table, A1_V_table, A2_V_table, B1_V_table, B2_V_table, C1_V_table, C2_V_table, WQWD_table):
    if time == 0:
        A1_V_ref = A1_V_table[0]
        A2_V_ref = A2_V_table[0]
        B1_V_ref = B1_V_table[0]
        B2_V_ref = B2_V_table[0]
        C1_V_ref = C1_V_table[0]
        C2_V_ref = C2_V_table[0]
        WQWD_ref = WQWD_table[0]
    else:
        index = bisect_right(time_table, time / 60)  # time = 0 会报错，这个要单独做
        time_mod = time % 60

        A1_V_left = A1_V_table[index - 1]
        A1_V_right = A1_V_table[index]
        A1_V_ref = interpolation(A1_V_left, A1_V_right, time_mod)

        A2_V_left = A2_V_table[index - 1]
        A2_V_right = A2_V_table[index]
        A2_V_ref = interpolation(A2_V_left, A2_V_right, time_mod)

        B1_V_left = B1_V_table[index - 1]
        B1_V_right = B1_V_table[index]
        B1_V_ref = interpolation(B1_V_left, B1_V_right, time_mod)

        B2_V_left = B2_V_table[index - 1]
        B2_V_right = B2_V_table[index]
        B2_V_ref = interpolation(B2_V_left, B2_V_right, time_mod)

        C1_V_left = C1_V_table[index - 1]
        C1_V_right = C1_V_table[index]
        C1_V_ref = interpolation(C1_V_left, C1_V_right, time_mod)

        C2_V_left = C2_V_table[index - 1]
        C2_V_right = C2_V_table[index]
        C2_V_ref = interpolation(C2_V_left, C2_V_right, time_mod)

        WQWD_left = WQWD_table[index - 1]
        WQWD_right = WQWD_table[index]
        WQWD_ref = interpolation(WQWD_left, WQWD_right, time_mod)

    return A1_V_ref, A2_V_ref, B1_V_ref, B2_V_ref, C1_V_ref, C2_V_ref, WQWD_ref


def constraint_mode1(time, time_table, Change_percent, Change_table):
    if time == 0:
        change_max = 0
    else:
        index = bisect_right(time_table, time / 60)  # time = 0 会报错，这个要单独做
        time_mod = time % 60

        left_value = Change_table[index - 1]
        right_value = Change_table[index]
        base_value = interpolation(left_value, right_value, time_mod)
        change_max = (Change_percent / 100) * base_value

    return change_max


def constraint_mode2(time, time_table, Change_table):
    if time == 0:
        change_max = 0
    else:
        index = bisect_right(time_table, time / 60)  # time = 0 会报错，这个要单独做
        time_mod = time % 60

        left_value = Change_table[index - 1]
        right_value = Change_table[index]
        change_max = interpolation(left_value, right_value, time_mod)

    return change_max


def risk_control(current_add, Current_change_max, Current_base, H2_add, H2_change_hist, H2_LL_base, TCS_LL_base,
                 TCS_add, TCS_change_max):
    # current_add = min(current_add,Current_change_max)
    # current_add = max(current_add,0-Current_change_max)

    A1_I_TJ = Current_base[0] + current_add[0]
    A2_I_TJ = Current_base[1] + current_add[1]
    B1_I_TJ = Current_base[2] + current_add[2]
    B2_I_TJ = Current_base[3] + current_add[3]
    C1_I_TJ = Current_base[4] + current_add[4]
    C2_I_TJ = Current_base[5] + current_add[5]

    H2_TJLL = H2_LL_base + H2_add + H2_change_hist
    TCS_TJLL = TCS_LL_base + TCS_add
    H2_TJLL = min(H2_TJLL, H2_LL_base + H2_change_max)
    H2_TJLL = max(H2_TJLL, H2_LL_base - H2_change_max)

    return A1_I_TJ, A2_I_TJ, B1_I_TJ, B2_I_TJ, C1_I_TJ, C2_I_TJ, H2_TJLL, TCS_TJLL


def WuHua_detect(Power_info, WQWD_info, WuHua_status_last, time, WuHua_time):
    window_size = 30
    smoothed = np.convolve(np.asarray(Power_info), np.ones(window_size) / window_size, mode='valid')
    gl_diff = (smoothed[0] - smoothed[30]) / 30

    # 判��雾化状态并记录发生雾化的时间，时间为消除雾化模块的控制逻辑提供参考
    # 如果上次雾化状态与相同，则不更新雾化时间，如果与本次状态不同，认为是新出���的雾化，记录当前时间
    # 暂时假设不会一下子从低温变为高温雾化

    if (WQWD_info[0] < 420) & (gl_diff < -1.8):
        WuHua_status = 'WuHua_lowtemp'
        if WuHua_status_last == 'WuHua_lowtemp':
            WuHua_time = WuHua_time
        else:
            WuHua_time = time

    elif (WQWD_info[0] >= 420) & (gl_diff < -1.8):
        WuHua_status = 'WuHua_hightemp'
        if WuHua_status_last == 'WuHua_hightemp':
            WuHua_time = WuHua_time
        else:
            WuHua_time = time


    else:
        WuHua_status = 'Normal'
        WuHua_time = 0
    return WuHua_status, WuHua_time


def WuHua_control(WuHua_status, WuHua_time, time):
    if WuHua_status == 'WuHua_lowtemp':
        TCS_change = -100
        H2_change = 0
        Current_stop_add = 0

        if time - WuHua_time > 20:
            Current_change = 30
        elif time - WuHua_time > 15:
            Current_change = 20
        elif time - WuHua_time > 10:
            Current_change = 10

    elif WuHua_status == 'WuHua_hightemp':
        H2_change = 10
        TCS_change = 0
        Current_change = 0
        Current_stop_add = 0
        if time - WuHua_time > 5:
            H2_change = 30

        if time - WuHua_time > 10:
            H2_change = 50

        if time - WuHua_time > 15:
            H2_change = 50
            TCS_change = -50
            Current_stop_add = 1

        if time - WuHua_time > 25:
            H2_change = 50
            TCS_change = -50
            Curreng_change = -10
            Current_stop_add = 1

    return H2_change, TCS_change, Current_change, Current_stop_add


try:

    ############################ 共用参数读取 #####################################
    with open('parameters.json', 'r') as json_file:
        params = json.load(json_file)

    ParametersRange = json.loads(params['ParameterRange'][0])

    TCS_const_mode = ParametersRange['TCSDeviateUnit']
    H2_const_mode = ParametersRange['H2DeviateUnit']
    Current_const_mode = ParametersRange['CurrentDeviateUnit']  # ���大修改值的约束模式，0 百分比，1绝对值

    TCS_change_per = ParametersRange['TCSDeviateValue']
    H2_change_per = ParametersRange['H2DeviateValue']
    Current_change_per = ParametersRange['CurrentDeviateValue']

    TCS_change_table = ParametersRange['TCS']
    H2_change_table = ParametersRange['H2']
    Current_change_table = ParametersRange['Current']

    Table = json.loads(params['MaterialFormula'][0])
    H2_table = Table['H2']
    TCS_table = Table['TCS']

    A1_I_table = Table['A1']
    A2_I_table = Table['A2']
    B1_I_table = Table['B1']
    B2_I_table = Table['B2']
    C1_I_table = Table['C1']
    C2_I_table = Table['C2']

    time_table = Table['Time']
    isUseTable = float(Table['isUseMaterialFormula'])

    status = params['RunStatus'][0]

    adjustment_info = json.loads(params['deviation_set'][0])

    A1_Micro = adjustment_info['iA1Micro']
    A1_Phase = adjustment_info['iA1Phase']

    A2_Micro = adjustment_info['iA2Micro']
    A2_Phase = adjustment_info['iA2Phase']

    B1_Micro = adjustment_info['iB1Micro']
    B1_Phase = adjustment_info['iB1Phase']

    B2_Micro = adjustment_info['iB2Micro']
    B2_Phase = adjustment_info['iB2Phase']

    C1_Micro = adjustment_info['iC1Micro']
    C1_Phase = adjustment_info['iC1Phase']

    C2_Micro = adjustment_info['iC2Micro']
    C2_Phase = adjustment_info['iC2Phase']

    H2_phase = adjustment_info['h2Phase']
    H2_auto = adjustment_info['h2Auto']
    H2_manual = adjustment_info['h2Manual']

    TCS_phase = adjustment_info['tcsPhase']
    TCS_auto = adjustment_info['tcsAuto']
    TCS_manual = adjustment_info['tcsManual']

    # 数采参数

    time = params['RunTime'][0] * 60
    DLtime = params['DLTime'][0] * 60

    A1_V = params['V_A1']
    A2_V = params['V_A2']
    B1_V = params['V_B1']
    B2_V = params['V_B2']
    C1_V = params['V_C1']
    C2_V = params['V_C2']

    B2_V_30_60 = params['V_B2_HalfHour']

    A1_P = params['P_A1']
    A2_P = params['P_A2']
    B1_P = params['P_B1']
    B2_P = params['P_B2']
    C1_P = params['P_C1']
    C2_P = params['P_C2']

    WQWD = params['WQWD']

    window_size = 10
    smoothed_WQWD = np.convolve(np.asarray(WQWD), np.ones(window_size) / window_size, mode='valid')

    p_total = [sum(pair) for pair in zip(A1_P, A2_P, B1_P, B2_P, C1_P, C2_P)]
    window_size = 10
    smoothed_p = np.convolve(np.asarray(p_total), np.ones(window_size) / window_size, mode='valid')

    window_size = 10
    smoothed_A1 = np.convolve(np.asarray(A1_V), np.ones(window_size) / window_size, mode='valid')

    window_size = 10
    smoothed_B2 = np.convolve(np.asarray(B2_V), np.ones(window_size) / window_size, mode='valid')

    # 人工介入状态
    Expert = json.loads(params['Expert'][0])
    control = Expert['control']  # 0=>正常, 1 => 顺控, 2 => 智控, 3 => 人工介入   我们只管状态2 3就行
    excep = Expert[
        'excep']  # 0=>正常, 异常 1: 高温雾化; 2: 低温�����������������化; 3: 高温亮环; 4: 室温亮环; 5: 低温��������环; 6: 倒棒; 7: 缺相; 8: 拉�����������������������������������������������������������������������������������������������������������������������������
    towards = Expert['towards']

    # 挂起状态
    Suspend_info = json.loads(params['Hang_Up'][0])
    Suspend_status = float(Suspend_info['Status'])

    # WQWD = [490,490,490]
    A1_I = params['I_A1'][0]
    A2_I = params['I_A2'][0]
    B1_I = params['I_B1'][0]
    B2_I = params['I_B2'][0]
    C1_I = params['I_C1'][0]
    C2_I = params['I_C2'][0]
    TCS_LL = params['TCSLL'][0]
    H2_LL = params['H2LL'][0]
    LQS_LL = params['LBLQSLL'][0]  # 炉壁冷却水流量
    HSWD = params['LTHSWD'][0]  # 炉筒回水温度

    power_max = json.loads(params['maxPower'][0])['maxPower']
    JDDL_A1 = params['JDDL_A1'][0]
    JDDL_A2 = params['JDDL_A2'][0]
    JDDL_B1 = params['JDDL_B1'][0]
    JDDL_B2 = params['JDDL_B2'][0]
    JDDL_C1 = params['JDDL_C1'][0]
    JDDL_C2 = params['JDDL_C2'][0]
    JDDL = [JDDL_A1, JDDL_A2, JDDL_B1, JDDL_B2, JDDL_C1, JDDL_C2]
    try:
        last_data = json.loads(params['pid_outparams'][0])
        H2_change_hist = last_data['H2_change']
        current_add = last_data['Current_change']
        TCS_add = last_data['TCS_change']

        WuHua_status_last = last_data['WuHua']
        WuHua_time = last_data['WuHua_time']
        H2_LL_last = last_data['H2']
        TCS_LL_last = last_data['TCS']
        A1_I_last = last_data['A1_I']
        A2_I_last = last_data['A2_I']
        B1_I_last = last_data['B1_I']
        B2_I_last = last_data['B2_I']
        C1_I_last = last_data['C1_I']
        C2_I_last = last_data['C2_I']
        JDDL_H2 = last_data['JDDL_H2']
        JDDL_record = last_data['JDDL_record']
        hist_input = 1

    except Exception as e1:
        H2_change_hist = 0
        current_add = [0, 0, 0, 0, 0, 0]
        TCS_add = 0

        WuHua_time = 0
        WuHua_status_last = 'Normal'
        H2_LL_last = H2_LL
        TCS_LL_last = TCS_LL
        A1_I_last = A1_I
        A2_I_last = A2_I
        B1_I_last = B1_I
        B2_I_last = B2_I
        C1_I_last = C1_I
        C2_I_last = C2_I
        JDDL_H2 = 0
        JDDL_record = [0, 0, 0, 0, 0, 0]
        hist_input = e1

    ## AI 料表
    name_list = os.listdir('./')
    for file in name_list:
        if os.path.basename(file)[0:14] == 'ReferenceTable':
            file_name = file
    ReferenceTable = pd.read_csv(file_name)
    A1_I_table_ai = ReferenceTable['A1_I'].tolist()
    A2_I_table_ai = ReferenceTable['A2_I'].tolist()
    B1_I_table_ai = ReferenceTable['B1_I'].tolist()
    B2_I_table_ai = ReferenceTable['B2_I'].tolist()
    C1_I_table_ai = ReferenceTable['C1_I'].tolist()
    C2_I_table_ai = ReferenceTable['C2_I'].tolist()
    H2_table_ai = ReferenceTable['H2'].tolist()
    TCS_table_ai = ReferenceTable['TCS'].tolist()

    run_time = time + 1
    DL_time = DLtime + 1

    if status != 22:

        H2_LL_final = H2_LL
        TCS_LL_final = TCS_LL
        A1_I_final = A1_I
        A2_I_final = A2_I
        B1_I_final = B1_I
        B2_I_final = B2_I
        C1_I_final = C1_I
        C2_I_final = C2_I

        message = 'executed successfully'
        code = 1
        if status == 0:
            code = 0
            message = 'error status=0'
        data = {'TCS': float(TCS_LL_final), 'H2': float(H2_LL_final), 'A1_I': float(A1_I_final),
                'A2_I': float(A2_I_final), 'B1_I': float(B1_I_final),
                'B2_I': float(B2_I_final), 'C1_I': float(C1_I_final), 'C2_I': float(C2_I_final), 'last_status': status,
                'TCS_last': TCS_LL_last, 'H2_last': H2_LL_last, 'A1_I_last': A1_I_last,
                'A2_I_last': A2_I_last, 'B1_I_last': B1_I_last, 'B2_I_last': B2_I_last, 'C1_I_last': C1_I_last,
                'C2_I_last': C2_I_last, 'run_Time': run_time}

        log_data = {}

        output = {}

        output['Code'] = code
        output['data'] = data
        output['logdata'] = log_data
        output['message'] = message
        output['algorithmname'] = 'test1'
        print(json.dumps(output))



    else:

        time_mode = time % 20
        pid_run = 0

        ############# 完全按照料表控制 ##########
        if isUseTable == 1:

            TCS_fengkong = 1000
            H2_fengkong = 200
            A1_I_fengkong = 100
            A2_I_fengkong = 100
            B1_I_fengkong = 100
            B2_I_fengkong = 100
            C1_I_fengkong = 100
            C2_I_fengkong = 100

            if run_time <= 60:

                H2_notuse, TCS_notuse, Current_base = look_table(run_time, DL_time,
                                                                 time_table, H2_table, TCS_table, A1_I_table,
                                                                 A2_I_table, B1_I_table, B2_I_table, C1_I_table,
                                                                 C2_I_table)

                # Ori_value = params['PSRFAIParam']['PSRFAIOriginTcsH2']

                H2_ori = 65
                TCS_ori = 800

                H2_LL_base = (run_time - 30) * (H2_table[1] - H2_ori) / 30 + H2_ori
                TCS_LL_base = (run_time - 30) * (TCS_table[1] - TCS_ori) / 30 + TCS_ori

                Current_base[0] = (run_time - 30) * (A1_I_table[1] - A1_I_table[0]) / 30 + A1_I_table[0]
                Current_base[1] = (run_time - 30) * (A2_I_table[1] - A2_I_table[0]) / 30 + A2_I_table[0]
                Current_base[2] = (run_time - 30) * (B1_I_table[1] - B1_I_table[0]) / 30 + B1_I_table[0]
                Current_base[3] = (run_time - 30) * (B2_I_table[1] - B2_I_table[0]) / 30 + B2_I_table[0]
                Current_base[4] = (run_time - 30) * (C1_I_table[1] - C1_I_table[0]) / 30 + C1_I_table[0]
                Current_base[5] = (run_time - 30) * (C2_I_table[1] - C2_I_table[0]) / 30 + C2_I_table[0]

                WuHua_status = 'Normal'
                WuHua_time = 0

                TCS_TJLL = TCS_LL_base + TCS_manual + TCS_phase
                H2_TJLL = H2_LL_base + H2_manual + H2_phase
                A1_I_TJ = Current_base[0] + A1_Micro + A1_Phase
                A2_I_TJ = Current_base[1] + A2_Micro + A2_Phase
                B1_I_TJ = Current_base[2] + B1_Micro + B1_Phase
                B2_I_TJ = Current_base[3] + B2_Micro + B2_Phase
                C1_I_TJ = Current_base[4] + C1_Micro + C1_Phase
                C2_I_TJ = Current_base[5] + C2_Micro + C2_Phase

                TCS_LL_final = min(TCS_TJLL, TCS_LL_base + TCS_fengkong)
                H2_LL_final = min(H2_TJLL, H2_LL_base + H2_fengkong)
                A1_I_final = min(A1_I_TJ, Current_base[0] + A1_I_fengkong)
                A2_I_final = min(A2_I_TJ, Current_base[1] + A2_I_fengkong)
                B1_I_final = min(B1_I_TJ, Current_base[2] + B1_I_fengkong)
                B2_I_final = min(B2_I_TJ, Current_base[3] + B2_I_fengkong)
                C1_I_final = min(C1_I_TJ, Current_base[4] + C1_I_fengkong)
                C2_I_final = min(C2_I_TJ, Current_base[5] + C2_I_fengkong)

                TCS_LL_final = max(TCS_LL_final, TCS_LL_base - TCS_fengkong)
                H2_LL_final = max(H2_LL_final, H2_LL_base - H2_fengkong)
                A1_I_final = max(A1_I_final, Current_base[0] - A1_I_fengkong)
                A2_I_final = max(A2_I_final, Current_base[1] - A2_I_fengkong)
                B1_I_final = max(B1_I_final, Current_base[2] - B1_I_fengkong)
                B2_I_final = max(B2_I_final, Current_base[3] - B2_I_fengkong)
                C1_I_final = max(C1_I_final, Current_base[4] - C1_I_fengkong)
                C2_I_final = max(C2_I_final, Current_base[5] - C2_I_fengkong)

                H2_change = H2_LL_final - H2_LL_base
                TCS_change = TCS_LL_final - TCS_LL_base
                Current_change = [A1_I_final - Current_base[0]]
                Current_change.append(A2_I_final - Current_base[1])
                Current_change.append(B1_I_final - Current_base[2])
                Current_change.append(B2_I_final - Current_base[3])
                Current_change.append(C1_I_final - Current_base[4])
                Current_change.append(C2_I_final - Current_base[5])


            else:
                H2_LL_base, TCS_LL_base, Current_base = look_table(run_time, DL_time,
                                                                   time_table, H2_table, TCS_table, A1_I_table,
                                                                   A2_I_table, B1_I_table, B2_I_table, C1_I_table,
                                                                   C2_I_table)

                H2_LL_base_ai, TCS_LL_base_ai, Current_base_ai = look_table(run_time, DL_time,
                                                                            time_table, H2_table_ai, TCS_table_ai,
                                                                            A1_I_table_ai, A2_I_table_ai, B1_I_table_ai,
                                                                            B2_I_table_ai, C1_I_table_ai, C2_I_table_ai)

                WuHua_status = 'Normal'
                WuHua_time = 0

                TCS_TJLL = TCS_LL_base + TCS_manual + TCS_phase
                H2_TJLL = H2_LL_base + H2_manual + H2_phase
                A1_I_TJ = Current_base[0] + A1_Micro + A1_Phase
                A2_I_TJ = Current_base[1] + A2_Micro + A2_Phase
                B1_I_TJ = Current_base[2] + B1_Micro + B1_Phase
                B2_I_TJ = Current_base[3] + B2_Micro + B2_Phase
                C1_I_TJ = Current_base[4] + C1_Micro + C1_Phase
                C2_I_TJ = Current_base[5] + C2_Micro + C2_Phase

                TCS_LL_final = min(TCS_TJLL, TCS_LL_base + TCS_fengkong)
                H2_LL_final = min(H2_TJLL, H2_LL_base + H2_fengkong)
                A1_I_final = min(A1_I_TJ, Current_base[0] + A1_I_fengkong)
                A2_I_final = min(A2_I_TJ, Current_base[1] + A2_I_fengkong)
                B1_I_final = min(B1_I_TJ, Current_base[2] + B1_I_fengkong)
                B2_I_final = min(B2_I_TJ, Current_base[3] + B2_I_fengkong)
                C1_I_final = min(C1_I_TJ, Current_base[4] + C1_I_fengkong)
                C2_I_final = min(C2_I_TJ, Current_base[5] + C2_I_fengkong)

                TCS_LL_final = max(TCS_LL_final, TCS_LL_base - TCS_fengkong)
                H2_LL_final = max(H2_LL_final, H2_LL_base - H2_fengkong)
                A1_I_final = max(A1_I_final, Current_base[0] - A1_I_fengkong)
                A2_I_final = max(A2_I_final, Current_base[1] - A2_I_fengkong)
                B1_I_final = max(B1_I_final, Current_base[2] - B1_I_fengkong)
                B2_I_final = max(B2_I_final, Current_base[3] - B2_I_fengkong)
                C1_I_final = max(C1_I_final, Current_base[4] - C1_I_fengkong)
                C2_I_final = max(C2_I_final, Current_base[5] - C2_I_fengkong)

                H2_change = H2_LL_final - H2_LL_base_ai
                TCS_change = TCS_LL_final - TCS_LL_base_ai
                Current_change = [A1_I_final - Current_base_ai[0]]
                Current_change.append(A2_I_final - Current_base_ai[1])
                Current_change.append(B1_I_final - Current_base_ai[2])
                Current_change.append(B2_I_final - Current_base_ai[3])
                Current_change.append(C1_I_final - Current_base_ai[4])
                Current_change.append(C2_I_final - Current_base_ai[5])
        ############## PID���制 ###############
        else:
            # 得��控��参��风��值

            name_list = os.listdir('./')
            for file in name_list:
                if os.path.basename(file)[0:9] == 'Power_ref':
                    file_name = file
            power_table = pd.read_csv(file_name)

            power_line = power_table['power'].tolist()

            if TCS_const_mode == 0:
                TCS_change_max = constraint_mode1(run_time, time_table, TCS_change_per, TCS_change_table)
            else:
                TCS_change_max = constraint_mode2(run_time, time_table, TCS_change_table)

            if H2_const_mode == 0:
                H2_change_max = constraint_mode1(run_time, time_table, H2_change_per, H2_change_table)
            else:
                H2_change_max = constraint_mode2(run_time, time_table, H2_change_table)

            if Current_const_mode == 0:
                Current_change_max = constraint_mode1(run_time, time_table, Current_change_per, Current_change_table)
            else:
                Current_change_max = constraint_mode2(run_time, time_table, Current_change_table)

            H2_change_max = 80

            # WuHua_status,WuHua_time = WuHua_detect(A1_P,WQWD,WuHua_status_last,run_time,WuHua_time)
            WuHua_status = 'Normal'
            WuHua_time = 0
            if WuHua_status == 'Normal':
                if run_time <= 60:
                    H2_notuse, TCS_notuse, Current_base = look_table(run_time, DL_time,
                                                                     time_table, H2_table_ai, TCS_table_ai,
                                                                     A1_I_table_ai, A2_I_table_ai, B1_I_table_ai,
                                                                     B2_I_table_ai, C1_I_table_ai, C2_I_table_ai)

                    # Ori_value = params['PSRFAIParam']['PSRFAIOriginTcsH2']

                    H2_ori = 65
                    TCS_ori = 800

                    H2_LL_base = (run_time - 30) * (H2_table_ai[1] - H2_ori) / 30 + H2_ori
                    TCS_LL_base = (run_time - 30) * (TCS_table_ai[1] - TCS_ori) / 30 + TCS_ori

                    Current_base[0] = (run_time - 30) * (A1_I_table[1] - A1_I_table[0]) / 30 + A1_I_table[0]
                    Current_base[1] = (run_time - 30) * (A2_I_table[1] - A2_I_table[0]) / 30 + A2_I_table[0]
                    Current_base[2] = (run_time - 30) * (B1_I_table[1] - B1_I_table[0]) / 30 + B1_I_table[0]
                    Current_base[3] = (run_time - 30) * (B2_I_table[1] - B2_I_table[0]) / 30 + B2_I_table[0]
                    Current_base[4] = (run_time - 30) * (C1_I_table[1] - C1_I_table[0]) / 30 + C1_I_table[0]
                    Current_base[5] = (run_time - 30) * (C2_I_table[1] - C2_I_table[0]) / 30 + C2_I_table[0]

                    TCS_TJLL = TCS_LL_base + TCS_add
                    H2_TJLL = H2_LL_base + H2_change_hist
                    A1_I_TJ = Current_base[0] + current_add[0]
                    A2_I_TJ = Current_base[1] + current_add[1]
                    B1_I_TJ = Current_base[2] + current_add[2]
                    B2_I_TJ = Current_base[3] + current_add[3]
                    C1_I_TJ = Current_base[4] + current_add[4]
                    C2_I_TJ = Current_base[5] + current_add[5]

                    H2_change = H2_change_hist
                    TCS_change = TCS_add
                    Current_change = current_add
                elif run_time <= 120:
                    H2_LL_base, TCS_LL_base, Current_base = look_table(run_time, DL_time,
                                                                       time_table, H2_table_ai, TCS_table_ai,
                                                                       A1_I_table_ai, A2_I_table_ai, B1_I_table_ai,
                                                                       B2_I_table_ai, C1_I_table_ai, C2_I_table_ai)

                    TCS_TJLL = TCS_LL_base + TCS_add
                    H2_TJLL = H2_LL_base + H2_change_hist
                    A1_I_TJ = Current_base[0] + current_add[0]
                    A2_I_TJ = Current_base[1] + current_add[1]
                    B1_I_TJ = Current_base[2] + current_add[2]
                    B2_I_TJ = Current_base[3] + current_add[3]
                    C1_I_TJ = Current_base[4] + current_add[4]
                    C2_I_TJ = Current_base[5] + current_add[5]

                    H2_change = H2_change_hist
                    TCS_change = TCS_add
                    Current_change = current_add
                elif run_time <= 180:
                    H2_LL_base, TCS_LL_base, Current_base = look_table(run_time, DL_time,
                                                                       time_table, H2_table_ai, TCS_table_ai,
                                                                       A1_I_table_ai, A2_I_table_ai, B1_I_table_ai,
                                                                       B2_I_table_ai, C1_I_table_ai, C2_I_table_ai)

                    time_mode = time % 10
                    if time % 10 < 1:
                        pid_run = 1

                        max_B2_V = max(B2_V_30_60)

                        if max_B2_V > 1260 and current_add[0] < 2:
                            current_add[0] = current_add[0] + 1
                            current_add[1] = current_add[1] + 1
                            current_add[2] = current_add[2] + 1
                            current_add[3] = current_add[3] + 0.6
                            current_add[4] = current_add[4] + 1
                            current_add[5] = current_add[5] + 1

                        TCS_TJLL = TCS_LL_base + TCS_add
                        H2_TJLL = H2_LL_base + H2_change_hist
                        A1_I_TJ = Current_base[0] + current_add[0]
                        A2_I_TJ = Current_base[1] + current_add[1]
                        B1_I_TJ = Current_base[2] + current_add[2]
                        B2_I_TJ = Current_base[3] + current_add[3]
                        C1_I_TJ = Current_base[4] + current_add[4]
                        C2_I_TJ = Current_base[5] + current_add[5]

                        H2_change = H2_change_hist
                        TCS_change = TCS_add
                        Current_change = current_add


                    else:

                        TCS_TJLL = TCS_LL_base + TCS_add
                        H2_TJLL = H2_LL_base + H2_change_hist
                        A1_I_TJ = Current_base[0] + current_add[0]
                        A2_I_TJ = Current_base[1] + current_add[1]
                        B1_I_TJ = Current_base[2] + current_add[2]
                        B2_I_TJ = Current_base[3] + current_add[3]
                        C1_I_TJ = Current_base[4] + current_add[4]
                        C2_I_TJ = Current_base[5] + current_add[5]

                        H2_change = H2_change_hist
                        TCS_change = TCS_add
                        Current_change = current_add

                        # elif run_time <= 300:
                #    H2_LL_base,TCS_LL_base,Current_base = look_table(run_time,DL_time,
                #        time_table,H2_table_ai,TCS_table_ai,A1_I_table_ai,A2_I_table_ai,B1_I_table_ai,B2_I_table_ai,C1_I_table_ai,C2_I_table_ai)

                #   TCS_TJLL = TCS_LL_base + TCS_add
                #   H2_TJLL = H2_LL_base + H2_change_hist
                #   A1_I_TJ = Current_base[0] + current_add[0]
                #   A2_I_TJ = Current_base[1] + current_add[1]
                #   B1_I_TJ = Current_base[2] + current_add[2]
                #   B2_I_TJ = Current_base[3] + current_add[3]
                #   C1_I_TJ = Current_base[4] + current_add[4]
                #   C2_I_TJ = Current_base[5] + current_add[5]

                #  H2_change = H2_change_hist
                #  TCS_change = TCS_add
                #  Current_change = current_add
                elif run_time <= 780:
                    H2_LL_base, TCS_LL_base, Current_base = look_table(
                        run_time, 
                        DL_time,
                        time_table, 
                        H2_table_ai, 
                        TCS_table_ai,
                        A1_I_table_ai, 
                        A2_I_table_ai, 
                        B1_I_table_ai,
                        B2_I_table_ai, 
                        C1_I_table_ai, 
                        C2_I_table_ai
                    )
                    time_mode = time % 20
                    H2_ratio = ((H2_LL_base + H2_change_hist) / 2) / (TCS_LL_base / 135.5)
                    # 每 30 分钟一次调控
                    if time % 20 < 1:
                        pid_run = 1
                        index = int((time - 30) // 10)

                        power_diff_goal = power_line[index] - power_line[index - 6]  # 这次运行的功率斜率目标
                        power_diff_goal_past = power_line[index - 2] - power_line[index - 8]  # 10���������������的功率斜率目标

                        power_diff_goal = min(power_diff_goal, 190)
                        power_diff_goal_past = min(power_diff_goal_past, 190)

                        power_diff = smoothed_p[0] - smoothed_p[60]
                        power_diff_past = smoothed_p[20] - smoothed_p[80]
                        # PID
                        value_p = power_diff_goal - power_diff
                        value_I = power_diff_goal_past - power_diff_past
                        value_d = value_p - value_I

                        power_goal = power_line[index]
                        power_goal_past = power_line[index - 6]
                        value_p_power = power_goal - smoothed_p[0]
                        value_I_power = power_goal_past - smoothed_p[20]

                        value_p_power = min(0, value_p_power)
                        value_I_power = min(0, value_I_power)
                        value_d_power = value_p_power - value_I_power

                        if run_time <= 300:
                            H2_add_max = 3
                        else:
                            H2_add_max = 3

                        if abs(H2_change_hist) < 150 and H2_ratio >= 1.7:

                            # 如果差的��多了，就吧kp，kd设小�� 减少超调，震荡
                            if abs(value_p) < 3:
                                kp = 0.05
                                kp2 = 0.0002
                                # ki = 0.5
                                kd = 0.05
                                kd2 = 0.0001
                            else:
                                kp = 0.1
                                kp2 = 0.0005
                                # ki = 0.5
                                kd = 0.03
                                kd2 = 0.0002

                            # kd ��衡��面kp
                            # 比如10分���前���率���目���高10，现在��高8，此���kp还�����H2，但是kd为正，�������������������������氢�������调整量
                            # 因为最后会再把之前的氢气调整量加上，暂时就不加ki了，那个调整量相当于ki
                            H2_add = kp * value_p + kd * value_d + kp2 * value_p_power + kd2 * value_d_power

                            H2_add = min(H2_add, 3)
                            H2_add = max(H2_add, 0 - H2_add_max)
                        elif H2_ratio < 1.7:
                            H2_add = 3
                        else:
                            H2_add = 0

                        # if value_d < -5 and current_add[0]<10:
                        #    current_add[0] = current_add[0] + 1.5
                        #    current_add[1] = current_add[1] + 1.5
                        #    current_add[2] = current_add[2] + 1.5
                        #    current_add[3] = current_add[3] + 0.9
                        #    current_add[4] = current_add[4] + 1.5
                        #    current_add[5] = current_add[5] + 1.5

                        WQWD_sec_diff = (smoothed_WQWD[0] - smoothed_WQWD[30]) - (smoothed_WQWD[30] - smoothed_WQWD[60])
                        WQWD_diff = smoothed_WQWD[0] - smoothed_WQWD[30]

                        if WQWD_diff > 4 and WQWD_sec_diff > 1.5:
                            H2_add = 1 * (WQWD_diff - 3) + 1.5 * (WQWD_sec_diff - 0)
                            H2_add = min(H2_add, 8)
                            H2_add = max(H2_add, 0)
                        elif WQWD_diff > 3 and WQWD_sec_diff > 1:
                            H2_add = 2 * (WQWD_diff - 2.5) + 1.5 * (WQWD_sec_diff - 0.7)
                            H2_add = min(H2_add, 3)
                            H2_add = max(H2_add, -2)
                        elif smoothed_p[0] - smoothed_p[5] < 5:
                            H2_add = 0.8 * (5 - (smoothed_p[0] - smoothed_p[5]))
                            H2_add = min(H2_add, 8)
                            H2_add = max(H2_add, 3)
                        elif WQWD_diff > 6:
                            H2_add = 2 * (WQWD_diff - 3)
                            H2_add = min(H2_add, 10)
                            H2_add = max(H2_add, 0)

                        A1_I_TJ, A2_I_TJ, B1_I_TJ, B2_I_TJ, C1_I_TJ, C2_I_TJ, H2_TJLL, TCS_TJLL = risk_control(
                            current_add,
                            Current_change_max, 
                            Current_base, 
                            H2_add, 
                            H2_change_hist, 
                            H2_LL_base, 
                            TCS_LL_base, 
                            TCS_add,
                            TCS_change_max
                        )
                    else:
                        A1_I_TJ, A2_I_TJ, B1_I_TJ, B2_I_TJ, C1_I_TJ, C2_I_TJ, H2_TJLL, TCS_TJLL = risk_control(
                            current_add,
                            Current_change_max, 
                            Current_base, 
                            0,  # H2_add
                            H2_change_hist, 
                            H2_LL_base, 
                            TCS_LL_base,
                            TCS_add,
                            TCS_change_max
                        )
                elif run_time <= 1500:
                    H2_LL_base, TCS_LL_base, Current_base = look_table(run_time, DL_time,
                                                                       time_table, H2_table_ai, TCS_table_ai,
                                                                       A1_I_table_ai, A2_I_table_ai, B1_I_table_ai,
                                                                       B2_I_table_ai, C1_I_table_ai, C2_I_table_ai)

                    time_mode = time % 20
                    H2_ratio = ((H2_LL_base + H2_change_hist) / 2) / (TCS_LL_base / 135.5)
                    if run_time < 1200:
                        H2_change_max_u = 5
                        H2_change_max_d = 3
                    else:
                        H2_change_max_u = 5
                        H2_change_max_d = 3

                    if time % 20 < 1:
                        pid_run = 1
                        index = int((time - 30) // 10)
                        power_diff_goal = power_line[index] - power_line[index - 6]  # 这��运��的��率��率目��
                        power_diff_goal_past = power_line[index - 1] - power_line[index - 7]  # 10分钟前的功率斜率目标

                        #power_diff_goal2 = 2 * (smoothed_p[30] - smoothed_p[60])
                        #power_diff_goal = min(power_diff_goal1, power_diff_goal2)
                        #power_diff_goal = max(0, power_diff_goal)

                        #power_diff_goal_past2 = 2 * (smoothed_p[40] - smoothed_p[70])
                        #power_diff_goal_past = min(power_diff_goal_past1, power_diff_goal_past2)
                        #power_diff_goal_past = max(0, power_diff_goal_past)

                        power_diff = smoothed_p[0] - smoothed_p[60]
                        power_diff_past = smoothed_p[10] - smoothed_p[70]

                        value_p = power_diff_goal - power_diff
                        value_I = power_diff_goal_past - power_diff_past
                        value_d = value_p - value_I

                        # H2_add_max = 5
                        if abs(H2_change_hist) < 150 and H2_ratio >= 1.9:
                            # ��果��������������������，就吧kp���kd������ ������超调�����震��
                            if abs(value_p) < 3:
                                kp = 0.1
                                ki = 0.5
                                kd = 0.1
                            else:
                                kp = 0.3
                                ki = 0.5
                                kd = 0.1

                            H2_add = kp * value_p + kd * value_d

                            H2_add = min(H2_add, H2_change_max_u)
                            H2_add = max(H2_add, 0 - H2_change_max_d)

                        elif H2_ratio < 1.9:
                            H2_add = 3
                        else:
                            H2_add = 0

                        WQWD_sec_diff = (smoothed_WQWD[0] - smoothed_WQWD[30]) - (smoothed_WQWD[30] - smoothed_WQWD[60])
                        WQWD_diff = smoothed_WQWD[0] - smoothed_WQWD[30]

                        if WQWD_diff > 3 and WQWD_sec_diff > 1:
                            H2_add = 2 * (WQWD_diff - 2) + 2.5 * (WQWD_sec_diff - 0)

                            H2_add = min(H2_add, 15)
                            H2_add = max(H2_add, 0)

                        elif WQWD_diff > 5:
                            H2_add = 2 * (WQWD_diff - 2.5)

                            H2_add = min(H2_add, 15)
                            H2_add = max(H2_add, 0)

                        # elif WQWD_diff > 3.5 and WQWD_sec_diff > 0.7 and smoothed_WQWD[0] > 540:

                        #    H2_add = 2 * (WQWD_diff - 2.5) + 1.5 * (WQWD_sec_diff - 0.7)
                        #    H2_add = min(H2_add, 2)
                        #    H2_add = max(H2_add, -2)

                        elif smoothed_p[0] - smoothed_p[5] < 5 and run_time < 1000:
                            H2_add = 0.8 * (5 - (smoothed_p[0] - smoothed_p[5]))
                            H2_add = min(H2_add, 15)
                            H2_add = max(H2_add, 5)

                        A1_I_TJ, A2_I_TJ, B1_I_TJ, B2_I_TJ, C1_I_TJ, C2_I_TJ, H2_TJLL, TCS_TJLL = risk_control(
                            current_add,
                            Current_change_max, Current_base, H2_add, H2_change_hist, H2_LL_base, TCS_LL_base, TCS_add,
                            TCS_change_max)

                    else:
                        A1_I_TJ, A2_I_TJ, B1_I_TJ, B2_I_TJ, C1_I_TJ, C2_I_TJ, H2_TJLL, TCS_TJLL = risk_control(
                            current_add,
                            Current_change_max, Current_base, 0, H2_change_hist, H2_LL_base, TCS_LL_base, TCS_add,
                            TCS_change_max)
                elif run_time <= 1800:
                    H2_LL_base, TCS_LL_base, Current_base = look_table(run_time, DL_time,
                                                                       time_table, H2_table_ai, TCS_table_ai,
                                                                       A1_I_table_ai, A2_I_table_ai, B1_I_table_ai,
                                                                       B2_I_table_ai, C1_I_table_ai, C2_I_table_ai)

                    H2_ratio = ((H2_LL_base + H2_change_hist) / 2) / (TCS_LL_base / 135.5)
                    time_mode = time % 20
                    if time % 20 < 1:
                        pid_run = 1
                        index = int((time - 30) // 10)
                        power_diff_goal = power_line[index] - power_line[index - 6]  # 这��运��的��率��率目����
                        power_diff_goal_past = power_line[index - 1] - power_line[index - 7]  # 10分钟前的功率斜率目标

                        power_diff = smoothed_p[0] - smoothed_p[60]
                        power_diff_past = smoothed_p[10] - smoothed_p[70]

                        value_p = power_diff_goal - power_diff
                        value_I = power_diff_goal_past - power_diff_past
                        value_d = value_p - value_I

                        # H2_add_max = 5
                        if power_max > 6500:
                            H2_add_max_d = 1.5
                            H2_add_max_u = 5
                        elif power_max > 5900:
                            H2_add_max_d = 1.5
                            H2_add_max_u = 5
                        else:
                            H2_add_max_d = 1.5
                            H2_add_max_u = 5

                        if abs(H2_change_hist) < 150:
                            # ��果����������������������，就吧kp���kd������ ������超调�����震��
                            if abs(value_p) < 3:
                                kp = 0.1
                                ki = 0.5
                                kd = 0.1
                            else:
                                kp = 0.3
                                ki = 0.5
                                kd = 0.1

                            H2_add = kp * value_p + kd * value_d

                            H2_add = min(H2_add, H2_add_max_u)
                            H2_add = max(H2_add, 0 - H2_add_max_d)

                        else:
                            H2_add = 0

                        WQWD_sec_diff = (smoothed_WQWD[0] - smoothed_WQWD[30]) - (smoothed_WQWD[30] - smoothed_WQWD[60])
                        WQWD_diff = smoothed_WQWD[0] - smoothed_WQWD[30]

                        if WQWD_diff > 3 and WQWD_sec_diff > 1:
                            H2_add = 1 * (WQWD_diff - 2) + 1.5 * (WQWD_sec_diff - 0)

                            H2_add = min(H2_add, 15)
                            H2_add = max(H2_add, 0)

                        elif WQWD_diff > 5:
                            H2_add = 2 * (WQWD_diff - 3)

                            H2_add = min(H2_add, 15)
                            H2_add = max(H2_add, 0)

                        # elif WQWD_diff > 3.5 and WQWD_sec_diff > 1 and smoothed_WQWD[0] > 540:

                        #   H2_add = 2 * (WQWD_diff - 2.5) + 1.5 * (WQWD_sec_diff - 0.7)
                        #   H2_add = min(H2_add, 2)
                        #   H2_add = max(H2_add, -2)

                        A1_I_TJ, A2_I_TJ, B1_I_TJ, B2_I_TJ, C1_I_TJ, C2_I_TJ, H2_TJLL, TCS_TJLL = risk_control(
                            current_add,
                            Current_change_max, Current_base, H2_add, H2_change_hist, H2_LL_base, TCS_LL_base, TCS_add,
                            TCS_change_max)

                    else:
                        A1_I_TJ, A2_I_TJ, B1_I_TJ, B2_I_TJ, C1_I_TJ, C2_I_TJ, H2_TJLL, TCS_TJLL = risk_control(
                            current_add,
                            Current_change_max, Current_base, 0, H2_change_hist, H2_LL_base, TCS_LL_base, TCS_add,
                            TCS_change_max)

                        # 降料阶段
                elif run_time <= 2400:
                    H2_LL_base, TCS_LL_base, Current_base = look_table(run_time, DL_time,
                                                                       time_table, H2_table_ai, TCS_table_ai,
                                                                       A1_I_table_ai, A2_I_table_ai, B1_I_table_ai,
                                                                       B2_I_table_ai, C1_I_table_ai, C2_I_table_ai)

                    H2_ratio = ((H2_LL_base + H2_change_hist) / 2) / (TCS_LL_base / 135.5)
                    time_mode = time % 20
                    if time % 20 < 1:
                        pid_run = 1

                        index = int((time - 30) // 10)
                        power_diff_goal = power_line[index] - power_line[index - 6]  # ��次运行���功率斜率目标
                        power_diff_goal_past = power_line[index - 1] - power_line[index - 7]  # 10分���前���功���斜���目���

                        power_diff = smoothed_p[0] - smoothed_p[60]
                        power_diff_past = smoothed_p[20] - smoothed_p[80]

                        value_p = power_diff_goal - power_diff
                        value_I = power_diff_goal_past - power_diff_past
                        value_d = value_p - value_I

                        if power_max > 6500:
                            H2_add_max_u = 5
                            H2_add_max_d = 1.5
                        elif power_max > 5800:
                            H2_add_max_u = 5
                            H2_add_max_d = 1.5
                        else:
                            H2_add_max_u = 5
                            H2_add_max_d = 1.5

                        # H2_add_max = 6
                        if abs(H2_change_hist) < 150:
                            # 如果���的不�����，就吧kp，kd设�����������点 减少超调，震荡
                            if abs(value_p) < 5:
                                kp = 0.05
                                ki = 0.5
                                kd = 0.02
                            else:
                                kp = 0.2
                                ki = 0.5
                                kd = 0.03

                            H2_add = kp * value_p + kd * value_d

                            H2_add = min(H2_add, H2_add_max_u)
                            H2_add = max(H2_add, 0 - H2_add_max_d)
                        else:
                            H2_add = 0

                        # JDDL_max = max(JDDL)
                        # JDDL_avg = np.average(JDDL)
                        # JDDL_diff = [JDDL[i]-JDDL_record[i] for i in range(0,6)]
                        # JDDL_diff_max = max(JDDL_diff)

                        # if H2_add <=0:
                        #    if JDDL_max> 600 or JDDL_avg > 500:
                        #        if JDDL_H2 ==0:
                        #            H2_add = 5
                        #            JDDL_H2 = JDDL_H2 + 5
                        #            JDDL_record = JDDL.copy()
                        # elif JDDL_diff_max > 50:
                        #    H2_add = 5
                        #     JDDL_H2 = JDDL_H2 + 5
                        #      JDDL_record = JDDL.copy()
                        #   else:
                        #        H2_add = 0
                        # elif JDDL_max > 500 or JDDL_avg > 400:
                        # H2_add = 0

                        WQWD_sec_diff = (smoothed_WQWD[0] - smoothed_WQWD[30]) - (smoothed_WQWD[30] - smoothed_WQWD[60])
                        WQWD_diff = smoothed_WQWD[0] - smoothed_WQWD[30]

                        if WQWD_diff > 3.5 and WQWD_sec_diff > 1.5:
                            H2_add = 2.5 * (WQWD_diff - 3) + 2.5 * (WQWD_sec_diff - 1)

                            H2_add = min(H2_add, 15)
                            H2_add = max(H2_add, 0)

                        elif WQWD_diff > 6:
                            H2_add = 2 * (WQWD_diff - 3)

                            H2_add = min(H2_add, 15)
                            H2_add = max(H2_add, 0)

                        # elif WQWD_diff > 3.5 and WQWD_sec_diff > 1.4 :
                        #    H2_add = 2.5 * (WQWD_diff - 2.5) + 2 * (WQWD_sec_diff - 0.2)
                        #    H2_add = min(H2_add, 5)
                        #    H2_add = max(H2_add, -5)

                        A1_I_TJ, A2_I_TJ, B1_I_TJ, B2_I_TJ, C1_I_TJ, C2_I_TJ, H2_TJLL, TCS_TJLL = risk_control(
                            current_add,
                            Current_change_max, Current_base, H2_add, H2_change_hist, H2_LL_base, TCS_LL_base, TCS_add,
                            TCS_change_max)

                    else:
                        A1_I_TJ, A2_I_TJ, B1_I_TJ, B2_I_TJ, C1_I_TJ, C2_I_TJ, H2_TJLL, TCS_TJLL = risk_control(
                            current_add,
                            Current_change_max, Current_base, 0, H2_change_hist, H2_LL_base, TCS_LL_base, TCS_add,
                            TCS_change_max)
                # ��������完��� ���������压��幅
                elif run_time <= 3600:
                    H2_LL_base, TCS_LL_base, Current_base = look_table(run_time, DL_time,
                                                                       time_table, H2_table_ai, TCS_table_ai,
                                                                       A1_I_table_ai, A2_I_table_ai, B1_I_table_ai,
                                                                       B2_I_table_ai, C1_I_table_ai, C2_I_table_ai)

                    H2_ratio = ((H2_LL_base + H2_change_hist) / 2) / (TCS_LL_base / 135.5)
                    time_mode = time % 20
                    if time % 20 < 1:
                        pid_run = 1
                        index = int((time - 30) // 10)
                        # power_diff_goal = power_line[index] - power_line[index-6]   #这��运����的功���斜���目���
                        # power_diff_goal_past =  power_line[index-1] - power_line[index-7]
                        Voltage_diff_goal = (smoothed_A1[30] - smoothed_A1[90]) / 2 + (
                                    smoothed_B2[30] - smoothed_B2[90]) + 0.3

                        if Voltage_diff_goal < 0:
                            Voltage_diff_goal = max(Voltage_diff_goal, -22)
                            Voltage_diff_goal = min(Voltage_diff_goal, -10)
                        else:
                            Voltage_diff_goal = -10

                        A1_V_diff = smoothed_A1[0] - smoothed_A1[60]
                        A1_V_diff_past = smoothed_A1[20] - smoothed_A1[80]

                        B2_V_diff = smoothed_B2[0] - smoothed_B2[60]
                        B2_V_diff_past = smoothed_B2[20] - smoothed_B2[80]

                        # power_diff = smoothed_p[0]-smoothed_p[50]
                        # power_diff_past =  smoothed_p[10]-smoothed_p[60]
                        # H2_TCS_ratio =
                        value_p = (Voltage_diff_goal - A1_V_diff) / 2 + Voltage_diff_goal / 2 - B2_V_diff
                        value_I = (Voltage_diff_goal - A1_V_diff_past) / 2 + Voltage_diff_goal / 2 - B2_V_diff_past
                        value_d = value_p - value_I

                        H2_add_max = 3
                        if abs(H2_change_hist) < 150 and H2_ratio > 2.3:
                            # 如果���的���多���，���吧kp，kd设小点 减��超调，��荡
                            if abs(value_p) < 2:
                                kp = 0.3
                                ki = 0.5
                                kd = 0.1
                            else:
                                kp = 0.6
                                ki = 0.5
                                kd = 0.3

                            H2_add = kp * value_p + kd * value_d

                            H2_add = min(H2_add, 1.5)
                            H2_add = max(H2_add, 0 - H2_add_max)
                        elif H2_ratio < 2.3:
                            H2_add = 3
                        else:
                            H2_add = 0

                        WQWD_sec_diff = (smoothed_WQWD[0] - smoothed_WQWD[30]) - (smoothed_WQWD[30] - smoothed_WQWD[60])
                        WQWD_diff = smoothed_WQWD[0] - smoothed_WQWD[30]

                        if WQWD_diff > 5 and WQWD_sec_diff > 2:
                            H2_add = 1.5 * (WQWD_diff - 4) + 1.5 * (WQWD_sec_diff - 1)

                            H2_add = min(H2_add, 5)
                            H2_add = max(H2_add, -5)

                        elif WQWD_diff > 7:
                            H2_add = 1.5 * (WQWD_diff - 4)

                            H2_add = min(H2_add, 5)
                            H2_add = max(H2_add, -5)

                        elif WQWD_diff > 5 and smoothed_WQWD[0] > 580:
                            H2_add = 0.25 * (smoothed_WQWD[0] - 580)

                            H2_add = min(H2_add, 3)
                            H2_add = max(H2_add, -3)

                        elif WQWD_diff > 4 and WQWD_sec_diff > 1.8 and smoothed_WQWD[0] > 530:
                            H2_add = 2 * (WQWD_diff - 2.5) + 1 * (WQWD_sec_diff - 0.7)
                            H2_add = min(H2_add, 3)
                            H2_add = max(H2_add, -3)

                        A1_I_TJ, A2_I_TJ, B1_I_TJ, B2_I_TJ, C1_I_TJ, C2_I_TJ, H2_TJLL, TCS_TJLL = risk_control(
                            current_add,
                            Current_change_max, Current_base, H2_add, H2_change_hist, H2_LL_base, TCS_LL_base, TCS_add,
                            TCS_change_max)

                    else:
                        A1_I_TJ, A2_I_TJ, B1_I_TJ, B2_I_TJ, C1_I_TJ, C2_I_TJ, H2_TJLL, TCS_TJLL = risk_control(
                            current_add,
                            Current_change_max, Current_base, 0, H2_change_hist, H2_LL_base, TCS_LL_base, TCS_add,
                            TCS_change_max)
                elif run_time <= 4200:
                    time_mode = time % 20
                    H2_LL_base, TCS_LL_base, Current_base = look_table(run_time, DL_time,
                                                                       time_table, H2_table_ai, TCS_table_ai,
                                                                       A1_I_table_ai, A2_I_table_ai, B1_I_table_ai,
                                                                       B2_I_table_ai, C1_I_table_ai, C2_I_table_ai)

                    H2_ratio = ((H2_LL_base + H2_change_hist) / 2) / (TCS_LL_base / 135.5)

                    if time % 20 < 1:

                        pid_run = 1
                        index = int((time - 30) // 10)
                        # power_diff_goal = power_line[index] - power_line[index-6]   #��次��行的功率斜率目标
                        # power_diff_goal_past =  power_line[index-1] - power_line[index-7]
                        Voltage_diff_goal = -9

                        A1_V_diff = smoothed_A1[0] - smoothed_A1[60]
                        A1_V_diff_past = smoothed_A1[20] - smoothed_A1[80]

                        B2_V_diff = smoothed_B2[0] - smoothed_B2[60]
                        B2_V_diff_past = smoothed_B2[20] - smoothed_B2[80]

                        # power_diff = smoothed_p[0]-smoothed_p[50]
                        # power_diff_past =  smoothed_p[10]-smoothed_p[60]
                        # H2_TCS_ratio =

                        value_p = (Voltage_diff_goal - A1_V_diff) / 2 + Voltage_diff_goal / 2 - B2_V_diff
                        value_I = (Voltage_diff_goal - A1_V_diff_past) / 2 + Voltage_diff_goal / 2 - B2_V_diff_past
                        value_d = value_p - value_I

                        H2_add_max = 3
                        if abs(H2_change_hist) < 150 and H2_ratio > 2.5:

                            # 如果���的���多���，���吧kp，kd设小点 减���超���，�����
                            if abs(value_p) < 3:

                                kp = 0.8
                                ki = 0.5
                                kd = 0.02
                            else:
                                kp = 1.6
                                ki = 0.5
                                kd = 0.3

                            H2_add = kp * value_p + kd * value_d

                            H2_add = min(H2_add, H2_add_max)
                            H2_add = max(H2_add, 0 - H2_add_max)
                        elif H2_ratio < 2.5:
                            H2_add = 3
                        else:
                            H2_add = 0

                        WQWD_sec_diff = (smoothed_WQWD[0] - smoothed_WQWD[30]) - (smoothed_WQWD[30] - smoothed_WQWD[60])
                        WQWD_diff = smoothed_WQWD[0] - smoothed_WQWD[30]

                        if WQWD_diff > 5 and WQWD_sec_diff > 3:
                            H2_add = 1.5 * (WQWD_diff - 4) + 1.5 * (WQWD_sec_diff - 1)

                            H2_add = min(H2_add, 2)
                            H2_add = max(H2_add, -2)

                        elif WQWD_diff > 8:
                            H2_add = 1.5 * (WQWD_diff - 4)

                            H2_add = min(H2_add, 2)
                            H2_add = max(H2_add, -2)

                        elif WQWD_diff > 5 and smoothed_WQWD[0] > 580:
                            H2_add = 0.05 * (smoothed_WQWD[0] - 580)

                            H2_add = min(H2_add, 2)
                            H2_add = max(H2_add, -2)

                        A1_I_TJ, A2_I_TJ, B1_I_TJ, B2_I_TJ, C1_I_TJ, C2_I_TJ, H2_TJLL, TCS_TJLL = risk_control(
                            current_add,
                            Current_change_max, Current_base, H2_add, H2_change_hist, H2_LL_base, TCS_LL_base, TCS_add,
                            TCS_change_max)

                    else:
                        A1_I_TJ, A2_I_TJ, B1_I_TJ, B2_I_TJ, C1_I_TJ, C2_I_TJ, H2_TJLL, TCS_TJLL = risk_control(
                            current_add,
                            Current_change_max, Current_base, 0, H2_change_hist, H2_LL_base, TCS_LL_base, TCS_add,
                            TCS_change_max)
                elif run_time <= 6600:
                    time_mode = time % 60
                    H2_LL_base, TCS_LL_base, Current_base = look_table(run_time, DL_time,
                                                                       time_table, H2_table_ai, TCS_table_ai,
                                                                       A1_I_table_ai, A2_I_table_ai, B1_I_table_ai,
                                                                       B2_I_table_ai, C1_I_table_ai, C2_I_table_ai)

                    if time % 60 < 1:

                        pid_run = 1

                        B2_V_diff = smoothed_B2[0] - smoothed_B2[60]
                        H2_ratio = ((H2_LL_base + H2_change_hist) / 2) / (TCS_LL_base / 135.5)
                        # print(H2_ratio)
                        if H2_ratio < 3.7 and B2_V_diff < -1:
                            H2_add = 3
                        elif H2_ratio < 2.9:
                            H2_add = 3

                        A1_I_TJ, A2_I_TJ, B1_I_TJ, B2_I_TJ, C1_I_TJ, C2_I_TJ, H2_TJLL, TCS_TJLL = risk_control(
                            current_add,
                            Current_change_max, Current_base, H2_add, H2_change_hist, H2_LL_base, TCS_LL_base, TCS_add,
                            TCS_change_max)

                    else:
                        A1_I_TJ, A2_I_TJ, B1_I_TJ, B2_I_TJ, C1_I_TJ, C2_I_TJ, H2_TJLL, TCS_TJLL = risk_control(
                            current_add,
                            Current_change_max, Current_base, 0, H2_change_hist, H2_LL_base, TCS_LL_base, TCS_add,
                            TCS_change_max)
                else:

                    H2_LL_base, TCS_LL_base, Current_base = look_table(run_time, DL_time,
                                                                       time_table, H2_table_ai, TCS_table_ai,
                                                                       A1_I_table_ai, A2_I_table_ai, B1_I_table_ai,
                                                                       B2_I_table_ai, C1_I_table_ai, C2_I_table_ai)

                    if time % 20 < 1:

                        H2_add = 0

                        A1_I_TJ, A2_I_TJ, B1_I_TJ, B2_I_TJ, C1_I_TJ, C2_I_TJ, H2_TJLL, TCS_TJLL = risk_control(
                            current_add,
                            Current_change_max, Current_base, H2_add, H2_change_hist, H2_LL_base, TCS_LL_base, TCS_add,
                            TCS_change_max)

                    else:
                        A1_I_TJ, A2_I_TJ, B1_I_TJ, B2_I_TJ, C1_I_TJ, C2_I_TJ, H2_TJLL, TCS_TJLL = risk_control(
                            current_add,
                            Current_change_max, Current_base, 0, H2_change_hist, H2_LL_base, TCS_LL_base, TCS_add,
                            TCS_change_max)

                if run_time <= 120:
                    f_safe1 = 1
                    f_safe2 = 1
                else:
                    f_safe1 = 0.05
                    f_safe2 = 0.015

                H2_LL_final = min(H2_LL + H2_LL * f_safe1, H2_TJLL)
                TCS_LL_final = min(TCS_LL + TCS_LL * f_safe1, TCS_TJLL)
                A1_I_final = min(A1_I + A1_I * f_safe2, A1_I_TJ)
                A2_I_final = min(A2_I + A2_I * f_safe2, A2_I_TJ)
                B1_I_final = min(B1_I + B1_I * f_safe2, B1_I_TJ)
                B2_I_final = min(B2_I + B2_I * f_safe2, B2_I_TJ)
                C1_I_final = min(C1_I + C1_I * f_safe2, C1_I_TJ)
                C2_I_final = min(C2_I + C2_I * f_safe2, C2_I_TJ)

                H2_LL_final = max(H2_LL - H2_LL * f_safe1, H2_LL_final)
                TCS_LL_final = max(TCS_LL - TCS_LL * f_safe1, TCS_LL_final)
                A1_I_final = max(A1_I - A1_I * f_safe2, A1_I_final)
                A2_I_final = max(A2_I - A2_I * f_safe2, A2_I_final)
                B1_I_final = max(B1_I - B1_I * f_safe2, B1_I_final)
                B2_I_final = max(B2_I - B2_I * f_safe2, B2_I_final)
                C1_I_final = max(C1_I - C1_I * f_safe2, C1_I_final)
                C2_I_final = max(C2_I - C2_I * f_safe2, C2_I_final)

                H2_change = np.round(H2_LL_final - H2_LL_base, 1)
                TCS_change = TCS_add
                Current_change = current_add
            else:
                H2_change, TCS_change, Current_change, Current_add_stop = WuHua_control(WuHua_status, WuHua_time,
                                                                                        run_time)
                H2_LL_final = np.round(H2_LL_base + H2_change, 1)
                TCS_LL_final = np.round(TCS_LL_base + TCS_change, 1)

                if Current_add_stop == 1:
                    A1_I_final = np.round(last_data['A1_I'] + Current_change, 1)
                    A2_I_final = np.round(last_data['A2_I'] + Current_change, 1)
                    B1_I_final = np.round(last_data['B1_I'] + Current_change, 1)
                    B2_I_final = np.round(last_data['B2_I'] + Current_change, 1)
                    C1_I_final = np.round(last_data['C1_I'] + Current_change, 1)
                    C2_I_final = np.round(last_data['C2_I'] + Current_change, 1)
                else:
                    A1_I_final = np.round(Current_base[0] + Current_change, 1)
                    A2_I_final = np.round(Current_base[1] + Current_change, 1)
                    B1_I_final = np.round(Current_base[2] + Current_change, 1)
                    B2_I_final = np.round(Current_base[3] + Current_change, 1)
                    C1_I_final = np.round(Current_base[4] + Current_change, 1)
                    C2_I_final = np.round(Current_base[5] + Current_change, 1)

        if control == '3':
            towards = Expert['towards'].split(',')
            value = Expert['value']
            A1_value = value['a1_value']
            A2_value = value['a2_value']
            B1_value = value['b1_value']
            B2_value = value['b2_value']
            C1_value = value['c1_value']
            C2_value = value['c2_value']

            A1_with_time = value['a1_with_time']
            A2_with_time = value['a2_with_time']
            B1_with_time = value['b1_with_time']
            B2_with_time = value['b2_with_time']
            C1_with_time = value['c1_with_time']
            C2_with_time = value['c2_with_time']

            A1_I_delta = Current_base[0] - last_data['A1_I']
            A2_I_delta = Current_base[1] - last_data['A2_I']
            B1_I_delta = Current_base[2] - last_data['B1_I']
            B2_I_delta = Current_base[3] - last_data['B2_I']
            C1_I_delta = Current_base[4] - last_data['C1_I']
            C2_I_delta = Current_base[5] - last_data['C2_I']

            H2_value = value['h2_value']
            TCS_value = value['tcs_value']
            start_time = float(Expert['productionTime'])

            H2_adjust_time = value['h2_adjust_time']
            TCS_adjust_time = value['tcs_adjust_time']

            time_remain = H2_adjust_time - (run_time - start_time)

            if time_remain <= 0:
                H2_LL_final = H2_value
            else:

                H2_LL_final = H2_LL_last + (H2_value - H2_LL_last) / time_remain

            for j in towards:
                exec('time_vary = {}_with_time'.format(j))
                if time_vary == '0':
                    exec('{}_I_final = {}_value'.format(j, j))
                else:
                    exec('{}_I_final = {}_value + {}_I_delta'.format(j, j, j))

        psrf_recover = 0
        Suspend_module_act = 0
        if Suspend_status != 0:
            Suspend_module_act = 1
            import Suspend_V2 as Suspend

            data = Suspend.input_data('parameters.json')
            current_data = data.read_data()

            if Suspend_status == 1:
                suspend = Suspend.Suspend_start(current_data)
                TJLL = suspend.start_suspend(10, 20, 10)
                status = suspend.suspend_finish()

            if Suspend_status == 2:
                suspend = Suspend.Suspend_recover(current_data)
                TJLL = suspend.recover_suspend(10, 20, 10)
                status = suspend.recover_finish()
                psrf_recover = status

            TCS_LL_final = TJLL['TCS']
            H2_LL_final = TJLL['H2']
            A1_I_final = TJLL['current_final'][0]
            A2_I_final = TJLL['current_final'][1]
            B1_I_final = TJLL['current_final'][2]
            B2_I_final = TJLL['current_final'][3]
            C1_I_final = TJLL['current_final'][4]
            C2_I_final = TJLL['current_final'][5]

        code = 1
        if time * status * H2_LL * TCS_LL * A1_I * A2_I * B1_I * B2_I * C1_I * C2_I == 0:
            code = 0
        data = {'TCS': round(TCS_LL_final, 3), 'H2': round(H2_LL_final, 3), 'A1_I': round(A1_I_final, 3),
                'A2_I': round(A2_I_final, 3), 'B1_I': round(B1_I_final, 3),
                'B2_I': round(B2_I_final, 3), 'C1_I': round(C1_I_final, 3), 'C2_I': round(C2_I_final, 3),
                'H2_change': round(H2_change, 3),
                'TCS_change': round(TCS_change, 3), 'Current_change': Current_change, 'WuHua': WuHua_status,
                'WuHua_time': WuHua_time,
                'psrf_recover': psrf_recover, 'TCS_last': TCS_LL_last, 'H2_last': H2_LL_last, 'A1_I_last': A1_I_last,
                'A2_I_last': A2_I_last, 'B1_I_last': B1_I_last, 'B2_I_last': B2_I_last, 'C1_I_last': C1_I_last,
                'C2_I_last': C2_I_last, 'run_Time': run_time,
                'time_mode': time_mode, 'DL_time': DL_time, 'JDDL_H2': JDDL_H2, 'JDDL_record': JDDL_record}

        log_data = {'WQWD': WQWD[0], 'use_material_table': isUseTable, 'Suspend_module_act': Suspend_module_act,
                    'Status': status, 'run_Time': round(time),
                    'pid_hist': str(hist_input), 'pid_run': pid_run}

        output = {}
        output['Code'] = code
        output['data'] = data
        output['logdata'] = log_data
        output['message'] = 'executed successfully'
        output['algorithmname'] = 'test1'
        print(json.dumps(output))
except Exception as e:
    output = {}
    status = 0
    output['Code'] = status
    output['Data'] = {}
    output['Message'] = str(e)
    output['LogData'] = {}
    print(json.dumps(output))
