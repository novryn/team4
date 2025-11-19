from src.pages.chat_page import chat_basic
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def test_chat_advanced_001(driver, login):
    chat = chat_basic(driver)
    chat.open_chat(login)

    chat.click_plus()
    WebDriverWait(driver, 10)
    chat.click_image_button()

    chat.send_message("달")
    WebDriverWait(driver, 10)
    chat.click_image_popup()
    WebDriverWait(driver, 10)

    chat.close_image_popup()

def test_chat_advanced_005(driver, login):# 퀴즈생성,퀴즈생성 완료시까지 대기하는 부분 미완성 
    chat = chat_basic(driver)
    chat.open_chat(login)
    
    chat.click_plus()
    WebDriverWait(driver, 10)

    chat.click_image_quiz()
    chat.send_message("사칙연산, 객관식")

    assert WebDriverWait(driver, 30).until(EC.visibility_of_element_located((
        By.CSS_SELECTOR,
        "div.bg-muted.p-3.rounded-md"
    )))


    

def test_chat_advanced_006(driver, login):
    chat = chat_basic(driver)
    chat.open_chat(login)
    
    chat.click_plus()
    WebDriverWait(driver, 10)

    chat.click_image_quiz()
    chat.send_message("사칙연산, 답이 복수인 객관식")

    assert WebDriverWait(driver, 30).until(EC.visibility_of_element_located((
        By.CSS_SELECTOR,
        "div.bg-muted.p-3.rounded-md"
    )))


def test_chat_advanced_007(driver, login):
    chat = chat_basic(driver)
    chat.open_chat(login)
    
    chat.click_plus()
    WebDriverWait(driver, 10)

    chat.click_image_quiz()
    chat.send_message("사칙연산, 주관식")

    assert WebDriverWait(driver, 30).until(EC.visibility_of_element_located((
        By.CSS_SELECTOR,
        "div.bg-muted.p-3.rounded-md"
    )))

    



