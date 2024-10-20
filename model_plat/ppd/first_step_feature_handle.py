import datetime
import collections
import random
import sys
from importlib import reload
from matplotlib import pyplot as plt

from model_plat.ppd.scorecard_functions_V3 import *

reload(sys)
# -*- coding: utf-8 -*-

################################
######## UDF: 自定义函数 ########
################################
### 对时间窗口，计算累计产比 ###
def TimeWindowSelection(df, daysCol, time_windows):
    '''
    :param df: the dataset containg variabel of days
    :param daysCol: the column of days
    :param time_windows: the list of time window
    :return:
    '''
    freq_tw = {}
    for tw in time_windows:
        freq = sum(df[daysCol].apply(lambda x: int(x<=tw)))
        freq_tw[tw] = freq
    return freq_tw


def DeivdedByZero(nominator, denominator):
    '''
    当分母为0时，返回0；否则返回正常值
    '''
    if denominator == 0:
        return 0
    else:
        return nominator*1.0/denominator


#对某些统一的字段进行统一
def ChangeContent(x):
    y = x.upper()
    if y == '_MOBILEPHONE':
        y = '_PHONE'
    return y

def MissingCategorial(df,x):
    missing_vals = df[x].map(lambda x: int(x!=x))
    return sum(missing_vals)*1.0/df.shape[0]

def MissingContinuous(df,x):
    missing_vals = df[x].map(lambda x: int(np.isnan(x)))
    return sum(missing_vals) * 1.0 / df.shape[0]

def MakeupRandom(x, sampledList):
    if x==x:
        return x
    else:
        randIndex = random.randint(0, len(sampledList)-1)
        return sampledList[randIndex]



############################################################
#Step 0: 数据分析的初始工作, 包括读取数据文件、检查用户Id的一致性等#
############################################################
import os
path = os.path.abspath("..")
folderOfData = os.path.join(path, "data/ppd/")
print(folderOfData)
#folderOfData = '/Users/Code/Data Collections/bank default/'
data1 = pd.read_csv(folderOfData+'PPD_LogInfo_3_1_Training_Set.csv', header = 0)
data2 = pd.read_csv(folderOfData+'PPD_Training_Master_GBK_3_1_Training_Set.csv', header = 0,encoding = 'gbk')
data3 = pd.read_csv(folderOfData+'PPD_Userupdate_Info_3_1_Training_Set.csv', header = 0)

#############################################################################################
# Step 1: 从PPD_LogInfo_3_1_Training_Set &  PPD_Userupdate_Info_3_1_Training_Set数据中衍生特征#
#############################################################################################
# compare whether the four city variables match
data2['city_match'] = data2.apply(lambda x: int(x.UserInfo_2 == x.UserInfo_4 == x.UserInfo_8 == x.UserInfo_20),axis = 1)
del data2['UserInfo_2']
del data2['UserInfo_4']
del data2['UserInfo_8']
del data2['UserInfo_20']

### 提取申请日期，计算日期差，查看日期差的分布
data1['logInfo'] = data1['LogInfo3'].map(lambda x: datetime.datetime.strptime(x,'%Y-%m-%d'))
data1['Listinginfo'] = data1['Listinginfo1'].map(lambda x: datetime.datetime.strptime(x,'%Y-%m-%d'))
data1['ListingGap'] = data1[['logInfo','Listinginfo']].apply(lambda x: (x[1]-x[0]).days,axis = 1)
plt.hist(data1['ListingGap'],bins=200)
plt.title('Days between login date and listing date')
ListingGap2 = data1['ListingGap'].map(lambda x: min(x,365))
plt.hist(ListingGap2,bins=200)

timeWindows = TimeWindowSelection(data1, 'ListingGap', range(30,361,30))

'''
使用180天作为最大的时间窗口计算新特征
所有可以使用的时间窗口可以有7 days, 30 days, 60 days, 90 days, 120 days, 150 days and 180 days.
在每个时间窗口内，计算总的登录次数，不同的登录方式，以及每种登录方式的平均次数
'''
time_window = [7, 30, 60, 90, 120, 150, 180]
var_list = ['LogInfo1','LogInfo2']
data1GroupbyIdx = pd.DataFrame({'Idx':data1['Idx'].drop_duplicates()})

for tw in time_window:
    data1['TruncatedLogInfo'] = data1['Listinginfo'].map(lambda x: x + datetime.timedelta(-tw))
    temp = data1.loc[data1['logInfo'] >= data1['TruncatedLogInfo']]
    for var in var_list:
        #count the frequences of LogInfo1 and LogInfo2
        count_stats = temp.groupby(['Idx'])[var].count().to_dict()
        data1GroupbyIdx[str(var)+'_'+str(tw)+'_count'] = data1GroupbyIdx['Idx'].map(lambda x: count_stats.get(x,0))

        # count the distinct value of LogInfo1 and LogInfo2
        Idx_UserupdateInfo1 = temp[['Idx', var]].drop_duplicates()
        uniq_stats = Idx_UserupdateInfo1.groupby(['Idx'])[var].count().to_dict()
        data1GroupbyIdx[str(var) + '_' + str(tw) + '_unique'] = data1GroupbyIdx['Idx'].map(lambda x: uniq_stats.get(x,0))

        # calculate the average count of each value in LogInfo1 and LogInfo2
        data1GroupbyIdx[str(var) + '_' + str(tw) + '_avg_count'] = data1GroupbyIdx[[str(var)+'_'+str(tw)+'_count',str(var) + '_' + str(tw) + '_unique']].\
            apply(lambda x: DeivdedByZero(x[0],x[1]), axis=1)


data3['ListingInfo'] = data3['ListingInfo1'].map(lambda x: datetime.datetime.strptime(x,'%Y/%m/%d'))
data3['UserupdateInfo'] = data3['UserupdateInfo2'].map(lambda x: datetime.datetime.strptime(x,'%Y/%m/%d'))
data3['ListingGap'] = data3[['UserupdateInfo','ListingInfo']].apply(lambda x: (x[1]-x[0]).days,axis = 1)
collections.Counter(data3['ListingGap'])
hist_ListingGap = np.histogram(data3['ListingGap'])
hist_ListingGap = pd.DataFrame({'Freq':hist_ListingGap[0],'gap':hist_ListingGap[1][1:]})
hist_ListingGap['CumFreq'] = hist_ListingGap['Freq'].cumsum()
hist_ListingGap['CumPercent'] = hist_ListingGap['CumFreq'].map(lambda x: x*1.0/hist_ListingGap.iloc[-1]['CumFreq'])

'''
对 QQ和qQ, Idnumber和idNumber,MOBILEPHONE和PHONE 进行统一
在时间切片内，计算
 (1) 更新的频率
 (2) 每种更新对象的种类个数
 (3) 对重要信息如IDNUMBER,HASBUYCAR, MARRIAGESTATUSID, PHONE的更新
'''
data3['UserupdateInfo1'] = data3['UserupdateInfo1'].map(ChangeContent)
data3GroupbyIdx = pd.DataFrame({'Idx':data3['Idx'].drop_duplicates()})

time_window = [7, 30, 60, 90, 120, 150, 180]
for tw in time_window:
    data3['TruncatedLogInfo'] = data3['ListingInfo'].map(lambda x: x + datetime.timedelta(-tw))
    temp = data3.loc[data3['UserupdateInfo'] >= data3['TruncatedLogInfo']]

    #frequency of updating
    freq_stats = temp.groupby(['Idx'])['UserupdateInfo1'].count().to_dict()
    data3GroupbyIdx['UserupdateInfo_'+str(tw)+'_freq'] = data3GroupbyIdx['Idx'].map(lambda x: freq_stats.get(x,0))

    # number of updated types
    Idx_UserupdateInfo1 = temp[['Idx','UserupdateInfo1']].drop_duplicates()
    uniq_stats = Idx_UserupdateInfo1.groupby(['Idx'])['UserupdateInfo1'].count().to_dict()
    data3GroupbyIdx['UserupdateInfo_' + str(tw) + '_unique'] = data3GroupbyIdx['Idx'].map(lambda x: uniq_stats.get(x, x))

    #average count of each type
    data3GroupbyIdx['UserupdateInfo_' + str(tw) + '_avg_count'] = data3GroupbyIdx[['UserupdateInfo_'+str(tw)+'_freq', 'UserupdateInfo_' + str(tw) + '_unique']]. \
        apply(lambda x: x[0] * 1.0 / x[1], axis=1)

    #whether the applicant changed items like IDNUMBER,HASBUYCAR, MARRIAGESTATUSID, PHONE
    Idx_UserupdateInfo1['UserupdateInfo1'] = Idx_UserupdateInfo1['UserupdateInfo1'].map(lambda x: [x])
    Idx_UserupdateInfo1_V2 = Idx_UserupdateInfo1.groupby(['Idx'])['UserupdateInfo1'].sum()
    for item in ['_IDNUMBER','_HASBUYCAR','_MARRIAGESTATUSID','_PHONE']:
        item_dict = Idx_UserupdateInfo1_V2.map(lambda x: int(item in x)).to_dict()
        data3GroupbyIdx['UserupdateInfo_' + str(tw) + str(item)] = data3GroupbyIdx['Idx'].map(lambda x: item_dict.get(x, x))

# Combine the above features with raw features in PPD_Training_Master_GBK_3_1_Training_Set
allData = pd.concat([data2.set_index('Idx'), data3GroupbyIdx.set_index('Idx'), data1GroupbyIdx.set_index('Idx')],axis= 1)
allData.to_csv(folderOfData+'allData_0.csv',encoding = 'gbk')

