# 작성자 이홍주
# 
#

from src.pages.chat_basic import chat_basic
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import pytest
import time
from time import sleep
import pyperclip






def test_chat_basic_001(driver, login):# 채팅 입력, 정상 실행 
    login("team4b@elice.com", "team4belice!@!")

    chat = chat_basic(driver)

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'textarea:not([aria-hidden="true"])')
        )
    )
    #response_text = chat.send_message(" ")
    response_text = chat.send_message("자기소개를 부탁해")

    assert len(response_text) > 0
    print(f"✅ Helpy 응답: {response_text}")

    
    

        
"""
def test_chat_basic_002(driver):#파일 업로드, 추후 구현

def test_chat_basic_003(driver):


def test_chat_basic_004(driver):# 클립보드, 정상 실행 
    chat = chat_basic(driver)

    chat.click_clipboard()

    sleep(1)

    copied_text = pyperclip.paste()
    if copied_text.strip():
        print("✅ 클립보드에 내용이 복사되었습니다.")
    else:
        print("❌ 클립보드가 비어 있습니다!")
        assert False, "클립보드에 내용이 없습니다!"


def test_chat_basic_005(driver):# 도움됨 클릭 후 피드백 입력 및 전송, 도움됨 버튼까지 정상작동

    chat = chat_basic(driver)

    chat.click_thumbs_up()

    sleep(1)


def test_chat_basic_006(driver):# 도움 안됨 클릭후 피드백 입력 및 전송, 도움 안됨 버튼까지 정상작동

    chat = chat_basic(driver)

    chat.click_thumbs_down()

def test_chat_basic_007(driver):# 이미 입력한 채팅 수정, 수정버튼 인식 불량
    sleep(5)
    chat = chat_basic(driver)
    chat.click_edit()
    chat.send_edit("사과")
    chat.click_edit()


def test_chat_basic_008(driver): # 채팅 수정 선택했다 취소하기, 취소버튼 인식 불량
    chat = chat_basic(driver)
    chat.click_edit()
    chat.send_edit("사과")
    chat.click_edit()


def test_chat_basic_009(driver): 스크롤바 기능 확인 1
    chat = chat_basic(driver)

    chat.send_message("오늘 날짜를 알려줘")

    chat.scroll_bar()
def test_chat_basic_010(driver): 스크롤바 기능 확인 2




def test_chat_basic_011(driver): # 초기화 버튼, 정상 실행
    chat = chat_basic(driver)

    chat.reset_chat()
    #sleep(20)


def test_chat_basic_012(driver):# 채팅 성능 테스트, 정상 실행
    chat = chat_basic(driver)

    #WebDriverWait(self, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea:not([aria-hidden="true"])')))

    chat.send_message_timer("자기소개를 부탁해")
    WebDriverWait(driver, 10)

"""
def test_chat_basic_013(driver): # 스크립트 입력, 정상 실행
    chat = chat_basic(driver)

    chat.open_chat()

    response_text = chat.send_message("<script>alert('XSS')</script>")

    assert len(response_text) > 0
    print(f"✅ Helpy 응답: {response_text}")

"""
def test_chat_basic_014(driver): # 비정상 채팅 입력, 정상 실행
    chat = chat_basic(driver)

    response_text = chat.send_message("ㅑㄴ루ㅏ두ㅐㄴ")

    assert len(response_text) > 0
    print(f"✅ Helpy 응답: {response_text}")


def test_chat_basic_015(driver): # 스페이스바만 입력, 실행은 정상, 성공 확인여부 수정 필요
    chat = chat_basic(driver)

    response_text = chat.send_message(" ")

    assert len(response_text) > 0
    print(f"✅ Helpy 응답: {response_text}")

"""
