from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:

    def __init__(self, driver):
        self.driver = driver
        # 모든 페이지에서 공통으로 사용하는 기본 페이지 클래스

    def open(self, url):
        self.driver.get(url)
        # 웹 페이지 열기

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

    def get_chat_list(self):
        # 사이드바의 채팅 히스토리 목록 강제 로드 + chat_items 반환

        # 대화 목록 전체 컨테이너 대기
        container = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-testid="virtuoso-item-list"]')
            )
        )

        # 강제 스크롤 → 가상 리스트 DOM 렌더링
        self.driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight", container
        )

        # DOM에 a 태그(대화 항목)가 렌더링될 때까지 대기
        chat_items = WebDriverWait(self.driver, 10).until(
            lambda d: container.find_elements(By.TAG_NAME, "a")
            if len(container.find_elements(By.TAG_NAME, "a")) > 0
            else False
        )

        # 존재 확인
        assert len(chat_items) > 0, "대화 항목이 존재하지 않습니다."
        print(f"[BasePage] 대화 목록이 {len(chat_items)}개 있습니다.")

        return chat_items

    # -------------------- 11/14 김은아 추가 --------------------
    def get_menu_buttons(self):
        chat_items = self.get_chat_list()  # 기존 메서드 재사용
        menu_buttons = []
        for item in chat_items:
            buttons = item.find_elements(By.CSS_SELECTOR, "div.menu-button button")
            if buttons:
                menu_buttons.append(buttons[0])
        return menu_buttons

    def get_popup_buttons(self):
        wait = WebDriverWait(self.driver, 10)
        rename_button = wait.until(
            EC.presence_of_element_located((By.XPATH, "//span[text()='Rename']"))
        )
        delete_button = wait.until(
            EC.presence_of_element_located((By.XPATH, "//p[text()='Delete']"))
        )
        return rename_button, delete_button

    def scroll_into_view(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        