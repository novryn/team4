import pytest
from selenium.webdriver.common.by import By
from src.pages.base_page import BasePage


@pytest.mark.usefixtures("login", "driver")
class TestCustomAgent:

    def test_open_custom_agent_page(self, driver):
        """
        TC 1: Custom Agent 페이지 진입 확인
        """
        page = BasePage(driver)
        page.open_custom_agent()
        assert "custom-agent" in driver.current_url, "Custom Agent 페이지 진입 실패"

    def test_first_ai_card_icon(self, driver):
        """
        TC 2: Custom Agent 첫 번째 AI 카드 아이콘 확인
        """
        page = BasePage(driver)
        page.open_custom_agent()

        first_card = page.wait_for_element(
            (By.CSS_SELECTOR, "div[data-testid='ai-card']:first-child"),
            timeout=15
        )
        assert first_card.is_displayed(), "첫 번째 AI 카드가 보이지 않음"

    def test_chat_history_sort_order(self, driver):
        """
        TC 3: 채팅 히스토리 정렬 순서 확인
        """
        page = BasePage(driver)
        page.open_chat_history()

        # 채팅 리스트 컨테이너 로딩 대기
        chat_container_selector = "div[data-testid='chat-list']"
        page.wait_for_element((By.CSS_SELECTOR, chat_container_selector), timeout=15)

        # 채팅 리스트 가져오기
        chat_items = page.get_chat_list()
        texts = [item.text.strip() for item in chat_items if item.text.strip()]

        assert texts, "채팅 리스트가 비어있음"

        # 문자열 기준 역정렬 확인 (최신순)
        assert texts == sorted(texts, reverse=True), "채팅 히스토리가 최신순으로 정렬되지 않음"
