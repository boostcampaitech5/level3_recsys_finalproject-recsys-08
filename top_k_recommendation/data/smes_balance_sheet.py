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

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
service = ChromeService(ChromeDriverManager("114.0.5735.16").install())
driver = webdriver.Chrome(
    service=service,
    options=options,
)

file_path = "./company.json"
with open(file_path, "r") as file:
    companies = json.load(file)

companies_js = defaultdict(dict)
company_keys = list(companies.keys())
n = len(company_keys)
for company in tqdm(company_keys):
    link = companies[company]
    try:
        driver.get(url=link)
        time.sleep(0.1)
        # 일반정보 페이지
        saup = driver.find_element(
            By.XPATH,
            '//*[@id="real_contents"]/div/div[1]/div[1]/table/tbody/tr[4]/td[1]',
        ).text
        companies_js[company]["사업자번호"] = saup

        ## 재무정보 > 대차대조표 페이지 이동
        driver.find_element(By.XPATH, '//*[@id="real_contents"]/div/ul/li[2]/a').click()
        time.sleep(0.2)
        # 마지막 연도
        latest_year = driver.find_element(
            By.XPATH,
            '//*[@id="real_contents"]/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div[1]/table/thead/tr/th[2]',
        ).text
        companies_js[company]["latest_year"] = latest_year

        for j in range(57):
            col = driver.find_element(
                By.XPATH,
                f'//*[@id="real_contents"]/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div[1]/table/tbody/tr[{j+1}]/th',
            ).text
            data = []
            for i in range(3):
                data.append(
                    driver.find_element(
                        By.XPATH,
                        f'//*[@id="real_contents"]/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div[1]/table/tbody/tr[{j+1}]/td[{i+1}]',
                    ).text
                )
            companies_js[company][col] = data

        for j in range(27):
            col = driver.find_element(
                By.XPATH,
                f'//*[@id="real_contents"]/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div[2]/table/tbody/tr[{j+1}]/th',
            ).text
            data = []
            for i in range(3):
                data.append(
                    driver.find_element(
                        By.XPATH,
                        f'//*[@id="real_contents"]/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div[2]/table/tbody/tr[{j+1}]/td[{i+1}]',
                    ).text
                )
            companies_js[company][col] = data
        print(companies_js[company])
    except NoSuchElementException:
        pass

with open("companies_info.json", "w") as f:
    json.dump(companies_js, f, ensure_ascii=False)