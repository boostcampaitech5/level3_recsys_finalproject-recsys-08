import os

import requests
from bs4 import BeautifulSoup
from html_table_parser import parser_functions as parser
import pandas as pd

# 필요에 맞게 url 추가
url = ''

lines = ''''''.splitlines()

data = dict()
for line in lines:
    key, value = line.replace(' ', '').split(':')
    if key == 'accountGubun':
        if 'accountGubun' not in data:
            data[key] = []
        data[key].append(value)
    else:
        data[key] = None if value == '' else value
print(data)
select_year = ['2019', '2020', '2021', '2022', '2023']
report_code = ['11013', '11012', '11014', '11011'] # 1분기, 반기, 3분기, 사업보고서
select_toc = ['0', '5']

for toc in select_toc:
    df = pd.DataFrame()
    for year in select_year:
        print(f'{toc}-{year}')
        for code in report_code:
            data['selectYear'] = year
            data['reportCode'] = code
            page = 1
            while True:
                data['pageIndex'] = str(page)
                response = requests.post(url, data=data)
                soup = BeautifulSoup(response.text, 'html.parser')

                # 표(table) 추출
                temp = soup.find_all('table','tb_result')
                p = parser.make2d(temp[0])

                # 데이터 추출
                page_info = soup.select_one('.page_info').text.strip()
                current_page = int(page_info.split('/')[0].strip('['))
                total_pages = int(page_info.split('/')[1].split(']')[0])

                # DataFrame 생성
                if current_page == 1:
                    temp_df = pd.DataFrame(p[1:], columns=p[0])
                else:
                    temp_df = pd.concat([temp_df, pd.DataFrame(p[1:], columns=p[0])], ignore_index=True)

                # 다음 페이지로 이동할지 확인
                if current_page == total_pages:
                    break

                page += 1

            temp_df['year'] = year
            temp_df['report_code'] = code

            df = pd.concat([df, temp_df], ignore_index=True)
            print(df.head())

    if toc == '0':
        df.to_csv(f'./data/요약연결재무제표.csv', index=False)
    else:
        df.to_csv(f'./data/요약재무제표.csv', index=False)
