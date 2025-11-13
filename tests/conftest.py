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
from src.config.settings import get_default_admin

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


@pytest.fixture(scope="session") # 11/13 황지애. chrome_options, chrome_driver_path 추가. driver, login 수정
def chrome_options():
    """Chrome 옵션을 세션당 한 번만 생성"""
    opts = Options()
    
    if os.getenv("HEADLESS", "0") == "1":
        opts.add_argument("--headless=new")
    
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    
    return opts

# ChromeDriver 경로를 세션당 한 번만 설정
@pytest.fixture(scope="session")
def chrome_driver_path():
    """ChromeDriver 경로를 세션 시작 시 한 번만 가져옴"""
    path = ChromeDriverManager().install()
    print(f"\n[Setup] ChromeDriver 경로: {path}")
    return path

@pytest.fixture
def driver(chrome_driver_path):
    """각 테스트마다 새 브라우저 인스턴스 생성"""
    opts = Options()
    
    # Headless 모드 설정
    if os.getenv("HEADLESS", "0") == "1":
        opts.add_argument("--headless=new")
    
    opts.add_argument("--window-size=1920,1080")
    
    # ChromeDriver 서비스 생성 (이미 설치된 경로 재사용)
    service = Service(chrome_driver_path)
    browser = webdriver.Chrome(service=service, options=opts)
    
    yield browser
    
    # 테스트 종료 후 브라우저 닫기
    browser.quit()

@pytest.fixture
def login(driver):
    """
    로그인 fixture
    
    사용법:
        driver = login()           # .env의 MY_ADMIN_ACCOUNT 사용
        driver = login(ADMIN2)     # 특정 계정 지정
    """
    def _login(account=None):
        # 1. 계정 선택
        acc = account or get_default_admin()
        
        # 2. 계정 정보 확인
        if not acc.username or not acc.password:
            raise ValueError(f"계정 정보가 .env에 없습니다: {acc}")
        
        print(f"\n[로그인] {acc.description} ({acc.username})")
        
        # 3. 로그인 페이지 이동
        driver.get(
            "https://accounts.elice.io/accounts/signin/me"
            "?continue_to=https%3A%2F%2Fqaproject.elice.io%2Fai-helpy-chat"
        )
        
        # 4. 쿠키/스토리지 정리
        driver.delete_all_cookies()
        try:
            driver.execute_script("window.localStorage.clear();")
            driver.execute_script("window.sessionStorage.clear();")
        except Exception:
            pass
        
        # 5. 로그인 필드 대기
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "input[autocomplete='username'], input[type='email']")
            )
        )
        
        # 6. 아이디/비밀번호 입력
        id_input = driver.find_element(By.CSS_SELECTOR, "input[autocomplete='username'], input[type='email']")
        pw_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        
        id_input.clear()
        pw_input.clear()
        id_input.send_keys(acc.username)
        pw_input.send_keys(acc.password)
        
        # 7. 로그인 버튼 클릭
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # 8. 로그인 완료 대기
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
