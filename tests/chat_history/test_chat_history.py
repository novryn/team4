import pytest
from selenium.webdriver.common.by import By
from pages.base_page import BasePage # 공통 기능 상속용

@pytest.mark.ui
@pytest.mark.medium

    driver = login("team4@elice.com", "team4elice!@") # 로그인 픽스쳐 사용

    page = BasePage(driver) # BasePage 객체 생성 (driver 전달)

    sidebar = driver.find_element(By.CSS_SELECTOR, ".MuiList-root[data-testid='virtuoso-item-list']")
    
    assert page.is_displayed((By.CSS_SELECTOR, ".MuiList-root[data-testid='virtuoso-item-list']")), \
        "채팅 히스토리 영역이 표시되지 않음"
        
    if not page.is_displayed((By.CSS_SELECTOR, ".MuiList-root[data-testid='virtuoso-item-list']")):
        page.take_screenshot("chat_history_error.png")
        
        # 실패 시 스크린샷 저장