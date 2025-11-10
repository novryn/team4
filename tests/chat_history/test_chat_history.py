import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage  # 공통 기능 상속용

# ----------------------- CHAT-HIS-001 -----------------------
@pytest.mark.ui
@pytest.mark.medium

# def test_chat_history_display(login, driver):
#     driver = login("team4@elice.com", "team4elice!@")  # 로그인 픽스처 사용
    
#     # iframe 요소 기다리기
#     iframe = WebDriverWait(driver, 30).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#ch-plugin-script-iframe"))
#     )
#     driver.switch_to.frame(iframe)
    
#     # iframe 내부 요소 기다리기
#     sidebar = WebDriverWait(driver, 30).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, ".MuiList-root[data-testid='virtuoso-item-list']"))
#     )
    
#     # 기본 프레임 돌아오기
#     driver.switch_to.default_content()
    
#     # 요소 표시 여부 확인, 안 보이면 스크린샷 저장
#     assert sidebar.is_displayed(), "채팅 히스토리 영역이 표시되지 않음"
#     if not sidebar.is_displayed():
#         driver.save_screenshot("CHAT-HIS-001_error.png")

def test_chat_history_display(login, driver):
    driver = login("team4@elice.com", "team4elice!@")  # 로그인 픽스처 사용
    
    # iframe 요소 기다리기
    iframe = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#ch-plugin-script-iframe"))
    )
    driver.switch_to.frame(iframe)

    # 기존 채팅 내역 요소
    CHAT_HISTORY = (By.CSS_SELECTOR, "a[data-index]")
    
    # 채팅 내역 존재 여부 확인
    try:
        sidebar = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located(CHAT_HISTORY)
        )
        exists = True
    except TimeoutException:
        exists = False
        driver.save_screenshot("CHAT-HIS-001_no_history.png")

    # 기본 프레임 돌아오기
    driver.switch_to.default_content()
    
    # 존재 여부 콘솔 출력
    if exists:
        print("기존 채팅 내역이 표시됨")
    else:
        print("기존 채팅 내역이 없음 (정상 상태일 수 있음)")

    # assert로 확인
    assert exists, "채팅 내역이 존재하지 않음"
    
# ----------------------- CHAT-HIS-002 -----------------------
# @pytest.mark.ui
# @pytest.mark.medium
# def test_chat_history_scroll(page):

#     # 사이드바 검색 버튼 클릭
#     page.click((By.CSS_SELECTOR, ".search-button"))

#     # 팝업창 내 채팅 히스토리 영역
#     chat_history_area = page.wait_for_element((By.CSS_SELECTOR, '[data-testid="virtuoso-scroller"]'))

#     # 세로 스크롤바 존재 여부 확인
#     has_scrollbar = page.driver.execute_script(
#         "return arguments[0].scrollHeight > arguments[0].clientHeight;", chat_history_area
#     )
#     if not has_scrollbar:
#         page.take_screenshot("CHAT-HIS-002_error.png")

@pytest.mark.ui
@pytest.mark.medium
def test_chat_history_scroll(login, driver):
    driver = login("team4@elice.com", "team4elice!@")  # 로그인 후 세션 유지

    # iframe이 로딩될 때까지 기다리고 프레임 전환
    iframe = WebDriverWait(driver, 10).until(
        EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe#ch-plugin-script-iframe"))
    )

    # ✅ 불필요한 채팅 목록 대기 제거
    # 기존 코드:
    # CHAT_HISTORY = (By.CSS_SELECTOR, "a[data-index]")
    # try:
    #     WebDriverWait(driver, 10).until(
    #         EC.presence_of_all_elements_located(CHAT_HISTORY)
    #     )
    #     print("채팅 목록이 화면에 존재하여 DOM이 로딩 완료됨")
    # except TimeoutException:
    #     print("채팅 목록이 존재하지 않음 (정상 상태일 수 있음)")

    # 스크롤 영역 확인
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
# @pytest.mark.ui
# @pytest.mark.medium
# def test_chat_history_sort_order(page):
    
#     # 리스트 전체 가져오기
#     items = page.wait_for_element((By.CSS_SELECTOR, ".MuiList-root[data-testid='virtuoso-item-list']"))
#     texts = [item.text for item in items.find_elements(By.CSS_SELECTOR, ".MuiListItemText-primary")]

#     # 내림차순 비교
#     if texts != sorted(texts, reverse=True):
#         page.take_screenshot("CHAT-HIS-003_error.png")
#         assert False, "채팅 히스토리가 내림차순으로 정렬되어 있지 않습니다."
@pytest.mark.ui
@pytest.mark.medium
def test_chat_history_sort_order(login, driver):
    driver = login("team4@elice.com", "team4elice!@")  # 로그인 후 세션 유지

    # ✅ 1. iframe이 로딩될 때까지 기다리고 전환 (TC2와 동일)
    iframe = WebDriverWait(driver, 10).until(
        EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe#ch-plugin-script-iframe"))
    )

    # ✅ 2. 채팅 영역 렌더링 확인 (스크롤 영역 존재 확인)
    try:
        chat_area = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="virtuoso-scroller"]'))
        )
        print("채팅 영역 로딩 완료")
    except TimeoutException:
        print("채팅 영역 로딩 실패")
        driver.switch_to.default_content()
        assert False, "채팅 영역이 존재하지 않아 정렬 확인 불가"

    # ✅ 3. 채팅 목록 가져오기 (DOM 존재 여부 확인)
    CHAT_ITEMS = chat_area.find_elements(By.CSS_SELECTOR, "a[data-index]")
    if not CHAT_ITEMS:
        driver.switch_to.default_content()
        driver.save_screenshot("CHAT-HIS-003_no_items.png")
        assert False, "채팅 아이템이 존재하지 않아 정렬 확인 불가"

    # ✅ 4. 텍스트 리스트로 변환 후 내림차순 비교
    texts = [item.text for item in CHAT_ITEMS]
    if texts != sorted(texts, reverse=True):
        driver.save_screenshot("CHAT-HIS-003_error.png")
        driver.switch_to.default_content()
        assert False, "채팅 히스토리가 내림차순으로 정렬되어 있지 않습니다."

    # ✅ 5. 테스트 종료 후 기본 프레임으로 복귀
    driver.switch_to.default_content()

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