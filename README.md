# 안녕하세요, Recsys 8조 EXIT입니다.
* 최근 기술 산업 시장은 기술 확장을 위해 MOU 를 체결하거나 M&A 하는 경향성을 보이고 있습니다. EXIT는 기술적 성장을 도모하는 기업을 위해 전략적 파트너 기업을 추천하는 서비스입니다. 의뢰 기업의 과거 특허 데이터를 기반으로, 미래에 출원할 특허를 예측하고 그와 유사한 특허 양상을 지닌 기업들을 추천합니다. 인공지능 모델을 도입하여 파트너 기업 선정 시 불필요하게 사용되는 시간 및 인력을 줄이고자 서비스를 기획하였습니다. 

## 서비스 파이프라인
* 같은 맥락에서 바로, End to End 구성부터 소개드리겠습니다. User와 상호작용하는 웹의 경우 Streamlit 으로 구현하였고, 이를 Dockerize 하여 GCP의 Cloud Run을 통해 배포하였습니다. 데이터의 경우 GCP의 CloudSQL에서 제공하는 MySQL 데이터베이스와 Google Cloud Storage를 통해 관리하여 필요한 시점에 필요한 데이터를 로딩하여 사용했습니다. 마지막으로, GPU를 활용해 Inference 속도를 줄이고자 Inference는 V100 서버에서 이루어졌으며, 해당 과정에서 소켓 통신을 활용했습니다.

## 모델 파이프라인
1. Business Embedding
    * 특허 데이터와 기업 업종 데이터를 이용하여 각 기업의 기술력을 임베딩 벡터로 표현하는 Business Embedding 입니다. summarization, sentence embedding, retrieval 과정을 거쳐서 하나의 상장기업에 대해 기술적으로 유사한 기업들을 매핑한 결과를 도출합니다.
2. Enterprise Valuation
    * 시장 내 기업의 상대적 위치를 파악하고, 기술의 유효성을 정량평가할 수 있는 지표인 기업 가치를 예측하여 의뢰 기업에게 설득의 근거로 작용하는 것을 목표로 합니다.
3. Top-K Recommendation
    * 의뢰기업의 과거 특허 데이터를 이용해 다음으로 낼 특허를 예측하여 유사한 특허를 보유하고 있는 기업을 대상으로, Ordering & Filtering 단계를 거쳐서 선정된 상위 K개의 기업을 최종적으로 전략적 파트너로 추천합니다.

## 역할
* 김지우 : Top-K Recommendation 구현, 데이터 크롤링 및 전처리 업무를 수행
* 박수현 : Product Manager 및 Business Embedding을 구현
* 석예림 : Top-K Recommendation 구현, 데이터 크롤링 및 전처리 업무를 수행
* 임소영 : Enterprise Valuation 구현, Streamlit을 개발
* 전증원 : Enterprise Valuation 구현, Database 를 구축 


## 7월 31일(월) 마무리 예정입니다!



