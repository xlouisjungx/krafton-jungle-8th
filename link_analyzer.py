import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

#trouble shooting => beautiful soup로는 동적인 요소 로드 불가능 => selenium활용
def analyze_link(url):
    try:
        if 'http' in url:
            url = url.split('http')[1]
            url = 'http' + url
            
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")  # 브라우저 창을 띄우지 않고 실행 => 렌더링 문제로 띄우게 함.
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        place_data = {
            'title' : "",
            'place' : "",
            'phone_number' : ""
        }
        # 링크가 다른 화면으로 리다이렉트 되는 경우 고려
        driver.get(url)
        time.sleep(2)
        current_url = driver.current_url

        # 페이지 로딩 후 HTML 가져오기
        # 원하는 요소 선택
            if "kakao" in current_url:
                after_place = ''
                if 'item' in current_url:
                    after_place = current_url.split("itemId=")[1]
                    new_url = 'https://place.map.kakao.com/' + after_place
                else:
                    new_url=current_url
                driver.get(new_url)
                time.sleep(2)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                place_data = kakao_analyzer(soup)
            #네이버는 html안에 또 다른 html이 있음
            elif "naver" in current_url:
                after_place = ''
                if 'restaurant' in current_url:
                    after_place = current_url.split("restaurant/")[1]
                elif 'place' in current_url:
                    after_place = current_url.split("place/")[1]
                base_url = 'https://pcmap.place.naver.com/restaurant/' + after_place
                driver.get(base_url)
                time.sleep(2)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                place_data = naver_analyzer(soup)
            else:
                place_data = other_analyzer(soup)
    except:
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
    place = soup.select_one('#mainContent > div.main_detail.home > div.detail_cont > div.section_comm.section_defaultinfo > div.default_info > div:nth-child(1) > div > div:nth-child(1) > span').string.strip()
    phone_number = soup.select_one('#mainContent > div.main_detail.home > div.detail_cont > div.section_comm.section_defaultinfo > div.default_info > div:nth-child(3) > div > div > span').string.strip()

    place_data = place_data_changer(title, place, phone_number)
    return place_data

def naver_analyzer(soup):
    title = soup.select_one('#_title > div > span.GHAhO').string.strip()
    place = soup.select_one('#app-root > div > div > div > div:nth-child(5) > div > div:nth-child(2) > div > div > div.O8qbU.tQY7D > div > a > span.LDgIH').string.strip()
    phone_number = soup.select_one('#app-root > div > div > div > div:nth-child(5) > div > div:nth-child(2) > div > div > div.O8qbU.nbXkr > div > span.xlx7Q').string.strip()

    place_data = place_data_changer(title, place, phone_number)
    return place_data

def other_analyzer(soup):
    i

