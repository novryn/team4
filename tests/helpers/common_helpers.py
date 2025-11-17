from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
import re


def _click_profile(driver, wait):
    """
    우상단 프로필 버튼 클릭
    헤더의 가장 오른쪽 버튼 선택 + 열린 메뉴 검증
    """
    # 1) 헤더 찾기
    header = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "header, [role='banner']")))

    # 2) 헤더 안에서 클릭 가능한 후보 수집
    candidates = header.find_elements(
        By.CSS_SELECTOR,
        "button, [role='button'], a[role='button']"
    )
    assert candidates, "헤더 내 클릭 가능한 버튼이 없음"

    # 3) 화면상 가장 오른쪽(x가 가장 큰) 요소 선택
    def rect_x(e):
        return driver.execute_script("return arguments[0].getBoundingClientRect().x;", e)

    # x가 큰 순서로 정렬하여 하나씩 시도 (툴팁 애니메이션/겹침 방지)
    candidates = sorted(candidates, key=rect_x, reverse=True)

    last_error = None
    for el in candidates[:4]:  # 상위 4개만 시도 (과도한 클릭 방지)
        try:
            wait.until(EC.element_to_be_clickable(el))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            el.click()
            
            # 드롭다운 메뉴가 나타날 때까지 대기
            WebDriverWait(driver, 2).until(
                lambda d: any(
                    f.is_displayed() 
                    for xp in ["//*[contains(text(),'Payment History') or contains(text(),'결제 내역')]"]
                    for f in d.find_elements(By.XPATH, xp)
                )
            )
            
            print("✅ 프로필 드롭다운 열림")
            return True
        except Exception as e:
            last_error = e
            continue

    raise Exception(f"프로필 버튼 클릭 실패 (우측 후보들 시도) : {last_error}")


def _find_payment_history(driver, wait):
    """프로필 → Payment History 버튼 '보이는지' 확인"""
    _click_profile(driver, wait)

    payment_history = wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//*[contains(text(), 'Payment History') or contains(text(), '결제 내역')]"
            )
        )
    )

    # 추가 검증
    assert payment_history.is_displayed(), "Payment History 버튼이 visible 상태가 아님"

    print("✅ Payment History 버튼 visible 확인")


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



def _select_profile_avatar_menu_item(driver, wait, text: str):
    """
    아바타 편집 드롭다운에서 메뉴 항목 클릭
    예: '프로필 이미지 변경', '프로필 이미지 제거'
    """
    item = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        f"//li[.='{text}' or contains(., '{text}')]"
    )))
    item.click()
    print(f"✅ 아바타 메뉴 클릭: {text}")

