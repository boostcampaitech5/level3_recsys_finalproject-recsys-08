#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import re
from collections import deque


# ## Dart에서 API로 data 받아온 것

# In[2]:


def process_partner_company(s:str):
    lines = s.split('\n')
    company_list = deque([])
    for line in lines:
        company_list.extend([x.strip() for x in line.split(',') if len(x.strip()) > 0])
        if line[-1] != ',':
            break
    return company_list


# In[3]:


def split_merged_company(df_org:pd.DataFrame,col_name:dict) -> pd.DataFrame:
    '''
    하나의 합병회사와 여러개의 피합병회사로 이루어진 경우 처리
    '''
    df = df_org.copy()
    df.rename(columns = col_name, inplace = True)
    df_to_split = df[df['partner'].str.startswith('피합병')][col_name.values()]
    idxs = set(df_to_split.index)
    no_change = set()
    for row in idxs:
        data_row = df.loc[row,:]
        merged_companies = data_row['partner'].split(':')[1].strip()
        merged_companies = process_partner_company(merged_companies)
        for merged_company in merged_companies:
            new_row = data_row.copy()
            new_row['partner'] = merged_company
            if len(merged_companies) == 1:
                no_change.add(row)
                df.loc[row]= new_row
                continue
            df.loc[df.shape[0]+1]= new_row
    idxs = idxs - no_change
    return df.drop(idxs).reset_index(drop=True)


# In[4]:


def filtering_company(company):
    if pd.isna(company):
        return np.nan
    original = company
    # 긴 것 -> 작은 것(ex> 주식회사 -> 주)
    # company = company.replace('(농업회사법인유한회사) ', '')
    # company = company.replace(' (농업회사법인유한회사)', '')
    company = company.replace('(농업회사법인유한회사)', '')
    # company = company.replace('의료법인) ', '')
    # company = company.replace(' 의료법인)', '')
    company = company.replace('의료법인)', '')
    # company = company.replace('농업회사법인 ', '')
    # company = company.replace(' 농업회사법인', '')
    company = company.replace('농업회사법인', '')
    # company = company.replace('가부시키가이샤 ', '') # 가부시키가이샤 = 주식회사
    # company = company.replace(' 가부시키가이샤', '')
    company = company.replace('가부시키가이샤', '')
    # company = company.replace('카부시키카이샤 ', '')
    # company = company.replace(' 카부시키카이샤', '')
    company = company.replace('카부시키카이샤', '')
    # company = company.replace('(유한회사) ', '')
    # company = company.replace(' (유한회사)', '')
    company = company.replace('(유한회사)', '')
    # company = company.replace('주식회사 ', '')
    # company = company.replace(' 주식회사', '')
    company = company.replace('주식회사', '')
    # company = company.replace('㈜ ', '')
    # company = company.replace(' ㈜', '')
    company = company.replace('㈜', '')
    # company = company.replace('(주) ', '')
    # company = company.replace(' (주)', '')
    company = company.replace('(주)', '')
    company = company.replace('（주）', '')
    # company = company.replace('( 주 ) ', '')
    # company = company.replace(' ( 주 )', '')
    company = company.replace('( 주 )', '')
    # company = company.replace('( 주) ', '')
    # company = company.replace(' ( 주)', '')
    company = company.replace('( 주)', '')
    # company = company.replace('(주 ) ', '')
    # company = company.replace(' (주 )', '')
    company = company.replace('(주 )', '')
    # company = company.replace('주) ', '')
    # company = company.replace(' 주)', '')
    company = company.replace('주)', '')
    # company = company.replace('(주 ', '')
    # company = company.replace(' (주', '')
    # company = company.replace('(주', '')
    # company = company.replace('주 ) ', '')
    # company = company.replace(' 주 )', '')
    company = company.replace('주 )', '')
    # company = company.replace('(유) ', '')
    # company = company.replace(' (유)', '')
    company = company.replace('(유)', '')
    # company = company.replace('유) ', '')
    # company = company.replace(' 유)', '')
    company = company.replace('유)', '')
    # company = company.replace('우) ', '')
    # company = company.replace(' 우)', '')
    company = company.replace('우)', '')
    # company = company.replace('(사) ', '')
    # company = company.replace(' (사)', '')
    company = company.replace('(사)', '')
    # company = company.replace('사) ', '')
    # company = company.replace(' 사)', '')
    company = company.replace('사)', '')
    # company = company.replace(' ', '')
    company = company.replace('  ', ' ') # 신정보개발주식회사 ~~
    company = company.split('|')[0] # 상위 -> 하위
    try:
        length = len(company)
        index = set(range(length))
        pairs1 = list()
        stack = list()
        for i in range(length):
            if company[i] == '(':
                stack.append(i)
            elif company[i] == ')':
                if stack:
                    pairs1.append((stack.pop(), i))
                else:
                    if pairs1:
                        pairs1.append((pairs1.pop()[0], i))
                    else:
                        pairs1.append((i, i))
        if stack:
            pairs1.append((stack[0], length-1))
        pairs2 = list()
        stack = list()
        for i in range(length):
            if company[i] == '[':
                stack.append(i)
            elif company[i] == ']':
                if stack:
                    pairs2.append((stack.pop(), i))
                else:
                    if pairs2:
                        pairs2.append((pairs2.pop()[0], i))
                    else:
                        pairs2.append((i, i))
        if stack:
            pairs2.append((stack[0], length-1))
        for start, end in pairs1 + pairs2:
            index -= set(range(start, end+1))
        index = list(index)
        index.sort()
        company = ''.join([company[idx] for idx in index])
        # company = company.split('/')[0]
        # company = company.split(',')[0]
        # company = company.split(' ')[0]
        company = company.strip()
    except:
        print(original, '--->', company)
    return company


# In[5]:


def to_datetime(df:pd.DataFrame,col_name:dict):
    _from,_to = [' ','년','월','일'],['','-','-','']
    for i in range(len(_from)):
        df['date'] = df['date'].apply(lambda x:x.replace(_from[i], _to[i]))
    df['contract_date'] = df['date'].apply(lambda x: None if x=='-' else x )
    df['contract_date'] = pd.to_datetime(df['contract_date'])


# ### <span style="background-color:#CEECF5"> 주요사항보고서 </span>

# In[6]:


df_mna_mm = pd.read_csv('./data/mna_api_mainmatter.csv',dtype={'corp_code':object})
col_mm = {'corp_name':'corp','mgptncmp_cmpnm':'partner','mgsc_mgctrd':'date'}


# **필요한 전처리**
# - 하나의 합병회사와 여러개의 피합병회사로 이루어진 경우 처리
# - 피합병회사의 Naming이 지저분하게 되어있는 경우 처리 &rarr; 완료
#     - (주)가 붙어있는 경우 (앞,뒤로)
#     - 주식회사가 붙어있는 경우 (앞,뒤로)
#     - 유한회사가 붙어있는 경우
# - 이상한 형태로 합병상대회사가 들어가있는 경우 처리
#     - 아예 없는 경우
# - '회사명'과 '합병상대회사(회사명)' column이 있는데
#     - 회사명이 꼭 매수회사가 아님. 매도회사가 보고서를 낸 경우도 있음 &rarr; 보류
#     - 일단은 기업간의 관계 고려하지 않고 수집!
#     - 메타 데이터를 Merge해서 Rule-Base Logic을 짜자!
# - 계약일을 기준으로, 같은 날짜에 같은 기업끼리 한 계약인 경우, 중복된 데이터로 판단
#     - 계약일을 datetime 형태로 변환

# - 하나의 합병회사와 여러개의 피합병회사로 이루어진 경우 처리

# In[7]:


df_mna_mm = split_merged_company(df_mna_mm,col_mm)


# - 피합병회사의 Naming이 지저분하게 되어있는 경우 처리 &rarr; 완료
#     - (주)가 붙어있는 경우 
#     - 주식회사가 붙어있는 경우 
#     - 유한회사가 붙어있는 경우

# In[8]:


df_mna_mm['corp'] = df_mna_mm['corp'].apply(filtering_company)
df_mna_mm['partner'] = df_mna_mm['partner'].apply(filtering_company)
drop_list = ['-',"'17. 기타 투자판단에 참고할 사항' 참고하시기 바랍니다.",'본 합병시 합병상대회사','']
for drop in drop_list:
    idxs = df_mna_mm[df_mna_mm['partner']==drop].index
    df_mna_mm = df_mna_mm.drop(idxs,axis=0)
df_mna_mm = df_mna_mm.reset_index(drop=True)


# - 계약일을 datetime 형태로 변환

# In[9]:


to_datetime(df_mna_mm,col_mm)


# In[10]:


idxs = df_mna_mm[df_mna_mm['contract_date'].isna()].index
contract_date_na= df_mna_mm.iloc[idxs].reset_index(drop=True)
df_mna_mm = df_mna_mm.drop(idxs,axis=0).reset_index(drop=True)


# ### <span style="background-color:#CEECF5"> 증권신고서 </span>

# In[11]:


df_mna_scr = pd.read_csv('./data/mna_api_scrits.csv',dtype={'corp_code':object})
col_scr = {'ctrd':'date','corp_name':'corp','cmpnm':'partner'}


# In[12]:


df_mna_scr = split_merged_company(df_mna_scr,col_scr)


# In[13]:


df_mna_scr['corp'] = df_mna_scr['corp'].apply(filtering_company)
df_mna_scr['partner'] = df_mna_scr['partner'].apply(filtering_company)
idxs = df_mna_scr[df_mna_scr['corp']==df_mna_scr['partner']].index
df_mna_scr = df_mna_scr.drop(idxs,axis=0).reset_index(drop=True)


# In[14]:


to_datetime(df_mna_scr,col_scr)


# ### 최종 전처리 완료 데이터

# In[15]:


df_mna = pd.concat([df_mna_mm[['corp','partner','contract_date']],df_mna_scr[['corp','partner','contract_date']]])


# ### <span style="background-color:#CEECF5"> 2018년 인수합병정보 합병정보 </span>

# In[16]:


df_mna_2018 = pd.read_csv('./data/mna_2018.csv',encoding='cp949',parse_dates=['계약일자'],dtype={'종목코드':object})
col_2018 = {'계약일자':'contract_date','회사명':'corp','상대회사업종명':'partner'}
df_mna_2018 = split_merged_company(df_mna_2018,col_2018)
df_mna_2018['corp'] = df_mna_2018['corp'].apply(filtering_company)
df_mna_2018['partner'] = df_mna_2018['partner'].apply(filtering_company)
print(f'2018년 인수합병정보 합병정보데이터: {df_mna_2018.shape[0]}개')


# In[17]:


df_mna = pd.concat([df_mna,df_mna_2018[['corp','partner','contract_date']]])
df_mna = df_mna.drop_duplicates(subset=['corp','partner']).reset_index(drop=True)


# ### <span style="background-color:#CEECF5"> 2019년 인수합병정보 합병정보 </span>

# In[18]:


df_mna_2019 = pd.read_csv('./data/mna_2019.csv',encoding='cp949',parse_dates=['계약일자'],dtype={'종목코드':object})
col_2019 = {'계약일자':'contract_date','회사명':'corp','상대회사업종명':'partner'}
df_mna_2019 = split_merged_company(df_mna_2019,col_2019)
df_mna_2019['corp'] = df_mna_2019['corp'].apply(filtering_company)
df_mna_2019['partner'] = df_mna_2019['partner'].apply(filtering_company)
print(f'2019년 인수합병정보 합병정보데이터: {df_mna_2019.shape[0]}개')


# In[19]:


df_mna = pd.concat([df_mna,df_mna_2019[['corp','partner','contract_date']]])
df_mna['contract_year'] =  df_mna['contract_date'].dt.year


# ### <span style="background-color:#FFE6E6"> 2020년 인수합병 공개매수정보 &rarr; 사용불가 </span>

# In[20]:


df_mna_2020 = pd.read_csv('./data/mna_2020.csv',encoding='cp949',parse_dates=['결정일자'],dtype={'종목코드':object})


# ### <span style="background-color:#FFE6E6"> &rarr; 상대회사가 제대로 나와있지 않아서 활용하기 어려운 데이터 </span>
# - <span style="color:red"> 종목코드도 매수하려는 회사의 종목코드여서 활용 불가 </span>

# ### <span style="background-color:#CEECF5"> M&A 사례 데이터 </span>
# - 국내-국내 데이터만 모아오기

# In[21]:


df_mna_case = pd.read_csv('./data/mna_case_data.csv')
# 국내-국내 기업간 데이터만 filtering
df_mna_case = df_mna_case[df_mna_case['분류명']=='국내-국내(In-In)']
col_case = {'인수합병연도':'contract_year','기업명':'corp','매도기업명':'partner'}
df_mna_case = split_merged_company(df_mna_case,col_case)
df_mna_case['corp'] = df_mna_case['corp'].apply(filtering_company)
df_mna_case['partner'] = df_mna_case['partner'].apply(filtering_company)
df_mna_case['contract_year'] = pd.to_datetime(df_mna_case['contract_year'],format='%Y').dt.year
print(f'M&A 사례 데이터: {df_mna_case.shape[0]}개')


# In[22]:


df_mna = pd.concat([df_mna,df_mna_case[['corp','partner','contract_year']]])
df_mna = pd.concat([df_mna,contract_date_na[['corp','partner']]])
df_mna = df_mna.drop_duplicates(subset=['corp','partner']).reset_index(drop=True)
print(f'중복을 제거하고 2019년 인수합병정보데이터까지 추가한 최종 데이터 개수: {df_mna.shape[0]}개')


# In[23]:


corp_table = pd.read_table('./data/biz2common.tsv')
corp2idx = dict(zip(corp_table['회사명'],corp_table['index']))
df_mna['corp_key'] = df_mna['corp'].map(corp2idx)
df_mna['parter_key'] = df_mna['partner'].map(corp2idx)


# In[24]:


df_mna = df_mna[df_mna['corp_key'].notna() & df_mna['parter_key'].notna()]


# In[25]:


df_mna.to_csv('./data/mna_final.csv',index=False)


# ### <span style="background-color:#CEECF5"> Tech M&A에 해당하는 데이터만 수집 </span>
# #### 주요사항보고서 
# - 주요사항보고서에는 **mgptncmp_rl_cmpn**라는 column이 있어서 확인 가능   
# 
# <img src="attachment:38e72501-6217-45a6-8b7f-246de0cbe8ad.png" width="50%" height="50%">
# 
# - mgptncmp_rl_cmpn : 합병상대회사(회사와의 관계)
#     - 계열사: 어느 한 기업집단에 속한 회사로, 2인 이상의 사업자가 공동의 이익을 목적으로 조직한 결합체. 모 회사의 자본적인 지배관계에 있는 회사는 아니나, 모 회사의 지배구조 안에 있는 회사
#     - 자회사: 다른 회사에 의해 지배, 종속 되고 있는 기업.즉, 자회사는 모 회사에서 출자를 받아서 새로운 회사를 설립한 것 
# 
# #### 2018, 2019년도 인수합병정보 합병정보 데이터
# - **당사자관계구분명**이라는 column이 있어서 확인 가능
# 
# #### 증권신고서
# - **증권신고서에는 해당 column이 없어서 Rule-Based로 가야할 듯**
# 
# #### M&A 사례 데이터
# - **M&A 사례 데이터에는 해당 column이 없어서 Rule-Based로 가야할 듯**

# In[41]:


df_mna_mm['mgptncmp_rl_cmpn'].value_counts()


# In[42]:


df_mna_mm[df_mna_mm['mgptncmp_rl_cmpn']=='자회사']


# In[43]:


df_mna_2018['당사자관계구분명'].value_counts()


# In[44]:


df_mna_2019['당사자관계구분명'].value_counts()


# In[ ]:




