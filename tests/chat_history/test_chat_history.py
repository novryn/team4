import pytest
from selenium.webdriver.common.by import By

@pytest.mark.ui
@pytest.mark.medium

def test_chat_history_visible(driver, login):
sidebar = driver.find_element(By.CSS_SELECTOR, "aside.sidebar")
    history_area = sidebar.find_element(By.CSS_SELECTOR, ".chat-history")
    assert history_area.is_displayed(), "채팅 히스토리 영역이 표시되지 않음"

