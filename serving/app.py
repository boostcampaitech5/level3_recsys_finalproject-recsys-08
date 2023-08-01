import streamlit as st
import pandas as pd
import numpy as np
from streamlit_elements import elements, mui, dashboard
import os
from google.cloud import storage
import unicodedata
from datetime import timedelta
from google.cloud.sql.connector import Connector
import sqlalchemy
import pymysql.cursors
import time 
import socket
import json

# delete HOST & PORT 
HOST = '0.0.0.0' 
PORT = 0

if 'flag' not in st.session_state:
    st.session_state.flag  = True

if st.session_state.flag:
    st.session_state.flag = False
    clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSock.connect((HOST, PORT))

    sendData = dict()
    sendData['transformer_version'] = 'version1'
    sendData['ann_version'] = 'version1'
    sendData['valuation_version'] = 'version1'

    clientSock.send(json.dumps(sendData).encode('utf-8'))
    recvData = clientSock.recv(1024).decode('utf-8')
    print(recvData, st.session_state.flag)

    clientSock.close()

# delete GCS info
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './gcs-key.json'
bucket_name = 'gcs-bucket'
storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)

# delete CloudSQL info
data_path = '.'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './sql-key.json'
connector = Connector()
def getconn():
    conn = connector.connect(
        'sql-info',
        'pymysql',
        user='user-name',
        password='password',
        db='db-name'
    )
    return conn
pool = sqlalchemy.create_engine('mysql+pymysql://', creator=getconn)
db_conn = pool.connect()

@st.cache_data
def load_sql(query):
    result = db_conn.execute(sqlalchemy.text(query)).fetchall()  # company, company_img
    return result

@st.cache_data
def load_img(corp_name):
    file_name = unicodedata.normalize('NFD', corp_name)
    source_blob_name = f'imgs/{file_name}.jpg'
    blob = bucket.blob(source_blob_name)
    return blob.generate_signed_url(version='v4', expiration=timedelta(1), method='GET')

# css
streamlit_style = '''
    <style>
		html, body, [class*="css"], iframe {
            text-align:center;
		}
        .stButton{
            margin-top:1rem;
        }
        .row-widget{
            font-size:3rem;
        }
        button[kind='secondary']{
            width:70%;
            border-radius:10rem;
            padding:1rem;
            background-color:#3563E9;
            color:#ffffff;
        }
        img{
            object-fit: contain;
        }
        .MuiAccordionSummary-contentGutters{
            display:flex;
            flex-direction:row;
            align-items:center;
        }
        
    </style>
'''

st.markdown(streamlit_style, unsafe_allow_html=True,)

st.title('EXIT')
st.divider()

with elements('multiple_childeren'):
    b_num = st.text_input("사업자 번호를 입력하세요 👇",
                        label_visibility='visible',
                        disabled=False,
                        placeholder='- 부호를 포함하여 입력하세요')

    p_sec = st.text_input("선호하는 업종 키워드를 입력하세요 👇",
                        label_visibility='visible',
                        disabled=False,
                        placeholder='상세하게 입력할수록 추천 성능이 좋아집니다 🤗')

    if st.button('추천 결과 확인하기', key='start'):
        clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSock.connect((HOST, PORT))

        sendData = dict()
        sendData['business_number'] = str(b_num)
        clientSock.send(json.dumps(sendData).encode('utf-8'))

        recvData = clientSock.recv(2048).decode('utf-8')
        recvData = recvData.split()
        client = recvData[:4] # 회사명, 기업가치, index, biz_number
        targets = [recvData[i*4:(i+1)*4] for i in range(1, len(recvData) // 4)]
        print(len(client))
        print(len(targets))
        clientSock.close()
        
        user_corp = client[0]
        with mui.Box(sx={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center','p': 3}):
            mui.CardMedia(component='img', sx={'height': 0.5, 'width': 0.5, 'border-radius': 10, 'object-fit': 'cover', 'overflow': 'hidden', 'mb': '1rem'} ,
                          src=load_img(user_corp))
            with mui.Box(sx={'display': 'flex'}):
                mui.Typography(f'{user_corp}', sx={'color': '#3563E9', 'fontSize': 25, 'fontWeight':'bold'})
                mui.Typography('님,', sx={'fontSize': 25})
            mui.Typography(f'기업파트너를 추천드립니다.', sx={'fontSize': 20})
            mui.Typography(f'귀사의 기업 가치는 {format(abs(int(float(client[1]))), ",")} 원입니다.', sx={'fontSize': 15})

        st.divider()

        reco_result = tuple()
        for i, r in enumerate(targets):
            # reco_result = reco_result + (r[2],)
            reco_result = reco_result + (r[3],)

        with elements("multiple_children"):
            # corp_patent = load_sql(f'SELECT * FROM patent_temp WHERE index IN {reco_result};')
            # corp_patent = load_sql(f'SELECT * FROM patent_temp WHERE 사업자번호 IN {reco_result};')
            # cp = pd.DataFrame(corp_patent)
            for i, corp in enumerate(targets): # 회사명, 기업가치, index, biz_number
                print(i)
                if corp[1] == 'nan':
                    value = '평가불가'
                else:
                    value = f'{format(abs(int(corp[1].split(".")[0])), ",")}원'
                if i == 10: break
                with mui.Accordion(key=corp[0], elevation=3, sx={'display': 'block', 'borderRadius': 3, 'p': 1}):
                    with mui.AccordionSummary(id='card-header', area='patent', expandIcon='▼', sx={'display':'flex', 'flexDirection':'row', 'height': 0.7, 'justifyContent': 'center', 'alignItems': 'center', 'borderRadius': 3}):
                        with mui.Box(sx={'display':'flex', 'flexDirection':'row', 'align-items':'center', 'width':1, 'height':1}):
                            with mui.Box(sx={'display':'flex', 'flexDirection':'row', 'align-items': 'center', 'justify-content': 'center', 'width': 1/8, 'height': 1}):
                                mui.Typography(f'{i+1}', sx={'text-align':'center', 'vertical-align':'middle', 'color': '#3563E9', 'fontSize': 40, 'fontWeight': 'bold'})
                            with mui.Box(sx={'display': 'flex', 'flexDirection': 'row', 'alig-items': 'center', 'justify-content': 'center', 'width': 2/8, 'height': 1}):
                                prev = time.time()
                                mui.CardMedia(component='img', sx={'height': 1, 'width': 0.8, 'border-radius': 10, 'object-fit': 'cover', 'overflow':'hidden'},
                                            src=load_img(corp[0]))

                            with mui.Box(sx={'display': 'flex', 'justifyContent': 'center', 'width': 6/16, 'height': 1, 'flexDirection': 'column', 'ml': 2}):
                                mui.Typography(f'{corp[0]}', sx={'fontSize': 25, 'fontWeight': 'bold'})
                                mui.Typography(f"{corp[3]}", sx={'fontSize': 12, 'fontWeight': 'light', 'mb': 2})
                                mui.Typography(f'예상 기업 가치', sx={'fontSize': 12, 'fontWeight': 'light'})
                                mui.Typography(value, sx={'fontSize': 20})
                        # with mui.Box(sx={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'alignItems': 'center', 'width': 3/16, 'height': 1}):
                        #     mui.Typography(f'추천 스코어', sx={'fontSize': 15, 'fontWeight': 'light'})
                        #     mui.Typography(f'{r["추천스코어"]}', sx={'fontSize': 30, 'fontWeight': 'bold'})
                    with mui.AccordionDetails():
                        mui.Divider(sx={'margin':2})
                        # patent = cp[cp['index'] == (corp[2])]
                        # patent = cp[cp['사업자번호'] == corp[3]]
                        patent = pd.DataFrame(load_sql(f'SELECT * FROM patent_temp WHERE 사업자번호 = "{corp[3]}" limit 3;'))
                        # mui.Typography(f'특허 총 {len(corp_patent)}개', sx={'fontSize': 25, 'fontWeight': 'bold'})
                        c = 0
                        for i_p, p in patent.iterrows():
                            c += 1
                            if c == 3:
                                break
                            if i_p == 3: 
                                break
                            with mui.Box(sx={'margin':2}):
                                mui.Typography(p['출원번호'], sx={'fontSize': 12})
                                mui.Typography(p['발명의명칭'], sx={'fontSize': 20, 'fontWeight': 'bold'})
                                mui.Typography(p['summarized_abstract'], sx={'fontSize': 12})