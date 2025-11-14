# 표준 라이브러리
import os
import time

# 서드파티 라이브러리
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class BasePage:

    def __init__(self, driver):
        self.driver = driver
        # 모든 페이지에서 공통으로 사용하는 기본 페이지 클래스

    def open(self, url):
        self.driver.get(url)
        # 웹 페이지 열기
        
    def wait_for_clickable(self, locator, timeout=30):
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )

    def click(self, locator):
        element = self.wait_for_clickable(locator)
        element.click()

    def wait_for_element(self, locator, timeout=30):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
        
        # 단일 요소
        # 화면에 요소가 나타날 때까지 기다림 (locator: 찾고 싶은 버튼/입력창/영역 위치)
    
    def wait_for_elements(self, locator, timeout=30):
        
        # 여러 요소를 기다려서 리스트로 반환
        # locator: (By.CSS_SELECTOR, 'selector') 형태
        
        return WebDriverWait(self.driver, timeout).until(
            lambda d: d.find_elements(*locator) if d.find_elements(*locator) else False
        )

    def click(self, locator):
        element = self.wait_for_element(locator)
        element.click()
        # 버튼 클릭

    def type(self, locator, text):
        element = self.wait_for_element(locator)
        element.clear()          # 기존 글자 지우기
        element.send_keys(text)  # 새 글자 입력
        # 텍스트 입력

    def get_text(self, locator):
        element = self.wait_for_element(locator)
        return element.text
        # 화면에 있는 글자 가져오기

    def is_displayed(self, locator):
        try:
            element = self.wait_for_element(locator)
            return element.is_displayed()  # True / False 반환
        except:
            return False
        # 요소가 화면에 보이는지 확인

    def scroll_to_element(self, locator):
        element = self.wait_for_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        # 화면 스크롤해서 요소 보이게 만들기

    def take_screenshot(self, name="screenshot.png"):
        self.driver.save_screenshot(name)
        # 테스트 실패 화면 캡처 저장
        # 11/10 김은아 작성

    def get_chat_list(self, timeout=10):
        """
        사이드바의 채팅 히스토리 목록 강제 로드 + chat_items 반환
        마지막까지 스크롤해서 모든 항목을 가져오도록 수정
        """

        # 대화 목록 전체 컨테이너 대기
        container = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="virtuoso-item-list"]'))
        )

        # 반복 스크롤: 마지막까지 DOM 렌더링
        prev_height = -1
        while True:
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
            time.sleep(0.5)  # 렌더링 안정화
            curr_height = self.driver.execute_script("return arguments[0].scrollHeight", container)
            if curr_height == prev_height:
                break
            prev_height = curr_height

        # a 태그(대화 항목) 요소 가져오기
        chat_items = WebDriverWait(self.driver, timeout).until(
            lambda d: container.find_elements(By.TAG_NAME, "a")
            if len(container.find_elements(By.TAG_NAME, "a")) > 0
            else False
        )

        assert len(chat_items) > 0, "대화 항목이 존재하지 않습니다."
        print(f"[BasePage] 대화 목록이 {len(chat_items)}개 있습니다.")

        return chat_items


    # -------------------- 11/14 김은아 추가 --------------------
    def get_menu_buttons(self):
        chat_items = self.get_chat_list()
        menu_buttons = []

        for item in chat_items:
            # svg 아이콘 먼저 찾기
            svg = item.find_elements(
                By.CSS_SELECTOR,
                "button.MuiIconButton-root svg[data-testid='ellipsis-verticalIcon']"
            )
            if svg:
                # svg의 부모 = button
                menu_buttons.append(svg[0].find_element(By.XPATH, "./.."))

        return menu_buttons

    def get_popup_buttons(self):
        # 메뉴 클릭 후 뜨는 Rename / Delete li 요소
        wait = WebDriverWait(self.driver, 10)
        rename_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//li//span[text()='Rename']")
            )
        )
        delete_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//li//p[text()='Delete']")
            )
        )
        return rename_button, delete_button
    
    def click_delete_popup(self):
        # 마지막 Delete 버튼 (팝업 안)
        wait = WebDriverWait(self.driver, 10)
        final_delete = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[id*=':r'][type='button']")
            )
        )
        final_delete.click()
        
    def scroll_into_view(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
    
    def logout(self):
        wait = WebDriverWait(self.driver, 10)

        # 프로필 버튼 클릭
        profile_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.MuiAvatar-root"))
        )
        profile_btn.click()
        print("프로필 버튼 클릭 완료")

        # Logout 버튼 클릭 (JS 사용)
        logout_btn = wait.until(
            EC.presence_of_element_located((By.XPATH, "//p[text()='Logout']"))
        )
        self.driver.execute_script("arguments[0].click();", logout_btn)
        print("로그아웃 버튼 클릭 완료")
        
    # 11/14 로그아웃 픽스쳐 추가(김은아)    

    



    

        