import os
import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import MoveTargetOutOfBoundsException

from src.pages.base_page import BasePage


DEBUG_MODE = os.getenv('TEST_DEBUG', 'false').lower() == 'true'


class BillingPage(BasePage):
    """결제/크레딧 관련 페이지"""

    # ==================== 셀렉터 상수 ====================
    
    PROFILE_BUTTON = (By.CSS_SELECTOR, "button.MuiAvatar-root")
    PAYMENT_HISTORY_LINK = (By.XPATH, "//*[contains(text(), 'Payment History') or contains(text(), '결제 내역')]")
    CREDIT_BUTTON = (By.CSS_SELECTOR, "a[href$='/admin/org/billing/payments/credit'], a:has(svg[data-testid*='circle-c'])")

    # CSS 속성 목록 (hover 체크용)
    CSS_PROPS = ["background-color", "color", "border-color", "box-shadow"]

    # ==================== 디버그/스크린샷 ====================

    def debug_wait(self, seconds=0.5):
        """디버그 모드에서만 대기"""
        if DEBUG_MODE:
            time.sleep(seconds)
            print(f"[DEBUG] {seconds}초 대기")

    def dump_debug(self, name="debug"):
        """페이지 소스와 스크린샷 저장"""
        path = os.path.join(os.getcwd(), f"{name}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        self.driver.save_screenshot(f"{name}.png")
        print(f"디버그 저장: {path}")

    def dump_on_fail(self, name="credit_debug"):
        """테스트 실패 시 디버그 정보 저장"""
        try:
            self.driver.save_screenshot(f"{name}.png")
            with open(f"{name}.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
        except Exception:
            pass

    # ==================== 네비게이션 ====================

    def open_payment_history(self):
        """프로필 → Payment History 클릭"""
        # 프로필 클릭
        profile_btn = self.wait_for_clickable(self.PROFILE_BUTTON)
        profile_btn.click()
        
        # Payment History 버튼 클릭
        payment_history = self.wait_for_clickable(self.PAYMENT_HISTORY_LINK)
        payment_history.click()
        print("✅ Payment History 클릭")

    def find_credit_button(self):
        """크레딧 버튼 찾기"""
        return self.wait_for_element(self.CREDIT_BUTTON)

    # ==================== 크레딧 관련 ====================

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

    def has_won_symbol(self, element, raw_text, retry=3):
        """
        요소에 원화 기호(₩)가 있는지 확인
        여러 번 시도해서 안정적으로 검증
        """
        for i in range(retry):
            txt = (raw_text or "").replace("¥", "₩")
            if "₩" in txt:
                return True

            # 접근성/툴팁 속성 확인
            for attr in ("aria-label", "title", "data-tooltip"):
                v = (element.get_attribute(attr) or "").replace("¥", "₩")
                if "₩" in v:
                    return True

            # 의사요소 content 검사
            before = self.driver.execute_script(
                "return getComputedStyle(arguments[0],'::before').content;", element
            ) or ""
            after = self.driver.execute_script(
                "return getComputedStyle(arguments[0],'::after').content;", element
            ) or ""
            
            if "₩" in before.replace("¥", "₩") or "₩" in after.replace("¥", "₩"):
                return True
            
            if i < retry - 1:
                time.sleep(0.3)
        
        return False

    # ==================== CSS/스타일 관련 ====================

    def get_css(self, element, prop):
        """요소의 CSS 속성값 가져오기"""
        return self.driver.execute_script(
            "return window.getComputedStyle(arguments[0]).getPropertyValue(arguments[1]);",
            element, prop
        )

    def get_background_color(self, element):
        """요소의 배경색 가져오기"""
        return self.driver.execute_script(
            "return getComputedStyle(arguments[0]).backgroundColor;", element
        )

    def style_snapshot(self, element):
        """요소의 스타일 스냅샷 생성"""
        props = [
            "background-color", "color", "border-color", "outline-color", "outline-width",
            "box-shadow", "text-shadow",
            "opacity", "filter", "backdrop-filter", "transform",
        ]
        snap = {p: self.get_css(element, p) for p in props}
        snap["::before-bg"] = self.driver.execute_script(
            "return getComputedStyle(arguments[0],'::before').backgroundColor;", element
        )
        snap["::after-bg"] = self.driver.execute_script(
            "return getComputedStyle(arguments[0],'::after').backgroundColor;", element
        )
        return snap

    def any_prop_changed(self, element, before_props):
        """CSS 속성이 변경되었는지 확인"""
        after = {p: self.get_css(element, p) for p in self.CSS_PROPS}
        changed = any(before_props[p] != after[p] for p in self.CSS_PROPS)
        return changed, after

    # ==================== 마우스 인터랙션 ====================

    def hover(self, element):
        """요소에 마우스 호버"""
        ActionChains(self.driver).move_to_element(element).perform()

    def hover_strong(self, element):
        """강화된 마우스 호버 (스크롤 + 다중 시도)"""
        # 뷰포트 중앙으로 스크롤
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center', inline:'center'});", element
        )
        WebDriverWait(self.driver, 1).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        # 요소로 이동
        actions = ActionChains(self.driver)
        try:
            actions.move_to_element(element).perform()
        except MoveTargetOutOfBoundsException:
            w = max(1, int(element.size.get("width", 2)) - 2)
            h = max(1, int(element.size.get("height", 2)) - 2)
            actions.move_to_element_with_offset(element, w//2, h//2).perform()

        # JS 이벤트로 보강
        self.driver.execute_script("""
            const e = arguments[0];
            for (const type of ['mouseover','mouseenter']) {
                e.dispatchEvent(new MouseEvent(type, {bubbles:true, cancelable:true}));
            }
        """, element)

    def is_in_hover_chain(self, element):
        """요소가 현재 hover 체인에 포함되어 있는지 확인"""
        return self.driver.execute_script("""
            const hovered = document.querySelectorAll(':hover');
            return Array.from(hovered).some(h => h === arguments[0] || h.contains(arguments[0]));
        """, element) is True
