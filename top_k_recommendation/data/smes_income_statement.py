from selenium.common.exceptions import NoSuchElementException
from collections import defaultdict
from tqdm import tqdm
import time
import json

# selenium 4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


file_path = '../../smes_data/company.json'
with open(file_path, 'r') as file:
    companies = json.load(file)


options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
# options.add_argument("--single-process")
# options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager("114.0.5735.16").install()), options=options)

companies_js = defaultdict(dict)
company_keys = list(companies.keys())
n = len(company_keys)
for company in tqdm(company_keys):
    link = companies[company]
    try:
        driver.get(url=link)
        time.sleep(0.1)

        ## 재무정보 > 대차대조표 페이지 이동
        driver.find_element(By.XPATH, '//*[@id="real_contents"]/div/ul/li[2]/a').click()
        time.sleep(0.1)

        ## 재무정보 > 손익계산서 페이지 이동
        driver.find_element(By.XPATH, '//*[@id="real_contents"]/div/div[1]/div[2]/ul/li[2]/a').click()
        time.sleep(0.1)
        
        # 마지막 연도 
        latest_year = driver.find_element(By.CSS_SELECTOR,'#real_contents > div > div.board_tab_con_box > div:nth-child(2) > div > div:nth-child(2) > div:nth-child(2) > table > thead > tr > th:nth-child(2)').text
        companies_js[company]['latest_year'] = latest_year
        
        # 손익계산서 
        columns = driver.find_elements(By.XPATH,f'//*[@id="real_contents"]/div/div[1]/div[2]/div/div[2]/div[2]/table/tbody/tr/th')
        for i in range(len(columns)):
            col_name = columns[i].text
            data = []
            for j in range(3):
                data.append(driver.find_element(By.XPATH, f'//*[@id="real_contents"]/div/div[1]/div[2]/div/div[2]/div[2]/table/tbody/tr[{i+1}]/td[{j+1}]').text)
            companies_js[company][col_name] = data
        print(companies_js[company])
    except NoSuchElementException:
        pass

with open('companies_info_first.json', 'w') as f:
    json.dump(companies_js, f, ensure_ascii = False)

