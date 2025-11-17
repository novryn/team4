# tests/agent/test_custom_agent.py
import pytest
from pages.base_page import BasePage
from selenium.webdriver.common.by import By


# ---------------------------------------------------------
# 공통: 에이전트 탐색(Agent Explorer) 화면 진입 함수
# ---------------------------------------------------------
def go_to_agent_explorer(base: BasePage):
    # 사이드바 Agent Explorer 버튼 locator
    sidebar_agent_btn = (By.CSS_SELECTOR, "TODO")

    base.click(sidebar_agent_btn)
    # Agent Explorer 홈 화면 요소
    agent_home = (By.CSS_SELECTOR, "TODO")
    base.wait_for_element(agent_home)
    
# ----------------------- 001 ------------------------------
# 화면 진입

def test_CUSTOM_001_agent_explorer_entry(driver, login):
    base = BasePage(driver)

    go_to_agent_explorer(base)

    # 초기 페이지 요소 locator
    initial_page = (By.CSS_SELECTOR, "TODO")
    assert base.is_displayed(initial_page)

# ----------------------- 002 ------------------------------
# 메인 화면 검색창 표시 확인

def test_CUSTOM_002_search_bar_visible(driver, login):
    base = BasePage(driver)

    go_to_agent_explorer(base)

    search_input = (By.CSS_SELECTOR, "TODO")  # 검색창
    search_icon = (By.CSS_SELECTOR, "TODO")   # 검색 아이콘

    assert base.is_displayed(search_input)
    assert base.is_displayed(search_icon)
    
# ----------------------- 003 ------------------------------
# 상단 로고/이름/안내문 표시 검증

def test_CUSTOM_003_top_info_visible(driver, login):
    base = BasePage(driver)

    go_to_agent_explorer(base)

    # 에이전트 실행 버튼
    agent_button = (By.CSS_SELECTOR, "TODO")
    base.click(agent_button)

    logo = (By.CSS_SELECTOR, "TODO")
    title = (By.CSS_SELECTOR, "TODO")
    guide = (By.CSS_SELECTOR, "TODO")

    assert base.is_displayed(logo)
    assert base.is_displayed(title)
    assert base.is_displayed(guide)

# ----------------------- 004 ------------------------------
# 이미지 alt 속성 검증

def test_CUSTOM_004_alt_text_validation(driver, login):
    base = BasePage(driver)

    go_to_agent_explorer(base)

    # 실행할 에이전트 선택 버튼
    agent_button = (By.CSS_SELECTOR, "TODO")
    base.click(agent_button)

    images = driver.find_elements(By.TAG_NAME, "img")
    assert len(images) > 0

    for img in images:
        alt = img.get_attribute("alt")
        assert alt is not None and alt != "", f"이미지 alt 속성 없음 → {img}"
        
# ----------------------- 005 ------------------------------
# 검색 기능 동작 검증

def test_CUSTOM_005_search_feature(driver, login):
    base = BasePage(driver)

    go_to_agent_explorer(base)

    search_input = (By.CSS_SELECTOR, "TODO")
    base.type(search_input, "AI")

    # 검색 실행 버튼
    search_icon = (By.CSS_SELECTOR, "TODO")
    base.click(search_icon)

    # 검색 결과 영역
    result_list = (By.CSS_SELECTOR, "TODO")
    assert base.is_displayed(result_list)
    
# ----------------------- 006 ------------------------------
# 커스텀 에이전트 수정/삭제 후 반영 속도 검증

def test_CUSTOM_006_update_delete_speed(driver, login):
    base = BasePage(driver)

    go_to_agent_explorer(base)

    # 점(⋮) 버튼 hover/select
    more_btn = (By.CSS_SELECTOR, "TODO")
    base.click(more_btn)

    # 수정/삭제 버튼
    update_btn = (By.CSS_SELECTOR, "TODO")
    base.click(update_btn)

    # 속도 측정
    import time
    start = time.time()

    # 수정/삭제 완료 메시지
    complete_msg = (By.CSS_SELECTOR, "TODO")
    base.wait_for_element(complete_msg)

    elapsed = time.time() - start
    assert elapsed <= 3

# ----------------------- 007 ------------------------------
# 동일 이름 중복 생성 예외 처리

def test_CUSTOM_007_duplicate_name_error(driver, login):
    base = BasePage(driver)

    go_to_agent_explorer(base)

    # Create 버튼
    create_btn = (By.CSS_SELECTOR, "TODO")
    base.click(create_btn)

    # 이름 입력
    name_input = (By.CSS_SELECTOR, "TODO")
    base.type(name_input, "중복테스트")

    # 만들기 버튼
    create_submit = (By.CSS_SELECTOR, "TODO")
    base.click(create_submit)

    # 오류 메시지
    error_msg = (By.CSS_SELECTOR, "TODO")

    assert base.is_displayed(error_msg)

# ----------------------- 008 ------------------------------
# 새 에이전트 생성

def test_CUSTOM_008_create_new_agent(driver, login):
    base = BasePage(driver)

    go_to_agent_explorer(base)

    # Create 클릭
    create_btn = (By.CSS_SELECTOR, "TODO")
    base.click(create_btn)

    # 필드 입력
    name_input = (By.CSS_SELECTOR, "TODO")
    rule_input = (By.CSS_SELECTOR, "TODO")

    base.type(name_input, "테스트")
    base.type(rule_input, "기본 규칙")

    # 활성화 확인 후 클릭
    create_submit = (By.CSS_SELECTOR, "TODO")
    base.click(create_submit)

    # 생성 완료 메시지 확인
    done_msg = (By.CSS_SELECTOR, "TODO")
    assert base.is_displayed(done_msg)



# ----------------------- 009 ------------------------------
# 필수 필드 미입력 오류

def test_CUSTOM_009_required_field_error(driver, login):
    base = BasePage(driver)

    go_to_agent_explorer(base)

    create_btn = (By.CSS_SELECTOR, "TODO")
    base.click(create_btn)

    # 빈 값 유지 후 만들기 클릭
    create_submit = (By.CSS_SELECTOR, "TODO")
    base.click(create_submit)

    # 경고 메시지
    name_err = (By.CSS_SELECTOR, "TODO")
    rule_err = (By.CSS_SELECTOR, "TODO")

    assert base.is_displayed(name_err)
    assert base.is_displayed(rule_err)

# ----------------------- 016 ------------------------------
# 생성된 에이전트 목록 삭제

def test_CUSTOM_016_delete_agent(driver, login):
    base = BasePage(driver)

    go_to_agent_explorer(base)

    # 생성된 에이전트 클릭
    agent_item = (By.CSS_SELECTOR, "TODO")
    base.click(agent_item)

    # 삭제 버튼
    delete_btn = (By.CSS_SELECTOR, "TODO")
    base.click(delete_btn)

    # 경고창 삭제 클릭
    confirm_delete = (By.CSS_SELECTOR, "TODO")
    base.click(confirm_delete)

    # 삭제 완료 메시지
    done_msg = (By.CSS_SELECTOR, "TODO")
    assert base.is_displayed(done_msg)

