<<<<<<< HEAD
import pytest
from selenium.webdriver.common.by import By

@pytest.mark.ui
@pytest.mark.medium

sidebar = driver.find_element(By.CSS_SELECTOR, "aside.sidebar")
    history_area = sidebar.find_element(By.CSS_SELECTOR, ".chat-history")
    assert history_area.is_displayed(), "채팅 히스토리 영역이 표시되지 않음"
=======
>>>>>>> b638d6763b78e066d01835b2482db9aae4ba2a36

