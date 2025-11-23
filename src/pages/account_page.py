import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from src.pages.base_page import BasePage


class AccountPage(BasePage):
    """계정 관련 페이지 - 로그인, 로그아웃, 프로필, 아바타"""

    # ==================== 셀렉터 상수 ====================
    
    # 프로필 관련
    PROFILE_BUTTON = (By.CSS_SELECTOR, "button.MuiAvatar-root")
    LOGOUT_BUTTON = (By.XPATH, "//*[@data-testid='arrow-right-from-bracketIcon']/ancestor::*[@role='button' or @role='menuitem']")
    ACCOUNT_MGMT_LINK = (By.XPATH, "//*[contains(text(), '계정 관리') or contains(text(), 'Account Management')]")
    
    # 아바타 관련
    AVATAR_EDIT_BUTTON = (By.CSS_SELECTOR, "[data-testid='avatar-edit-button']")
    AVATAR_UPLOAD_INPUT = (By.CSS_SELECTOR, "input[type='file']")

    # ========== 로그아웃 11/14 추가(김은아), 11/18 수정(황지애)==========
    
    def logout(self):
        """
        우측 상단 프로필 아바타 버튼을 클릭해 드롭다운을 연 뒤 로그아웃 메뉴를 클릭한다.
        🔹 이 함수는 "로그아웃 버튼을 누르는 행위"까지만 책임집니다.
        🔹 "로그인 페이지로 이동했는지" 확인은 각 테스트에서 상황에 맞게 검증하세요.
        """
        wait = WebDriverWait(self.driver, self.timeout)

        # 1) 프로필 클릭
        try:
            profile_btn = wait.until(
                EC.element_to_be_clickable(self.PROFILE_BUTTON)
            )
            self.driver.execute_script("arguments[0].click();", profile_btn)
            print("✅ 프로필 버튼 클릭")
        except TimeoutException as e:
            pytest.fail(f"로그아웃 실패: 프로필 버튼 없음: {e}")

        # 드롭다운 열릴 때까지 대기
        time.sleep(1)

        # 2) 로그아웃 버튼 찾기
        # SVG 아이콘으로 찾고 → 부모 요소 클릭
        logout_btn = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//*[@data-testid='arrow-right-from-bracketIcon']/ancestor::*[@role='button' or @role='menuitem']"
            ))
        )
        
        # 3) 클릭
        try:
            self.driver.execute_script("arguments[0].click();", logout_btn)
            print("✅ 로그아웃 버튼 클릭")
        except Exception as e:
            pytest.fail(f"로그아웃 버튼 클릭 실패: {e}")

    # ==================== 프로필 ====================

    def click_profile(self):
        """프로필 버튼 클릭 (드롭다운 열기)"""
        profile_btn = self.wait_for_clickable(self.PROFILE_BUTTON)
        self.driver.execute_script("arguments[0].click();", profile_btn)
        print("✅ 프로필 버튼 클릭")

    def open_account_management(self):
        """계정 관리 페이지 열기 (새 탭)"""
        self.click_profile()
        time.sleep(0.5)
        
        account_mgmt = self.wait_for_clickable(self.ACCOUNT_MGMT_LINK)
        account_mgmt.click()
        print("✅ 계정 관리 클릭")
        
        # 새 탭 전환
        WebDriverWait(self.driver, 5).until(lambda d: len(d.window_handles) > 1)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        print("✅ 새 탭으로 전환")

    # ==================== 아바타 ====================

    def click_avatar_edit(self):
        """아바타 편집 버튼 클릭"""
        self.click(self.AVATAR_EDIT_BUTTON)
        print("✅ 아바타 편집 버튼 클릭")

    def upload_avatar(self, file_path):
        """아바타 이미지 업로드"""
        file_input = self.driver.find_element(*self.AVATAR_UPLOAD_INPUT)
        file_input.send_keys(file_path)
        print(f"✅ 아바타 업로드: {file_path}")

    def get_avatar_src(self, locator=None, normalize=True):
        """
        아바타 이미지 src 가져오기
        - img 태그가 있으면 src 반환
        - svg 태그가 있으면 "PersonIcon" 반환 (기본 아바타)
        - 없으면 None 반환
        """
        locator = locator or self.PROFILE_BUTTON
        
        try:
            avatar_container = self.wait_for_element(locator)
            
            # img 태그 확인
            try:
                img = avatar_container.find_element(By.TAG_NAME, "img")
                src = img.get_attribute("src")
                
                if not src:
                    return None
                
                if not normalize:
                    return src
                
                # 정규화: 파일명만 추출
                base = src.split("?", 1)[0]
                filename = base.rsplit("/", 1)[-1]
                return filename
                
            except NoSuchElementException:
                # img 없으면 SVG (기본 아바타) 확인
                try:
                    avatar_container.find_element(By.TAG_NAME, "svg")
                    return "PersonIcon"
                except NoSuchElementException:
                    return None
                    
        except Exception as e:
            print(f"⚠️ 아바타 찾기 실패 ({locator}): {e}")
            return None
