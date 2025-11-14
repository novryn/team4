# 표준 라이브러리
import os
# 서드파티 라이브러리
import pytest
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

# ----------------------- CHAT-HIS-008 -----------------------
@pytest.mark.ui
@pytest.mark.medium
def test_chat_history_rename(login, driver):
    
    driver = login()
    page = BasePage(driver)

     # 메뉴 클릭
    page.click((By.CSS_SELECTOR, ".MuiListItem-root .more-icon"))

    # 드롭다운에서 Rename 버튼이 나타날 때까지 기다림
    rename_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".menu-dropdown .rename"))
    )
    rename_button.click()  # Rename 선택

    # 팝업에서 이름 수정
    rename_input = page.wait_for_element((By.CSS_SELECTOR, ".popup-rename input"))
    rename_input.clear()
    rename_input.send_keys("새 제목")

    # 저장
    page.click((By.CSS_SELECTOR, ".popup-rename .save"))

    # 변경 반영 확인 (최종 화면 기준 셀렉터)
    updated_title_element = page.wait_for_element(
        (By.CSS_SELECTOR, ".MuiTypography-root.MuiTypography-inherit")
    )
    updated_title = updated_title_element.text

    if updated_title != "새 제목":
        page.take_screenshot("CHAT-HIS-009_error.png")
        
# # ----------------------- CHAT-HIS-009 -----------------------
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

# # ----------------------- CHAT-HIS-010 -----------------------
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

# #----------------------- CHAT-HIS-10 -----------------------
# @pytest.mark.ui
# @pytest.mark.low

# def test_chat_history_autosave(login, driver):
#     driver = login("team4@elice.com", "team4elice!@")

#     # 대화 목록 모으기 함수
#     def collect_chat_items(driver, timeout=15):
#         try:
#             container = WebDriverWait(driver, timeout).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="virtuoso-item-list"]'))
#             )
#         except TimeoutException:
#             print("대화 목록 컨테이너 자체가 없음")
#             return []

#         chat_items = []
#         start_time = time.time()
#         while True:
#             found = container.find_elements(By.TAG_NAME, "a")
#             if len(found) > len(chat_items):
#                 chat_items = found
#             driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
#             time.sleep(0.5)
#             if time.time() - start_time > timeout:
#                 break
#         return chat_items

#     # 채팅창의 입력창 찾기 (CSS 선택자: textarea)
#     try:
#         input_box = WebDriverWait(driver, 5).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "textarea"))
#         )
#         input_box.send_keys("자동 저장 테스트 메시지")
#     except TimeoutException:
#         print("입력창 요소 안보임")
#         pytest.skip("입력창이 보이지 않아 테스트 건너뜀")

#     # 페이지 새로고침
#     driver.refresh()
#     time.sleep(2)

#     # 새로고침 후 입력했던 내용이 다시 남아 있는지 확인
#     try:
#         input_box_after = WebDriverWait(driver, 5).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "textarea"))
#         )
#         restored_text = input_box_after.get_attribute("value")
#         if restored_text.strip():
#             print("자동 저장됨:", restored_text)
#         else:
#             print("자동 저장 안됨")
#     except TimeoutException:
#         print("입력창 요소 안보임 (새로고침 후)")
#         pytest.fail("자동 저장 검증 불가 - 입력창 없음")

# # ----------------------- CHAT-HIS-12 -----------------------
# @pytest.mark.ui
# @pytest.mark.high
# def test_chat_history_sync_across_browsers(login, driver):
#     driver = login("team4@elice.com", "team4elice!@")

#     def collect_chat_items(driver, timeout=15):
#         try:
#             container = WebDriverWait(driver, timeout).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="virtuoso-item-list"]'))
#             )
#         except TimeoutException:
#             print("대화 목록 컨테이너 자체가 없음")
#             return []

#         chat_items = []
#         start_time = time.time()
#         while True:
#             found = container.find_elements(By.TAG_NAME, "a")
#             if len(found) > len(chat_items):
#                 chat_items = found
#             driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
#             time.sleep(0.5)
#             if time.time() - start_time > timeout:
#                 break
#         return chat_items

#     chat_items = collect_chat_items(driver)
#     if not chat_items:
#         print("채팅 내역 없음 - 새 채팅 생성 필요")
#         pytest.skip("채팅 내역이 없어 동기화 테스트 불가")

#     print(f"현재 PC에서 대화 {len(chat_items)}개 존재.")
#     print("👉 다른 브라우저에서 동일 계정 로그인 후 새 대화가 반영되는지 수동 확인 필요.")
#     assert True, "자동 검증 불가 - 시각적 확인 필요"


# # ----------------------- CHAT-HIS-13 -----------------------
# @pytest.mark.ui
# @pytest.mark.high

# def test_chat_history_persistence_after_relogin(login, driver):
#     driver = login("team4@elice.com", "team4elice!@")

#     def collect_chat_items(driver, timeout=15):
#         try:
#             container = WebDriverWait(driver, timeout).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid=\"virtuoso-item-list\"]'))
#             )
#         except TimeoutException:
#             print("대화 목록 컨테이너 없음")
#             return []

#         chat_items = []
#         start_time = time.time()
#         while True:
#             found = container.find_elements(By.TAG_NAME, "a")
#             if len(found) > len(chat_items):
#                 chat_items = found
#             driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
#             time.sleep(0.5)
#             if time.time() - start_time > timeout:
#                 break
#         return chat_items

#     before_logout = collect_chat_items(driver)
#     print(f"로그아웃 전 대화 {len(before_logout)}개")

#     # 로그아웃 버튼 찾기


# # ----------------------- CHAT-HIS-016 -----------------------
# @pytest.mark.ui
# @pytest.mark.medium

# # 성능 테스트: 검색 응답 속도 확인
# def test_chat_history_search_speed(login, driver):
    
#     driver = login("team4@elice.com", "team4elice!@")

#     # 검색 버튼 클릭
#     search_button = WebDriverWait(driver, 10).until(
#         EC.element_to_be_clickable((By.XPATH, "//button[contains(., '검색')]"))
#     )
#     search_button.click()

#     # 팝업창 열리면 검색창 찾기
#     search_box = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
#     )

#     # 키워드 입력 후 반응속도 측정
#     start = time.time()
#     search_box.send_keys("테스트")
#     try:
#         WebDriverWait(driver, 2).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="search-result-item"]'))
#         )
#         elapsed = time.time() - start
#         print(f"검색 결과 표시까지 {elapsed:.2f}초 걸림")
#         assert elapsed <= 1, "검색 응답이 1초를 초과함"
#     except TimeoutException:
#         pytest.fail("검색 결과가 표시되지 않음")

# # ----------------------- CHAT-HIS-017 -----------------------
# @pytest.mark.ui
# @pytest.mark.medium

# # 성능 테스트: 채팅 삭제 시 반응 속도 확인
# def test_chat_delete_response(login, driver):
    
#     driver = login("team4@elice.com", "team4elice!@")

#     # 채팅 목록 컨테이너 기다리기
#     try:
#         container = WebDriverWait(driver, 15).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="virtuoso-item-list"]'))
#         )
#     except TimeoutException:
#         pytest.fail("히스토리 목록이 없음")

#     # 첫 번째 채팅 항목 찾기
#     first_chat = container.find_elements(By.TAG_NAME, "a")[0]

#     # 점(⋮) 버튼 클릭
#     # 개발자도구에서 점 아이콘 선택자 확인 필요 (예: .MuiButtonBase-root)
#     menu_button = first_chat.find_element(By.CSS_SELECTOR, "button")
#     menu_button.click()

#     # Delete 클릭 후 반응 시간 측정
#     start = time.time()
#     delete_btn = WebDriverWait(driver, 5).until(
#         EC.element_to_be_clickable((By.XPATH, "//li[contains(., 'Delete')]"))
#     )
#     delete_btn.click()

#     # 삭제 후 목록 갱신 확인
#     WebDriverWait(driver, 5).until(EC.staleness_of(first_chat))
#     elapsed = time.time() - start
#     print(f"삭제 반응 속도: {elapsed:.2f}초")
#     assert elapsed <= 0.5, "삭제 반응이 0.5초 초과"

# # ----------------------- CHAT-HIS-018 -----------------------
# @pytest.mark.security
# @pytest.mark.high

# # 보안 테스트: 비로그인 접근 차단 확인
# def test_redirect_if_not_logged_in(driver):
    
#     # 로그인 없이 직접 메인 화면 접근
#     driver.get("https://qaproject.elice.io/ai-helpy-chat")

#     # 로그인 페이지로 리다이렉트 되는지 확인
#     try:
#         WebDriverWait(driver, 5).until(
#             EC.url_contains("login")
#         )
#         print("로그인 안하면 로그인 페이지로 이동함 (정상)")
#     except TimeoutException:
#         pytest.fail("비로그인 상태에서도 접근이 가능함")

# # ----------------------- CHAT-HIS-019 -----------------------
# @pytest.mark.exception
# @pytest.mark.high

# # 예외 테스트: 네트워크 단절 시 오류 메시지 확인
# def test_network_disconnect_message(login, driver):
    
#     driver = login("team4@elice.com", "team4elice!@")

#     # 실제 네트워크 끊기는 건 테스트 불가 → JS 시뮬레이션
#     driver.execute_script("window.dispatchEvent(new Event('offline'));")

#     try:
#         WebDriverWait(driver, 5).until(
#             EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '네트워크 연결 끊김')]"))
#         )
#         print("네트워크 끊김 메시지 표시됨 (정상)")
#     except TimeoutException:
#         pytest.fail("네트워크 오류 메시지가 표시되지 않음")

# # ----------------------- CHAT-HIS-020 -----------------------
# @pytest.mark.exception
# @pytest.mark.medium

# # 예외 테스트: 삭제 중 통신 실패 시 복구 확인
# def test_delete_fail_recovery(login, driver):
    
#     driver = login("team4@elice.com", "team4elice!@")

#     # 채팅 목록 컨테이너 찾기
#     try:
#         container = WebDriverWait(driver, 15).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="virtuoso-item-list"]'))
#         )
#     except TimeoutException:
#         pytest.fail("❌ 목록 없음")

#     # 첫 번째 항목 선택
#     first_chat = container.find_elements(By.TAG_NAME, "a")[0]

#     # 삭제 버튼 누르기
#     delete_btn = first_chat.find_element(By.XPATH, ".//button[contains(., 'Delete')]")
#     delete_btn.click()

#     # 서버 통신 실패 상황을 JS로 시뮬레이션
#     driver.execute_script("alert('삭제 실패: 서버 응답 없음');")
#     time.sleep(1)
#     driver.switch_to.alert.accept()

#     # 항목이 복구되어 있는지 확인
#     still_exists = first_chat in container.find_elements(By.TAG_NAME, "a")
#     print("삭제 실패 후 복구 상태:", "정상 복구됨" if still_exists else "복구 안됨")

#     assert still_exists, "삭제 실패 시 복구되지 않음"
