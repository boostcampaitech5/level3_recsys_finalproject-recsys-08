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
    if key == 'corpType':
        if 'corpType' not in data:
            data[key] = []
        data[key].append(value)
    else:
        data[key] = None if value == '' else value

label_text = {
    'LA': '주식의_총수_현황', 
    'L': '자기주식_취득_및_처분_현황',
    'D': '배당에_관한_사항', 
    'E': '증자_감자_현황', 
    'RA': '채무증권_발행실적', 
    'RB': '기업어음증권_미상환_잔액', 
    'RC': '단기사채_미상환_잔액', 
    'RD': '회사채_미상환_잔액', 
    'RE': '신종자본증권_미상환_잔액', 
    'RF': '조건부_자본증권_미상환_잔액', 
    'VA': '공모자금의_사용내역', 
    'VB': '사모자금의_사용내역', 
    'SA': '회계감사인의_명칭_및_감사의견', 
    'SB': '감사용역_체결현황', 
    'SC': '회계감사인과의_비감사용역_계약체결_현황',
    'TA': '사외이사_및_그_변동현황', 
    'C': '최대주주_현황', 
    'M': '최대주주_변동현황', 
    'N': '소액주주_현황', 
    'K': '임원_현황', 
    'B': '직원_현황', 
    'U': '미등기임원_보수현황', 
    'OA': '이사_감사_전체의_보수현황_주주총회_승인금액', 
    'O': '이사_감사_전체의_보수현황_보수지급금액_이사_감사_전체', 
    'OB': '이사_감사_전체의_보수현황_보수지급금액_유형별', 
    'A': '이사_감사의_개인별_보수현황_5억원_이상',
    'P': '개인별_보수지급금액_5억원_이상_상위_5인',
    'Q': '타법인_출자현황'
    }


select_year = ['2019', '2020', '2021', '2022', '2023']
report_code = ['11013', '11012', '11014', '11011']

for key, value in label_text.items():
    df = pd.DataFrame()
    data['gubun'] = key
    print(key, value)
    for year in select_year:
        for code in report_code:
            print(f"{year}-{code}")
            data['selectYear'] = year
            data['reportCode'] = code
            page = 1
            while True:
                data['pageIndex'] = str(page)
                response = requests.post(url, data=data)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 페이지 정보 추출
                page_info = soup.select_one('.page_info').text.strip()
                current_page = int(page_info.split('/')[0].strip('['))
                total_pages = int(page_info.split('/')[1].split(']')[0])

                temp = soup.find_all('table','tb_result')
                p = parser.make2d(temp[0])
                # print(temp)
                # print("-----------------------------------")
                # print(p)

                # if p[:][0] == '회사명':
                #     p[1] = p[1][1:]
                # if len(p) > 2:
                #     print(p[2])
                #     if len(p[2]) > 1:
                #         if p[2][0] == '회사명':
                #             p[2] = p[2][1:]
                
                for i in range(len(p)):
                    if i == 0:
                        continue
                    if len(p[i]) > len(p[0]):
                        if len(p[i]) > 1:
                            p[i] = p[i][1:]
    
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

            df = pd.concat([df, temp_df], ignore_index = True)

    df.to_csv(f'./data/{value}.csv', index=False)
