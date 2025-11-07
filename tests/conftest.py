import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

APP_URL = os.getenv("APP_URL", "http://localhost:3000")
WAIT_SEC = int(os.getenv("WAIT_SEC", 10))

@pytest.fixture
def driver():
    """각 테스트마다 새 브라우저"""
    opts = Options()
    if os.getenv("HEADLESS", "0") == "1":
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1920,1080")
    d = webdriver.Chrome(options=opts)
    yield d
    d.quit()

@pytest.fixture
def login(driver):
    def _login(username, password):
        driver.delete_all_cookies()
        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")

        driver.get("https://accounts.elice.io/accounts/signin/me?continue_to=https%3A%2F%2Fqaproject.elice.io%2Fai-helpy-chat")

        # ✅ 랜덤 ID 회피: 의미 기반 셀렉터 사용
        id_input = driver.find_element(By.CSS_SELECTOR, "input[autocomplete='username'], input[type='email']")
        pw_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")

        id_input.send_keys(username)
        pw_input.send_keys(password)

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(driver, 10).until(
            EC.url_contains("/ai-helpy-chat")
        )
        return driver
    return _login