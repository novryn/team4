# 작성자: 이홍주

import os
import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep

#import platform
#import pyautogui
#import pyperclip

def wait_for_new_response(driver, prev_count, timeout=40):
    """새로운 챗봇 응답(article)이 로드될 때까지 대기"""
    def _new_article_loaded(d):
        try:
            articles = d.find_elements(By.CSS_SELECTOR, 'div[role="article"]')
            if len(articles) <= prev_count:
                return False
            latest = articles[-1]
            text = latest.text.strip()
            return text != ""
        except StaleElementReferenceException:
            return False

    WebDriverWait(driver, timeout).until(_new_article_loaded)
    return driver.find_elements(By.CSS_SELECTOR, 'div[role="article"]')


'''
pyautugui 사용 미완성
def paste_path_and_confirm(file_path, timeout=10):
    """클립보드에 경로 복사 후 붙여넣기 + Enter. OS에 따라 붙여넣기 키 다름."""
    system = platform.system()
    pyperclip.copy(file_path)  # 클립보드에 복사 -> 붙여넣기 방식이 안정적
    time.sleep(0.15)  # 복사 안정화
    if system == "Darwin":  # macOS
        pyautogui.hotkey('command', 'v')
    else:  # Windows / Linux
        pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.1)
    pyautogui.press('enter')
'''

class chat_basic:

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def open_chat(self):
        self.driver.get("https://qaproject.elice.io/ai-helpy-chat")

    


    def send_message(self, message: str): # 메시지 입력

        input_box = self.driver.find_element(By.CSS_SELECTOR, 'textarea:not([aria-hidden="true"])')

        prev_count = len(self.driver.find_elements(By.CSS_SELECTOR, 'div[role="article"]'))
        

        # ✅ 메시지 입력
        input_box.send_keys(message)
        input_box.send_keys("\n")

        responses = wait_for_new_response(self.driver, prev_count)
        return responses[-1].text


    def click_plus(self): # + 버튼 클릭
       input_button = self.driver.find_element(By.XPATH, "//*[@id='message-composer']/div[2]/div/button[1]")
       input_button.click()

    def click_upload(self): # 파일 업로드 버튼 클릭
        upload_button = self.driver.find_element(By.XPATH, "/html/body/div[3]/div[3]/ul/div[1]")
        upload_button.click()

    """
    # 파일 업로드 창 제어 미완성
    def upload_file(self, file_path: str, wait_before=2, wait_after=2): # 파일 업로드
        FILE_PATH = r""   # 업로드할 파일의 절대경로 (OS에 맞게)
        PAGE_URL = "https://example.com"          # 테스트할 페이지
        UPLOAD_BUTTON_SELECTOR = '[data-action="file-upload"]'

        time.sleep(0.6)  # 작동하지 않으면 0.8~1.2로 늘리기

        # 붙여넣기 + Enter
        paste_path_and_confirm(FILE_PATH)

        # 업로드가 실제로 완료될 때까지 대기(페이지에 따라 조정)
        # 예: 업로드 완료 메시지나 업로드된 파일 목록이 나타나는 셀렉터로 WebDriverWait 사용
        # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".upload-success")))

        # 필요 시 더 대기
        time.sleep(1)
        print("파일 업로드 시도 완료. (성공 여부는 페이지 상태 확인 필요)")
    """

    def click_make_image(self): # 이미지 생성 버튼 클릭
        make_image_button = self.driver.find_element(By.XPATH, "/html/body/div[3]/div[3]/ul/div[3]")
        make_image_button.click()

    def click_clipboard(self): # 클립보드 버튼 클릭
        clipboard_button = self.driver.find_element(By.CSS_SELECTOR, "button:has(svg.lucide-copy)")
        clipboard_button.click()
    
    def click_thumbs_up(self): # 도움됨 버튼 클릭
        thumbs_up_button = self.driver.find_element(By.CSS_SELECTOR, "button:has(svg.lucide-thumbs-up)")
        thumbs_up_button.click()
        dialog = WebDriverWait(self, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog' and @data-state='open']")))

        title = dialog.find_element(By.XPATH, ".//h2[span[text()='의견 추가']]")
        assert title.is_displayed()
    
    def click_thumbs_down(self): # 도움안됨 버튼 클릭
        thumbs_down_button = self.driver.find_element(By.CSS_SELECTOR, "button:has(svg.lucide-thumbs-d)")
        thumbs_down_button.click()
        dialog = WebDriverWait(self, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog' and @data-state='open']")))

        title = dialog.find_element(By.XPATH, ".//h2[span[text()='의견 추가']]")
        assert title.is_displayed()

    def send_feedback(self, message: str): # 피드백 입력
        input_box = self.driver.find_element(By.XPATH, "//*[@id='radix-:r14:']/textarea")
        input_box.click()
        input_box.send_keys(message)

    def click_feedback(self): # 피드백 제출 버튼 클릭
        input_button = self.driver.find_element(By.XPATH, "//*[@id='submit-feedback']")
        input_button.click()

    def click_feedback_cancel(self):
        input_button = self.driver.find_elementBy.XPATH,("//button[.//*[local-name()='svg' and contains(@class,'lucide-x')]]")
        input_button.click()

    def click_edit(self): # 수정 제출 버튼 클릭
        wait = WebDriverWait(self, 10)
        actions = ActionChains(self)

        message_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".message.group")))
        actions.move_to_element(message_div).perform()
        input_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.edit-message")))
        input_button.click()

    def edit_message(self, message: str): # 메시지 입력
        input_box = self.driver.find_element(By.ID, "edit-chat-input")
        input_box.clear()
        input_box.send_keys(message)

    def click_edit_admin(self):
        input_button = self.driver.find_element(By.XPATH, "//button[normalize-space()='취소' or .//span[normalize-space()='확인']]")
        input_button.click()
        input_button.click()

    def click_edit_cancel(self):
        input_button = self.driver.find_element(By.XPATH, "//button[normalize-space()='취소' or .//span[normalize-space()='취소']]")
        input_button.click()


    def scroll_bar(self):
        scroll_container = self.driver.find_element(By.CSS_SELECTOR,"div.relative.flex.flex-col.flex-grow.overflow-y-auto")
        
        before = self.driver.execute_script("return arguments[0].scrollTop;", scroll_container)
        self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scroll_container)
        after = self.driver.execute_script("return arguments[0].scrollTop;", scroll_container)

        print(f"스크롤 이동 여부: {before} → {after}")

    def reset_chat(self):
        wait = WebDriverWait(self.driver, 10)
    
        # ① 'pen-to-square' 아이콘을 가진 svg 찾기
        svg_icon = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "svg[data-icon='pen-to-square']")))

        # ② svg 아이콘을 포함한 상위 li (role=button)로 올라가 클릭
        new_chat_button = svg_icon.find_element(By.XPATH, "./ancestor::div[@role='button']")

        # ③ 버튼 클릭
        new_chat_button.click()
        print("✅ '새 대화' 버튼 클릭 완료")

    def send_message_timer(self, message: str): # 메시지 입력
        
                                      
        input_box = self.driver.find_element(By.CSS_SELECTOR, 'textarea:not([aria-hidden="true"])')

        prev_count = len(self.driver.find_elements(By.CSS_SELECTOR, 'div[role="article"]'))

        input_box.send_keys(message)
        input_box.send_keys("\n")

        try:
            # ✅ 5초 안에 새로운 응답(div[role="article"])이 생길 때까지 대기
            WebDriverWait(self.driver, 5).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, 'div[role="article"]')) > prev_count
            )

            responses = self.driver.find_elements(By.CSS_SELECTOR, 'div[role="article"]')
            print("✅ 메시지 응답 수신 완료")
            return responses[-1].text

        except TimeoutException:
            print("❌ 5초 내에 응답이 완전히 로드되지 않았습니다.")
            return None

