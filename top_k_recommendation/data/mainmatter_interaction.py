# DART open API로 데이터 수집

from urllib import request
from zipfile import ZipFile
import ssl, os
import xml.etree.ElementTree as ET

import pandas as pd
import numpy as np

import requests
from bs4 import BeautifulSoup


# 회사별 M&A 기록 가져오기

corp = pd.read_csv('project/data/corp.csv', dtype={'corp_code':object,'stock_code':object})
cols = ['corp_cls','corp_code','corp_name','mg_mth','mg_stn','mg_pp','mg_rt','mgptncmp_cmpnm','mgptncmp_mbsn','mgptncmp_rl_cmpn','mgsc_mgctrd']
# 법인구분, 고유번호, 회사명, 합병방법, 합병형태, 합병목적, 합병비율, 합병상대회사(회사명), 합병상대회사(주요사업), 합병상대회사(회사명), 합병상대회사(주요사업),합병일정(합병계약일)
df_mna = pd.DataFrame(columns = cols)

# api_key와 url은 블라인드 처리
def collect_data_per_corp(crtfc_key,corp_code):
    url = '?'

    bgn_de = '20150101'
    end_de = '20230610'

    response = requests.get(f'{url}crtfc_key={crtfc_key}&corp_code={corp_code}&bgn_de={bgn_de}&end_de={end_de}')
    cols = ['corp_cls','corp_code','corp_name','mg_mth','mg_stn','mg_pp','mg_rt','mgptncmp_cmpnm','mgptncmp_mbsn','mgptncmp_rl_cmpn','mgsc_mgctrd']
    tree = ET.fromstring(response.text)
    if tree.find('status').text != '000':
        return (False,tree.find('status').text)
    for mna in tree.findall('list'):
        infos = []
        for col in cols:
            info = mna.find(col).text
            infos.append(info)
        df_mna.loc[df_mna.shape[0]+1] = infos
    return (True,'000')

api_key = []
last_corp = '00434003'
last_idx = 0

for key in api_key:
    print(f'Start Preprocessing from Idx:{last_idx}')
    from_last_corp_code = corp['corp_code'][corp[corp['corp_code']==last_corp].index[0]:]
    for corp_code in from_last_corp_code:
        try:
            ret = collect_data_per_corp(key,corp_code)
            last_corp = corp_code
            last_idx = corp[corp['corp_code']==last_corp].index[0]
            if ret[1] == '020':
                print(f'Exceed number of accesses with key:{key}')
                print(f'Processed up to Idx:{last_idx}')
                break
        except:
            from_last_corp_code = corp['corp_code'][corp[corp['corp_code']==last_corp].index[0]:]
    print(df_mna.shape)


df_mna.to_csv('mna_api.csv',index=False)