import os
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.common.exceptions import MoveTargetOutOfBoundsException

from src.pages.base_page import BasePage

DEBUG_MODE = os.getenv('TEST_DEBUG', 'false').lower() == 'true'


class BillingPage(BasePage):
    """결제 및 크레딧 관련 페이지"""

    # 셀렉터 상수
    CREDIT_BUTTON = (
        By.CSS_SELECTOR,
        "a[href$='/admin/org/billing/payments/credit'], a:has(svg[data-testid*='circle-c'])"
    )
    PAYMENT_HISTORY_LINK = (
        By.CSS_SELECTOR,
        "a[href='https://payments.elice.io']"
    )
    PAYMENT_HISTORY_MENU = (
        By.XPATH,
        "//*[contains(text(), 'Payment History') or contains(text(), '결제 내역')]"
    )

    # hover 관련 CSS 속성들
    HOVER_PROPS = [
        "background-color",
        "color",
        "border-color",
        "box-shadow",
    ]

    def __init__(self, driver, timeout=15):
        super().__init__(driver, timeout)

    # ======================
    # ✅ 디버그/스크린샷 함수
    # ======================

    def debug_wait(self, seconds=0.5):
        """디버그 모드에서만 대기"""
        import time
        if DEBUG_MODE:
            time.sleep(seconds)
            print(f"[DEBUG] {seconds}초 대기")

    def dump(self, name):
        """페이지 소스와 스크린샷 저장"""
        path = os.path.join(os.getcwd(), name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        self.take_screenshot(name.replace(".html", ".png"))
        print("디버그 저장:", path)

    def dump_on_fail(self, name="credit_debug"):
        """테스트 실패 시 디버그 정보 저장"""
        try:
            self.take_screenshot(f"{name}.png")
            with open(f"{name}.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
        except Exception:
            pass

    # ======================
    # ✅ 크레딧 관련 함수
    # ======================

    def find_credit_btn(self):
        """크레딧 버튼 찾기"""
        return self.wait_for_element(self.CREDIT_BUTTON)

    def extract_amount(self, text):
        """
        'Credit ₩1,234,567' → 1234567
        텍스트에서 금액 숫자만 추출
        """
        text = text.replace("￦", "₩").replace(",", "")
        m = re.search(r"(\d+)", text)
        if not m:
            raise ValueError(f"금액 추출 실패: {text}")
        return int(m.group(1))

    def get_credit_amount(self):
        """크레딧 금액 안전하게 가져오기"""
        # 크레딧 버튼 대기
        credit_btn = self.wait_for_element(self.CREDIT_BUTTON)
        
        # 금액 로드 대기
        WebDriverWait(self.driver, 10).until(
            lambda d: "₩" in d.find_element(*self.CREDIT_BUTTON).text
        )
        
        # 최신 텍스트로 금액 추출
        credit_btn = self.driver.find_element(*self.CREDIT_BUTTON)
        amount = self.extract_amount(credit_btn.text)
        
        print(f"크레딧 텍스트: '{credit_btn.text}' → 금액: ₩{amount:,}")
        return amount

    def has_won_symbol(self, el, raw_text: str, retry=3):
        """
        요소에 원화 기호(₩)가 있는지 확인
        여러 번 시도해서 안정적으로 검증
        """
        for i in range(retry):
            # 텍스트 내 변환 문자 통합
            txt = (raw_text or "").replace("¥", "₩")
            if "₩" in txt:
                return True

            # 접근성/툴팁 속성
            for attr in ("aria-label", "title", "data-tooltip"):
                v = (el.get_attribute(attr) or "").replace("¥", "₩")
                if "₩" in v:
                    return True

            # 의사요소 content 검사
            before = self.driver.execute_script(
                "return getComputedStyle(arguments[0],'::before').content;", el
            ) or ""
            after = self.driver.execute_script(
                "return getComputedStyle(arguments[0],'::after').content;", el
            ) or ""
            before = before.replace("¥", "₩")
            after = after.replace("¥", "₩")
            
            if ("₩" in before) or ("₩" in after):
                return True
            
            # 재시도 전 짧은 대기 (DOM 업데이트 시간)
            if i < retry - 1:
                WebDriverWait(self.driver, 0.3).until(lambda d: True)
        
        return False

    # ======================
    # ✅ CSS/스타일 관련 함수
    # ======================

    def get_css(self, el, prop):
        """요소의 CSS 속성값 가져오기"""
        return self.driver.execute_script(
            "return window.getComputedStyle(arguments[0]).getPropertyValue(arguments[1]);",
            el, prop
        )

    def computed_bg(self, el):
        """요소의 배경색 가져오기"""
        return self.driver.execute_script(
            "return getComputedStyle(arguments[0]).backgroundColor;", el
        )

    def any_prop_changed(self, el, before_props):
        """CSS 속성이 변경되었는지 확인"""
        after = {p: self.get_css(el, p) for p in self.HOVER_PROPS}
        changed = any(before_props[p] != after[p] for p in self.HOVER_PROPS)
        return changed, after

    def style_snapshot(self, el):
        """요소의 스타일 스냅샷 생성"""
        props = [
            # 색/배경/선
            "background-color", "color", "border-color", "outline-color", "outline-width",
            # 효과
            "box-shadow", "text-shadow",
            # 테마가 자주 쓰는 값들
            "opacity", "filter", "backdrop-filter", "transform",
        ]
        snap = {p: self.get_css(el, p) for p in props}
        # 의사요소(오버레이)까지 확인
        snap["::before-bg"] = self.driver.execute_script(
            "return getComputedStyle(arguments[0],'::before').backgroundColor;", el
        )
        snap["::after-bg"] = self.driver.execute_script(
            "return getComputedStyle(arguments[0],'::after').backgroundColor;", el
        )
        return snap

    # ======================
    # ✅ 마우스 인터랙션 함수
    # ======================

    def hover(self, el):
        """요소에 마우스 호버"""
        ActionChains(self.driver).move_to_element(el).perform()

    def hover_strong(self, el):
        """강화된 마우스 호버 (스크롤 + 다중 시도)"""
        # 1) 뷰포트 중앙으로 스크롤
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center', inline:'center'});", el
        )
        # 스크롤 완료 대기
        WebDriverWait(self.driver, 1).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        # 2) 가장 안전한 방법: 요소로 직접 이동
        actions = ActionChains(self.driver)
        try:
            actions.move_to_element(el).perform()
        except MoveTargetOutOfBoundsException:
            # 일부 드라이버에서 요소 경계 계산이 어긋날 때 대비
            w = max(1, int(el.size.get("width", 2)) - 2)
            h = max(1, int(el.size.get("height", 2)) - 2)
            actions.move_to_element_with_offset(el, w//2, h//2).perform()

        # 3) JS 이벤트로 보강 (라이브러리 의존 UI에서 필요할 때가 있음)
        self.driver.execute_script("""
            const e = arguments[0];
            for (const type of ['mouseover','mouseenter']) {
                e.dispatchEvent(new MouseEvent(type, {bubbles:true, cancelable:true}));
            }
        """, el)

    def is_in_hover_chain(self, el):
        """요소가 현재 hover 체인에 포함되어 있는지 확인"""
        # 현재 :hover 경로(루트→리프) 중에 el 또는 조상이 포함되면 True
        return self.driver.execute_script("""
            const hovered = document.querySelectorAll(':hover');
            return Array.from(hovered).some(h => h === arguments[0] || h.contains(arguments[0]));
        """, el) is True

    # ======================
    # ✅ 메뉴 관련 함수
    # ======================

    def find_payment_history(self):
        """
        Payment History(결제 내역) 버튼 찾기
        (프로필 메뉴를 먼저 열어야 함)
        """
        # Payment History가 보일 때까지 대기
        payment_history = self.wait_for_element(self.PAYMENT_HISTORY_LINK)
        
        assert payment_history.is_displayed()
        print("✅ Payment History 버튼 visible 확인")
        return payment_history

    def open_payment_history(self):
        """프로필 → Payment History 클릭"""
        self.click_profile()
        
        # Payment History 버튼이 클릭 가능할 때까지 대기
        payment_history = self.wait_for_clickable(self.PAYMENT_HISTORY_MENU)
        payment_history.click()
        print("✅ Payment History 클릭")
