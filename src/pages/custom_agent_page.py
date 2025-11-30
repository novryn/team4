from src.pages.base_page import BasePage


class CustomAgentPage(BasePage):
    """커스텀 에이전트 페이지 관련 기능"""

    def open_custom_agent(self):
        self.open("https://qaproject.elice.io/ai-helpy-chat/custom-agent")

# ------------------- 11/18 커스텀 페이지 로그인 파트 추가 (김은아) -------------------

