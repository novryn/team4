import re
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

# --- Avatar Locators ---

# 1) 계정 관리 페이지 - 왼쪽 큰 아바타
ACCOUNT_LEFT_AVATAR = (By.CSS_SELECTOR, ".MuiAvatar-root")

# 2) 우측 상단 헤더 아바타 (전체 페이지 공통)
HEADER_AVATAR = (By.CSS_SELECTOR, "button.MuiAvatar-root")

# 3) 프로필 드롭다운 내 아바타
ACCOUNT_DROPDOWN_AVATAR = (By.CSS_SELECTOR, ".MuiListItemAvatar-root")

# 4) 메인 페이지 - 사용자 정보 블록의 아바타
MAIN_DROPDOWN_AVATAR = (By.CSS_SELECTOR, "[data-elice-user-profile-header] .MuiAvatar-root")

# 5) 로그인 페이지 아바타
LOGIN_PAGE_AVATAR = (By.CSS_SELECTOR, ".MuiAvatar-root.MuiAvatar-circular")


def _click_profile(driver, wait: WebDriverWait):
    """
    우측 상단 프로필 아바타 버튼을 클릭해 드롭다운 메뉴를 연다.
    - button.MuiAvatar-root 를 기준으로 클릭
    - 드롭다운이 실제로 열렸는지 Logout/로그아웃 또는 계정 정보 블록이 보이는지로 확인
    """
    try:
        # 1) 우측 상단 프로필 버튼 클릭
        profile_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.MuiAvatar-root"))
        )
        profile_btn.click()

        # 2) 드롭다운이 실제로 열린 것 확인
        wait.until(
            EC.visibility_of_any_elements_located((
                By.XPATH,
                "//*[contains(text(),'Logout') or contains(text(),'로그아웃') "
                "or contains(text(),'계정 관리') or contains(text(),'Account Management')]"
            ))
        )

        # 여기까지 오면 성공
        return True

    except TimeoutException as e:
        raise Exception(f"프로필 드롭다운이 열리지 않았습니다: {e}") from e
    except Exception as e:
        raise Exception(f"프로필 버튼 클릭 실패: {e}") from e
    

def _find_payment_history(driver, wait):
    """
    Payment History(결제 내역) 버튼 찾기
    (프로필 메뉴를 먼저 열어야 함)
    """
    # Payment History가 보일 때까지 대기
    payment_history = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "a[href='https://payments.elice.io']")
        )
    )
    
    assert payment_history.is_displayed()
    print("✅ Payment History 버튼 visible 확인")
    return payment_history


def _set_language_korean(driver):
    """페이지 언어를 한국어로 설정"""
    try:
        # localStorage 설정
        driver.execute_script("""
            localStorage.setItem('language', 'ko');
            localStorage.setItem('locale', 'ko-KR');
            localStorage.setItem('lang', 'ko');
            localStorage.setItem('i18nextLng', 'ko');
        """)
        
        # URL에서 기존 lang 파라미터 제거 후 lang=ko 추가
        current_url = driver.current_url
        
        # lang= 파라미터 제거
        url_without_lang = re.sub(r'[&?]lang=[^&]*', '', current_url)
        
        # lang=ko 추가
        separator = "&" if "?" in url_without_lang else "?"
        new_url = f"{url_without_lang}{separator}lang=ko"
        
        driver.get(new_url)
        
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        print("✅ 한국어 설정 완료")
        return True
        
    except Exception as e:
        print(f"⚠️ 언어 설정 실패: {e}")
        return False
    

def _account_mgmt_page_open(driver):
    wait = WebDriverWait(driver, 15)

    # 계정 관리 버튼 클릭
    account_mgmt = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//*[contains(text(), '계정 관리') or contains(text(), 'Account Management')]"
    )))
    account_mgmt.click()
    print("✅ 계정 관리 클릭")

    # 새 탭 전환
    driver.switch_to.window(driver.window_handles[-1])
    print("✅ 새 탭으로 전환")

    # 페이지 로드 대기
    wait.until(EC.url_contains("members/account"))
    WebDriverWait(driver, 5).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    print(f"✅ 계정 관리 페이지 로드: {driver.current_url}")

    # 한국어 설정 확인
    current_url = driver.current_url
    if "lang=ko" not in current_url:
        _set_language_korean(driver)
        wait.until(EC.url_contains("members/account"))
    else:
        print("✅ 이미 한국어 설정됨")


def _click_profile_avatar_edit_button(driver, wait):
    btn = wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR, "svg[data-icon='pen-to-square']"
    )))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
    btn.click()
    print("✅ 계정 관리 편집 버튼 클릭")


def _upload_profile_avatar_image(driver, filename: str = "profile_avatar.jpg"):
    """
    프로필 아바타 이미지 업로드 헬퍼
    - 현재 파일(common_helpers.py)의 위치를 기준으로 프로젝트 루트(team4)를 찾고,
      그 아래 src/resources/filename 경로를 사용한다.
    - 로컬/도커/젠킨스 어디서나 같은 폴더 구조면 동작하도록 설계.
    """
    # 1) 현재 파일 위치 기준으로 프로젝트 루트(team4) 찾기.
    # 로컬 / Docker / Jenkins 어디서든 동일하게 동작하도록 상대경로로 설정
    here = Path(__file__).resolve()
    #   team4/tests/helpers/common_helpers.py   
    project_root = here.parent.parent.parent

    image_path = project_root / "src" / "resources" / filename

    assert image_path.exists(), f"이미지 없음: {image_path}"

    # 2) 파일 인풋 찾기 (type=file + image accept)
    file_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.CSS_SELECTOR,
            "input[type='file'][accept^='image']"
        ))
    )

    # 3) 파일 경로 전달 (send_keys는 str 경로 필요)
    file_input.send_keys(str(image_path))
    print(f"✅ 프로필 이미지 업로드: {image_path}")


def _select_profile_avatar_menu(driver, wait, text: str):
    """
    아바타 편집 드롭다운에서 메뉴 항목 클릭 가능한지 확인
    예: '프로필 이미지 변경', '프로필 이미지 제거'
    """
    item = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        f"//li[.='{text}' or contains(., '{text}')]"
    )))
    
    # 클릭 가능한지 확인
    assert item.is_displayed(), f"{text} 항목이 표시되지 않음"
    
    return item


# AC-021 공통 유틸: avatar src 추출
def _get_avatar_src(driver, locator, wait: WebDriverWait | None = None, normalize: bool = True) -> str | None:
    try:
        if wait is not None:
            avatar_container = wait.until(EC.presence_of_element_located(locator))
        else:
            avatar_container = driver.find_element(*locator)
        
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


# 계정 관리 페이지: 3곳 src 수집
def _get_account_mgmt_avatar_srcs(driver, wait: WebDriverWait):
    
    # 1) 왼쪽 큰 아바타 src
    src_left = _get_avatar_src(driver, ACCOUNT_LEFT_AVATAR, wait)

    # 2) 우측 상단 헤더 아바타 src
    src_header = _get_avatar_src(driver, HEADER_AVATAR, wait)

    # 3) 드롭다운 내부 아바타 src - 드롭다운 먼저 열어야 함
    _click_profile(driver, wait)
    src_dropdown = _get_avatar_src(driver, ACCOUNT_DROPDOWN_AVATAR, wait)

    return src_left, src_header, src_dropdown


# 메인 페이지: 2곳 src 수집
def _get_main_page_avatar_srcs(driver, wait: WebDriverWait):
    """
    메인 페이지에서:
    - 좌측 사용자 정보 블록
    - 우측 상단 헤더 아바타
    의 src 두 개 반환
    """
    src_main_dropdown = _get_avatar_src(driver, MAIN_DROPDOWN_AVATAR, wait)
    src_header = _get_avatar_src(driver, HEADER_AVATAR, wait)

    return src_main_dropdown, src_header


# 로그인 페이지: 1곳 src 수집
def _get_login_page_avatar_src(driver, wait: WebDriverWait):
    """
    로그인 페이지의 아바타 src 하나 반환
    """
    return _get_avatar_src(driver, LOGIN_PAGE_AVATAR, wait)