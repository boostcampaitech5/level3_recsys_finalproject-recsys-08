import glob
import pandas as pd
import re

def preprocess(filename,to_find):
    f = open(filename,'r',encoding='cp949')
    lines = f.readlines()
    header = lines[0].split()
    df_bs = pd.DataFrame(columns = header[:13])
    report_code = {'1분기보고서':'11013', '반기보고서':'11012','3분기보고서': '11014','사업보고서': '11011'}
    for line in lines[1:]:
        data = line.strip().split('\t')[:13]
        data[1] = re.sub('[^0-9]','',data[1])
        data[-1] = re.sub('[^0-9]','',data[-1])
        data[11] = data[11].strip()
        if data[11] == to_find:
            df_bs.loc[df_bs.shape[0]+1] = data
    df_bs['year'] = df_bs['결산기준일'].apply(lambda x:x[:4])
    df_bs['report_code'] = df_bs['보고서종류'].map(report_code)
    f.close()
    return df_bs

def preprocess(filename):
    f = open(filename,'r',encoding='cp949')
    lines = f.readlines()
    header = lines[0].split()
    df_bs = pd.DataFrame(columns = header[:13])
    report_code = {'1분기보고서':'11013', '반기보고서':'11012','3분기보고서': '11014','사업보고서': '11011'}
    for line in lines[1:]:
        data = line.strip().split('\t')[:13]
        data[1] = re.sub('[^0-9]','',data[1])
        data[-1] = re.sub('[^0-9]','',data[-1])
        data[11] = data[11].strip()
        # if data[11] == to_find:
        #     df_bs.loc[df_bs.shape[0]+1] = data
    df_bs['year'] = df_bs['결산기준일'].apply(lambda x:x[:4])
    df_bs['report_code'] = df_bs['보고서종류'].map(report_code)
    f.close()
    return df_bs

def get_file(opt):
    file_path = "./data/**/*"+ opt +"_[0-9]*.txt"
    file_path_quarter = glob.iglob(file_path,recursive=True)
    first = True
    if opt == '재무상태표':
        to_find = '현금및현금성자산'
    elif opt == '현금흐름표':
        to_find = '감가상각비'
    for file in file_path_quarter:
        if file.endswith()
        preprocess(file)
        if first:
            df = preprocess(file,to_find)
            first = False
        else:
            df_per_file = preprocess(file,to_find)
            df = pd.concat([df,df_per_file])
        print('*'*50+'Done Preprocessing'+'*'*50)
    df.to_csv('./data/'+opt+'_통합본.csv',index=False)


get_file('재무상태표')
get_file('현금흐름표')

