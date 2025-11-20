# test_custom_agent.py

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
import time

def go_to_agent_page(driver, wait):
    # Agent Explorer 클릭 후 Custom Agent 페이지로 이동
    try:
        element = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.MuiListItemButton-root[href='/ai-helpy-chat/agent']"))
        )
    except TimeoutException:
        try:
            element = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//li[a[contains(@href,"/ai-helpy-chat/agent")]]/a'))
            )
        except TimeoutException:
            driver.save_screenshot("artifacts/agent_explorer_not_found.png")
            raise Exception("Agent Explorer 버튼을 찾을 수 없음")
    element.click()
    try:
        wait.until(lambda d: "/agent" in d.current_url)
    except TimeoutException:
        driver.save_screenshot("artifacts/custom_agent_page_not_loaded.png")
        raise Exception("Custom Agent 페이지 URL 확인 실패")

@pytest.mark.usefixtures("driver", "login")
class TestCustomAgent:

    # ---------------- TEST 1: Custom Agent 페이지 진입 ----------------
    @pytest.mark.ui
    @pytest.mark.medium
    def test_open_custom_agent_page(self, driver, login):
        # Agent Explorer 버튼 클릭 후 Custom Agent 페이지 진입 확인
        driver = login()
        wait = WebDriverWait(driver, 20)
        go_to_agent_page(driver, wait)
        print("Agent Explorer 버튼 클릭 완료, Custom Agent 페이지 진입 확인")

    # ---------------- TEST 2: 메인 화면 검색창 표시 확인 ----------------
    @pytest.mark.ui
    @pytest.mark.medium
    def test_main_search_bar_display(self, driver, login):
        # 메인 화면 검색창 존재 확인
        driver = login()
        wait = WebDriverWait(driver, 20)
        go_to_agent_page(driver, wait)

        try:
            wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input.MuiInputBase-input[placeholder='Search AI agents']"))
            )
        except TimeoutException:
            driver.save_screenshot("artifacts/search_input_not_found.png")
            raise Exception("메인 검색창 요소 확인 실패")
        print("메인 화면 검색창 정상 표시됨")

    # ---------------- TEST 3: 에이전트 실행 화면 상단 요소 확인 ----------------
    @pytest.mark.ui
    @pytest.mark.medium
    def test_agent_header_display(self, driver, login):
        # 첫 번째 에이전트 카드 클릭 후 상단 요소 확인
        driver = login()
        wait = WebDriverWait(driver, 20)
        go_to_agent_page(driver, wait)

        retries = 2
        for _ in range(retries):
            try:
                first_card = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-index='0'] a.MuiCard-root"))
                )
                first_card.click()
                break
            except StaleElementReferenceException:
                time.sleep(0.5)
        else:
            driver.save_screenshot("artifacts/first_ai_card_not_found.png")
            raise Exception("첫 번째 AI 카드 찾기 실패")

        try:
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.MuiStack-root.css-143xypo img.MuiAvatar-img")))
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.MuiStack-root.css-143xypo h6.MuiTypography-root")))
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.MuiStack-root.css-143xypo p.MuiTypography-body1")))
        except TimeoutException:
            driver.save_screenshot("artifacts/agent_header_not_found.png")
            raise Exception("에이전트 실행 상단 요소 확인 실패")
        print("에이전트 상단 정보 정상 표시됨")

# ---------------- TEST 4: 이미지 alt 속성 검증 ----------------
@pytest.mark.ui
@pytest.mark.high
def test_agent_images_alt_text(self, driver, login):
    driver = login()
    wait = WebDriverWait(driver, 20)
    go_to_agent_page(driver, wait)

    # 첫 번째 카드 클릭
    try:
        card = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-index='0'] a.MuiCard-root"))
        )
        card.click()
    except TimeoutException:
        raise Exception("첫 번째 AI 카드 찾기 실패")

    # 이미지 alt 체크
    images = wait.until(lambda d: d.find_elements(By.TAG_NAME, "img"))
    missing_alt = []
    empty_alt = []

    for img in images:
        alt = img.get_attribute("alt")
        if alt is None:
            missing_alt.append(img)
        elif alt.strip() == "":
            empty_alt.append(img)

    if missing_alt or empty_alt:
        raise Exception("alt 속성 비정상 이미지 존재함")

    print(f"✅ alt 속성 정상 이미지 수: {len(images)}")


# ---------------- TEST 5: 검색 기능 검증 ----------------
@pytest.mark.function
@pytest.mark.medium
def test_main_screen_search_function(self, driver, login):
    # 메인 화면 검색창 입력 후 결과 확인
    driver = login()
    wait = WebDriverWait(driver, 20)
    go_to_agent_page(driver, wait)

    try:
        search_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.MuiInputBase-input"))
        )
    except TimeoutException:
        driver.save_screenshot("artifacts/search_input_not_found.png")
        raise Exception("검색창 찾기 실패")

    keyword = "생기부"
    search_input.clear()
    search_input.send_keys(keyword + Keys.ENTER)

    try:
        results = wait.until(lambda d: d.find_elements(
            By.XPATH,
            "//div[@data-testid='virtuoso-item-list']//a[contains(@class,'MuiCard-root')]"
        ))
        if not results:
            raise Exception("검색 결과 없음")

        title = results[0].find_element(
            By.XPATH, ".//p[contains(@class,'MuiTypography-body1')]"
        ).text

        if keyword not in title:
            raise Exception("검색 결과 제목에 키워드 없음")

    except Exception as e:
        raise Exception(f"검색 기능 오류: {str(e)}")

    print("✅ 검색 기능 정상 작동")


# ---------------- TEST 6: 새 에이전트 생성 ----------------
def test_create_new_agent(self, driver, login):
    # Custom Agent 페이지에서 새 에이전트 생성
    driver = login()
    wait = WebDriverWait(driver, 20)
    go_to_agent_page(driver, wait)

    # iframe 전환
    try:
        iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe")))
        driver.switch_to.frame(iframe)
    except TimeoutException:
        driver.save_screenshot("artifacts/iframe_not_found.png")
        raise Exception("iframe 찾기 실패")

    retries = 2
    for _ in range(retries):
        try:
            create_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Create')]"))
            )
            create_btn.click()
            break
        except StaleElementReferenceException:
            time.sleep(0.5)
    else:
        driver.save_screenshot("artifacts/create_button_not_found.png")
        raise Exception("Create 버튼 없음")

    # 에이전트 이름 입력 및 저장
    try:
        name_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='agentName']"))
        )
        name_input.send_keys("테스트 에이전트")

        save_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Save')]"))
        )
        save_btn.click()
    except TimeoutException:
        driver.save_screenshot("artifacts/agent_save_failed.png")
        raise Exception("에이전트 입력 or 저장 실패")

    # iframe 종료
    driver.switch_to.default_content()
    print("✅ 새 에이전트 생성 완료")