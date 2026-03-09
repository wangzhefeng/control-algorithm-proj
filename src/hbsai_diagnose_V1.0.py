import pandas as pd
import numpy as np
from sklearn.ensemble import BaggingRegressor
from sklearn.tree import ExtraTreeRegressor
from sklearn.model_selection import train_test_split
import warnings
from pycaret.regression import *
warnings.filterwarnings("ignore")
warnings.simplefilter(action="ignore",category=FutureWarning)
import sys
import json
import traceback
import datetime
path = sys.argv[1]
reportid = sys.argv[2]
# args = '{"address":"/Users/loubeibei/Documents/工作/体检升级/filteredData_2023091900012.txt","reportId":"2023100900023"}'
# json_str = args.replace('\\', '')
# json_str = json_str.replace('["{', '[{')
# json_str = json_str.replace('}"]', '}]')
# json_str = json_str.replace('","', ',')
# json_str = json_str.strip('"')
# params = json.loads(json_str)
# print(path)
# print(reportid)
# path = params['address']
# path = '/Users/loubeibei/Downloads/filteredData_2023101800002.txt'
# reportid='2023100900023'
def read_file(path):
    """
    读取数据,获得分钟级数据和秒级数据
    """
    data = pd.read_csv(path,parse_dates=['time'],index_col=False)
    data.set_index('time',drop=True,inplace=True)
    data_minute = data.resample('1min').mean()
    data_minute.reset_index(inplace=True)
    data.reset_index(inplace=True)
    return data_minute
    # f = open(path,encoding="utf-8")
    # df = f.read()
    # f.close()
    # params = json.loads(df)
    # data = pd.DataFrame(params[0]['heat_data'])
    # data['time'] = data['time'].apply(lambda x: datetime.datetime.strptime(x,"%Y-%m-%d %H:%M:%S"))
    # return data

def add_seconds(dataset):
    """
    加入周期、时间
    """
    r = 1
    m = 1
    period = [1]
    minute = [1]
    for i in range(1,len(dataset)):
        if (dataset['time'][i] - dataset['time'][i-1]).seconds < 600:
            m = m+1
        else:
            m = 1
            r = r+1
        period.append(r)
        minute.append(m)
              
    dataset['minute'] = minute
    dataset['period'] = period
    return dataset

def add_seconds_period(data,luid):
    r = 1
    s = 0
    second = [0]
    period = [1]
    timebase = data['time'][0]
    for i in range(1,len(data)):
        if (data['time'][i] - data['time'][i-1]).seconds > 600:
            r = r+1
            s = 0
            timebase = data['time'][i]
        else:
            s = (data['time'][i] - timebase).seconds
            
            
        period.append(r)
        second.append(s)
    data['period'] = period
    data['second'] = second
    return data
    
def get_boundary(dataset,luid):
    
    """
    获取建模数据
    0、数据筛选从燃烧时间、送风时间、拱顶温度、烟道温度；数据整理，非燃烧期（rsz,sfz)流量均为0
    1、拼接燃烧期和送风期数据，获得lfll,lfwd,sf_time,sf_cw,sf_mw,hl_time
    
    """
    mqll = 'rfl'+str(luid)+'mqll'
    ydwd = 'rfl'+str(luid)+'ydwd'
    rsswd = 'rfl'+str(luid)+'rsswd'
    rsz = 'rfl'+str(luid)+'rsz'
    sfz = 'rfl'+str(luid)+'sfz'
    mlzsf = 'rfl'+str(luid)+'mlzsf'
#     data_set = dataset[['time',rsswd, ydwd,mqll,rsz,sfz,mlzsf,'hfqrfwd','lfll', 'lfwd','rfwdd','rfwdx']]
    data_set = dataset[['time',rsswd, ydwd,mqll,rsz,sfz,mlzsf,'hfqrfwd','lfll', 'lfwd']]
    #数据筛选
    data_set[mqll].loc[data_set[rsz]==0]=0
    data_rsz = data_set.loc[data_set[mqll]>15000]
    data_sfz = data_set.loc[data_set[mqll]<15000]
#     data_sfz[mqll].loc[data_sfz[rsz]==0]=0

    data_rsz.reset_index(drop=True,inplace=True)
    data_sfz.reset_index(drop=True,inplace=True)
    data_rsz = add_seconds(data_rsz)
    data_sfz = add_seconds(data_sfz)
    
    #删除燃烧时间小于95分钟的
    temp0 = data_rsz.groupby('period').count()
    pop_period_rsz = temp0.loc[temp0['time']<95]
    pop_period_rsz1 = temp0.loc[temp0['time']>120]
    data_rsz = data_rsz.loc[~data_rsz['period'].isin(pop_period_rsz.index)]
    data_rsz = data_rsz.loc[~data_rsz['period'].isin(pop_period_rsz1.index)]
    
    #删除送风时间小于60分钟的
    temp =data_sfz.groupby('period').count()
    pop_period = temp.loc[temp['time']<55]
#     pop_period1 = temp.loc[temp['time']>70]
    data_sfz1 = data_sfz.loc[~data_sfz['period'].isin(pop_period.index)]
#     data_sfz1 = data_sfz1.loc[~data_sfz1['period'].isin(pop_period1.index)]
#     plt.figure()
#     for i in data_rsz['period'].unique():
#         dt = data_rsz.loc[data_rsz['period']==i]
#         plt.plot(dt['minute'],dt[rsswd])
# #     plt.grid()
#     plt.show()
    
#     plt.figure()
#     for i in data_rsz['period'].unique():
#         dt = data_rsz.loc[data_rsz['period']==i]
#         plt.plot(dt['minute'],dt[ydwd])
# #     plt.grid()
#     plt.show()
    
    # print("燃烧周期总数:%d" %len(data_rsz['period'].unique()))
    #烟道末温数据
    # ydwd_limit = int(input("please input lower limit ydwd:"))
    ydwd_limit = 355
    temp1 = data_rsz.groupby('period').max()
    pop_period_yd = temp1.loc[temp1[ydwd]<ydwd_limit]
    data_rsz = data_rsz.loc[~data_rsz['period'].isin(pop_period_yd.index)]
    # print("烟道不达标删除的周期: %d" %len(pop_period_yd))
    
    
    #拱顶温度
    # gdwd_limit = int(input("please input lower limit gdwd:"))
    gdwd_limit = 1275
    data_rsz_gd = data_rsz.loc[data_rsz['minute']>20]
    data_rsz_gd_pop = data_rsz_gd.loc[data_rsz_gd[rsswd]<gdwd_limit]
    temp2 = data_rsz_gd_pop.groupby('period').count()
    pop_period_gd = temp2.loc[temp2[rsswd]>20]
    data_rsz = data_rsz.loc[~data_rsz['period'].isin(pop_period_gd.index)]
    # print("拱顶不达标删除的周期 %d" %len(pop_period_gd))
    
    
    #做燃烧期与送风期的连接
    concat_sfz= data_sfz1.groupby('period').first()

    concat_rsz = data_rsz.groupby('period').last()
    concat_rsz['isburning'] = 1
    concat_sfz['isburning'] = 0
    concat_rsz.reset_index(inplace=True)
    concat_sfz.reset_index(inplace=True)
    concat = pd.concat([concat_rsz,concat_sfz],axis=0)
    concat.sort_values(by='time',inplace=True)
    concat['merge'] = 0
    concat.reset_index(drop=True,inplace=True)
    m = 0
    for i in range(1,len(concat)):
        if concat['isburning'][i] ==0 and concat['isburning'][i-1]==1:
            if (concat['time'][i] - concat['time'][i-1]).seconds<=180:
                m = m+1
                concat['merge'][i] = m
                concat['merge'][i-1] = m
        else:
            pass
    #删除没有连接起来的周期
    concat = concat.loc[~concat['merge'].isin([0])]
    periodsfz = concat.loc[concat['isburning']==0]
    periodsfz = periodsfz['period'].tolist()
    
    
    trans_minute = []
    lfll=[]
    lfwd=[]
#     hffmfk=[]
    sf_time = []
    sf_mw = []
    sf_cw = []

    for i in periodsfz:
        m =0
        dataset = data_sfz1.loc[data_sfz1['period']==i]
        dataset.reset_index(inplace=True)
        for i in range(len(dataset)):
            if dataset[sfz][i]==1:
                break
            else:
                m = m+1
               

        trans_minute.append(m)
        dataset = dataset.loc[dataset[sfz]==1]
        dataset.reset_index(drop=True,inplace=True)
#         max_hff = max(dataset['hffmfk'])
#         min_hff = min(dataset['hffmfk'])
#         diff_hff = max_hff-min_hff
        sf_cw.append(max(dataset['hfqrfwd'][0:30]))
        sf_mw.append(min(dataset['hfqrfwd'][-10:]))
        lfll.append(dataset.mean()['lfll'])
        lfwd.append(dataset.mean()['lfwd'])
#         hffmfk.append(diff_hff)
        sf_time.append(len(dataset))

    target =pd.DataFrame()
    target['period'] = periodsfz
    target['lfll'] = lfll
    target['lfwd'] = lfwd
#     target['hffmfk'] = hffmfk
    target['sf_time'] = sf_time
    target['sf_cw'] = sf_cw
    target['sf_mw'] = sf_mw
    target['hl_time'] = trans_minute
    
    data_gdyd_sf = concat.loc[concat['isburning']==0]
    data_gdyd_sf = data_gdyd_sf.loc[data_gdyd_sf['period'].isin(periodsfz)]


    merge_period = data_gdyd_sf['merge'].tolist()
    # print(len(merge_period))
    data_gdyd_rs = concat.loc[concat['isburning']==1]
    data_gdyd_rs = data_gdyd_rs.loc[data_gdyd_rs['merge'].isin(merge_period)]

    target[rsswd] = data_gdyd_rs[rsswd].tolist()
    target[ydwd] = data_gdyd_rs[ydwd].tolist()
    target['period_rs'] = data_gdyd_rs['period'].tolist()
    
    return target,data_rsz

def build_model(data,luid):
    """
    构建模型,预测拱顶温度边界值
    """
    ydwd = 'rfl'+str(luid)+'ydwd'
    rsswd = 'rfl'+str(luid)+'rsswd'
#     data = data.loc[data[rsswd]>1270]
    data.reset_index(drop=True,inplace=True)
    train_data = data[['lfll', 'lfwd',  'sf_time', 'hl_time','sf_cw','sf_mw', rsswd,ydwd]]
    train_data = np.round(train_data,0)
    X_train,X_test = train_test_split(train_data,test_size=0.2,random_state=42)
    Y_exit = X_test.pop(rsswd)
    exp_reg101 = setup(data = X_train, target = rsswd, session_id=123)
    best = compare_models()
    rfs = create_model(best)
    output = rfs.predict(X_test)
    X_test[rsswd] = Y_exit
    X_test['predict'] = output
    get_average = np.mean(train_data)
    get_average = pd.DataFrame(get_average).T
    get_average.pop(rsswd)
    predict_rsswd = rfs.predict(get_average)
    return rfs,X_test,predict_rsswd

def optimize(data,data_rsz,luid):
    ydwd = 'rfl'+str(luid)+'ydwd'
    period_unique = data['period_rs'].unique()
    predict_yd = pd.DataFrame()
    ext_yd_sum = []
    pre_yd_sum = []
    rfmw_d = []
    target_yd =[]
    ydmw = []
    # sfmw_low_limit = int(input("please input the floor limit:"))
    sfmw_low_limit = 1160
    for i in period_unique:
        dataset = data_rsz.loc[data_rsz['period']==i]
        dataset = dataset.loc[dataset['minute']>=10]
        length = len(dataset)
        sum_yd = sum(dataset[ydwd])
        dataset.reset_index(inplace=True,drop=True)
        yd_cw = dataset[ydwd][0]

        yd_mw = dataset[ydwd][-1:].values[0]
        rfmw = data.loc[data['period_rs']==i]['sf_mw'].values[0]
        
        rfmw_c = np.maximum(np.minimum(rfmw - sfmw_low_limit,6),0)
        ydwd_target = yd_mw - rfmw_c*2.5
        sum_yd_target = (ydwd_target+yd_cw)*length/2
        ext_yd_sum.append(sum_yd)
        pre_yd_sum.append(sum_yd_target)
        rfmw_d.append(rfmw)
        target_yd.append(ydwd_target)
        ydmw.append(yd_mw)
    predict_yd['period'] = period_unique
    predict_yd['exit_yd'] = ext_yd_sum
    predict_yd['pred_yd'] = pre_yd_sum
    predict_yd['rf_mw'] = rfmw_d
    predict_yd['ydwd_target'] = target_yd
    predict_yd['yd_mw'] = ydmw
    yd_predict = np.mean(predict_yd['yd_mw'])
    return yd_predict

def main():
    try:
        data_minute = read_file(path)
        outputs = {}
        result = {}
        for i in range(1,4):
            target,data_rsz = get_boundary(data_minute,i)
            rfs,X_test,predict_rsswd = build_model(target,i)
            predict_yd = optimize(target,data_rsz,i)
            result['predict_gdwd'+str(i)] = np.array(predict_rsswd).tolist()
            result['predict_ydwd'+str(i)] = np.array(predict_yd).tolist()
            result['reportid'] = reportid
        status = 1
        outputs['Code'] = status    
        outputs['Data'] = result
        outputs['Message'] = 'Input Status : 1'
        outputs['LogData'] = [0]
        print(json.dumps(outputs))
        # print(result)
    except Exception as e:
        traceback.print_exc()
        outputs={}
        status = 0
        outputs['Code'] = status
        outputs['Data'] = {}
        outputs['Message'] = str(e)
        outputs['LogData'] = [0]
        print(json.dumps(outputs))

       
if __name__ == "__main__":
    main()