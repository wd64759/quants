# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 14:17:49 2019

@author: wangx
"""

import tushare as ts
import pandas as pd
import re


def data_pro(table):
    
    table = table.astype(str) # 将数字转换为字符串
    grouped = table.groupby(['code','name'])
    result = grouped.agg(lambda x:'|'.join(x))
    
    result['code'] = [x[0] for x in result.index]
    result['name'] = [x[1] for x in result.index]
    result.index = [i for i in range(len(result))]
    
    return result
    
    
def classified():
    
    #在现实交易中，经常会按行业统计股票的涨跌幅或资金进出，本接口按照sina财经对沪深股票进行的行业分类，返回所有股票所属行业的信息。
    #注意：有的股票属于两个行业：如000587
    industry = ts.get_industry_classified()
    industry = industry.drop_duplicates()
    industry_new = data_pro(industry)
    industry_new.rename(columns = {'c_name':'industry'}, inplace=True)
    
    
    #返回股票概念的分类数据，现实的二级市场交易中，经常会以”概念”来炒作，在数据分析过程中，可根据概念分类监测资金等信息的变动情况。
    concept = ts.get_concept_classified()
    concept = concept.drop_duplicates()
    concept_new = data_pro(concept)
    concept_new.rename(columns = {'c_name': 'concept'}, inplace=True)
    
    
    #按地域对股票进行分类，即查找出哪些股票属于哪个省份。
    area = ts.get_area_classified()
    area = area.drop_duplicates()
    area_new = data_pro(area)
    
    
    #获取中小板股票数据，即查找所有002开头的股票
    sme = ts.get_sme_classified()
    sme['belong_bk'] = '中小板'
    #获取创业板股票数据，即查找所有300开头的股票
    gem = ts.get_gem_classified()
    gem['belong_bk'] = '创业板'
    #获取风险警示板股票数据，即查找所有st股票
    st = ts.get_st_classified()
    st['belong_bk'] = '风险警示板'
    bk = pd.concat([sme, gem, st], join='outer', axis=0)
    bk = bk.drop_duplicates()
    bk = data_pro(bk)
    
    
    # 获取沪深300当前成份股及所占权重
    hs300s = ts.get_hs300s()
    hs300s = hs300s.iloc[:,1:-1]
    hs300s['belong_cfg'] = '沪深300成份股'
    # 获取上证50成份股
    sz50s = ts.get_sz50s()
    sz50s = sz50s.iloc[:,1:]
    sz50s['belong_cfg'] = '上证50成份股'    
    # 获取中证500成份股
    zz500s = ts.get_zz500s()
    zz500s = zz500s.iloc[:,1:-1]
    zz500s['belong_cfg'] = '中证500成份股'
    cfg = pd.concat([hs300s, sz50s, zz500s], join='outer', axis=0)
    cfg = cfg.drop_duplicates()
    cfg = data_pro(cfg)
    
    
    # 获取已经被终止上市的股票列表，数据从上交所获取，目前只有在上海证券交易所交易被终止的股票。
    terminated = ts.get_terminated()
    if terminated != None:
        terminated['终止上市'] ='终止上市'
    
    
    # 获取被暂停上市的股票列表，数据从上交所获取，目前只有在上海证券交易所交易被终止的股票。
    suspended = ts.get_suspended()
    if suspended != None:
        suspended['暂停上市'] = '暂停上市'
        
        
    # 数据拼接
    table_list = [industry_new, concept_new, area_new, bk, cfg]
    for i in range(len(table_list)):
        if i == 0:
            classified_data = table_list[i]
        else:
            classified_data = pd.merge(classified_data, table_list[i], how='outer', on=['code','name'])
    classified_data = classified_data.fillna('未知')
    
    
    #一个代码对应多个名称的数据整理
    classified_temp = classified_data.groupby(['code'])
    classified_new = classified_temp.agg(lambda x:'|'.join(x))
    classified_dict = {
            'industry': '所属行业',
            'name' : '名称',
            'concept': '概念',
            'area': '区域',
            'belong_bk': '所属板块',
            'belong_cfg': '所属成分股'
            }
    classified_new.columns = classified_new.columns.map(classified_dict)
    
    industry_list = classified_new['所属行业']
    industry_list = [i.split('|')[0] for i in industry_list]
    
    classified_new['所属行业'] = industry_list
    return classified_new


def basics(year, month):
    
    # 获取沪深上市公司基本情况
    basics = ts.get_stock_basics()
    basics['code'] = basics.index
    basics = data_pro(basics)
    basics_dict = {
                'code':'代码',
                'name':'名称',
                'industry':'所属子行业',
                'area':'地区',
                'pe':'市盈率',
                'outstanding':'流通股本(亿)',
                'totals':'总股本(亿)',
                'totalAssets':'总资产(万)',
                'liquidAssets':'流动资产',
                'fixedAssets':'固定资产',
                'reserved':'公积金',
                'reservedPerShare':'每股公积金',
                'esp':'每股收益',
                'bvps':'每股净资',
                'pb':'市净率',
                'timeToMarket':'上市日期',
                'undp':'未分利润',
                'perundp':'每股未分配',
                'rev':'收入同比(%)',
                'profit':'利润同比(%)',
                'gpr':'毛利率(%)',
                'npr':'净利润率(%)',
                'holders':'股东人数'
            }
    basics.columns =  basics.columns.map(basics_dict)
    order = [ '代码', '名称', '所属子行业', '地区', '市盈率', '流通股本(亿)', '总股本(亿)', \
             '总资产(万)', '流动资产', '固定资产', '公积金', '每股公积金', '每股收益', \
             '每股净资', '市净率', '上市日期', '未分利润', '每股未分配','收入同比(%)', \
             '利润同比(%)', '毛利率(%)', '净利润率(%)', '股东人数']
    basics = basics[order]
    
    
    # 按年度、季度获取业绩报表数据。
    report = ts.get_report_data(year, month)
    report = report.drop_duplicates()
    report = data_pro(report)
    report_dict = {
                'code':'代码',
                'name':'名称',
                'eps':str(year) + str(month) + '每股收益',
                'eps_yoy':str(year) + str(month) + '每股收益同比(%)',
                'bvps':str(year) + str(month) + '每股净资产',
                'roe':str(year) + str(month) + '净资产收益率(%)',
                'epcf':str(year) + str(month) + '每股现金流量(元)',
                'net_profits':str(year) + str(month) + '净利润(万元)',
                'profits_yoy':str(year) + str(month) + '净利润同比(%)',
                'distrib':str(year) + str(month) + '分配方案',
                'report_date':'发布日期'
            }
    report.columns = report.columns.map(report_dict)
    
    
    #按年度、季度获取盈利能力数据
    profit = ts.get_profit_data(year, month)
    profit = profit.drop_duplicates()
    profit = data_pro(profit)
    profit_dict = {
                'code':'代码',
                'name':'名称',
                'roe':str(year) + str(month) + '净资产收益率(%)',
                'net_profit_ratio':str(year) + str(month) + '净利率(%)',
                'gross_profit_rate':str(year) + str(month) + '毛利率(%)',
                'net_profits':str(year) + str(month) + '净利润(万元)',
                'eps':str(year) + str(month) + '每股收益',
                'business_income':str(year) + str(month) + '营业收入(百万元)',
                'bips':str(year) + str(month) + '每股主营业务收入(元)'
            }
    profit.columns = profit.columns.map(profit_dict)
    
    
    #营运能力:按年度、季度获取营运能力数据
    operation = ts.get_operation_data(year, month)
    operation = operation.drop_duplicates()
    operation = data_pro(operation)
    operation_dict = {
                'code':'代码',
                'name':'名称',
                'arturnover':str(year) + str(month) + '应收账款周转率(次)',
                'arturndays':str(year) + str(month) + '应收账款周转天数(天)',
                'inventory_turnover':str(year) + str(month) + '存货周转率(次)',
                'inventory_days':str(year) + str(month) + '存货周转天数(天)',
                'currentasset_turnover':str(year) + str(month) + '流动资产周转率(次)',
                'currentasset_days':str(year) + str(month) + '流动资产周转天数(天)'
            }
    operation.columns = operation.columns.map(operation_dict)
    
    # 按年度、季度获取成长能力数据
    growth = ts.get_growth_data(year, month)
    growth = growth.drop_duplicates()
    growth = data_pro(growth)
    growth_dict = {
                'code':'代码',
                'name':'名称',
                'mbrg':str(year) + str(month) + '主营业务收入增长率(%)',
                'nprg':str(year) + str(month) + '净利润增长率(%)',
                'nav':str(year) + str(month) + '净资产增长率',
                'targ':str(year) + str(month) + '总资产增长率',
                'epsg':str(year) + str(month) + '每股收益增长率',
                'seg':str(year) + str(month) + '股东权益增长率'          
            }
    growth.columns = growth.columns.map(growth_dict)
    
    
    # 按年度、季度获取偿债能力数据
    debtpaying = ts.get_debtpaying_data(year, month)
    debtpaying = debtpaying.drop_duplicates()
    debtpaying = data_pro(debtpaying)
    debtpaying_dict = {
                'code':'代码',
                'name':'名称',
                'currentratio':str(year) + str(month) + '流动比率',
                'quickratio':str(year) + str(month) + '速动比率',
                'cashratio':str(year) + str(month) + '现金比率',
                'icratio':str(year) + str(month) + '利息支付倍数',
                'sheqratio':str(year) + str(month) + '股东权益比率',
                'adratio':str(year) + str(month) + '股东权益增长率'
            }
    debtpaying.columns = debtpaying.columns.map(debtpaying_dict)
    
    
    #按年度、季度获取现金流量数据
    cashflow = ts.get_cashflow_data(year, month)
    cashflow = cashflow.drop_duplicates()
    cashflow = data_pro(cashflow)
    cashflow_dict = {
                'code':'代码',
                'name':'名称',
                'cf_sales':str(year) + str(month) + '经营现金净流量对销售收入比率',
                'rateofreturn':str(year) + str(month) + '资产的经营现金流量回报率',
                'cf_nm':str(year) + str(month) + '经营现金净流量与净利润的比率',
                'cf_liabilities':str(year) + str(month) + '经营现金净流量对负债比率',
                'cashflowratio':str(year) + str(month) + '现金流量比率'          
            }
    cashflow.columns = cashflow.columns.map(cashflow_dict)
    
    table_list = [basics, report, profit, operation, growth, debtpaying, cashflow]
    for i in range(len(table_list)):
        if i == 0:
            basics_data = table_list[i]
        else:
            basics_data = pd.merge(basics_data, table_list[i], how='outer', on=['代码','名称'])

    basics_data = basics_data.fillna('未知')        
    basics_temp = basics_data.groupby(['代码'])
    basics_new = basics_temp.agg(lambda x:'|'.join(x))
    
    return basics_new

      
##################################################################################
#超级大盘股：资产规模大于1000亿
def largecap_index(data): 
    largecap = []
    for i in data['总资产(万)']:
        num = '^[-+]{0,1}[0-9]{1,}.{0,1}[0-9]{0,}'
        int_i = re.findall(num, str(i))
        if len(int_i) != 0:
            if float(int_i[0]) > 1000000.0:
                largecap.append('大盘股')
            else:
                largecap.append('否')
        else:
            largecap.append('否')
    
    data['资产规模'] = largecap
    return data


###################################################################################
#低价股
def valuation_index(data):

    def getDatetime():
        from datetime import datetime, date
        from dateutil.relativedelta import relativedelta
        
        today = date.today()  #date类型
        today = datetime.strptime(str(today), '%Y-%m-%d') #date转str再转datetime
        end_day = today + relativedelta(days = -1) #减去一天
        start_day = end_day + relativedelta(years=-10)
        
        end_day = end_day.date()
        start_day = start_day.date()
        
        return start_day, end_day
    
    def stock_valuation(stock_index, start_day, end_day):
        valuation = ''
        hist = ts.get_hist_data(stock_index, start= str(start_day), end=str(end_day))
        
        if hist is not None:
            close_max = max(hist['close'])
            close_min = min(hist['close'])
            
            selling_point1 = (close_max - close_min)/m + close_min
            selling_point2 = (close_max - close_min)/n + close_min
            buy_point = ((close_max - close_min)/b + close_min)/v
            
            if hist['close'][0] > selling_point2:
                valuation = '高价股, 第二次建议卖'
                print(stock_index, '高价股, 第二次建议卖出')
                
            elif hist['close'][0] > selling_point1:
                valuation = '高价股, 第一次建议卖出'
                print(stock_index, '高价股, 第一次建议卖出')
                
            elif hist['close'][0] < buy_point:
                valuation = '低价股，建议买入'
                print(stock_index, '低价股，建议买入')
        else:
            valuation = '未知'
        return valuation
            
    valuation_list = []
    for stock_index in data.index:
        start_day, end_day = getDatetime()
        valuation = stock_valuation(stock_index, start_day, end_day)
        valuation_list.append(valuation)
    data['估值'] = valuation_list
    return data, end_day


####################################################################################
#利润率<-100%
def del_npr_index(data):
    del_npr = []
    for i in data['净利润率(%)']:
        num = '^[-+]{0,1}[0-9]{1,}.{0,1}[0-9]{0,}'
        int_i = re.findall(num, str(i))
        if len(int_i) != 0:
            if float(int_i[0]) < -100:
                del_npr.append('业绩差')
            else:
                del_npr.append('否')
        else:
            del_npr.append('否')
    data['业绩'] = del_npr
    return data
##################################################################################


## 选股策略
if __name__ == '__main__':
    m, n, b, v =1,2,3,4
    year = 2018; month = 4
    classified_new = classified()
    basics_new = basics(year, month)
    basics_new = basics_new.drop(['名称'], axis=1)
    data = pd.merge(classified_new, basics_new, left_index=True, right_index=True, how='outer')
    
    data = largecap_index(data)
    data, yesterday = valuation_index(data)
    data = del_npr_index(data)
    data.to_excel('./data.xlsx')

    finall_data = data[data['业绩'] != '业绩差']
    finall_data = finall_data[finall_data['估值'] == '低价股，建议买入']
    #finall_data = finall_data[finall_data['资产规模'] != '大盘股']