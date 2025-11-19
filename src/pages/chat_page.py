# 작성자: 이홍주

import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains



#import pyperclip

def wait_for_new_response(driver, prev_count, timeout=40):
    """새로운 챗봇 응답(article)이 로드될 때까지 대기"""
    SELECTOR = 'div[role="article"]'
    def _new_article_loaded(d):
        try:
            articles = d.find_elements(By.CSS_SELECTOR, SELECTOR)
            if len(articles) <= prev_count:
                return False
            latest = articles[-1]
            text = latest.text.strip()

            return len(text) > 0
        
        except StaleElementReferenceException:
            return False

    WebDriverWait(driver, timeout).until(_new_article_loaded)
    return driver.find_elements(By.CSS_SELECTOR, SELECTOR)



class chat_basic:

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def open_chat(self, login):
        self = login()

        WebDriverWait(self, 15).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'textarea:not([aria-hidden="true"])')
        )
    )

    def send_message(self, message: str): # 메시지 입력

        input_box = self.driver.find_element(By.CSS_SELECTOR, 'textarea:not([aria-hidden="true"])')

        prev_count = len(self.driver.find_elements(By.CSS_SELECTOR, 'div[role="article"]'))
        
        input_box.send_keys(message)
        input_box.send_keys("\n")

        responses = wait_for_new_response(self.driver, prev_count)
        return responses[-1].text


    def click_plus(self): # + 버튼 클릭
       input_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-haspopup='true']")
       input_button.click()

    def file_upload(self, file_name: str): # 파일 업로드 버튼 클릭
        PAGE_DIR = os.path.dirname(os.path.abspath(__file__)) # 현재 폴더 절대 경로로 반환
        self.resource_dir = os.path.realpath(os.path.join(PAGE_DIR, "..", "resources"))# 현재 폴더 기준으로 resources 폴더 경로 절대경로로 반환
        prev_count = len(self.driver.find_elements(By.CSS_SELECTOR, 'div[role="article"]'))
        
        file_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]')))
        file_path = os.path.join(self.resource_dir, file_name)
        file_input.send_keys(file_path)
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH,f"//span[contains(@class, 'truncate') and contains(text(), '{os.path.basename(file_path)}')]")))


        input_box = self.driver.find_element(By.CSS_SELECTOR, 'textarea:not([aria-hidden="true"])')
        input_box.send_keys("\n")
   
        responses = wait_for_new_response(self.driver, prev_count)
        return responses[-1].text
   

    def click_make_image(self): # 이미지 생성 버튼 클릭
        make_image_button = self.driver.find_element(By.XPATH, "/html/body/div[3]/div[3]/ul/div[3]")# 경로변경하기
        make_image_button.click()

    def click_clipboard(self): # 클립보드 버튼 클릭
        clipboard_button = self.driver.find_element(By.CSS_SELECTOR, "button:has(svg.lucide-copy)")
        clipboard_button.click()
    
    def click_thumbs_up(self): # 도움됨 버튼 클릭
        thumbs_up_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button:has(svg.lucide-thumbs-up)")))
        thumbs_up_button.click()
        
        dialog = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div[role='dialog'][data-state='open']")
            )
        )
        dialog.find_element(
            By.XPATH,
            ".//h2/span"
        )

    
    def click_thumbs_down(self): # 도움안됨 버튼 클릭
        thumbs_down_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button:has(svg.lucide-thumbs-down)")))
        thumbs_down_button.click()

        dialog = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div[role='dialog'][data-state='open']")
            )
        )
        dialog.find_element(
            By.XPATH,
            ".//h2/span"
        )

    def send_feedback(self, message: str): # 피드백 입력
        dialog = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='dialog' and @data-state='open']"))
        )

        input_box = dialog.find_element(By.TAG_NAME, "textarea")
    
        input_box.click()
        input_box.send_keys(message)

    def click_feedback(self): # 피드백 제출 버튼 클릭
        input_button = self.driver.find_element(By.XPATH, "//*[@id='submit-feedback']")
        input_button.click()

    def click_feedback_cancel(self):
        input_button = self.driver.find_element(By.XPATH,("//button[.//*[local-name()='svg' and contains(@class,'lucide-x')]]"))
        input_button.click()

    def click_edit(self): # 수정 제출 버튼 클릭
        wait = WebDriverWait(self.driver, 10)

        # 1. 버튼의 부모 .group 요소를 hover (group-hover 때문에 필요)
        group_area = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".group"))
        )

        ActionChains(self.driver).move_to_element(group_area).perform()

        # 2. hover 후 visible 되는 edit-message 버튼 클릭
        button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.edit-message"))
        )
        button.click()

    def edit_message(self, message: str): # 메시지 입력
        input_box = self.driver.find_element(By.ID, "edit-chat-input")
        input_box.clear()
        input_box.send_keys(message)

    def click_edit_admin(self):
        input_button = self.driver.find_element(By.CSS_SELECTOR, "button.confirm-edit")
        input_button.click()

    def click_edit_cancel(self):
        input_button = self.driver.find_element(By.XPATH,"//button[contains(@class, 'hover:bg-accent') and contains(@class, 'py-2')]")
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

    def click_image_button(self):
        input_button = self.driver.find_element(By.XPATH, "//span[text()='이미지 생성']/ancestor::div[@role='button']")
        input_button.click()

    
        
    def click_image_popup(self):    
        img = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//img[contains(@src, 'tools_outputs')]")))


        img.click()

    def wait_image_popup(self, timeout=5):
        """이미지 클릭 후 팝업이 실제로 열렸는지 검증"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//div[@role='dialog' and @data-state='open']")
                )
            )
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//body[contains(@style,'pointer-events: none')]")
                )
            )
            return True

        except:
            return False
    
    def close_image_popup(self):
        input_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Close lightbox']")))
        input_button.click()

    def click_image_quiz(self):
        input_button = self.driver.find_element(By.XPATH, "//span[text()='퀴즈 생성']/ancestor::div[@role='button']")
        input_button.click()