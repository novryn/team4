import re
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.pages.base_page import BasePage


class AccountPage(BasePage):
    """계정 관리 페이지"""

    # Avatar Locators
    ACCOUNT_LEFT_AVATAR = (By.CSS_SELECTOR, ".MuiAvatar-root")
    HEADER_AVATAR = (By.CSS_SELECTOR, "button.MuiAvatar-root")
    ACCOUNT_DROPDOWN_AVATAR = (By.CSS_SELECTOR, ".MuiListItemAvatar-root")
    MAIN_DROPDOWN_AVATAR = (By.CSS_SELECTOR, "[data-elice-user-profile-header] .MuiAvatar-root")
    LOGIN_PAGE_AVATAR = (By.CSS_SELECTOR, ".MuiAvatar-root.MuiAvatar-circular")

    # 기타 셀렉터
    ACCOUNT_MGMT_MENU = (
        By.XPATH,
        "//*[contains(text(), '계정 관리') or contains(text(), 'Account Management')]"
    )
    PROFILE_EDIT_BUTTON = (By.CSS_SELECTOR, "svg[data-icon='pen-to-square']")
    FILE_INPUT = (By.CSS_SELECTOR, "input[type='file'][accept^='image']")

    def __init__(self, driver, timeout=15):
        super().__init__(driver, timeout)

    # ======================
    # ✅ 언어 설정
    # ======================

    def set_language_korean(self):
        """페이지 언어를 한국어로 설정"""
        try:
            # localStorage 설정
            self.driver.execute_script("""
                localStorage.setItem('language', 'ko');
                localStorage.setItem('locale', 'ko-KR');
                localStorage.setItem('lang', 'ko');
                localStorage.setItem('i18nextLng', 'ko');
            """)
            
            # URL에서 기존 lang 파라미터 제거 후 lang=ko 추가
            current_url = self.driver.current_url
            
            # lang= 파라미터 제거
            url_without_lang = re.sub(r'[&?]lang=[^&]*', '', current_url)
            
            # lang=ko 추가
            separator = "&" if "?" in url_without_lang else "?"
            new_url = f"{url_without_lang}{separator}lang=ko"
            
            self.driver.get(new_url)
            
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            print("✅ 한국어 설정 완료")
            return True
            
        except Exception as e:
            print(f"⚠️ 언어 설정 실패: {e}")
            return False

    # ======================
    # ✅ 계정 관리 페이지 이동
    # ======================

    def open_account_mgmt_page(self):
        """계정 관리 페이지 열기"""
        # 계정 관리 버튼 클릭
        account_mgmt = self.wait_for_clickable(self.ACCOUNT_MGMT_MENU)
        account_mgmt.click()
        print("✅ 계정 관리 클릭")

        # 새 탭 전환
        self.driver.switch_to.window(self.driver.window_handles[-1])
        print("✅ 새 탭으로 전환")

        # 페이지 로드 대기
        WebDriverWait(self.driver, 5).until(EC.url_contains("members/account"))
        WebDriverWait(self.driver, 5).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        print(f"✅ 계정 관리 페이지 로드: {self.driver.current_url}")

        # 한국어 설정 확인
        current_url = self.driver.current_url
        if "lang=ko" not in current_url:
            self.set_language_korean()
            WebDriverWait(self.driver, 10).until(EC.url_contains("members/account"))
        else:
            print("✅ 이미 한국어 설정됨")

    # ======================
    # ✅ 프로필 아바타 편집
    # ======================

    def click_profile_avatar_edit_button(self):
        """프로필 아바타 편집 버튼 클릭"""
        btn = self.wait_for_clickable(self.PROFILE_EDIT_BUTTON)
        self.scroll_into_view(btn)
        btn.click()
        print("✅ 계정 관리 편집 버튼 클릭")

    def upload_profile_avatar_image(self, filename: str = "profile_avatar.jpg"):
        """
        프로필 아바타 이미지 업로드 헬퍼
        - 현재 파일(account_page.py)의 위치를 기준으로 프로젝트 루트를 찾고,
          그 아래 src/resources/filename 경로를 사용한다.
        - 로컬/도커/젠킨스 어디서나 같은 폴더 구조면 동작하도록 설계.
        """
        # 현재 파일 위치 기준으로 프로젝트 루트 찾기
        here = Path(__file__).resolve()
        project_root = here.parent.parent.parent

        image_path = project_root / "src" / "resources" / filename

        assert image_path.exists(), f"이미지 없음: {image_path}"

        # 파일 인풋 찾기
        file_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.FILE_INPUT)
        )

        # 파일 경로 전달
        file_input.send_keys(str(image_path))
        print(f"✅ 프로필 이미지 업로드: {image_path}")

    def select_profile_avatar_menu(self, text: str):
        """
        아바타 편집 드롭다운에서 메뉴 항목 클릭 가능한지 확인
        예: '프로필 이미지 변경', '프로필 이미지 제거'
        """
        item = self.wait_for_clickable((
            By.XPATH,
            f"//li[.='{text}' or contains(., '{text}')]"
        ))
        
        # 클릭 가능한지 확인
        assert item.is_displayed(), f"{text} 항목이 표시되지 않음"
        
        return item

    # ======================
    # ✅ 아바타 src 추출
    # ======================

    def get_avatar_src(self, locator, normalize: bool = True):
        """avatar src 추출"""
        try:
            avatar_container = self.wait_for_element(locator)
            
            # 내부에 img 있는지 확인
            try:
                img = avatar_container.find_element(By.TAG_NAME, "img")
                src = img.get_attribute("src")
                
                if not src:
                    return None
                
                if not normalize:
                    return src
                
                base = src.split("?", 1)[0]
                filename = base.rsplit("/", 1)[-1]
                return filename
                
            except:
                # img 없으면 SVG (기본 아바타)
                try:
                    svg = avatar_container.find_element(By.TAG_NAME, "svg")
                    return "PersonIcon"
                except:
                    return None
        
        except Exception as e:
            print(f"⚠️ 아바타 찾기 실패 ({locator}): {e}")
            return None

    def get_account_mgmt_avatar_srcs(self):
        """계정 관리 페이지: 3곳 src 수집"""
        # 1) 왼쪽 큰 아바타 src
        src_left = self.get_avatar_src(self.ACCOUNT_LEFT_AVATAR)

        # 2) 우측 상단 헤더 아바타 src
        src_header = self.get_avatar_src(self.HEADER_AVATAR)

        # 3) 드롭다운 내부 아바타 src - 드롭다운 먼저 열어야 함
        self.click_profile()
        src_dropdown = self.get_avatar_src(self.ACCOUNT_DROPDOWN_AVATAR)

        return src_left, src_header, src_dropdown

    def get_main_page_avatar_srcs(self):
        """
        메인 페이지에서:
        - 좌측 사용자 정보 블록
        - 우측 상단 헤더 아바타
        의 src 두 개 반환
        """
        src_main_dropdown = self.get_avatar_src(self.MAIN_DROPDOWN_AVATAR)
        src_header = self.get_avatar_src(self.HEADER_AVATAR)

        return src_main_dropdown, src_header

    def get_login_page_avatar_src(self):
        """로그인 페이지의 아바타 src 하나 반환"""
        return self.get_avatar_src(self.LOGIN_PAGE_AVATAR)
