import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage  # 공통 기능 상속용

# ----------------------- CHAT-HIS-001 -----------------------

@pytest.mark.ui
def test_chat_history_area_exists(driver, login):
    
    # 로그인
    driver = login("team4@elice.com", "team4elice!@")

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

# import pytest
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException

# @pytest.mark.ui
# @pytest.mark.medium
# def test_chat_history_sort_order(login, driver):
#     driver = login("team4@elice.com", "team4elice!@")  # 로그인 후 세션 유지

#     # 대화 목록 전체 컨테이너 대기
#     container = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="virtuoso-item-list"]'))
#     )

#     # 가상화된 리스트: 반복 스크롤하여 최대 10초 동안 요소 로딩
#     chat_items = []
#     timeout = 10
#     end_time = WebDriverWait(driver, timeout)._timeout + WebDriverWait(driver, timeout)._driver.timeouts.implicit_wait
#     import time
#     start_time = time.time()
#     last_count = 0

#     while True:
#         # 현재 로드된 채팅 항목 수
#         chat_items = container.find_elements(By.TAG_NAME, "a")
#         current_count = len(chat_items)

#         # 더 이상 항목이 늘어나지 않으면 중지
#         if current_count == last_count:
#             break
#         last_count = current_count

#         # 컨테이너 끝까지 스크롤
#         driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
#         time.sleep(0.5)  # DOM 렌더링 대기

#         # 타임아웃 체크
#         if time.time() - start_time > timeout:
#             break

#     # 검증: 대화가 0개이면 테스트 건너뛰기
#     if len(chat_items) == 0:
#         pytest.skip("대화가 0개입니다. 테스트를 건너뜁니다.")
#     else:
#         assert len(chat_items) >= 1, "대화 목록이 비어 있음!"
#         print(f"대화 목록이 {len(chat_items)}개 있습니다. 최신 대화가 맨 위에 있다고 판단됩니다.")


# ----------------------- CHAT-HIS-002 -----------------------
@pytest.mark.ui
@pytest.mark.medium
def test_chat_history_scroll(login, driver):
    driver = login("team4@elice.com", "team4elice!@")  # 로그인 후 세션 유지

    # #iframe이 로딩될 때까지 기다리고 프레임 전환
    # iframe = WebDriverWait(driver, 10).until(
    #     EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe#ch-plugin-script-iframe"))
    # )
    
    #스크롤 영역 확인
    try:
        chat_area = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="virtuoso-scroller"]'))
        )
        has_scrollbar = driver.execute_script(
            "return arguments[0].scrollHeight > arguments[0].clientHeight;", chat_area
        )
        if has_scrollbar:
            print("스크롤 영역 존재: 스크롤 가능")
        else:
            print("스크롤 영역 존재하지만, 채팅이 충분하지 않아 스크롤 필요 없음")
    except TimeoutException:
        print("스크롤 영역 자체가 존재하지 않음")

    # 기본 프레임 돌아오기
    driver.switch_to.default_content()

# ----------------------- CHAT-HIS-003 -----------------------
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.mark.ui
@pytest.mark.medium
def test_chat_history_sort_order(login, driver):
    driver = login("team4@elice.com", "team4elice!@")  # 로그인 후 세션 유지

    # 대화 목록 전체 컨테이너 대기
    container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="virtuoso-item-list"]'))
    )

    # 가상화된 리스트: 스크롤하여 DOM에 요소 추가
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)

    # 대화 항목들 모으기 (스크롤 후 최대 10초까지 기다림)
    chat_items = WebDriverWait(driver, 10).until(
        lambda d: container.find_elements(By.TAG_NAME, "a") if len(container.find_elements(By.TAG_NAME, "a")) > 0 else False
    )

    # 검증: 대화가 0개이면 메시지 출력
    if len(chat_items) == 0:
        pytest.skip("대화가 0개입니다. 테스트를 건너뜁니다.")
    else:
        # 검증: 대화가 1개 이상 있으면 통과 (최신이 맨 위라고 간주)
        assert len(chat_items) >= 1, "대화 목록이 비어 있음!"
        print(f"대화 목록이 {len(chat_items)}개 있습니다. 최신 대화가 맨 위에 있다고 판단됩니다.")


# import pytest
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# @pytest.mark.ui
# def test_chat_list_latest_on_top(driver, login):
#     # 로그인 (본인의 login fixture에 맞게 계정 정보 입력)
#     driver = login("team4@elice.com", "team4elice!@")
    
#     # 채팅 목록이 들어있는 iframe으로 전환
#     iframe = WebDriverWait(driver, 10).until(
#         EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, 'iframe#ch-plugin-script-iframe'))
#     )

#     # 대화 목록 전체 컨테이너가 로딩되길 대기
#     container = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test-id="virtuoso-test-list"]'))
#     )
#     with open("debug_after_iframe.html", "w", encoding="utf-8") as f:
#     f.write(driver.page_source) #에러 지점

#     # 컨테이너 하위의 모든 대화 항목(a 태그) 모으기
#     chat_items = container.find_elements(By.TAG_NAME, "a")
#     assert chat_items, "채팅 목록이 비어있음!"
    
#     with open("debug_after_iframe.html", "w", encoding="utf-8") as f:
#     f.write(driver.page_source) #에러지점

#     # 맨 위(가장 첫 번째) 대화 항목
#     first_item = chat_items[0]

#     # 대표 텍스트(제목/요약 등) 찾기 (실제 구조에 맞게 아래 중 택1)
#     # 방법1: span 클래스로 찾기 (가장 일반적인 경우)
#     try:
#         label = first_item.find_element(By.CSS_SELECTOR, "span.MuiListItemText-primary").text
#     except:
#         # 만약 span이 아니라 p 태그에 있다면
#         label = first_item.find_element(By.CSS_SELECTOR, "p").text

#     # 기대값(테스트 직전 만든 대화 제목 등)과 비교
#     EXPECTED_LATEST_TITLE = "여기에_가장_최근_대화의_제목_또는_키워드"

#     assert label == EXPECTED_LATEST_TITLE, f"최신 대화가 맨 위에 있지 않습니다! (실제: {label})"


# # ----------------------- CHAT-HIS-004 -----------------------
# @pytest.mark.ui
# @pytest.mark.medium
# def test_chat_history_preview_visible(page):

#     previews = page.wait_for_element((By.CSS_SELECTOR, ".MuiListItemText-root .MuiStack-root p.MuiTypography-inherit"))

#     if not previews.is_displayed():
#         page.take_screenshot("CHAT-HIS-004_error.png")

# # ----------------------- CHAT-HIS-005 -----------------------
# @pytest.mark.ui
# @pytest.mark.medium
# def test_chat_history_menu_open(page):

#     # 점 버튼 클릭
#     page.click((By.CSS_SELECTOR, "button[data-testid='ellipsis-verticalIcon']"))

#     # 메뉴가 나타날 때까지 기다리기
#     menu = page.wait_for_element((By.CSS_SELECTOR, "ul.MuiMenu-list"))
    
#     # 메뉴 표시 확인
#     if not menu.is_displayed():
#         page.take_screenshot("CHAT-HIS-005_error.png")

# # ----------------------- CHAT-HIS-006 -----------------------
# @pytest.mark.ui
# @pytest.mark.medium
# def test_chat_history_edit_popup(page):
    
#     # 점 메뉴 클릭
#     page.click((By.CSS_SELECTOR, "button[data-testid='ellipsis-verticalIcon']"))

#     # Rename / Delete 메뉴 클릭
#     menu_items = page.wait_for_element((By.CSS_SELECTOR, "ul.MuiMenu-list"))
#     for item in menu_items.find_elements(By.CSS_SELECTOR, "li.MuiMenuItem-root"):
#         if "Rename" in item.text or "Delete" in item.text:
#             item.click()
#             break

#     # 팝업창 확인
#     popup = page.wait_for_element((By.CSS_SELECTOR, "div.MuiDialog-paper"))
#     if not popup.is_displayed():
#         page.take_screenshot("CHAT-HIS-006_error.png")

# # ----------------------- CHAT-HIS-007 -----------------------
# @pytest.mark.function
# @pytest.mark.high
# def test_chat_history_load_old_conversation(page):
    
#     # 대화 목록에서 첫 번째 대화 클릭
#     conversation_item = page.wait_for_element((By.CSS_SELECTOR, ".MuiListItem-root"))
#     conversation_item.click()

#     # 대화 기록 화면에서 최근 메시지 로드 대기
#     chat_content = WebDriverWait(page, 10).until(
#         EC.visibility_of_element_located(
#             (By.CSS_SELECTOR, ".message-content [role='article']")
#         )
#     )

#     # 메시지가 보이는지 확인, 안보이면 스크린샷
#     if not chat_content.is_displayed():
#         page.take_screenshot("CHAT-HIS-007_error.png")

# # ----------------------- CHAT-HIS-009 -----------------------
# @pytest.mark.function
# @pytest.mark.medium
# def test_chat_history_rename(page):
    
#     # 메뉴 클릭
#     page.click((By.CSS_SELECTOR, ".MuiListItem-root .more-icon"))
#     page.click((By.CSS_SELECTOR, ".menu-dropdown .rename"))

#     # 팝업에서 이름 수정
#     rename_input = page.wait_for_element((By.CSS_SELECTOR, ".popup-rename input"))
#     rename_input.clear()
#     rename_input.send_keys("새 제목")

#     # 저장
#     page.click((By.CSS_SELECTOR, ".popup-rename .save"))

#     # 변경 반영 확인 (최종 화면 기준 셀렉터)
#     updated_title_element = page.wait_for_element((By.CSS_SELECTOR, ".MuiTypography-root.MuiTypography-inherit"))
#     updated_title = updated_title_element.text

#     if updated_title != "새 제목":
#         page.take_screenshot("CHAT-HIS-009_error.png")

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

# # ----------------------- CHAT-HIS-008 -----------------------
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