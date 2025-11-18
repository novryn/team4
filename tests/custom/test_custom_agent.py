# test_custom_agent.py
import pytest
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

# ---------------- TEST 1: Custom Agent 페이지 진입 ----------------
@pytest.mark.ui
@pytest.mark.medium
def test_open_custom_agent_page(driver, login):
    
    # 로그인 후 Agent Explorer → Custom Agent 버튼 클릭 → Custom Agent 페이지 URL 확인
    
    driver = login()
    wait = WebDriverWait(driver, 20)

    # Agent Explorer 버튼 클릭 (CSS → XPath fallback)
    try:

        
        element = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a.MuiListItemButton-root[href='/ai-helpy-chat/agent']")
            )
        )
    except:
        try:
            element = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//li[a[contains(@href,"/ai-helpy-chat/agent")]]/a')
                )
            )
        except:
            driver.save_screenshot("artifacts/agent_explorer_not_found.png")
            pytest.fail("Agent Explorer 버튼을 찾을 수 없음")

    element.click()
    print("Agent Explorer 버튼 클릭 완료")

    # URL 체크
    try:
        wait.until(lambda d: "/agent" in d.current_url)
    except:
        driver.save_screenshot("artifacts/custom_agent_page_not_loaded.png")
        pytest.fail("Custom Agent 페이지 URL 확인 실패")

# ---------------- TEST 2: 메인 화면 검색창 표시 확인 ----------------
@pytest.mark.ui
@pytest.mark.medium
def test_main_search_bar_display(driver, login):
    
    # 로그인 후 메인 화면 진입 → 검색창(입력 필드 + 검색 아이콘) 노출 여부 확인
    
    driver = login()
    wait = WebDriverWait(driver, 20)

    # Agent Explorer 버튼 클릭
    try:
        agent_button = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a.MuiListItemButton-root[href='/ai-helpy-chat/agent']")
            )
        )
    except:
        try:
            agent_button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//li[a[contains(@href,"/ai-helpy-chat/agent")]]/a')
                )
            )
        except:
            driver.save_screenshot("artifacts/agent_explorer_not_found.png")
            pytest.fail("Agent Explorer 버튼을 찾을 수 없음")

    agent_button.click()

    # 검색창 표시 확인
    try:
        search_input = wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "input.MuiInputBase-input[placeholder='Search AI agents']")
            )
        )
    except:
        driver.save_screenshot("artifacts/search_input_not_found.png")
        pytest.fail("메인 화면 검색창 요소를 찾을 수 없음")

    print("✅ 메인 화면 검색창 정상 표시됨")

# ---------------- TEST 3: 에이전트 실행 화면 상단 요소 확인 ----------------
@pytest.mark.ui
@pytest.mark.medium
def test_agent_header_display(driver, login):
    
    # Custom Agent 초기 페이지에서 첫 번째 AI 에이전트 선택 → 에이전트 실행 화면 상단 요소(로고, 제목, 설명) 표시 확인
    
    driver = login()
    wait = WebDriverWait(driver, 20)

    # Agent Explorer 버튼 클릭
    try:
        agent_button = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a.MuiListItemButton-root[href='/ai-helpy-chat/agent']")
            )
        )
    except:
        try:
            agent_button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//li[a[contains(@href,"/ai-helpy-chat/agent")]]/a')
                )
            )
        except:
            driver.save_screenshot("artifacts/agent_explorer_not_found.png")
            pytest.fail("Agent Explorer 버튼을 찾을 수 없음")

    agent_button.click()

    # 첫 번째 AI 카드 클릭
    try:
        first_card = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div[data-index='0'] a.MuiCard-root")
            )
        )
    except:
        driver.save_screenshot("artifacts/first_ai_card_not_found.png")
        pytest.fail("첫 번째 AI 카드 요소를 찾을 수 없음")

    first_card.click()

    # 상단 로고, 제목, 설명 확인
    try:
        logo = wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.MuiStack-root.css-143xypo img.MuiAvatar-img")
            )
        )
        title = wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.MuiStack-root.css-143xypo h6.MuiTypography-root")
            )
        )
        description = wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.MuiStack-root.css-143xypo p.MuiTypography-body1")
            )
        )
    except:
        driver.save_screenshot("artifacts/agent_header_not_found.png")
        pytest.fail("에이전트 실행 화면 상단 요소(로고/제목/설명)를 찾을 수 없음")

    print("✅ 에이전트 실행 화면 상단 정보(로고/제목/설명) 정상 표시됨")
    
# ---------------- TEST 4: 에이전트 실행 화면 이미지 alt 속성 검증 ----------------
@pytest.mark.ui
@pytest.mark.high
def test_agent_images_alt_text(driver, login):
    
    # 첫 번째 AI 에이전트 실행 → 실행 화면 내 모든 이미지(<img>) alt 속성 확인
    # alt 존재 여부 → 빈 문자열(alt="") 아님
    
    driver = login()  # 로그인 후 driver 반환
    wait = WebDriverWait(driver, 20)

    # Agent Explorer 버튼 클릭
    try:
        agent_button = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a.MuiListItemButton-root[href='/ai-helpy-chat/agent']")
            )
        )
    except:
        try:
            agent_button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//li[a[contains(@href,"/ai-helpy-chat/agent")]]/a')
                )
            )
        except:
            driver.save_screenshot("artifacts/agent_explorer_not_found.png")
            pytest.fail("Agent Explorer 버튼을 찾을 수 없음")
    agent_button.click()

    # 첫 번째 AI 카드 클릭
    try:
        first_card = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div[data-index='0'] a.MuiCard-root")
            )
        )
    except:
        try:
            first_card = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id=":ra:"]/div/div/div[2]/div/div[2]/div/div[2]/div/div[1]')
                )
            )
        except:
            driver.save_screenshot("artifacts/first_ai_card_not_found.png")
            pytest.fail("첫 번째 AI 카드 요소를 찾을 수 없음")
    first_card.click()

    # 실행 화면 내 모든 <img> 수집
    try:
        images = wait.until(lambda d: d.find_elements(By.TAG_NAME, "img"))
        if not images:
            raise Exception("화면 내 이미지가 존재하지 않음")
    except Exception as e:
        driver.save_screenshot("artifacts/no_images_found.png")
        pytest.fail(f"이미지 수집 실패: {str(e)}")

    # alt 속성 존재 및 빈 문자열 확인
    missing_alt = []
    empty_alt = []
    for img in images:
        alt = img.get_attribute("alt")
        if alt is None:
            missing_alt.append(img)
        elif alt.strip() == "":
            empty_alt.append(img)

    if missing_alt or empty_alt:
        driver.save_screenshot("artifacts/images_alt_issue.png")
        msg = f"alt 속성 없는 이미지: {len(missing_alt)}, 빈 alt 이미지: {len(empty_alt)}"
        pytest.fail(msg)

    print(f"✅ 모든 이미지 alt 속성 정상: 총 이미지 {len(images)}개 확인됨")
    
# ---------------- TEST 5: 메인 화면 검색 기능 검증 ----------------
@pytest.mark.function
@pytest.mark.medium
def test_main_screen_search_function(driver, login):
    
    # 검색창에 '생기부' 입력 후 엔터 → 검색 결과 목록 중 첫 번째 카드 제목에 '생기부' 포함 여부 확인

    driver = login()
    wait = WebDriverWait(driver, 20)

    # Agent Explorer 버튼 클릭
    try:
        agent_explorer_btn = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a.MuiListItemButton-root[href='/ai-helpy-chat/agent']")
            )
        )
    except:
        try:
            agent_explorer_btn = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//li[a[contains(@href,"/ai-helpy-chat/agent")]]/a')
                )
            )
        except:
            driver.save_screenshot("artifacts/agent_explorer_not_found.png")
            pytest.fail("Agent Explorer 버튼을 찾을 수 없음")
    agent_explorer_btn.click()
    print("[Agent Explorer] 클릭 완료")

    # 검색창 찾기
    try:
        search_input = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input.MuiInputBase-input")
            )
        )
    except:
        try:
            search_input = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id=":r24:"]')
                )
            )
        except:
            driver.save_screenshot("artifacts/search_input_not_found.png")
            pytest.fail("검색창 요소를 찾을 수 없음")

    # 검색어 입력
    search_keyword = "생기부"
    search_input.clear()
    search_input.send_keys(search_keyword + Keys.ENTER)
    print(f"[검색창] '{search_keyword}' 입력 후 엔터")

    # 검색 결과 확인
    try:
        results = wait.until(
            lambda d: d.find_elements(
                By.XPATH,
                "//div[@data-testid='virtuoso-item-list']//a[contains(@class,'MuiCard-root')]"
            )
        )
        if not results:
            raise Exception("검색 결과 없음")
        
        first_card_title = results[0].find_element(
            By.XPATH, ".//p[contains(@class,'MuiTypography-body1')]"
        ).text

        assert search_keyword in first_card_title, f"첫 번째 카드 제목에 '{search_keyword}' 없음"
    except Exception as e:
        driver.save_screenshot("artifacts/search_results_check_failed.png")
        pytest.fail(f"검색 결과 확인 실패: {str(e)}")

    print(f"✅ 검색 결과 정상 표시 및 첫 번째 카드 제목에 '{search_keyword}' 포함됨")
    
# ---------------- TEST 6:  ----------------
def test_create_new_agent(driver, login):
    driver = login()
    wait = WebDriverWait(driver, 20)

    try:
        # 1. Agent Explorer 버튼 클릭
        try:
            agent_explorer_btn = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "a.MuiListItemButton-root[href='/ai-helpy-chat/agent']")
                )
            )
        except:
            try:
                agent_explorer_btn = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//li[a[contains(@href,"/ai-helpy-chat/agent")]]/a')
                    )
                )
            except:
                driver.save_screenshot("artifacts/agent_explorer_not_found.png")
                pytest.fail("Agent Explorer 버튼을 찾을 수 없음")

        agent_explorer_btn.click()
        print("[Agent Explorer] 클릭 완료")

        # 2. URL 체크
        try:
            wait.until(lambda d: "/agent" in d.current_url)
            print("Custom Agent 페이지 진입 확인 ✅")
        except TimeoutException:
            driver.save_screenshot("artifacts/custom_agent_page_not_loaded.png")
            pytest.fail("Custom Agent 페이지 URL 확인 실패")

        # 3. iframe 전환
        try:
            iframe = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe"))
            )
            driver.switch_to.frame(iframe)
            print("iframe 전환 완료 ✅")
        except TimeoutException:
            pytest.fail("Custom Agent 페이지 iframe을 찾을 수 없음")

        # 4. Create 버튼 클릭
        try:
            create_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Create')]"))
            )
            create_btn.click()
            print("Create 버튼 클릭 완료 ✅")
        except TimeoutException:
            driver.save_screenshot("artifacts/create_button_not_found.png")
            pytest.fail("Create 버튼을 찾을 수 없음")

        # 5. 새 에이전트 입력 후 저장
        try:
            name_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='agentName']"))
            )
            name_input.send_keys("테스트 에이전트")

            save_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Save')]"))
            )
            save_btn.click()
            print("새 에이전트 저장 완료 ✅")
        except TimeoutException:
            driver.save_screenshot("artifacts/agent_input_form_not_found.png")
            pytest.fail("에이전트 입력 폼 없음")

        # 6. iframe 종료
        driver.switch_to.default_content()

    finally:
        driver.quit()
        print("브라우저 종료 ✅")
