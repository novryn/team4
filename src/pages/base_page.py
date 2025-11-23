# 서드파티 라이브러리
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

class BasePage:

    # 셀렉터 상수
    PROFILE_BUTTON = (By.CSS_SELECTOR, "button.MuiAvatar-root")

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.timeout = timeout
        # 모든 페이지에서 공통으로 사용하는 기본 페이지 클래스

    def open(self, url):
        self.driver.get(url)
        # 웹 페이지 열기

    def wait_for_clickable(self, locator, timeout=30):
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )

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

    def scroll_into_view(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    def click_profile(self):
        """
        우측 상단 프로필 아바타 버튼을 클릭해 드롭다운 메뉴를 연다.
        드롭다운이 실제로 열렸는지 확인까지 수행.
        """
        try:
            # 1) 프로필 버튼 클릭
            profile_btn = self.wait_for_clickable(self.PROFILE_BUTTON)
            profile_btn.click()
            
            # 2) 드롭다운이 실제로 열린 것 확인
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_any_elements_located((
                    By.XPATH,
                    "//*[contains(text(),'Logout') or contains(text(),'로그아웃') "
                    "or contains(text(),'계정 관리') or contains(text(),'Account Management')]"
                ))
            )
            print("✅ 프로필 버튼 클릭")
            return True
            
        except TimeoutException as e:
            raise Exception(f"프로필 드롭다운이 열리지 않았습니다: {e}")
        except Exception as e:
            raise Exception(f"프로필 버튼 클릭 실패: {e}")
