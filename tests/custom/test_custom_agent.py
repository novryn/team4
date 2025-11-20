# test_custom_agent.py

import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

@pytest.mark.usefixtures("driver", "login")
class TestCustomAgent:

    # ---------------- TEST 1: Custom Agent 페이지 진입 ----------------
    @pytest.mark.ui
    @pytest.mark.medium
    def test_open_custom_agent_page(self, driver, login):

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
    def test_main_search_bar_display(self, driver, login):

        driver = login()
        wait = WebDriverWait(driver, 20)

        # Agent Explorer 클릭
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
            wait.until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "input.MuiInputBase-input[placeholder='Search AI agents']")
                )
            )
        except:
            driver.save_screenshot("artifacts/search_input_not_found.png")
            pytest.fail("메인 검색창 요소 확인 실패")

        print("✅ 메인 화면 검색창 정상 표시됨")


    # ---------------- TEST 3: 에이전트 실행 화면 상단 요소 확인 ----------------
    @pytest.mark.ui
    @pytest.mark.medium
    def test_agent_header_display(self, driver, login):

        driver = login()
        wait = WebDriverWait(driver, 20)

        # Agent Explorer 클릭
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

        # 첫 번째 카드 클릭
        try:
            first_card = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "div[data-index='0'] a.MuiCard-root")
                )
            )
        except:
            driver.save_screenshot("artifacts/first_ai_card_not_found.png")
            pytest.fail("첫 번째 AI 카드 찾기 실패")

        first_card.click()

        # 상단 요소 표시 확인
        try:
            wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.MuiStack-root.css-143xypo img.MuiAvatar-img")))
            wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.MuiStack-root.css-143xypo h6.MuiTypography-root")))
            wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.MuiStack-root.css-143xypo p.MuiTypography-body1")))
        except:
            driver.save_screenshot("artifacts/agent_header_not_found.png")
            pytest.fail("에이전트 실행 상단 요소(로고/제목/설명) 확인 실패")

        print("✅ 에이전트 상단 정보 정상 표시됨")


    # ---------------- TEST 4: 이미지 alt 속성 검증 ----------------
    @pytest.mark.ui
    @pytest.mark.high
    def test_agent_images_alt_text(self, driver, login):

        driver = login()
        wait = WebDriverWait(driver, 20)

        # Agent Explorer 클릭
        try:
            btn = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "a.MuiListItemButton-root[href='/ai-helpy-chat/agent']")
                )
            )
        except:
            try:
                btn = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//li[a[contains(@href,"/ai-helpy-chat/agent")]]/a')
                    )
                )
            except:
                pytest.fail("Agent Explorer 버튼 찾기 실패")

        btn.click()

        # 첫 번째 카드 클릭
        try:
            card = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "div[data-index='0'] a.MuiCard-root")
                )
            )
        except:
            pytest.fail("첫 번째 AI 카드 찾기 실패")

        card.click()

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
            pytest.fail("alt 속성 비정상 이미지 존재함")

        print(f"✅ alt 속성 정상 이미지 수: {len(images)}")


    # ---------------- TEST 5: 검색 기능 검증 ----------------
    @pytest.mark.function
    @pytest.mark.medium
    def test_main_screen_search_function(self, driver, login):

        driver = login()
        wait = WebDriverWait(driver, 20)

        # Agent Explorer 클릭
        try:
            btn = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "a.MuiListItemButton-root[href='/ai-helpy-chat/agent']")
                )
            )
        except:
            try:
                btn = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//li[a[contains(@href,"/ai-helpy-chat/agent")]]/a')
                    )
                )
            except:
                pytest.fail("Agent Explorer 버튼 찾기 실패")

        btn.click()

        # 검색창 찾기
        try:
            search_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.MuiInputBase-input"))
            )
        except:
            pytest.fail("검색창 찾기 실패")

        # 검색 실행
        keyword = "생기부"
        search_input.clear()
        search_input.send_keys(keyword + Keys.ENTER)

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

            title = results[0].find_element(
                By.XPATH, ".//p[contains(@class,'MuiTypography-body1')]"
            ).text

            assert keyword in title

        except Exception as e:
            pytest.fail(f"검색 기능 오류: {str(e)}")

        print("✅ 검색 기능 정상 작동")


    # ---------------- TEST 6: 새 에이전트 생성 ----------------
    def test_create_new_agent(self, driver, login):

        driver = login()
        wait = WebDriverWait(driver, 20)

        try:
            # 1. Agent Explorer 클릭
            try:
                agent_explorer_btn = wait.until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "a.MuiListItemButton-root[href='/ai-helpy-chat/agent']")
                    )
                )
            except:
                agent_explorer_btn = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//li[a[contains(@href,"/ai-helpy-chat/agent")]]/a')
                    )
                )

            agent_explorer_btn.click()
            print("[Agent Explorer] 클릭 완료")

            # 2. URL 체크
            try:
                wait.until(lambda d: "/agent" in d.current_url)
                print("Custom Agent 페이지 진입 확인 완료")
            except TimeoutException:
                pytest.fail("Custom Agent 페이지 로딩 실패")

            # 3. iframe 전환
            try:
                iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe")))
                driver.switch_to.frame(iframe)
                print("iframe 전환 완료")
            except TimeoutException:
                pytest.fail("iframe 찾기 실패")

            # 4. Create 버튼
            try:
                create_btn = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Create')]"))
                )
                create_btn.click()
                print("Create 버튼 클릭")
            except TimeoutException:
                pytest.fail("Create 버튼 없음")

            # 5. 에이전트 이름 입력
            try:
                name_input = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='agentName']"))
                )
                name_input.send_keys("테스트 에이전트")

                save_btn = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Save')]"))
                )
                save_btn.click()
                print("새 에이전트 저장 완료")
            except TimeoutException:
                pytest.fail("에이전트 입력 or 저장 실패")

            # 6. iframe 종료
            driver.switch_to.default_content()

        finally:
            driver.quit()
            print("브라우저 종료")
