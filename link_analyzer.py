import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

#우분투 서버 로그 분석기
from logger import logger

#trouble shooting => beautiful soup로는 동적인 요소 로드 불가능 => selenium활용
def analyze_link(url):
    print('test')
    try:
        if 'http' in url:
            url = url.split('http')[1]
            url = 'http' + url
            
        options = webdriver.ChromeOptions()
        # 과도한 요청으로 인한 접속 불가 => User Agent 추가
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        # 브라우저 창을 띄우지 않고 실행 => 렌더링 문제로 띄우게 함.
        options.add_argument("--headless")  
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        place_data = {
            'title' : "",
            'place' : "",
            'phone_number' : ""
        }
        # 링크가 다른 화면으로 리다이렉트 되는 경우 고려
        driver.get(url)
        time.sleep(3)
        current_url = driver.current_url

        # 페이지 로딩 후 HTML 가져오기
        # 원하는 요소 선택
        if "kakao" in current_url:
            first_cut = ''
            if 'item' in current_url:
                first_cut = current_url.split("itemId=")[1]
                new_url = 'https://place.map.kakao.com/' + first_cut
            else:
                new_url=current_url
            driver.get(new_url)
            time.sleep(4)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            place_data = kakao_analyzer(soup)
        #네이버는 html안에 또 다른 html이 있음
        elif "naver" in current_url:
            first_cut = ''
            if 'restaurant' in current_url:
                first_cut = current_url.split("restaurant/")[1]
                second_cut = first_cut.split("?")[0]
            elif 'place' in current_url:
                first_cut = current_url.split("place/")[1]
                second_cut = first_cut.split("?")[0]
            base_url = 'https://pcmap.place.naver.com/restaurant/' + second_cut
            driver.get(base_url)
            time.sleep(4)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            place_data = naver_analyzer(soup)
        else:
            place_data = other_analyzer(soup)
    except Exception as e:
        logger.info(e)
        place_data = None

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
    place = soup.select_one('#mainContent > div.main_detail.home > div.detail_cont > div.section_comm.section_defaultinfo > div.default_info > div:nth-child(1) > div > div:nth-child(1) > span')
    phone_number = soup.select_one('#mainContent > div.main_detail.home > div.detail_cont > div.section_comm.section_defaultinfo > div.default_info > div:nth-child(3) > div > div > span')

    if place:
        place = place.string.strip()
    if phone_number:
        phone_number = phone_number.string.strip()

    place_data = place_data_changer(title, place, phone_number)
    return place_data

def naver_analyzer(soup):
    title = soup.select_one('#_title > div > span.GHAhO')
    place = soup.select_one('#app-root > div > div > div > div:nth-child(5) > div > div:nth-child(2) > div > div > div.O8qbU.tQY7D > div > a > span.LDgIH')
    phone_number = soup.select_one('#app-root > div > div > div > div:nth-child(5) > div > div:nth-child(2) > div > div > div.O8qbU.nbXkr > div > span.xlx7Q')

    if title:
        title = title.string.strip()
    if place:
        place = place.string.strip()
    if phone_number:
        phone_number = phone_number.string.strip()

    place_data = place_data_changer(title, place, phone_number)
    return place_data

def other_analyzer(soup):
    i

