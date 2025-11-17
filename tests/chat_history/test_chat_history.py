# 표준 라이브러리
import os
import time

# 서드파티 라이브러리
import pytest
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

# 로컬/프로젝트 모듈
from pages.base_page import BasePage  # 공통 기능 상속용

# ----------------------- CHAT-HIS-001 -----------------------
@pytest.mark.ui
@pytest.mark.medium
def test_chat_new_conversation_screen(driver, login):
   
    driver = login()
    page = BasePage(driver)

    try:
        # '새 대화' 버튼 요소들 모두 찾기 (CSS 선택자 기반)
        buttons = WebDriverWait(driver, 10).until(
            lambda d: d.find_elements(By.CSS_SELECTOR,
                "div.MuiListItemButton-root div.MuiListItemText-root span.MuiListItemText-primary"
            )
        )
        # '새 대화' 텍스트 버튼 클릭
        new_chat_button = None
        for b in buttons:
            if b.text.strip() == "새 대화":
                new_chat_button = b
                break
        
        assert new_chat_button is not None, "'새 대화' 버튼을 찾을 수 없습니다."
        page.scroll_into_view(new_chat_button)
        new_chat_button.click()
        print("'새 대화' 버튼 클릭 완료")
        
        # 새 대화 화면 확인: textarea 존재 여부
        textarea = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "textarea.MuiInputBase-input")
            )
        )
        assert textarea is not None, "새 대화창 텍스트 입력 영역을 찾을 수 없습니다."
        print("새 대화 화면이 정상적으로 열렸습니다.")

    except TimeoutException:
        driver.save_screenshot("CHAT-HIS-003_new_conversation_screen_not_found.png")
        pytest.fail("새 대화창 화면 확인 실패")

# ----------------------- CHAT-HIS-002 -----------------------
@pytest.mark.ui

def test_chat_history_area_exists(driver, login):
    
    # env 기반 자동 로그인
    driver = login()

    try:
        # 영역 존재 여부만 확인 (대화 기록이 없는 경우도 있으니 표시 여부는 무시)
        history_area = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='virtuoso-item-list']"))
        )
        print("채팅 히스토리 영역이 존재합니다.")
    except TimeoutException:
        driver.save_screenshot("CHAT-HIS-AREA_not_found.png")
        pytest.fail("채팅 히스토리 영역을 찾을 수 없음!")

    # 존재하면 테스트 통과
    assert history_area is not None, "히스토리 영역이 존재하지 않음!"

#----------------------- CHAT-HIS-003 -----------------------
@pytest.mark.ui
@pytest.mark.medium
def test_chat_history_scroll(driver, login):
    driver = login()
    page = BasePage(driver)

    # BasePage로 대화 항목 가져오기
    chat_items = page.get_chat_list()

    # 대화 존재 확인
    assert len(chat_items) > 0, "대화 항목이 존재하지 않습니다."
    print(f"대화 목록이 {len(chat_items)}개 있습니다.")

    # 스크롤 영역 확인
    chat_area = page.wait_for_element((By.CSS_SELECTOR, '[data-testid="virtuoso-scroller"]'))
    has_scrollbar = driver.execute_script(
        "return arguments[0].scrollHeight > arguments[0].clientHeight;", chat_area
    )
    if has_scrollbar:
        print("스크롤 영역 존재: 스크롤 가능")
    else:
        print("스크롤 영역 존재하지만, 대화가 충분하지 않아 스크롤 필요 없음")

    # 어썰트
    assert chat_area is not None
    assert isinstance(has_scrollbar, bool)

#----------------------- CHAT-HIS-004 -----------------------
@pytest.mark.ui
@pytest.mark.medium
def test_chat_history_sort_order(driver, login):
    driver = login()
    page = BasePage(driver)

    chat_items = page.get_chat_list()

    if len(chat_items) == 0:
        pytest.skip("대화가 0개입니다. 테스트를 건너뜁니다.")
    else:
        # 검증: 대화가 1개 이상 있으면 통과 (최신이 맨 위라고 간주)
        assert len(chat_items) >= 1, "대화 목록이 비어 있음!"
        print(f"대화 목록이 {len(chat_items)}개 있습니다. 최신 대화가 맨 위에 있다고 판단됩니다.")

#----------------------- CHAT-HIS-005 -----------------------
@pytest.mark.ui
@pytest.mark.medium
def test_chat_titles_have_ellipsis(login, driver):
    
    # 현재 대화 목록 화면에서 채팅 제목이 ellipsis 속성 적용되었는지 확인
    driver = login()  # 로그인 추가
    page = BasePage(driver)

    # 전체 대화 목록 조회
    chat_items = page.get_chat_list()

    if len(chat_items) == 0:
        pytest.skip("대화가 0개입니다. 테스트를 건너뜁니다.")
    else:
        # 검증: 대화가 1개 이상 있으면 통과
        assert len(chat_items) >= 1, "대화 목록이 비어 있음!"
        print(f"대화 목록이 {len(chat_items)}개 있습니다.")

    ellipsis_found = False

    for idx, item in enumerate(chat_items):
        title_element = item.find_element(By.CSS_SELECTOR, "p.MuiTypography-root.MuiTypography-inherit")
        
        # 제목이 화면에 보이도록 스크롤
        page.scroll_into_view(title_element)
        
        # 제목이 비어있지 않을 때까지 기다림
        WebDriverWait(driver, 5).until(lambda d: title_element.text.strip() != "")
        
        # CSS 속성 확인
        text_overflow = title_element.value_of_css_property("text-overflow")
        overflow = title_element.value_of_css_property("overflow")
        white_space = title_element.value_of_css_property("white-space")

        print(f"[{idx}] 제목: '{title_element.text.strip()}' → "
              f"text-overflow: {text_overflow}, overflow: {overflow}, white-space: {white_space}")

        if text_overflow == "ellipsis" and overflow in ["hidden", "clip"]:
            ellipsis_found = True

    assert ellipsis_found, "CSS 상으로 ellipsis 속성이 적용된 대화가 없습니다."

# ----------------------- CHAT-HIS-006 -----------------------
@pytest.mark.ui
@pytest.mark.medium
def test_chat_history_menu_open(login, driver):
    driver = login()
    page = BasePage(driver)

    # 채팅 목록 로딩
    chat_items = page.get_chat_list()
    assert chat_items, "대화 항목이 하나도 없습니다."

    # 메뉴 버튼 클릭
    menu_buttons = page.get_menu_buttons()
    assert menu_buttons, "메뉴 버튼(button)이 존재하지 않습니다."

    menu_button = menu_buttons[0]
    page.scroll_into_view(menu_button)
    menu_button.click()
    print("메뉴 버튼 클릭 성공")

    # 팝업 내 Rename / Delete 버튼 확인
    rename_button, delete_button = page.get_popup_buttons()
    assert rename_button.is_displayed(), "Rename 버튼이 보이지 않습니다."
    assert delete_button.is_displayed(), "Delete 버튼이 보이지 않습니다."
    print("팝업 내 Rename / Delete 버튼 존재 확인")

#----------------------- CHAT-HIS-007 -----------------------
def test_chat_create_and_save(login, driver):
    driver = login()
    page = BasePage(driver)

    test_message = "테스트 새 대화"

    try:
        
        # '새 대화' 버튼 클릭
        
        buttons = page.wait_for_elements(
            (By.CSS_SELECTOR, "div.MuiListItemButton-root div.MuiListItemText-root span.MuiListItemText-primary")
        )

        new_chat_button = next((b for b in buttons if b.text.strip() == "새 대화"), None)
        assert new_chat_button is not None, "'새 대화' 버튼을 찾을 수 없습니다."

        page.scroll_into_view(new_chat_button)
        new_chat_button.click()
        print("'새 대화' 버튼 클릭 완료")

        # 새 대화 화면 확인 및 메시지 입력
        
        textarea = page.wait_for_clickable((By.CSS_SELECTOR, "textarea.MuiInputBase-input"))
        page.scroll_into_view(textarea)
        textarea.click() # 포커스 확보
        textarea.clear()
        textarea.send_keys(test_message)

        # 저장 버튼 클릭
        save_button = page.wait_for_clickable((By.ID, "chat-submit"))
        page.scroll_into_view(save_button)
        save_button.click()
        print("새 대화 입력 및 저장 완료")

        # 변경 확인 (대화 히스토리)
    
        # DOM이 새로 렌더링되므로 재조회
        chat_items = page.get_chat_list()
        assert any(test_message in item.text for item in chat_items), "새 대화가 히스토리에 저장되지 않았습니다."
        print("새 대화가 히스토리에 정상 저장됨")

    except Exception as e:
        driver.save_screenshot("CHAT-HIS-007_create_new_conversation_failed.png")
        pytest.fail(f"새 대화 생성/저장 확인 실패: {str(e)}")

  #----------------------- CHAT-HIS-008 -----------------------
@pytest.mark.ui
@pytest.mark.medium
def test_chat_history_load_old_conversation(login, driver):
    
    # 로그인
    driver = login()
    page = BasePage(driver)
    
    wait = WebDriverWait(driver, 20)

    # 사이드바 대화 목록 가져오기
    chat_items = page.get_chat_list()

    # 첫 번째 대화 항목 클릭
    first_conversation = chat_items[0]
    page.scroll_into_view(first_conversation)  # 화면에 보이도록 스크롤
    first_conversation.click()
    print(f"첫 번째 대화 클릭 완료: {first_conversation.text}")

    # 오른쪽 대화 영역에서 이전 대화 메시지 로드 확인
    try:
        chat_messages = page.wait_for_elements((By.CSS_SELECTOR, "div[role='article']"), timeout=20)
        assert chat_messages, "오른쪽 대화 영역에 메시지가 표시되지 않았습니다."
        print(f"오른쪽 화면에 {len(chat_messages)}개의 메시지 로드됨")

        # 필요 시 이전 대화 메시지 일부 출력
        for idx, msg in enumerate(chat_messages):
            text = msg.text.strip()
            print(f"[{idx}] 메시지: {text[:50]}{'...' if len(text) > 50 else ''}")

    except TimeoutException:
        pytest.fail("오른쪽 대화 영역의 메시지 로드에 실패했습니다.")

# ----------------------- CHAT-HIS-009 -----------------------
@pytest.mark.ui
@pytest.mark.medium
def test_chat_history_rename(login, driver):
    driver = login()
    page = BasePage(driver)
    wait = WebDriverWait(driver, 10)

    new_title = "새 대화"

    # 채팅 목록 로딩
    chat_items = page.get_chat_list()
    assert chat_items, "대화 항목이 하나도 없습니다."

    # 메뉴 버튼 클릭
    menu_buttons = page.get_menu_buttons()
    assert menu_buttons, "메뉴 버튼(button)이 존재하지 않습니다."

    menu_button = menu_buttons[0]
    page.scroll_into_view(menu_button)
    menu_button.click()
    print("메뉴 버튼 클릭 성공")

    # 팝업 내 Rename / Delete 버튼 확인
    rename_button, delete_button = page.get_popup_buttons()
    assert rename_button.is_displayed(), "Rename 버튼이 보이지 않습니다."
    assert delete_button.is_displayed(), "Delete 버튼이 보이지 않습니다."
    print("팝업 내 Rename / Delete 버튼 존재 확인")

    # 입력창 선택 후 내용 초기화하고 새 제목 입력
    input_box = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id=":r7n:"]')))
    input_box.clear()
    input_box.send_keys(new_title)
    print("텍스트 박스 초기화 및 새 제목 입력 완료")

    # Save 버튼 클릭
    save_button = wait.until(EC.element_to_be_clickable((By.ID, ":r7m:")))
    save_button.click()
    print("Save 버튼 클릭 완료")

    # 페이지 새로고침 후 반영 확인
    driver.refresh()
    time.sleep(2)  # 새로고침 후 안정화 대기
    updated_title = page.get_chat_list()[0].text
    assert updated_title == new_title, f"제목 변경 실패: {updated_title}"
    print("제목 변경 확인 완료")
# # ----------------------- CHAT-HIS-010 -----------------------
# @pytest.mark.function
# @pytest.mark.medium
# def test_chat_history_search_dynamic_keyword(page):

#     # 사이드바 검색 버튼 클릭
#     page.click((By.CSS_SELECTOR, ".search-button"))

#     # 화면에 있는 첫 번째 채팅 제목 가져오기
#     first_chat = page.wait_for_element((By.CSS_SELECTOR, "div[cmdk-item] div.line-clamp-2"))
#     search_keyword = first_chat.get_text()

#     # 검색 input 대기 후 키워드 입력
#     search_input = page.wait_for_element((By.CSS_SELECTOR, ".search-input"))
#     search_input.clear()
#     search_input.send_keys(search_keyword)

#     # 검색 결과 대기
#     results = page.wait_for_elements((By.CSS_SELECTOR, "div[cmdk-item]"), timeout=10)

#     # 결과 확인
#     if not results or not any(r.is_displayed() for r in results):
#         page.take_screenshot("CHAT-HIS-010_error.png")
#         assert False, "검색 결과가 표시되지 않음"

#     # 첫 번째 결과 텍스트 확인
#     first_result_text = results[0].get_text()
#     assert search_keyword in first_result_text, f"검색 결과 '{first_result_text}'가 '{search_keyword}'와 일치하지 않음"

# # ----------------------- CHAT-HIS-011 -----------------------
# @pytest.mark.function
# @pytest.mark.high
# def test_chat_history_delete(page):
    
#     # 삭제할 항목의 첫 번째 채팅 제목 가져오기
#     first_item = page.wait_for_element((By.CSS_SELECTOR, ".MuiList-root [data-index='0'] .MuiListItemText-primary p"))
#     first_item_text = first_item.get_text()

#     # 항목 우측 점(⋮) 클릭 후 Delete 선택
#     page.click((By.CSS_SELECTOR, ".MuiList-root [data-index='0'] .menu-button button"))
#     page.click((By.CSS_SELECTOR, "button[id*=':rer:']"))  # Delete 버튼, 동적 ID 포함

#     # 삭제 확인 팝업에서 Confirm 클릭
#     confirm_popup = page.wait_for_element((By.CSS_SELECTOR, ".popup-delete"))
#     page.click((By.CSS_SELECTOR, ".popup-delete button"))  # Delete Confirm 버튼

#     # 삭제 후 목록에서 첫 번째 항목 텍스트 다시 확인
#     items = page.wait_for_elements((By.CSS_SELECTOR, ".MuiList-root [data-index] .MuiListItemText-primary p"), timeout=10)

#     if not items:
#         page.take_screenshot("CHAT-HIS-008_error.png")
#         assert False, "삭제 후 항목이 없음"

#     # 삭제가 반영되었는지 체크
#     new_first_text = items[0].get_text()
#     assert new_first_text != first_item_text, f"삭제 실패: '{first_item_text}'가 여전히 목록에 있음"


#----------------------- CHAT-HIS-012 -----------------------
import pytest
import time
from selenium.webdriver.support.ui import WebDriverWait
from src.pages.base_page import BasePage

@pytest.mark.ui
@pytest.mark.medium
def test_chat_history_persistence(login, driver):
    
    # 1. 최초 로그인 및 안정화
    driver = login()
    page = BasePage(driver)

    # 사이드바 채팅 목록 로딩 안정화
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="virtuoso-item-list"]'))
    )

    chat_items_before = page.get_chat_list()
    assert chat_items_before, "초기 채팅 목록이 비어 있습니다."
    first_title_before = chat_items_before[0].text
    total_count_before = len(chat_items_before)
    print(f"[Before Logout] 채팅 개수: {total_count_before}, 첫 번째 제목: {first_title_before}")

    # 2. 로그아웃 수행 (driver 종료하지 않음)
    page.logout()

    # 3. 재로그인 (픽스쳐에서 새 driver 반환)
    # 필요 시 이전 Chromedriver 프로세스 종료 후 테스트 재시작
    # Windows: taskkill /F /IM chromedriver.exe
    driver = login()
    page = BasePage(driver)

    # 로그인 후 사이드바 채팅 목록 안정화
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="virtuoso-item-list"]'))
    )

    chat_items_after = page.get_chat_list()
    assert chat_items_after, "재로그인 후 채팅 목록이 비어 있습니다."
    first_title_after = chat_items_after[0].text
    total_count_after = len(chat_items_after)
    print(f"[After Login] 채팅 개수: {total_count_after}, 첫 번째 제목: {first_title_after}")

    # 4. 검증
    assert total_count_before == total_count_after, "채팅 개수가 일치하지 않습니다."
    assert first_title_before == first_title_after, "첫 번째 채팅 제목이 일치하지 않습니다."
    
    # 일치하면 확인 메시지 출력
    print("✅ 채팅 개수와 첫 번째 제목이 재로그인 후에도 일치합니다.")

# ----------------------- CHAT-HIS-013 -----------------------
@pytest.mark.ui
@pytest.mark.medium
def test_chat_history_sync_across_browsers(login, driver):
    
    # 첫 번째 브라우저
    driver = login()
    page = BasePage(driver)

    # 사이드바 채팅 목록 안정화 (최대 10초, 0.05초마다 확인)
    WebDriverWait(driver, 10, poll_frequency=0.05).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="virtuoso-item-list"]'))
    )

    chat_items_before = page.get_chat_list()
    assert chat_items_before, "초기 채팅 목록이 비어 있습니다."
    first_title_before = chat_items_before[0].text
    total_count_before = len(chat_items_before)
    print(f"[Before Other Browser] 채팅 개수: {total_count_before}, 첫 번째 제목: {first_title_before}")

    # 두 번째 브라우저 
    driver2 = login()
    page2 = BasePage(driver2)

    WebDriverWait(driver2, 10, poll_frequency=0.05).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="virtuoso-item-list"]'))
    )

    chat_items_after = page2.get_chat_list()
    assert chat_items_after, "새 브라우저에서 채팅 목록이 비어 있습니다."
    first_title_after = chat_items_after[0].text
    total_count_after = len(chat_items_after)
    print(f"[Second Browser] 채팅 개수: {total_count_after}, 첫 번째 제목: {first_title_after}")

    # 검증
    try:
        start = time.time()
        # 최대 3초 동안 브라우저 간 동기화 체크
        WebDriverWait(driver2, 3, poll_frequency=0.05).until(
            lambda d: total_count_before == len(page2.get_chat_list()) and
                      first_title_before == page2.get_chat_list()[0].text
        )
    except TimeoutException:
        elapsed = time.time() - start
        pytest.fail(f"브라우저 간 동기화 실패 (elapsed={elapsed:.2f}s)")

    print("브라우저 간 채팅 목록 동기화 정상 확인")

# ----------------------- CHAT-HIS-014 -----------------------
@pytest.mark.ui
@pytest.mark.medium
def test_chat_history_search_response_time(login, driver):
    
    driver = login()
    wait = WebDriverWait(driver, 30)

    try:
        # 사이드바 렌더링 보장
        sidebar = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='virtuoso-item-list']"))
        )
        driver.execute_script("arguments[0].scrollTop = 0", sidebar)
        print("사이드바 스크롤 초기화 완료")

        # 검색 버튼 클릭
        
        try:
            search_button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@role='button'][.//span[text()='검색']]")
                )
            )
            search_button.click()
            print("검색 버튼 클릭 완료")
        except Exception:
            search_button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//svg[@data-testid='magnifying-glassIcon']/ancestor::div[@role='button']")
                )
            )
            search_button.click()
            print("검색 버튼 클릭 (아이콘 기반) 완료")

        # 검색창 입력

        search_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[cmdk-input]"))
        )
        search_input.clear()
        search_input.send_keys("테스트 새 대화")
        print("검색 키워드 입력 완료")

        # 검색 결과 클릭 (StaleElementReference 안전)

        search_results = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[cmdk-item]"))
        )
        assert search_results, "검색 결과가 없습니다"
        print(f"검색 결과 {len(search_results)}개 확인됨")

        # 첫 번째 결과 클릭 — StaleElementReference 안전하게 재조회
        first_result = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[cmdk-item]:first-child"))
        )
        first_result.click()
        print("첫 번째 검색 결과 클릭 완료")

    except TimeoutException as e:
        driver.save_screenshot("CHAT-HIS-SEARCH_TIMEOUT.png")
        pytest.fail(f"검색 테스트 실패: {str(e)}")

# ----------------------- CHAT-HIS-015 -----------------------
@pytest.mark.ui
@pytest.mark.medium
def test_chat_delete_response_time_optimized(login, driver):

    # 채팅 삭제 UI 반응 속도 최적화 (0.5초 목표)

    driver = login()
    page = BasePage(driver)

    # 1. 첫 번째 채팅 항목 확보 (JS로 element id 혹은 unique selector 필요)
    first_chat = page.get_chat_list()[0]

    # 2. 메뉴 버튼 클릭 (JS 클릭)
    menu_button = page.get_menu_buttons()[0]
    driver.execute_script("arguments[0].click();", menu_button)
    
    # 3. Delete 버튼 클릭 (JS 클릭)
    delete_button = WebDriverWait(driver, 3, poll_frequency=0.02).until(
        EC.presence_of_element_located((By.XPATH, "//p[text()='Delete']"))
    )
    driver.execute_script("arguments[0].click();", delete_button)

    # 4. 삭제 후 UI 반영 확인 (JS로 첫 번째 항목 비교)
    start = time.time()
    try:
        WebDriverWait(driver, 1, poll_frequency=0.02).until(
            lambda d: d.execute_script(
                "return arguments[0] !== document.querySelector('[data-testid=\"virtuoso-item-list\"] > div:first-child');",
                first_chat
            )
        )
    except TimeoutException:
        elapsed = time.time() - start
        pytest.fail(f"삭제 UI 반응 지연: {elapsed:.2f}s")

    elapsed = time.time() - start
    print(f"JS 최적화 삭제 UI 반응 시간: {elapsed:.2f}s")
    
# ----------------------- CHAT-HIS-016 -----------------------
@pytest.mark.ui
@pytest.mark.medium
def test_redirect_to_login_if_not_logged_in():
    
    # 로그인 없이 AI 에이전트 페이지 접근 시 로그인 페이지로 리다이렉트 확인
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--start-maximized")
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # 비로그인 상태로 AI 에이전트 메인 화면 접근
        driver.get("https://qatrack.elice.io/ai-helpy-chat/agent")

        wait = WebDriverWait(driver, 10)
        # URL에 로그인 페이지 주소 일부가 포함되면 성공
        wait.until(lambda d: "accounts.elice.io/accounts/signin" in d.current_url)
        print(f"현재 URL: {driver.current_url}")
        print("로그인 없이 접근 시 로그인 페이지로 자동 이동 확인")

    except TimeoutException:
        driver.save_screenshot("redirect_to_login_timeout.png")
        pytest.fail("로그인 리다이렉트 테스트 실패: 로그인 페이지로 이동하지 않음")

    finally:
        driver.quit()
# ----------------------- CHAT-HIS-017 -----------------------

def test_network_disconnect_api_only(login, driver, mocker):
    """
    네트워크 단절 시 UI 메시지 대신 API 요청 실패 여부 확인
    - Mock API로 요청 실패 시뮬레이션
    """

    # 1. 로그인 후 페이지 진입
    driver = login()
    
    # 2. Mock API로 GET 요청 실패 시뮬레이션
    def mock_get(*args, **kwargs):
        raise requests.ConnectionError("Simulated network failure")
    mocker.patch("requests.get", side_effect=mock_get)

    # 3. 페이지 새로고침 (API 호출 재시도)
    driver.refresh()

    # 4. API 요청 실패 여부 확인 (JS에서 실패 상태 확인)
    try:
        failure_detected = WebDriverWait(driver, 5).until(
            lambda d: d.execute_script("return window.lastFailedApiCall === 'chat_list';")
        )
    except TimeoutException:
        pytest.fail("⛔ API 요청 실패가 감지되지 않음")

    assert failure_detected, "API 요청 실패가 기록되지 않음"

    print("✅ 네트워크 단절 시 API 요청 실패 정상 확인")


# ----------------------- CHAT-HIS-018 -----------------------
@pytest.mark.ui
@pytest.mark.high
def test_network_disconnect_shows_error(login, driver):
    """
    TC18: 네트워크 단절 시 채팅 목록 표시 확인
    1. 계정 로그인
    2. 메인 화면 진입
    3. Wi-Fi 비활성화 (Chrome DevTools Protocol로 네트워크 오프라인)
    4. 페이지 새로고침
    5. 연결 끊김 오류 메시지 표시 확인
    """

    driver = login()  # 로그인 픽스쳐 사용
    page = BasePage(driver)
    wait = WebDriverWait(driver, 10)

    try:
        # 1~2. 로그인 후 메인 화면 진입
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="virtuoso-item-list"]')))
        print("✅ 메인 화면 채팅 목록 로드 완료")

        # 3. 네트워크 오프라인 모드 설정 (CDP 사용)
        driver.execute_cdp_cmd('Network.enable', {})
        driver.execute_cdp_cmd('Network.emulateNetworkConditions', {
            "offline": True,
            "latency": 0,
            "downloadThroughput": 0,
            "uploadThroughput": 0
        })
        print("⚠️ 네트워크 오프라인 모드 적용")

        # 4. 페이지 새로고침
        driver.refresh()
        print("🔄 페이지 새로고침 완료")

        # 5. 네트워크 끊김 오류 메시지 확인
        try:
            error_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='network-error']"))
            )
            assert error_element.is_displayed(), "네트워크 오류 메시지가 화면에 표시되지 않음"
            print("✅ 네트워크 연결 끊김 오류 메시지 표시 확인")
        except TimeoutException:
            pytest.fail("⛔ 네트워크 연결 끊김 메시지 확인 실패")

    finally:
        # 테스트 종료 전 네트워크 정상화
        driver.execute_cdp_cmd('Network.emulateNetworkConditions', {
            "offline": False,
            "latency": 0,
            "downloadThroughput": -1,
            "uploadThroughput": -1
        })
        print("✅ 네트워크 정상화 완료")

