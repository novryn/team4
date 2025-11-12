import os
import sys

# sys.path 설정을 맨 위로 (다른 import보다 먼저)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(project_root, 'src'))

import re
import pytest
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from pages.base_page import BasePage  

ARTIFACT_DIR = os.getenv("ARTIFACT_DIR", "artifacts")  # 저장 폴더
CAPTURE_ON_XFAIL = os.getenv("CAPTURE_ON_XFAIL", "0") == "1"  # XFAIL도 캡처할지

def _safe_name(nodeid: str) -> str:
    # tests/billing/test_billing.py::test_credit_button_hover_color[param] → 안전한 파일명
    name = re.sub(r"[\\/:*?\"<>|]+", "_", nodeid)
    name = name.replace("::", "_").replace("/", "_").replace("[", "_").replace("]", "_")
    return name

def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")

def _capture(driver, nodeid: str, tag: str = "fail"):
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    base = f"{_timestamp()}_{_safe_name(nodeid)}_{tag}"
    png = os.path.join(ARTIFACT_DIR, base + ".png")
    html = os.path.join(ARTIFACT_DIR, base + ".html")
    try:
        driver.save_screenshot(png)
    except WebDriverException:
        pass
    try:
        with open(html, "w", encoding="utf-8") as f:
            f.write(driver.page_source or "")
    except Exception:
        pass
    # 참고용 경로 출력
    print(f"[artifact] {png}")
    print(f"[artifact] {html}")

@pytest.fixture
def driver():
    """각 테스트마다 새 브라우저"""
    opts = Options()
    if os.getenv("HEADLESS", "0") == "1":
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    d = webdriver.Chrome(service=service, options=opts)
    
    yield d
    d.quit()

@pytest.fixture
def login(driver):
    def _login(username, password):
        # 1) 로그인 페이지 먼저 오픈 (출처 확보)
        driver.get(
            "https://accounts.elice.io/accounts/signin/me"
            "?continue_to=https%3A%2F%2Fqaproject.elice.io%2Fai-helpy-chat"
        )

        # 2) 쿠키/스토리지 정리 (같은 출처 컨텍스트에서)
        driver.delete_all_cookies()
        try:
            driver.execute_script("window.localStorage.clear();")
            driver.execute_script("window.sessionStorage.clear();")
        except Exception:
            # 스토리지가 막혀있으면 무시하고 진행
            pass

        # 3) 필드 대기 후 입력
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[autocomplete='username'], input[type='email']"))
        )
        id_input = driver.find_element(By.CSS_SELECTOR, "input[autocomplete='username'], input[type='email']")
        pw_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")

        id_input.clear(); pw_input.clear()
        id_input.send_keys(username)
        pw_input.send_keys(password)

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(driver, 30).until(EC.url_contains("/ai-helpy-chat"))
        return driver
    return _login

# ------- 실패 아티팩트 공통 훅 ----------------------------------

# 각 테스트 단계(setup/call/teardown) 리포트를 node에 붙여줌
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

# ==== XFAIL 캡처 스위치 ===========================================================
CAPTURE_XFAIL = False  # ← 여기만 True/False로 켜고 끄면 됨. True로 바꾸면 xfail도 캡처
# ================================================================================

@pytest.fixture(autouse=True)
def _auto_artifacts_on_fail(request, driver):
    yield
    nodeid = request.node.nodeid
    rep_setup = getattr(request.node, "rep_setup", None)
    rep_call  = getattr(request.node, "rep_call", None)

    # setup 실패 → 캡처
    if rep_setup and rep_setup.failed:
        _capture(driver, nodeid, tag="setup")
        return

    # 테스트 본문 실패 → 캡처
    if rep_call and rep_call.failed:
        _capture(driver, nodeid, tag="call")
        return

    # xfail 시 캡처는 "스위치"로 제어
    if CAPTURE_XFAIL and rep_call and rep_call.skipped and "xfail" in rep_call.keywords:
        _capture(driver, nodeid, tag="xfail")
              
@pytest.fixture
def page(driver):
    
    return BasePage(driver) # 모든 테스트에서 BasePage 객체 재사용 (11/10 김은아. 해당 기능 추가)
