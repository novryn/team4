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
        
        # 화면에 요소가 나타날 때까지 기다림 (locator: 찾고 싶은 버튼/입력창/영역 위치)

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
        
    def wait_for_iframe_element(self, iframe_locator, element_locator, timeout=30):
        
        # iframe 나타날 때까지 대기
        iframe = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(iframe_locator)
        )
        self.driver.switch_to.frame(iframe)

        # iframe 안 요소 기다리기(iframe_locator: iframe 찾는 locator (By.ID, By.CSS_SELECTOR 등), element_locator: iframe 안 요소 locator)
        element = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(element_locator)
        )

        # 기본 프레임으로 돌아오기
        self.driver.switch_to.default_content()
        return element
        
        #11/10 김은아 작성
