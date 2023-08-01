import pandas as pd

df_bs = pd.read_csv("./data/재무상태표_통합본.csv")
df_cf = pd.read_csv("./data/현금흐름표_통합본.csv")

df_bs[['year','report_code']] = df_bs[['year','report_code']].astype(int)
df_cf[['year','report_code']] = df_cf[['year','report_code']].astype(int)

df_bs = df_bs[df_bs['재무제표종류']=='재무상태표, 유동/비유동법-별도재무제표']
df_cf = df_cf[df_cf['재무제표종류']=='현금흐름표, 간접법 - 별도재무제표']

df_bs = df_bs.groupby(['회사명','시장구분','year','report_code']).apply(lambda x:x.sort_values(by='결산기준일')).drop(['회사명','시장구분','year','report_code'],axis=1).reset_index()
df_bs = df_bs.drop_duplicates(subset = ['회사명','시장구분','year','report_code'],keep='last')

df_cf = df_cf.groupby(['회사명','시장구분','year','report_code']).apply(lambda x:x.sort_values(by='결산기준일')).drop(['회사명','시장구분','year','report_code'],axis=1).reset_index()
df_cf = df_cf.drop_duplicates(subset = ['회사명','시장구분','year','report_code'],keep='last')

def select_column(df,opt):
    if opt == 0:
        prefix = '재무상태표_'
    elif opt == 1:
        prefix = '현금흐름표_'
    df['법인유형'] = df['시장구분'].apply(lambda x:x[:-6])
    df = df[['회사명','법인유형','year','report_code','업종','업종명','결산월','당기']]
    mapping_dict = {}
    for col in df.columns[4:-1]:
        new_col = prefix + col
        mapping_dict[col] = new_col
    return df,mapping_dict

df_bs,dic_bs = select_column(df_bs,0)
dic_bs['당기'] = '재무상태표_현금_및_현금성자산'
df_bs.rename(columns=dic_bs,inplace=True)
df_bs.to_csv('./dart_data/Dart_재무상태표.csv',index=False)

df_cf,dic_cf = select_column(df_cf,1)
dic_cf['당기'] = '현금흐름표_감가상각비'
df_cf.rename(columns=dic_cf,inplace=True)
df_cf.to_csv('./dart_data/Dart_현금흐름표.csv',index=False)

