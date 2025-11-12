import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage  # 공통 기능 상속용

# -----------------------001 -----------------------
@pytest.mark.ui
@pytest.mark.medium

# CUSTOM-001: Agent Explorer 화면 진입
def test_custom_001_agent_explorer_entry(login, driver):
    
    driver = login("team4@elice.com", "team4elice!@")  # 로그인

    # 대화 목록 컨테이너 기다리고 스크롤해서 항목 모으기
    def collect_chat_items(driver, timeout=15):
        try:
            container = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="virtuoso-item-list"]'))  # 요소 찾아야됨
            )
        except TimeoutException:
            print("대화 목록 컨테이너 자체가 없음")
            return []

        chat_items = []
        start_time = time.time()
        while True:
            found = container.find_elements(By.TAG_NAME, "a")  # 요소: 실제 각 항목 <a> 태그 확인 필요
            if len(found) > len(chat_items):
                chat_items = found
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
            time.sleep(0.5)
            if time.time() - start_time > timeout:
                break
        return chat_items

    collect_chat_items(driver)

    # Agent Explorer 메뉴 클릭 후 초기 페이지 진입 확인
    try:
        sidebar_menu = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='agent-explorer-menu']"))  # 요소 찾아야됨
        )
        sidebar_menu.click()
        print("Agent Explorer 초기 페이지 정상 진입")
    except TimeoutException:
        print("Agent Explorer 메뉴를 찾을 수 없음")
        pytest.fail("Agent Explorer 초기 페이지 진입 실패")

# -----------------------002 -----------------------
@pytest.mark.ui
@pytest.mark.medium

def test_custom_002_search_display(login, driver):

    # CUSTOM-002: 메인 화면 검색창 표시 확인

    driver = login("team4@elice.com", "team4elice!@")

    # 대화 목록 컨테이너 기다리고 스크롤해서 항목 모으기
    def collect_chat_items(driver, timeout=15):
        try:
            container = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="virtuoso-item-list"]'))  # 요소 찾아야됨
            )
        except TimeoutException:
            print("대화 목록 컨테이너 자체가 없음")
            return []

        chat_items = []
        start_time = time.time()
        while True:
            found = container.find_elements(By.TAG_NAME, "a")  # 실제 각 항목 <a> 태그 확인 필요
            if len(found) > len(chat_items):
                chat_items = found
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
            time.sleep(0.5)
            if time.time() - start_time > timeout:
                break
        return chat_items

    collect_chat_items(driver)

    # 검색창 표시 확인
    try:
        search_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='검색']"))  # 요소 찾아야됨
        )
        search_icon = driver.find_element(By.CSS_SELECTOR, "button[data-testid='search-icon']")  # 요소 찾아야됨

        if search_input.is_displayed() and search_icon.is_displayed():
            print("검색창 정상 표시")
        else:
            print("검색창 표시 안됨")
            pytest.fail("검색창 UI 요소 화면에 표시되지 않음")

    except TimeoutException:
        print("검색창 요소를 찾지 못함")
        pytest.fail("검색창 UI 요소 탐색 실패")

# ----------------------- 003 -----------------------
@pytest.mark.ui
@pytest.mark.medium

def test_custom_003_agent_top_info(login, driver):

    # 에이전트 실행 화면 상단 정보 (로고/이름/사용방법 안내문) 표시 검증

    driver = login("team4@elice.com", "team4elice!@")

    # 대화 목록 컨테이너 기다리고 스크롤해서 항목 모으기
    def collect_chat_items(driver, timeout=15):
        try:
            container = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="virtuoso-item-list"]'))  # ⭐ 요소 찾아야됨
            )
        except TimeoutException:
            print("대화 목록 컨테이너 자체가 없음")
            return []

        chat_items = []
        start_time = time.time()
        while True:
            found = container.find_elements(By.TAG_NAME, "a")  # 실제 각 항목 <a> 태그 확인 필요
            if len(found) > len(chat_items):
                chat_items = found
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
            time.sleep(0.5)
            if time.time() - start_time > timeout:
                break
        return chat_items

    collect_chat_items(driver)

    # TC 목적: 상단 정보 요소 확인
    try:
        logo = driver.find_element(By.CSS_SELECTOR, "img[data-testid='agent-logo']")  # 요소 찾아야됨
        agent_name = driver.find_element(By.CSS_SELECTOR, "h1[data-testid='agent-name']")  # 요소 찾아야됨
        guide_text = driver.find_element(By.CSS_SELECTOR, "p[data-testid='agent-guide']")  # 요소 찾아야됨

        if logo.is_displayed() and agent_name.is_displayed() and guide_text.is_displayed():
            print("에이전트 상단 정보 정상 표시")
        else:
            print("상단 정보 일부 누락")
            pytest.fail("에이전트 상단 정보 표시 실패")

    except TimeoutException:
        print("상단 정보 요소를 찾지 못함")
        pytest.fail("에이전트 상단 정보 탐색 실패")

# ----------------------- 004 -----------------------
@pytest.mark.ui
@pytest.mark.high

def test_custom_004_image_alt_accessibility(login, driver):
    
    # 장애인 배려 UI 접근성 - 이미지 alt 속성 검증
    
    driver = login("team4@elice.com", "team4elice!@")

    # 대화 목록 컨테이너 기다리고 스크롤해서 항목 모으기
    def collect_chat_items(driver, timeout=15):
        try:
            container = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="virtuoso-item-list"]'))  # 요소 찾아야됨
            )
        except TimeoutException:
            print("대화 목록 컨테이너 자체가 없음")
            return []

        chat_items = []
        start_time = time.time()
        while True:
            found = container.find_elements(By.TAG_NAME, "a")  # 실제 각 항목 <a> 태그 확인 필요
            if len(found) > len(chat_items):
                chat_items = found
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
            time.sleep(0.5)
            if time.time() - start_time > timeout:
                break
        return chat_items

    collect_chat_items(driver)

    # 이미지 alt 속성 확인
    images = driver.find_elements(By.TAG_NAME, "img")  # 필요 시 더 구체적 선택자
    missing_alt = [img for img in images if img.get_attribute("alt") == ""]
    if missing_alt:
        print(f"alt 속성 없는 이미지 {len(missing_alt)}개 발견 ❌")
        pytest.fail("접근성 alt 속성 검증 실패")
    else:
        print("모든 이미지 alt 속성 정상")


# ----------------------- 005 -----------------------
@pytest.mark.ui
@pytest.mark.medium

def test_custom_005_agent_localization(login, driver):

    # 에이전트 생성 화면 내 언어 현지화 확인
    driver = login("team4@elice.com", "team4elice!@")

    # 대화 목록 컨테이너 기다리고 스크롤해서 항목 모으기
    def collect_chat_items(driver, timeout=15):
        try:
            container = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="virtuoso-item-list"]'))  # 요소 찾아야됨
            )
        except TimeoutException:
            print("대화 목록 컨테이너 자체가 없음")
            return []

        chat_items = []
        start_time = time.time()
        while True:
            found = container.find_elements(By.TAG_NAME, "a")  # 실제 각 항목 <a> 태그 확인 필요
            if len(found) > len(chat_items):
                chat_items = found
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
            time.sleep(0.5)
            if time.time() - start_time > timeout:
                break
        return chat_items

    collect_chat_items(driver)

    # 에이전트 생성 화면 텍스트 확인
    ui_text_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='agent-ui-text']")  # 요소 찾아야됨
    for el in ui_text_elements:
        text = el.text
        if any(c.isupper() for c in text if c.isalpha()):  # 단순 영어 존재 여부 체크
            print(f"영문 발견: {text} ❌")
            pytest.fail("언어 현지화 미적용")

# ----------------------- 006 -----------------------
@pytest.mark.ui
@pytest.mark.high

def test_custom_006_search_functionality(login, driver):

    # 메인 화면 검색 기능 동작 검증

    driver = login("team4@elice.com", "team4elice!@")

    # 대화 목록 컨테이너 기다리고 스크롤해서 항목 모으기
    def collect_chat_items(driver, timeout=15):
        try:
            container = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="virtuoso-item-list"]'))  # 요소 찾아야됨
            )
        except TimeoutException:
            print("대화 목록 컨테이너 자체가 없음")
            return []

        chat_items = []
        start_time = time.time()
        while True:
            found = container.find_elements(By.TAG_NAME, "a")  # 실제 각 항목 <a> 태그 확인 필요
            if len(found) > len(chat_items):
                chat_items = found
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
            time.sleep(0.5)
            if time.time() - start_time > timeout:
                break
        return chat_items

    collect_chat_items(driver)

    # 검색 입력 후 결과 확인
    try:
        search_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='검색']")  # 요소 찾아야됨
        search_input.send_keys("테스트 키워드")
        search_button = driver.find_element(By.CSS_SELECTOR, "button[data-testid='search-icon']")  # 요소 찾아야됨
        search_button.click()
        time.sleep(1)  # 검색 결과 로딩 대기
        results = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='search-result-item']")  # 요소 찾아야됨
        assert len(results) > 0, "검색 결과 없음"
        print(f"검색 결과 {len(results)}개 정상 표시")
    except TimeoutException:
        print("검색창/버튼/결과 요소 탐색 실패")
        pytest.fail("검색 기능 검증 실패")

# ----------------------- 007 -----------------------
@pytest.mark.ui
@pytest.mark.medium

def test_custom_007_agent_execution_top_info(login, driver):

    # 에이전트 실행 화면 상단 정보 검증 (로고/이름/가이드)

    driver = login("team4@elice.com", "team4elice!@")

    # 대화 목록 컨테이너 기다리고 스크롤해서 항목 모으기
    def collect_chat_items(driver, timeout=15):
        try:
            container = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="virtuoso-item-list"]'))  # 요소 찾아야됨
            )
        except TimeoutException:
            print("대화 목록 컨테이너 자체가 없음")
            return []

        chat_items = []
        start_time = time.time()
        while True:
            found = container.find_elements(By.TAG_NAME, "a")  # 실제 각 항목 <a> 태그 확인 필요
            if len(found) > len(chat_items):
                chat_items = found
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
            time.sleep(0.5)
            if time.time() - start_time > timeout:
                break
        return chat_items

    collect_chat_items(driver)

    # 상단 정보 요소 표시 확인
    logo = driver.find_element(By.CSS_SELECTOR, "img[data-testid='agent-logo']")  # 요소 찾아야됨
    name = driver.find_element(By.CSS_SELECTOR, "h1[data-testid='agent-name']")  # 요소 찾아야됨
    guide = driver.find_element(By.CSS_SELECTOR, "p[data-testid='agent-guide']")  # 요소 찾아야됨
    if logo.is_displayed() and name.is_displayed() and guide.is_displayed():
        print("상단 정보 정상 표시")
    else:
        pytest.fail("상단 정보 표시 실패")

# ----------------------- 008 -----------------------
@pytest.mark.ui
@pytest.mark.medium

def test_custom_008_agent_creation_ui_text(login, driver):

    # 에이전트 생성 화면 내 UI 텍스트 검증
 
    driver = login("team4@elice.com", "team4elice!@")

    # 대화 목록 컨테이너 기다리고 스크롤해서 항목 모으기
    def collect_chat_items(driver, timeout=15):
        try:
            container = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="virtuoso-item-list"]'))  # 요소 찾아야됨
            )
        except TimeoutException:
            print("대화 목록 컨테이너 자체가 없음")
            return []

        chat_items = []
        start_time = time.time()
        while True:
            found = container.find_elements(By.TAG_NAME, "a")  # 실제 각 항목 <a> 태그 확인 필요
            if len(found) > len(chat_items):
                chat_items = found
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
            time.sleep(0.5)
            if time.time() - start_time > timeout:
                break
        return chat_items

    collect_chat_items(driver)

    # UI 텍스트 전체 확인
    ui_text_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='agent-ui-text']")  # 요소 찾아야됨
    for el in ui_text_elements:
        text = el.text.strip()
        if not text:
            pytest.fail("UI 텍스트 일부 누락")
    print("UI 텍스트 모두 정상 표시")
 
