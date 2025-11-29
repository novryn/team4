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
import allure
import subprocess
import tempfile

# ───────────────────────────────────────────────────────────────
# 3. 내부 프로젝트 모듈
# ───────────────────────────────────────────────────────────────
from src.pages.base_page import BasePage
from src.pages.account_page import AccountPage
from src.config.settings import get_default_admin

# ───────────────────────────────────────────────────────────────
# 4. 환경변수 기반 아티팩트 설정
# ───────────────────────────────────────────────────────────────
ARTIFACT_DIR = os.getenv("ARTIFACT_DIR", "artifacts")  # 저장 폴더
CAPTURE_ON_XFAIL = os.getenv("CAPTURE_ON_XFAIL", "0") == "1"  # XFAIL도 캡처할지

# ───────────────────────────────────────────────────────────────
# 5. 유틸 함수
# ───────────────────────────────────────────────────────────────

def _safe_name(nodeid: str) -> str:
    name = re.sub(r"[\\/:*?\"<>|]+", "_", nodeid)
    name = name.replace("::", "_").replace("/", "_").replace("[", "_").replace("]", "_")
    return name

def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")

def _capture(driver, nodeid: str, tag: str = "fail"):
    """테스트 실패 시 스크린샷을 Allure 리포트에만 첨부"""
        
    try:
        # 임시 파일로 스크린샷 저장
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp_path = tmp.name
        
        driver.save_screenshot(tmp_path)
        
        # Allure에 첨부
        with open(tmp_path, "rb") as f:
            allure.attach(
                f.read(),
                name=f"{_safe_name(nodeid)}_{tag}",
                attachment_type=allure.attachment_type.PNG
            )
        
        print(f"[allure] Screenshot attached: {nodeid}")
        
    except WebDriverException as e:
        print(f"[allure] Screenshot failed: {e}")
    finally:
        # 임시 파일 정리
        try:
            if 'tmp_path' in locals():
                os.unlink(tmp_path)
        except:
            pass

# ───────────────────────────────────────────────────────────────
# 6. Chrome 설정(브라우저 옵션 fixture)      --- 11/13 추가(황지애)
# ───────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
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

# ───────────────────────────────────────────────────────────────
# 7. 크롬 드라이버 경로 (webdriver-manager)   --- 11/19 수정(황지애)
# ───────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def chrome_driver_path():
    """ChromeDriver 경로"""
    if os.getenv("CI"):
        return None   # ← Selenium이 PATH에서 찾음
    else:
        return ChromeDriverManager().install()


# ───────────────────────────────────────────────────────────────
# 8. driver fixture (function scope)       --- 11/19 수정(황지애)
# ───────────────────────────────────────────────────────────────

@pytest.fixture
def driver(chrome_driver_path):
    
    # 각 테스트마다 새 브라우저 인스턴스 생성
    opts = Options()
    
    # CI 환경(GitHub Actions)에서만 headless
    if os.getenv("CI"):
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
    
    # 모든 환경에서 동일한 창 크기
    opts.add_argument("--window-size=1920,1080")
    
    # 한국어 설정 추가
    opts.add_argument("--lang=ko-KR")
    opts.add_experimental_option('prefs', {
        'intl.accept_languages': 'ko-KR,ko,en-US,en'
    })
    
    # None이면 Service() 경로 없이 생성
    if chrome_driver_path:
        service = Service(chrome_driver_path)
    else:
        service = Service()  # Selenium이 PATH에서 자동으로 찾음
    
    browser = webdriver.Chrome(service=service, options=opts)
    
    yield browser
    
    # 테스트 종료 후 브라우저 닫기
    browser.quit()

# ───────────────────────────────────────────────────────────────
# 9. login fixture                         --- 11/13 수정(황지애)
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
        
        # 9. 언어를 한국어로 설정
        account_page = AccountPage(driver)
        account_page.set_language_korean()

        return driver

    return _login

# ───────────────────────────────────────────────────────────────
# 10. 실패 아티팩트 공통 훅 (테스트 결과 캡처) - 각 테스트 단계(setup/call/teardown) 리포트를 node에 붙여줌
# ───────────────────────────────────────────────────────────────

@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
    
# ───────────────────────────────────────────────────────────────
# 11. auto screenshot fixture (테스트 실패 시 자동 캡처)
# ───────────────────────────────────────────────────────────────

# XFAIL 캡처 스위치 ← True로 바꾸면 xfail도 캡처
CAPTURE_XFAIL = False

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
# 12. Page Object 주입 fixture (11/10 김은아. 해당 기능 추가)
# ───────────────────────────────────────────────────────────────

@pytest.fixture
def page(driver):
    return BasePage(driver)


# 11/13, 11/14 코드 로직 순서 및 정렬 정리. 김은아

# ────────────────────────────────────────────────
# 13. Custom Agent 관련 페이지/유틸 fixture
# ────────────────────────────────────────────────

@pytest.fixture
def custom_agent_page(login, page):
    """
    Custom Agent 페이지로 이동한 BasePage 객체를 반환
    """
    driver = login()
    page.open("https://qaproject.elice.io/ai-helpy-chat/custom-agent")
    return page

# ───────────────────────────────────────────────────────────────
# 14. 커스텀 에이전트 카드 반환 헬퍼 (TC2용)
# ───────────────────────────────────────────────────────────────

def wait_for_custom_card(page, index=0, timeout=10):
    """
    커스텀 에이전트 카드 리스트에서 index번째 카드 반환
    """
    cards = page.wait_for_elements((By.CSS_SELECTOR, "div[data-testid='ai-card']"), timeout=timeout)
    return cards[index]

# 11/18 김은아 추가

# ───────────────────────────────────────────────────────────────
# 15. Allure 
# ───────────────────────────────────────────────────────────────

def pytest_sessionfinish(session, exitstatus):
    """테스트 종료 후 자동으로 Allure 리포트 생성 및 열기"""
        
    print("\n📊 Allure 리포트 생성 중...")
    subprocess.run([
        "allure.cmd", "generate", 
        "allure-results", 
        "-o", "allure-report"
        # "--clean" ← 이력 유지
        ], shell=True)
    
    print("🌐 브라우저에서 리포트 열기...")
    subprocess.run(["allure.cmd", "open", "allure-report"
                    ], shell=True)