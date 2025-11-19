#작성자 이홍주

from src.pages.chat_page import chat_basic
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pyperclip




'''
def test_chat_basic_001(driver, login):# 채팅 입력, 정상 실행 

    chat = chat_basic(driver)
    chat.open_chat(login)

    response_text = chat.send_message("자기소개를 부탁해")

    assert len(response_text) > 0
    print(f"✅ Helpy 응답: {response_text}")
  

def test_chat_basic_002(driver, login):#파일 업로드
    chat = chat_basic(driver)
    chat.open_chat(login)
    
    response_text = chat.file_upload("Hello, World!.txt")

    assert len(response_text) > 0
    print(f"✅ Helpy 응답: {response_text}")



def test_chat_basic_003(driver, login):# 이미지 업로드
    chat = chat_basic(driver)
    chat.open_chat(login)

    response_text = chat.file_upload("apple.png")

    assert len(response_text) > 0
    print(f"✅ Helpy 응답: {response_text}")




def test_chat_basic_004(driver, login):# 클립보드, 정상 실행 
    chat = chat_basic(driver)
    chat.open_chat(login)
    chat.send_message("자기소개를 부탁해")

    chat.click_clipboard()

    WebDriverWait(driver, 15)
    copied_text = pyperclip.paste()
    if copied_text.strip():
        print("✅ 클립보드에 내용이 복사되었습니다.")
    else:
        print("❌ 클립보드가 비어 있습니다!")
        assert False, "클립보드에 내용이 없습니다!"



def test_chat_basic_005(driver, login):# 도움됨 클릭 후 피드백 입력 및 전송
    driver = login()
    chat = chat_basic(driver)

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'textarea:not([aria-hidden="true"])')
        )
    )
    chat.send_message("자기소개를 부탁해")

    chat.click_thumbs_up()

    chat.send_feedback("원하던 답변을 얻음")
    chat.click_feedback()



def test_chat_basic_006(driver, login):# 도움 안됨 클릭후 피드백 입력 및 전송
    driver = login()
    chat = chat_basic(driver)

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'textarea:not([aria-hidden="true"])')
        )
    )
    chat.send_message("자기소개를 부탁해")

    chat.click_thumbs_down()

    chat.send_feedback("원하던 답변을 얻지 못함")
    chat.click_feedback()


def test_chat_basic_007(driver, login):# 이미 입력한 채팅 수정
    driver = login()
    chat = chat_basic(driver)

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'textarea:not([aria-hidden="true"])')
        )
    )
    chat.send_message("자기소개를 부탁해")

    chat.click_edit()
    chat.edit_message("사과")

    chat.click_edit_admin()

'''

def test_chat_basic_008(driver, login): # 채팅 수정 선택했다 취소하기
    driver = login()
    chat = chat_basic(driver)

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'textarea:not([aria-hidden="true"])')
        )
    )
    chat.send_message("자기소개를 부탁해")

    chat.click_edit()
    chat.edit_message("사과")
    chat.click_edit_cancel()
'''

def test_chat_basic_009(driver, login): # 스크롤바 기능 확인 1
    driver = login()
    chat = chat_basic(driver)

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'textarea:not([aria-hidden="true"])')
        )
    )
    chat.send_message("자기소개를 부탁해")

    chat.send_message("오늘 날짜를 알려줘")

    chat.scroll_bar()




def test_chat_basic_010(driver, login): # 초기화 버튼, 정상 실행
    driver = login()
    chat = chat_basic(driver)

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'textarea:not([aria-hidden="true"])')
        )
    )
    chat.send_message("자기소개를 부탁해")

    chat.reset_chat()


def test_chat_basic_011(driver, login):# 채팅 성능 테스트, 정상 실행
    driver = login()
    chat = chat_basic(driver)

    

    chat.send_message_timer("자기소개를 부탁해")
    WebDriverWait(driver, 10)


def test_chat_basic_012(driver, login): # 스크립트 입력, 정상 실행
    driver = login()
    chat = chat_basic(driver)


    response_text = chat.send_message("<script>alert('XSS')</script>")

    assert len(response_text) > 0
    print(f"✅ Helpy 응답: {response_text}")


def test_chat_basic_013(driver, login): # 비정상 채팅 입력, 정상 실행
    driver = login()
    chat = chat_basic(driver)

    response_text = chat.send_message("ㅑㄴ루ㅏ두ㅐㄴ")

    assert len(response_text) > 0
    print(f"✅ Helpy 응답: {response_text}")


def test_chat_basic_014(driver, login): # 스페이스바만 입력, 실행은 정상, 성공 확인여부 수정 필요
    driver = login()
    chat = chat_basic(driver)

    response_text = chat.send_message(" ")

    assert len(response_text) > 0
    print(f"✅ Helpy 응답: {response_text}")

'''