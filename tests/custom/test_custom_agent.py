import pytest
from selenium.webdriver.common.by import By

@pytest.mark.usefixtures("login", "driver", "page")
class TestCustomAgent:

    def test_open_custom_agent_page(self, page, login):
        # TC 1: Custom Agent 페이지 진입 확인
        driver = login()  # 로그인 후 driver 반환
        page.open("https://qaproject.elice.io/ai-helpy-chat/custom-agent")
        assert "custom-agent" in driver.current_url, "Custom Agent 페이지 진입 실패"

    def test_first_ai_card_icon(self, page, login):
        # TC 2: 첫 번째 AI 카드 아이콘 확인
        driver = login()
        page.open("https://qaproject.elice.io/ai-helpy-chat/custom-agent")

        # CSS 시도
        try:
            first_card_icon_element = page.wait_for_element(
                (By.CSS_SELECTOR,
                 "#\\:rm\\: > div > div > div.flex-1.min-h-0.overflow-hidden > "
                 "div > div:nth-child(2) > div > div.MuiContainer-root.MuiContainer-maxWidthLg.css-irgchr > "
                 "div > div:nth-child(1) > a > div.MuiAvatar-root.MuiAvatar-circular.MuiAvatar-colorDefault.css-nicxjw > svg > path"),
                timeout=10
            )
        except:
            # CSS 실패 시 XPath로 fallback
            first_card_icon_element = page.wait_for_element(
                (By.XPATH, '//*[@id=":rm:"]/div/div/div[2]/div/div[2]/div/div[2]/div/div[1]/a/div[1]/svg/path'),
                timeout=10
            )

        assert first_card_icon_element.is_displayed(), "첫 번째 AI 카드 아이콘이 보이지 않음"

        # SVG path 검증
        expected_path = (
            "M327.5 85.2c-4.5 1.7-7.5 6-7.5 10.8s3 9.1 7.5 10.8L384 128l21.2 56.5c1.7 4.5 6 7.5 10.8 7.5s9.1-3 10.8-7.5L448 128l56.5-21.2c4.5-1.7 7.5-6 7.5-10.8s-3-9.1-7.5-10.8L448 64 426.8 7.5C425.1 3 420.8 0 416 0s-9.1 3-10.8 7.5L384 64 327.5 85.2z"
            "M205.1 73.3c-2.6-5.7-8.3-9.3-14.5-9.3s-11.9 3.6-14.5 9.3L123.3 187.3 9.3 240C3.6 242.6 0 248.3 0 254.6s3.6 11.9 9.3 14.5l114.1 52.7L176 435.8c2.6 5.7 8.3 9.3 14.5 9.3s11.9-3.6 14.5-9.3l52.7-114.1 114.1-52.7c5.7-2.6 9.3-8.3 9.3-14.5s-3.6-11.9-9.3-14.5L257.8 187.4 205.1 73.3z"
            "M384 384l-56.5 21.2c-4.5 1.7-7.5 6-7.5 10.8s3 9.1 7.5 10.8L384 448l21.2 56.5c1.7 4.5 6 7.5 10.8 7.5s9.1-3 10.8-7.5L448 448l56.5-21.2c4.5-1.7 7.5-6 7.5-10.8s-3-9.1-7.5-10.8L448 384l-21.2-56.5c-1.7-4.5-6-7.5-10.8-7.5s-9.1 3-10.8 7.5L384 384z"
        )
        actual_path = first_card_icon_element.get_attribute("d")
        assert actual_path == expected_path, "첫 번째 AI 카드 아이콘 path가 예상과 다름"

    def test_chat_history_sort_order(self, page, login):
        # TC 3: 채팅 히스토리 정렬 순서 확인
        driver = login()
        page.open("https://qaproject.elice.io/ai-helpy-chat/agent")

        # 채팅 리스트 컨테이너가 로딩될 때까지 최대 15초 대기
        chat_container_selector = "div[data-testid='chat-list']"
        page.wait_for_element((By.CSS_SELECTOR, chat_container_selector), timeout=15)

        # 채팅 리스트 가져오기
        chat_items = page.get_chat_list()
        texts = [item.text for item in chat_items]

        # 리스트가 비어있으면 테스트 실패
        assert texts, "채팅 리스트가 비어있음"

        # 최신순으로 정렬되어 있는지 확인
        assert texts == sorted(texts, reverse=True), "채팅 히스토리가 최신순으로 정렬되지 않음"

