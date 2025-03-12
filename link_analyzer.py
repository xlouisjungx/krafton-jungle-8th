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

    place_data = {
        'title' : "",
        'place' : "",
        'phone_number' : ""
    }

    # 페이지 로딩 후 HTML 가져오기
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # 원하는 요소 선택
    if "kakao" in url:
        place_data = kakao_analyzer(soup)
    elif "google" in url:
        place_data = google_analyzer(soup)
    else:
        place_data = other_analyzer(soup)

    driver.quit()
    return place_data

def place_data_changer(title, place, phone_number):
    place_data = {
        'title' : "",
        'place' : "",
        'phone_number' : ""
    }
    place_data['title'] = title
    place_data['place'] = place
    place_data['phone_number'] = phone_number

    return place_data

def kakao_analyzer(soup):
    title_tag = soup.find('meta', {'property': 'og:title'})
    title = ''
    if title_tag:
        title = title_tag.get('content')
    place = soup.select_one('#mainContent > div.main_detail.home > div.detail_cont > div.section_comm.section_defaultinfo > div.default_info > div:nth-child(1) > div > div:nth-child(1) > span').string.strip()
    phone_number = soup.select_one('#mainContent > div.main_detail.home > div.detail_cont > div.section_comm.section_defaultinfo > div.default_info > div:nth-child(3) > div > div > span').string.strip()

    place_data = place_data_changer(title, place, phone_number)
    return place_data

def google_analyzer(soup):
    i

def other_analyzer(soup):
    i

