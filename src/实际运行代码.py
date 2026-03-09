# -*- coding: utf-8 -*-

# ***************************************************
# * File        : 实际运行代码.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2024-07-29
# * Version     : 1.0.072917
# * Description : description
# * Link        : link
# * Requirement : 相关模块版本需求(例如: numpy >= 2.1.0)
# * TODO        : 1.
# ***************************************************

__all__ = []

# python libraries
import os
import sys
ROOT = os.getcwd()
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
import json
import time
import warnings
import traceback

import pandas as pd
import numpy as np

warnings.filterwarnings("ignore")
warnings.simplefilter(action="ignore", category=FutureWarning)

# global variable
LOGGING_LABEL = __file__.split('/')[-1][:-3]


# ------------------------------
# 工具函数
# ------------------------------
class Application_Scene:
    """
    本地测试、线上运行
    """
    
    def __init__(self, path):
        self.path = path
    
    @staticmethod
    def param_str_process(args):
        json_str = args.replace('\\', '')
        json_str = json_str.replace('["{', '[{')
        json_str = json_str.replace('}"]', '}]')
        json_str = json_str.replace('","', ',')
        json_str = json_str.strip('"')
        json_str = json.loads(json_str)
        return json_str
    
    def offline_apply(self):
        """
        线下测试
        """
        with open(self.path, 'r', encoding = 'utf-8') as f:
            args = f.read()
        params = self.param_str_process(args[1:])
        return params
    
    def online_apply(self):
        """
        线上运行
        """
        args = sys.argv[1:]  # 命令行参数
        params = self.param_str_process(args[0])
        return params


def PID_Modular_Control(params):
    # -----上料系统-------
    WYMSJ = params["PM_WYMSJ"]  # 无烟煤实际重量
    YMSJ = params["PM_YMSJ"]  # 烟煤实际重量
    MCLW = params["PM_MCLW"]  # 原煤仓料位
    GLJYY = params["PM_GLJYY"]  # 圆盘给料机油压
    GLJDL = params["PM_GLJDL"]  # 圆盘给料机电流
    WYMSJZB = params["PM_WYMSJZB"]  # 无烟煤实际占比
    # WYMZBSX = params["PM_WYMZBSX"]                                  # 无烟煤占比上限
    # WYMZBXX = params["PM_WYMZBXX"]                                  # 无烟煤占比下限
    GLFK = params["PM_GLFK"]  # 圆盘给料机反馈

    # ----燃烧系统-----
    BWFMFK = params["PM_BWTJFFK"]  # 保温调节阀实际值
    KQYL = params["PM_KQYL"][0]  # 助燃空气压力
    MQYL = params["PM_MQYL"][0]  # 煤气压力
    KQLL = params["PM_KQLL"]  # 空气流量
    MQLL = params["PM_MQLL"]  # 煤气流量
    MQSD10 = np.mean(params["PM_MQTJFFK"])

    MQFMFK = params["PM_MQTJFFK"]  # 煤气调节阀实际值
    KQFMFK = params["PM_KQTJFFK"]  # 空气助燃调节阀实际值
    FQZGFMFK = params["PM_YFJRKFFK"][0]  # 废气-引风机入口阀实际值
    FQZGCKWD = params["PM_YQLRKWD"][0]  # 烟气炉入口温度--废气总管出口温度
    FQZGYL = params["PM_YQLRKYL"][0]  # 烟气炉入口压力--废气总管出口压力

    # ----烟气炉------
    # YQL_LTWDSD = params["PM_RGSDLTWDMBZ"][0]  # 烟气炉炉膛温度-设定值---新增
    YQL_LTWD = params["PM_YQLLTWD"][0]  # 烟气炉炉膛温度
    YQL_LTYL = params["PM_YQLLTYL"][0]  # 烟气炉炉膛压力
    YQL_CKWD = params["PM_YQLCKWD"][0]  # 烟气炉出��温度

    # #----磨机----
    MJRKFFK = params["PM_MJRKFFK"][0]  # 磨机入口阀实际值
    MJRKWD = params["PM_MJRKWD"][0]  # 磨机入口温度
    MJRK_YL = params["PM_MJRKYL"][0]  # 磨机入口压力
    MQRK_CO2 = params["PM_MJRKYQ"][0]  # 磨机入口氧气
    MJRK_CO = params["PM_MJRKCO"][0]  # 磨机入口一氧化碳
    MJ_YC = params["PM_MJYC"][0]  # 磨机压差
    MJ_CKYL = params["PM_MJCKYL"][0]  # 磨机出口压力
    MJ_CKWD = params["PM_MJCKWD"][0]  # 磨机出口温度
    MQCK_CO2 = params["PM_MJCKYQ"][0]  # 磨机出口氧气
    MJCK_CO = params["PM_MJCKCO"][0]  # 磨机出口一氧化碳

    # ----布袋-------
    # # BDRKWD = params["PM_BDRKWD"][0]                               # 布袋入口温度，需要核实
    BD_CKWD = params["PM_BDCKWD"][0]  # 布袋出口温度
    BD_CKYL = params["PM_BDCKYL"][0]  # 布袋出口压力
    BD_CKLL = params["PM_BDCKLL"][0]  # 布袋出口流量

    # 新增字段-数采配置
    TJMQLL90 = params['TJMQLL90']  # 90s平均煤气流量---新增
    TJMQLL30 = params['TJMQLL30']  # 30s平均煤气流量---新增
    CKWD_mean = params['CKWD_mean'][0]  # 磨机出口平均温度---新增--需要核对一下计算多长时间的平均值

    # MJRKWD_mean = params["pid_outparams"][0]["MJRKWD_mean"]       # 磨机入口温度均值---新增字段
    AI_AT = params["AI_AT"]  # AI模型投用
    # AI_BW = params["YQL_AI_BW"][0]                                  # AI保温功能

    YCZT = params["pid_outparams"][0]["YCZT"]  # 新增
    p1 = params["pid_outparams"][0]["p1"]  # 新增

    NEXT = params["pid_outparams"][0]["NEXT"]
    MJCKSD = params["MJCKSD"][0]  # 新增
    MJRKWD_mean = params["pid_outparams"][0]["MJRKWD_mean"]  # 新增
    YQLLTWD_mean = np.mean(params["PM_YQLLTWD"])  # 新增

    if MQLL[0] > 500:
        RSZ = 1
    else:
        RSZ = 0

    TJMQLL90 = params['TJMQLL90']

    TJMQLL30 = params['TJMQLL30']

    TJMQLL = (TJMQLL90[1] * 90 - TJMQLL30[0] * 30) / 60 - 800

    LTJMQLL = np.minimum(np.maximum((TJMQLL90[1] * 90 - TJMQLL30[0] * 30) / 60, 3200), 8200) - 800
    KMB = np.mean(KQLL) / np.mean(MQLL)
    TJKQLL = TJMQLL * (1.75 * 0.7 + KMB * 0.3)  # 根据现场师傅改动空煤比系数,或者取2或者1.5之间的数值

    tanzhen1 = TJMQLL
    '''
    MJCKSD + 3 = 75+3 = 78
    MJ_CKWD = 79
    (78-79)*(3) = -3
    '''
    a = 0
    if MJ_CKWD > (MJCKSD + 3):
        a = (MJCKSD + 3 - MJ_CKWD) * 3
    elif MJ_CKWD < (MJCKSD + 1):
        a = (MJCKSD + 1 - MJ_CKWD) * 3
    if a > 6:
        a = 6
    elif a < -6:
        a = -6

    MJRKWD_max = (np.array([255, 257, 259, 260, 264]) - 5).tolist()
    MJRKWD_min = (np.array([220, 219, 215, 213, 210]) - 10).tolist()

    MJCKSD = np.maximum(np.minimum(MJCKSD, 74.5), 72.5)
    #
    # MJCKWD_min = (np.array([MJCKSD + 0.5, MJCKSD - 0.5, MJCKSD - 1, MJCKSD - 1.3, MJCKSD - 1.5])).tolist()
    # MJCKWD_max = (np.array([MJCKSD + 0.5, MJCKSD + 1, MJCKSD + 1.2, MJCKSD + 1.4, MJCKSD + 1.5])).tolist()

    # 磨机出口温度最大值，最小值
    MJCKWD_min = (np.array([74.5, 74, 73, 72.5, 72])).tolist()
    MJCKWD_max = (np.array([74.5, 74.7, 75, 75.5, 75.7])).tolist()

    if a != 0:
        NEXT += 1
    if a == 0:
        NEXT = 1

    if RSZ == 1:
        if (NEXT % 4) == 0:
            MJRKWD_mean = MJRKWD_mean + a
        MJRKWD_mean = np.minimum(np.maximum(MJRKWD_mean, 210), 255)

    # 烟气炉-炉膛温度最大值，最小值，依据设定值

    YQLLTWD_mean = np.maximum(np.minimum(YQLLTWD_mean, 830), 960)  # 炉膛温度

    YQL_LTWD_min = (np.array([870, 865, 860, 855, 850]) - 20).tolist()
    YQL_LTWD_max = (np.array([930, 935, 936, 938, 940])).tolist()

    tag = []

    cyhl_min = 3.0
    cyhl_max = 7.0
    cyhl_mean = (cyhl_min + cyhl_max) / 2

    if MJRKWD < MJRKWD_min[0]:
        TJMQLL = TJMQLL * 1.01
        tag.append("low2")
    if MJRKWD < MJRKWD_min[1]:
        TJMQLL = TJMQLL * 1.01
        tag.append("low3")
    if MJRKWD < MJRKWD_min[2]:
        TJMQLL = TJMQLL * 1.01
        tag.append("low4")
    if MJRKWD < MJRKWD_min[3]:
        TJMQLL = TJMQLL * 1.01
        tag.append("low5")
    if MJRKWD < MJRKWD_min[4]:
        TJMQLL = TJMQLL * 1.01
        tag.append("low6")

    # if RSZ == 1:
    #     if (MJRKWD - MJRKWD_mean) > 0:
    #         if (MQRK_CO2 - cyhl_mean) > 0:
    #             tag.append("5min_doubleHigh")
    #             TJKQLL = TJKQLL - 300 * np.minimum((MQRK_CO2 - cyhl_mean), 10)
    #             TJMQLL = TJMQLL - 200 * np.minimum((MJRKWD - MJRKWD_mean), 10)
    #
    #     if (MJRKWD - MJRKWD_mean) < 0:
    #         if (MQRK_CO2 - cyhl_mean) < 0:
    #             tag.append("5min_doublelow")
    #             TJKQLL = TJKQLL - 150 * np.maximum((MQRK_CO2 - cyhl_mean), -1)
    #             TJMQLL = TJMQLL - 200 * np.maximum((MJRKWD - MJRKWD_mean), -10)
    #
    #     if (MJRKWD - MJRKWD_mean) > 0:
    #         if (MQRK_CO2 - cyhl_mean) <= 0:
    #             tag.append("5min_CYHigh_YLow")
    #             TJKQLL = TJKQLL - np.maximum((MQRK_CO2 - cyhl_mean), -1) * 300
    #             # TJMQLL = TJMQLL - 80 * np.minimum((CYWD- cywd_mean),3)
    #             # TJMQLL = TJMQLL - 120 * np.minimum((CYWD - cywd_mean), 3)
    #             TJMQLL = TJMQLL - 200 * np.minimum((MJRKWD - MJRKWD_mean), 10)
    #
    #     if (MJRKWD - MJRKWD_mean) < 0:
    #         if (MQRK_CO2 - cyhl_mean) > 0:
    #             tag.append("5min_CYLow_YHigh")
    #             TJKQLL = TJKQLL - np.minimum((MQRK_CO2 - cyhl_mean), 1) * 150
    #             TJMQLL = TJMQLL - 200 * np.maximum((MJRKWD - MJRKWD_mean), -10)

    if RSZ == 1:
        # 如果实际磨机入口温度低于磨机入口温度预测值并且实际烟道温度低于烟道温度预测值
        if (MJ_CKWD - MJCKSD) > 0:
            if (MJRKWD - MJRKWD_mean) > 0:
                tag.append("5min_doubleHigh")
                TJKQLL = TJKQLL - 700 * np.minimum((MJ_CKWD - MJCKSD), 10)
                TJMQLL = TJMQLL - 300 * np.minimum((MJ_CKWD - MJCKSD), 10)
                TJMQLL = TJMQLL - 150 * np.minimum((MJRKWD - MJRKWD_mean), 10)

        # 如果实际磨机入口温度高于磨机入口温度预测值并且实际烟道温度高于烟道温度预测值
        if (MJ_CKWD - MJCKSD) < 0:
            if (MJRKWD - MJRKWD_mean) < 0:
                tag.append("5min_doublelow")
                TJKQLL = TJKQLL - 700 * np.maximum((MJ_CKWD - MJCKSD), -10)
                TJMQLL = TJMQLL - 150 * np.maximum((MJ_CKWD - MJCKSD), -10)
                TJMQLL = TJMQLL - 200 * np.maximum((MJRKWD - MJRKWD_mean), -10)

        # 如果实际磨机入口温度低于磨机入口温度预测值并且实际烟道温度高于烟道温度预测值
        if (MJ_CKWD - MJCKSD) > 0:
            if (MJRKWD - MJRKWD_mean) <= 0:
                tag.append("5min_LTHigh_MJLow")
                TJKQLL = TJKQLL - 700 * np.maximum((MJ_CKWD - MJCKSD), 10)
                TJMQLL = TJMQLL - 300 * np.maximum((MJ_CKWD - MJCKSD), 10)
                TJMQLL = TJMQLL - 200 * np.minimum((MJRKWD - MJRKWD_mean), -10)

        # 如果实际磨机入口温度高于磨机入口温度预测值并且实际烟道温度低于烟道温度预测值
        if (MJ_CKWD - MJCKSD) < 0:
            if (MJRKWD - MJRKWD_mean) > 0:
                tag.append("5min_LTLow_MJHigh")
                TJKQLL = TJKQLL - np.minimum((MJ_CKWD - MJCKSD), -10) * 700
                TJMQLL = TJMQLL - np.minimum((MJ_CKWD - MJCKSD), -10) * 150
                TJMQLL = TJMQLL - 150 * np.maximum((MJRKWD - MJRKWD_mean), 10)

    if YQL_LTWD > YQL_LTWD_max[0]:
        TJMQLL = TJMQLL / 1.02
        TJKQLL = TJKQLL / 1.07

    if YQL_LTWD > YQL_LTWD_max[1]:
        TJMQLL = TJMQLL / 1.02
        TJKQLL = TJKQLL / 1.07

    if YQL_LTWD > YQL_LTWD_max[2]:
        TJMQLL = TJMQLL / 1.03
        TJKQLL = TJKQLL / 1.08

    if YQL_LTWD > YQL_LTWD_max[3]:
        TJMQLL = TJMQLL / 1.04
        TJKQLL = TJKQLL / 1.09

    if YQL_LTWD > YQL_LTWD_max[4]:
        TJMQLL = TJMQLL / 1.05
        TJKQLL = TJKQLL / 1.10

    if YQL_LTWD < YQL_LTWD_min[0]:
        TJMQLL = TJMQLL * 1.01
    if YQL_LTWD < YQL_LTWD_min[1]:
        TJMQLL = TJMQLL * 1.01
    if YQL_LTWD < YQL_LTWD_min[2]:
        TJMQLL = TJMQLL * 1.01
    if YQL_LTWD < YQL_LTWD_min[3]:
        TJMQLL = TJMQLL * 1.01
    if YQL_LTWD < YQL_LTWD_min[4]:
        TJMQLL = TJMQLL * 1.01

    if MJ_CKWD > MJCKWD_max[0]:
        TJMQLL = TJMQLL / 1.02
        TJKQLL = TJKQLL / 1.03

    if MJ_CKWD > MJCKWD_max[1]:
        TJMQLL = TJMQLL / 1.04
        TJKQLL = TJKQLL / 1.05

    if MJ_CKWD > MJCKWD_max[2]:
        TJMQLL = TJMQLL / 1.06
        TJKQLL = TJKQLL / 1.06

    if MJ_CKWD > MJCKWD_max[3]:
        TJMQLL = TJMQLL / 1.08
        TJKQLL = TJKQLL / 1.08

    if MJ_CKWD > MJCKWD_max[4]:
        TJMQLL = TJMQLL / 1.10
        TJKQLL = TJKQLL / 1.10

    if MJ_CKWD < MJCKWD_min[0]:
        TJMQLL = TJMQLL * 1.01
    if MJ_CKWD < MJCKWD_min[1]:
        TJMQLL = TJMQLL * 1.01
    if MJ_CKWD < MJCKWD_min[2]:
        TJMQLL = TJMQLL * 1.02
    if MJ_CKWD < MJCKWD_min[3]:
        TJMQLL = TJMQLL * 1.02
    if MJ_CKWD < MJCKWD_min[4]:
        TJMQLL = TJMQLL * 1.03

    # TJKQLL = np.maximum(TJKQLL,1350)
    TJKQLL = np.maximum(TJKQLL, 1900.0)
    TJKQLL = np.minimum(TJKQLL, 7500.0)

    tanzhen2 = TJKQLL

    TJKQLL = np.minimum(2.00 * TJMQLL, TJKQLL)
    TJKQLL = np.maximum(1.70 * TJMQLL, TJKQLL)

    ss = 0.7
    TJMQLL = TJMQLL * ss + LTJMQLL * (1 - ss)

    if MJRKWD > MJRKWD_max[0]:
        TJMQLL = TJMQLL / 1.01

    if MJRKWD > MJRKWD_max[1]:
        TJMQLL = TJMQLL / 1.02

    if MJRKWD > MJRKWD_max[2]:
        TJMQLL = TJMQLL / 1.03

    if MJRKWD > MJRKWD_max[3]:
        TJMQLL = TJMQLL / 1.05

    if MJRKWD > MJRKWD_max[4]:
        TJMQLL = TJMQLL / 1.08

    if MQLL[1] > 0:
        TJMQLL = np.maximum(TJMQLL, 2000)
        # TJMQLL = np.maximum(TJMQLL, 3800)
        TJMQLL = np.minimum(TJMQLL, 8300)

    TJMQLL = np.maximum(TJMQLL, LTJMQLL - 800)
    TJMQLL = np.minimum(TJMQLL, LTJMQLL + 800)

    TJKQLL = np.minimum(2.00 * TJMQLL, TJKQLL)
    TJKQLL = np.maximum(1.70 * TJMQLL, TJKQLL)

    tanzhen3 = TJMQLL
    tanzhen4 = TJKQLL

    a1 = 50 * 10 ** -4
    b1 = 10 * 10 ** -5
    c1 = 10 * 10 ** -5
    d1 = 40 * 10 ** -6

    MQSD = MQFMFK[0] + a1 * (TJMQLL - MQLL[0]) + b1 * (TJMQLL - MQLL[1]) + c1 * (TJMQLL - MQLL[2]) + d1 * (
            TJMQLL - MQLL[3])

    MQSD = np.minimum(MQFMFK[0] + 1.3, MQSD)
    MQSD = np.maximum(MQFMFK[0] - 1.4, MQSD)

    tanzhen0_0 = MQSD

    # if (TJMQLL - MQLL[0]) > 300:
    #     MQSD = MQSD + 0.08
    # if (TJMQLL - MQLL[0]) < -300:
    #     MQSD = MQSD - 0.1

    if (TJMQLL - MQLL[0]) > 500:
        MQSD = MQSD + 0.1
    if (TJMQLL - MQLL[0]) < -500:
        MQSD = MQSD - 0.1

    if (TJMQLL - MQLL[0]) > 700:
        MQSD = MQSD + 0.1
    if (TJMQLL - MQLL[0]) < -700:
        MQSD = MQSD - 0.2

    if (TJMQLL - MQLL[0]) > 800:
        MQSD = MQSD + 0.1
    if (TJMQLL - MQLL[0]) < -800:
        MQSD = MQSD - 0.2

    if (TJMQLL - MQLL[0]) > 1000:
        MQSD = MQSD + 0.1
    if (TJMQLL - MQLL[0]) < -1000:
        MQSD = MQSD - 0.2

    if (TJMQLL - MQLL[0]) > 1200:
        MQSD = MQSD + 0.1
    if (TJMQLL - MQLL[0]) < -1200:
        MQSD = MQSD - 0.3

    if (TJMQLL - MQLL[0]) > 1500:
        MQSD = MQSD + 0.1
    if (TJMQLL - MQLL[0]) < -1500:
        MQSD = MQSD - 0.4

    # a1 = 50 * 10 ** -4
    # b1 = 10 * 10 ** -5
    # c1 = 10 * 10 ** -5
    # d1 = 40 * 10 ** -6

    KQ_a1 = 1 / 300
    KQ_b1 = 1 / 3000
    KQ_c1 = 1 / 30000
    KQ_d1 = 1 / 300000

    KQSD = KQFMFK[0] + KQ_a1 * (TJKQLL - KQLL[0]) + KQ_b1 * (TJKQLL - KQLL[1]) + KQ_c1 * (TJKQLL - KQLL[2]) + KQ_d1 * (
            TJKQLL - KQLL[3])

    KQSD = np.maximum(KQFMFK[0] - 2.0, KQSD)
    KQSD = np.minimum(KQFMFK[0] + 2.0, KQSD)

    if MQLL[0] == 0:
        MQSD = MQFMFK[0]

    # 通过增加或者减少阀门开�����������������������������������������������������������������������控制�������������������力，���������������压力过大，需要��加阀门开度，反之减小阀门开度
    # if MJ_CKYL > 0.8:
    #     MQSD = MQSD + np.minimum((MJ_CKYL - 0.80), 10) * 5
    # if MJ_CKYL < 0.6:
    #     MQSD = MQSD - np.minimum((0.6 - MJ_CKYL), 10) * 5
    MQYL = np.maximum(np.minimum(MQYL, 12), 8)
    MJ_CKWD = np.maximum(np.minimum(MJ_CKWD, 76), 72)
    MJRKWD = np.maximum(np.minimum(MJRKWD, 260), 220)
    MJ_YC = np.minimum(MJ_YC, 6990)
    MJRK_YL = np.maximum(np.minimum(MJRK_YL, -700), -1400)
    YQL_LTWD = np.maximum(np.minimum(YQL_LTWD, 960), 830)
    YQL_LTYL = np.maximum(np.minimum(YQL_LTYL, -200), -800)

    MQSD1 = (-1.2087) * MQYL + (-0.0063) * KQLL[0] + (0.0017) * MQLL[0] + (0.1475) * KQFMFK[0] + (1.1487) * FQZGFMFK + (
        -0.0398) * YQL_LTWD + (0.2802) * MJRKWD + (-0.1242) * MJ_CKWD + (0.0139) * MJRK_YL + (-0.0203) * YQL_LTYL
    MQSD1 = np.float32(MQSD1)

    MQSD1 = np.minimum(MQFMFK[0] + 1.4, MQSD1)
    MQSD1 = np.maximum(MQFMFK[0] - 1.6, MQSD1)

    KQSD1 = (0.4789) * MQYL + (0.0173) * KQLL[0] + (0.0005) * MQLL[0] + (0.0669) * MQFMFK[0] + (-0.6896) * FQZGFMFK + (
        -0.0165) * YQL_LTWD + (0.0310) * MJRKWD + (0.0734) * MJ_CKWD + (0.0143) * MJRK_YL + (-0.0052) * MJ_YC + (
                0.0027) * YQL_LTYL
    KQSD1 = np.float32(KQSD1)

    KQSD1 = np.maximum(KQFMFK[0] - 1.5, KQSD1)
    KQSD1 = np.minimum(KQFMFK[0] + 1.2, KQSD1)


    KQSD = np.maximum(np.minimum(KQSD, 60.0), 15)  # 空气阀门设定值最大值

    MQSD = np.maximum(np.minimum(MQSD, 36.0), 10)  # 煤气阀门设定值最大值

    # if AI_BW == 1:
    #
    #     KQSD = 0
    #     if YQL_LTWD < 750:
    #         TJMQLL = 300
    #     if YQL_LTWD < 740:
    #         TJMQLL = 500
    #     if YQL_LTWD < 720:
    #         TJMQLL = 800
    #         KQSD = 5
    #     if YQL_LTWD < 700:
    #         TJMQLL = 1200
    #         KQSD = 8
    #
    #     a1 = 8 * 10 ** -5
    #     b1 = 4 * 10 ** -6
    #     c1 = 2 * 10 ** -6
    #     d1 = 1 * 10 ** -6
    #
    #     MQSD1 = MQFMFK1[0] + a1 * (TJMQLL - MQLL[0]) + b1 * (TJMQLL - MQLL[1]) + c1 * (TJMQLL - MQLL[2]) + d1 * (
    #             TJMQLL - MQLL[3])
    #
    #     MQSD1 = np.minimum(MQFMFK1[0] + 1, MQSD1)
    #     MQSD1 = np.maximum(MQFMFK1[0] - 1, MQSD1)
    #
    #     if (TJMQLL - MQLL[0]) > 2000:
    #         MQSD1 = MQSD1 + 1
    #     if (TJMQLL - MQLL[0]) < -2000:
    #         MQSD1 = MQSD1 - 1
    #
    #     MQSD2 = MQSD1
    #
    #     MQSD1 = 0
    #     MQSD2 = 0
    #
    #     MQSD1 = np.maximum(np.minimum(MQSD1, 10.0), 0)
    #     MQSD2 = np.maximum(np.minimum(MQSD2, 10.0), 0)
    #     KQSD = np.minimum(KQSD, 60)

    YCZT = params["pid_outparams"][0]["YCZT"]
    p1 = params["pid_outparams"][0]["p1"]
    # YCZT = 10
    # p1 = 5
    if MJ_CKWD >= 105:
        MQSD1 = 0
        MQSD2 = 0
        KQSD = 6
        p1 = 1
    if MQFMFK[0] <= 5:
        if p1 == 1:
            YCZT = 1
    if AI_AT[0] == 0 and AI_AT[2] == 0:
        p1 = 0
    if p1 == 0:
        YCZT = 0

    # TJMQLL1 = 0
    # TJMQLL2 = 0
    # TJKQLL = 0
    # MQSD1 = 40
    # MQSD2 = 50
    # KQSD = 50
    # FQSD = 80
    MQSD = np.float32(MQSD)

    # FQSD = np.float32(FQSD)
    KQSD = np.float32(KQSD)
    outputs = {}

    fmsd = {}
    fmsd['MQSD'] = np.array(MQSD).tolist()
    fmsd['MQSD1'] = np.array(MQSD1).tolist()
    fmsd['KQSD'] = np.array(KQSD).tolist()
    fmsd['KQSD1'] = np.array(KQSD1).tolist()
    fmsd['MJRKWD_mean'] = np.array(MJRKWD_mean).tolist()
    fmsd['TJKQLL'] = np.array(TJKQLL).tolist()
    fmsd['TJMQLL'] = np.array(TJMQLL).tolist()
    fmsd['NEXT'] = np.array(NEXT).tolist()
    fmsd['YCZT'] = int(YCZT)
    fmsd['p1'] = int(p1)

    outputs['Data'] = fmsd

    LogData = {}
    LogData["TJMQLL"] = np.array(TJMQLL).tolist()
    LogData["MQFMFK"] = np.array(MQFMFK[0]).tolist()
    LogData["KQFMFK"] = np.array(KQFMFK[0]).tolist()
    LogData["tanzhen1"] = tanzhen1
    LogData["tanzhen2"] = tanzhen2
    LogData["tanzhen3"] = tanzhen3
    LogData["tanzhen4"] = tanzhen4
    LogData["tanzhen0_0"] = tanzhen0_0
    LogData["tag"] = tag
    LogData["MJRKWD_mean"] = MJRKWD_mean
    outputs['LogData'] = LogData
    outputs['Message'] = 'Input Status : 1'
    outputs['Code'] = 1
    return outputs


# 递归函数来转换字典和列表中的 numpy 类型为 Python 原生类型
def convert_numpy_to_builtin(obj):
    if isinstance(obj, dict):
        return {k: convert_numpy_to_builtin(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_to_builtin(v) for v in obj]
    elif isinstance(obj, (np.integer, np.floating)):  # 检查 numpy 整数和浮点数类型
        return obj.item()  # 使用 item() 方法将 numpy 类型转换为 Python 原生类型
    else:
        return obj


try:
    # -----线下测试代码-----------
    # # 本地测试输入数据路径
    # if sys.platform != "win32":
    #     path = "/Users/qiaoqiao/PycharmProjects/pythonProject/龙腾/实施文档/【2】代码/data_pid_V1.0.json"
    # else:
    #     path = "D:\power_plant_gas_boiler\data\luan_7\data_pid.json"
    #
    # with open(path, 'r', encoding='utf-8') as f:
    #     args = f.read()
    # params = param_str_process(args[1:])

    # --------线上测试---------------------
    args = sys.argv[1:]  # 命令行参数
    params = param_str_process(args[0])

    outputs = PID_Modular_Control(params)
    outputs = convert_numpy_to_builtin(outputs)
    print(json.dumps(outputs))
except Exception as e:
    times = time.asctime(time.localtime(time.time()))

    # -----线下测试代码
    # traceback.print_exc(file=open('/Users/qiaoqiao/PycharmProjects/pythonProject/龙腾/实施文档/【2】代码/log.txt', 'a'))

    # -----线上测试代码
    print("===" * 20, file=open('/home/fgfai/uploadPath/algorithm/python_pid/log.txt', 'a'))
    print(times, file=open('/home/fgfai/uploadPath/algorithm/python_pid/log.txt', 'a'))
    traceback.print_exc(file=open('/home/fgfai/uploadPath/algorithm/python_pid/log.txt', 'a'))

    outputs = {}
    status = 0
    outputs['Code'] = status
    outputs['Data'] = {}
    outputs['Message'] = str(e)
    print(json.dumps(outputs))



# ------------------------------
# 输出
# ------------------------------
class Output:
    """
    脚本输出
    """

    def __init__(self, params):
        for keys, values in params.items():
            setattr(self, keys, values)
            
    def output(self):
        # ------------------------------
        # 输出
        # ------------------------------
        outputs = {}
        # ------------------------------
        # Data
        # ------------------------------
        fmsd = {}
        fmsd["QHQSCKQFMGD"] = np.array(self.QHQSCKQFMGD).tolist()
        
        # 算法异常
        fmsd["Code"] = np.array(self.Code).tolist()
        
        outputs["Data"] = fmsd
        # ------------------------------
        # LogData
        # ------------------------------
        LogData = {}
        LogData["GAS_TREND"] = np.array(self.GAS_TREND).tolist()
        # 探针
        LogData["sc_mq_0"] = self.sc_mq_0
        
        outputs['LogData'] = LogData
        # ------------------------------
        # Code
        # ------------------------------
        outputs['Code'] = self.Code
        # ------------------------------
        # Message
        # ------------------------------
        outputs['Message'] = 'success'

        return outputs
    
    def exception_output(self, message):
        outputs = {}
        outputs['Data'] = {}
        outputs['LogData'] = [0]
        outputs['Code'] = 0.0
        outputs['Message'] = message
        
        return outputs



# 测试代码 main 函数
def main():
    try:
        # ------------------------------
        # 脚本运行设置
        # ------------------------------
        # 运行方式
        local_test = True
        
        # 本地测试输入数据路径
        if sys.platform != "win32":
            path = "/Users/zfwang/AIMS/projects/flue_gas_furnace/data/luan_7/data_pid.json"
        else:
            path = "D:\power_plant_gas_boiler\data\luan_7\data_pid.json"
        
        # 读取算法输入
        Boiler_Application_Scene = Application_Scene(path)
        if local_test:  # 本地测试
            params = Boiler_Application_Scene.offline_apply()
        else:  # 线上运行
            params = Boiler_Application_Scene.online_apply()
        # ------------------------------
        # 
        # ------------------------------
        # TODO
        # ------------------------------
        # 结果输出
        # ------------------------------
        PID_Output = Output(params = params)
        outputs = PID_Output.output()
        print(json.dumps(outputs))
    except Exception as e:
        PID_Output = Output(params)
        outputs = PID_Output.exception_output(message = str(e))
        print(json.dumps(outputs))
        traceback.print_exc()

if __name__ == "__main__":
    main()
