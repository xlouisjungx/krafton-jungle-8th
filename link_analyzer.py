import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

#trouble shooting => beautiful soup로는 동적인 요소 로드 불가능 => selenium활용
def analyze_link(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 브라우저 창을 띄우지 않고 실행
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(url)
    time.sleep(1)

    # 페이지 로딩 후 HTML 가져오기
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # 원하는 요소 선택


    driver.quit()

def kakao_finder(soup):
    title_tag = soup.find('meta', {'property': 'og:title'})
    title = ''
    if title_tag:
        title = title_tag.get('content')
    place = soup.select_one('#mainContent > div.main_detail.home > div.detail_cont > div.section_comm.section_defaultinfo > div.default_info > div:nth-child(1) > div > div:nth-child(1) > span').string.strip()
    work_day = soup.select('#foldDetail2 > .line_fold > .tit_fold')
    work_time = soup.select('#foldDetail2 > .line_fold > div > span')
    for i in range(len(work_day)):
      work_day[i] = work_day[i].string.strip()
      work_time[i] = work_time[i].string.strip()
    phone_number = soup.select_one('#mainContent > div.main_detail.home > div.detail_cont > div.section_comm.section_defaultinfo > div.default_info > div:nth-child(3) > div > div > span').string.strip()

def naver_finder():
    i

def google_finder():
    i

input_url = input()
analyze_link(input_url)