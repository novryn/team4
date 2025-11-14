# ───────────────────────────────────────────────────────────────
# 1. 기본 라이브러리
# ───────────────────────────────────────────────────────────────
import os
from dotenv import load_dotenv
load_dotenv()  # env 파일 전체를 미리 읽어서 login()에서 사용 가능하게 함

import re
from datetime import datetime

# ───────────────────────────────────────────────────────────────
# 2. 외부 라이브러리
# ───────────────────────────────────────────────────────────────
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# ───────────────────────────────────────────────────────────────
# 3. 내부 프로젝트 모듈
# ───────────────────────────────────────────────────────────────
from src.pages.base_page import BasePage
from src.config.settings import get_default_admin

# ───────────────────────────────────────────────────────────────
# 4. 환경변수 기반 아티팩트 설정
# ───────────────────────────────────────────────────────────────
ARTIFACT_DIR = os.getenv("ARTIFACT_DIR", "artifacts")  # 저장 폴더
CAPTURE_ON_XFAIL = os.getenv("CAPTURE_ON_XFAIL", "0") == "1"  # XFAIL도 캡처할지

# ───────────────────────────────────────────────────────────────
# 5. 유틸 함수 (11/13 황지애. chrome_options, chrome_driver_path 추가. driver, login 수정)
# ───────────────────────────────────────────────────────────────

def _safe_name(nodeid: str) -> str:
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

# ───────────────────────────────────────────────────────────────
# 6. Chrome 설정(브라우저 옵션 fixture) - Chrome 옵션을 세션당 한 번만 생성
# ───────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def chrome_options():
    opts = Options()
    if os.getenv("HEADLESS", "0") == "1":
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    return opts

# ───────────────────────────────────────────────────────────────
# 7. 크롬 드라이버 경로 (webdriver-manager)
# ───────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def chrome_driver_path():
    path = ChromeDriverManager().install()
    print(f"\n[Setup] ChromeDriver 경로: {path}")
    return path

# ───────────────────────────────────────────────────────────────
# 8. driver fixture (function scope)
# ───────────────────────────────────────────────────────────────

@pytest.fixture
def driver(chrome_driver_path):
    
    # 각 테스트마다 새 브라우저 인스턴스 생성
    opts = Options()
    
    # Headless 모드 설정
    if os.getenv("HEADLESS", "0") == "1":
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1920,1080")
    
    # 한국어 설정 추가
    opts.add_argument("--lang=ko-KR")
    opts.add_experimental_option('prefs', {
        'intl.accept_languages': 'ko-KR,ko,en-US,en'
    })
    
    # ChromeDriver 서비스 생성 (이미 설치된 경로 재사용)
    service = Service(chrome_driver_path)
    browser = webdriver.Chrome(service=service, options=opts)
    yield browser
    
    # 테스트 종료 후 브라우저 닫기
    browser.quit()

# ───────────────────────────────────────────────────────────────
# 9. 언어 설정 함수
# ───────────────────────────────────────────────────────────────

def _set_language_korean(driver):
    """
    페이지 언어를 한국어로 설정
    localStorage + URL 파라미터 조합
    """
    try:
        # localStorage 설정
        driver.execute_script("""
            localStorage.setItem('language', 'ko');
            localStorage.setItem('locale', 'ko-KR');
            localStorage.setItem('lang', 'ko');
            localStorage.setItem('i18nextLng', 'ko');
        """)
        
        # URL에 lang 파라미터 추가
        current_url = driver.current_url
        if "lang=" not in current_url:
            separator = "&" if "?" in current_url else "?"
            driver.get(f"{current_url}{separator}lang=ko")
        else:
            driver.refresh()
        
        # 로드 대기
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        print("✅ 한국어 설정 완료")
                
    except Exception as e:
        print(f"⚠️ 언어 설정 실패: {e}")
        

# ───────────────────────────────────────────────────────────────
# 10. login fixture
# ───────────────────────────────────────────────────────────────

@pytest.fixture
def login(driver):
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
        
        # 🆕 9. 언어를 한국어로 설정
        _set_language_korean(driver)

        return driver

    return _login

# ───────────────────────────────────────────────────────────────
# 11. 실패 아티팩트 공통 훅 (테스트 결과 캡처) - 각 테스트 단계(setup/call/teardown) 리포트를 node에 붙여줌
# ───────────────────────────────────────────────────────────────

@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
    
# XFAIL 캡처 스위치 ← 여기만 True/False로 켜고 끄면 됨. True로 바꾸면 xfail도 캡처
CAPTURE_XFAIL = False

# ───────────────────────────────────────────────────────────────
# 12. auto screenshot fixture (테스트 실패 시 자동 캡처)
# ───────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _auto_artifacts_on_fail(request, driver):
    yield
    nodeid = request.node.nodeid
    rep_setup = getattr(request.node, "rep_setup", None)
    rep_call = getattr(request.node, "rep_call", None)
    
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

# ───────────────────────────────────────────────────────────────
# 13. Page Object 주입 fixture (11/10 김은아. 해당 기능 추가)
# ───────────────────────────────────────────────────────────────

@pytest.fixture
def page(driver):
    return BasePage(driver)


# 11/13, 11/14 코드 로직 순서 및 정렬 정리. 김은아