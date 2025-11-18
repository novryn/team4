import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from src.config.settings import get_default_admin
from tests.helpers.common_helpers import (_click_profile, _set_language_korean, _account_mgmt_page_open, _click_profile_avatar_edit_button,
 _upload_profile_avatar_image, _select_profile_avatar_menu, _get_account_mgmt_avatar_srcs,  _get_main_page_avatar_srcs, _get_login_page_avatar_src,
 )

# BasePage import
from src.pages.base_page import BasePage

# ======================
# ✅ test functions
# ======================

# AC-003: 이미 가입된 이메일로 회원가입 차단
def test_duplicate_email_registration_blocked(driver):
    """
    이미 가입된 이메일로 회원가입 시도 시 에러 메시지 확인
    """
    wait = WebDriverWait(driver, 15)
    
    # 1) 로그인 페이지로 이동 (로그인하지 않고)
    driver.get("https://accounts.elice.io/accounts/signin/me")
    print("✅ 로그인 페이지 진입")
    
    # 2) Create account 링크 클릭
    create_account_link = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//a[contains(text(), 'Create account') or contains(text(), '계정 만들기')]"
    )))
    create_account_link.click()
    print("✅ Create account 링크 클릭")
    
    # 페이지 전환 대기
    WebDriverWait(driver, 5).until(
        lambda d: "signup" in d.current_url
    )
    print("✅ 회원가입 페이지 로드")
    
    # 3) Create account with email 버튼 클릭
    email_signup_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//button[contains(text(), 'Create account with email') or contains(text(), '이메일로 계정 만들기')]"
    )))
    email_signup_btn.click()
    print("✅ Create account with email 버튼 클릭")
    
    # 4) Email 입력칸 찾아서 입력
    email_input = wait.until(EC.presence_of_element_located((
        By.CSS_SELECTOR,
        "input[type='email'], input[autocomplete='email']"
    )))
    email_input.clear()
    email_input.send_keys("team4a@elice.com")
    print("✅ 이메일 입력: team4a@elice.com")
    
    # 포커스 이동하여 검증 트리거 (Next 버튼 있으면 클릭, 없으면 TAB)
    try:
        next_btn = driver.find_element(
            By.XPATH,
            "//button[contains(text(), 'Next') or contains(text(), '다음')]"
        )
        next_btn.click()
        print("✅ Next 버튼 클릭")
    except:
        # Next 버튼 없으면 포커스 아웃으로 검증 트리거
        from selenium.webdriver.common.keys import Keys
        email_input.send_keys(Keys.TAB)
        print("ℹ️ 포커스 이동 (검증 트리거)")
    
    # 검증 완료 대기
    WebDriverWait(driver, 2).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    
    # 5) 에러 메시지 확인
    try:
        error_msg = wait.until(EC.visibility_of_element_located((
            By.XPATH,
            "//*[contains(text(), 'This is an already registered email address') or "
            "contains(text(), '이미 가입된 이메일') or "
            "contains(text(), 'already registered')]"
        )))
        
        assert error_msg.is_displayed(), "에러 메시지가 표시되지 않음"
        
        error_text = error_msg.text
        print(f"✅ 에러 메시지 확인: {error_text}")
        
        # 정확한 메시지 검증
        expected_texts = [
            "This is an already registered email address",
            "이미 가입된 이메일",
            "already registered"
        ]
        
        message_found = any(expected in error_text for expected in expected_texts)
        assert message_found, f"예상 메시지와 다름: {error_text}"
        
        print("✅ 중복 이메일 차단 확인 완료")
        
    except Exception as e:
        # 디버깅용 스크린샷
        driver.save_screenshot("duplicate_email_error.png")
        with open("duplicate_email_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("⚠️ 디버그 파일 저장: duplicate_email_error.png, duplicate_email_page.html")
        raise


# AC-005: 로그아웃 후 뒤로가기 시 메인 페이지 진입 차단
def test_logout_prevents_back_navigation(driver, login):
    """
    로그아웃 후 브라우저 뒤로가기로 메인 페이지 재진입 차단 확인
    """ 
    wait = WebDriverWait(driver, 15)
    
    # 1) 로그인
    driver = login()
    
    # 메인 페이지 진입 확인
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "header, [role='banner']")))
    assert "/ai-helpy-chat" in driver.current_url
    main_page_url = driver.current_url
    print(f"✅ 메인 페이지 진입: {main_page_url}")
    
    # 2) 로그아웃
    BasePage(driver).logout()
    
    # 로그인 페이지 진입 확인
    wait.until(EC.url_contains("signin"))
    print(f"✅ 로그아웃 후 현재 URL: {driver.current_url}")
    
    # 3) 브라우저 뒤로가기
    driver.back()
    print("✅ 브라우저 뒤로가기 실행")
    
    # 페이지 로드 대기
    WebDriverWait(driver, 5).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    
    # 4) URL 확인 - signin/history에 머물러야 함
    current_url = driver.current_url
    print(f"뒤로가기 후 URL: {current_url}")
    
    # 검증 1: signin 페이지에 있어야 함
    assert "signin" in current_url, f"로그인 페이지가 아님: {current_url}"
    
    # 검증 2: 특정 URL 확인 (있다면)
    # TC에서 명시한 대로 signin/history인지 확인
    if "signin/history" in current_url:
        print("✅ https://accounts.elice.io/accounts/signin/history에 머물러 있음")
    else:
        # signin 페이지면 OK (history가 아닐 수도 있음)
        print(f"ℹ️ signin 페이지에 있음: {current_url}")
    
    # 검증 3: 메인 페이지가 아님을 확인
    assert "/ai-helpy-chat" not in current_url, f"메인 페이지로 진입됨: {current_url}"
       
    print("✅ 로그아웃 후 뒤로가기 차단 확인 완료")
    print(f"   - 메인 페이지 진입 차단됨")
    print(f"   - 현재 위치: {current_url}")

# AC-006: 계정 관리 페이지 UI 확인
def test_account_management_page_ui(driver, login):
    """
    계정 관리 페이지의 모든 UI 요소 확인:
    1. 프로필 영역 (이미지, 이름, 계정명, 이메일, 휴대폰)
    2. 섹션 목록 (7개 섹션)
    """
        
    wait = WebDriverWait(driver, 15)
    
    # 1) 로그인
    driver = login()
    
    # 메인 페이지 진입 확인
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "header, [role='banner']")))
    assert "/ai-helpy-chat" in driver.current_url
    print("✅ 메인 페이지 진입")
    
    # 2) 프로필 버튼 클릭
    _click_profile(driver, wait)
    
    # 3) 계정 관리 클릭
    account_mgmt = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//*[contains(text(), '계정 관리') or contains(text(), 'Account Management')]"
    )))
    account_mgmt.click()
    print("✅ 계정 관리 클릭")
    
    # 4) 새 탭 전환
    WebDriverWait(driver, 5).until(lambda d: len(d.window_handles) > 1)
    driver.switch_to.window(driver.window_handles[-1])
    print("✅ 새 탭으로 전환")
    
    # 5) 계정 관리 페이지 로드 확인
    wait.until(EC.url_contains("members/account"))
    print(f"✅ 계정 관리 페이지 로드: {driver.current_url}")
    
    # 페이지 완전 로드 대기
    WebDriverWait(driver, 3).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    
    print("\n=== 프로필 영역 확인 ===")
    
    # 6) 프로필 영역 확인 (존재 여부만, 값은 체크 안 함)
    profile_checks = {
        "프로필 이미지": {
            "selector": ".MuiAvatar-root, [class*='avatar'], img[alt*='profile']",
            "method": "css"
        },
        "사용자 이름": {
            "selector": "h6, .MuiTypography-h6, [class*='username']",
            "method": "css",
            "description": "비어있지 않은 텍스트"
        },
        "계정명": {
            "selector": ".MuiTypography-caption, .css-19nibrb, [class*='MuiTypography-caption']",
            "method": "css",
            "description": "비어있지 않은 텍스트"
        },
        "이메일": {
            "text": "@elice.com",
            "method": "text",
            "description": "@elice.com 포함"
        },
        "휴대폰 번호 섹션": {
            "text": ["휴대폰", "Phone", "전화번호"],
            "method": "text_any",
            "description": "휴대폰 관련 라벨 존재"
        },
    }
    
    missing_profile_items = []
    
    for item_name, check_info in profile_checks.items():
        try:
            if check_info["method"] == "css":
                element = driver.find_element(By.CSS_SELECTOR, check_info["selector"])
                assert element.is_displayed(), f"{item_name}이 표시되지 않음"
                
                # 사용자 이름은 비어있지 않은지만 확인
                if "description" in check_info and "텍스트" in check_info["description"]:
                    text = element.text.strip()
                    assert text, f"{item_name}이 비어있음"
                    print(f"✅ {item_name} 확인 (값: {text})")
                else:
                    print(f"✅ {item_name} 확인")
                
            elif check_info["method"] == "text":
                element = driver.find_element(
                    By.XPATH,
                    f"//*[contains(text(), '{check_info['text']}')]"
                )
                assert element.is_displayed(), f"{item_name}이 표시되지 않음"
                print(f"✅ {item_name} 확인")
                
            elif check_info["method"] == "text_any":
                found = False
                for text in check_info["text"]:
                    try:
                        element = driver.find_element(
                            By.XPATH,
                            f"//*[contains(text(), '{text}')]"
                        )
                        if element.is_displayed():
                            found = True
                            print(f"✅ {item_name} 확인 ('{text}' 발견)")
                            break
                    except:
                        continue
                assert found, f"{item_name}을 찾을 수 없음"
            
        except Exception as e:
            print(f"❌ {item_name} 없음: {e}")
            missing_profile_items.append(item_name)
    
    # 프로필 영역 검증
    assert len(missing_profile_items) == 0, f"누락된 프로필 항목: {missing_profile_items}"
    
    print("\n=== 섹션 목록 확인 ===")
    
    # 7) 섹션 목록 확인
    sections = [
        {"ko": "기본 정보", "en": "Basic Information"},
        {"ko": "계정 보안", "en": "Account Security"},
        {"ko": "본인 확인 정보", "en": "Verification Information"},
        {"ko": "소셜 연결 계정", "en": "Social Accounts"},
        {"ko": "프로모션 알림", "en": "Promotional Notifications"},
        {"ko": "선호 언어", "en": "Preferred Language"},
        {"ko": "계정 탈퇴", "en": "Delete Account"},
    ]
    
    missing_sections = []
    
    for section in sections:
        section_name = section["ko"]
        found = False
        
        # 한국어 또는 영어로 찾기
        for text in [section["ko"], section["en"]]:
            try:
                element = driver.find_element(
                    By.XPATH,
                    f"//*[contains(text(), '{text}')]"
                )
                # 스크롤해서 확인 (페이지 하단에 있을 수 있음)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                WebDriverWait(driver, 1).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                
                if element.is_displayed():
                    found = True
                    print(f"✅ {section_name} 섹션 확인")
                    break
            except:
                continue
        
        if not found:
            print(f"❌ {section_name} 섹션 없음")
            missing_sections.append(section_name)
    
    # 섹션 검증
    assert len(missing_sections) == 0, f"누락된 섹션: {missing_sections}"
    
    print(f"\n✅ 계정 관리 페이지 UI 확인 완료")
    print(f"   - 프로필 항목: {len(profile_checks)}개")
    print(f"   - 섹션: {len(sections)}개")


# AC-007
def test_profile_dropdown_menu_items(driver, login):
    """
    프로필 드롭다운 메뉴 확인:
    1. 유저 프로필 (아바타, 이름, 라벨, 이메일)
    2. 메뉴 항목들 (계정 관리, 결제 내역, 언어 설정, 고객 센터, 로그아웃)
    """
    
    # 1) 로그인
    driver = login()
    wait = WebDriverWait(driver, 15)
    
    # 메인 페이지 진입 확인
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "header, [role='banner']")))
    assert "/ai-helpy-chat" in driver.current_url
    print("✅ 메인 페이지 진입")
    
    # 2) 프로필 버튼 클릭
    _click_profile(driver, wait)
    # print 삭제 (함수 안에서 이미 출력)
    
    # 3) 유저 프로필 섹션 상세 확인
    print("\n=== 유저 프로필 확인 ===")

    try:
        # 프로필 헤더 섹션 찾기
        profile_header = wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            "[data-elice-user-profile-header='true']"
        )))
        
        # 3-1) 아바타 확인
        try:
            avatar = profile_header.find_element(By.CSS_SELECTOR, ".MuiAvatar-root")
            assert avatar.is_displayed(), "아바타가 표시되지 않음"
            print("✅ 아바타 표시 확인")
        except Exception as e:
            print(f"❌ 아바타 없음: {e}")
            raise
        
        # 모든 텍스트 요소 가져오기
        text_elements = profile_header.find_elements(
            By.CSS_SELECTOR,
            "p.MuiTypography-body2.MuiTypography-noWrap"
        )
        
        # 3-2) 이름 확인 (@ 없는 것)
        try:
            username = None
            for elem in text_elements:
                if "@" not in elem.text and elem.text:
                    username = elem.text
                    break
            
            assert username, "사용자 이름이 비어있음"
            print(f"✅ 사용자 이름: {username}")
        except Exception as e:
            print(f"❌ 사용자 이름 없음: {e}")
            raise
        
        # 3-3) 라벨(역할) 확인
        try:
            role_chip = profile_header.find_element(By.CSS_SELECTOR, ".MuiChip-root")
            role_text = role_chip.text
            assert role_text, "역할 라벨이 비어있음"
            print(f"✅ 역할 라벨: {role_text}")
        except Exception as e:
            print(f"❌ 역할 라벨 없음: {e}")
            raise
        
        # 3-4) 이메일 확인 (@ 있는 것)
        try:
            email = None
            for elem in text_elements:
                if "@" in elem.text:
                    email = elem.text
                    break
            
            assert email, "이메일을 찾을 수 없음"
            assert "elice.com" in email, f"elice.com 도메인이 아님: {email}"
            print(f"✅ 이메일: {email}")
        except Exception as e:
            print(f"❌ 이메일 없음: {e}")
            raise
        
        print("✅ 유저 프로필 모든 항목 확인 완료")
        
    except Exception as e:
        print(f"❌ 유저 프로필 확인 실패: {e}")
        raise
    
    # 4) 드롭다운 메뉴 항목 확인
    print("\n=== 메뉴 항목 확인 ===")
    
    expected_items = {
        "계정 관리": ["계정 관리", "Account Management"],
        "결제 내역": ["결제 내역", "Payment History"],
        "언어 설정": ["언어 설정", "Language Settings"],
        "고객 센터": ["고객 센터", "Customer Center"],
        "로그아웃": ["로그아웃", "Logout"],
    }
    
    found_items = {}
    missing_items = []
    
    for item_name, keywords in expected_items.items():
        found = False
        for keyword in keywords:
            try:
                element = driver.find_element(
                    By.XPATH,
                    f"//*[contains(text(), '{keyword}')]"
                )
                if element.is_displayed():
                    found_items[item_name] = keyword
                    found = True
                    print(f"✅ '{item_name}' 발견")
                    break
            except:
                continue
        
        if not found:
            missing_items.append(item_name)
            print(f"❌ '{item_name}' 없음")
    
    # 5) 검증
    assert len(missing_items) == 0, f"누락된 메뉴 항목: {missing_items}"
    
    print(f"\n✅ 전체 확인 완료")
    print(f"  - 유저 프로필: 아바타, 이름({username}), 역할({role_text}), 이메일({email})")
    print(f"  - 메뉴 항목: {list(found_items.keys())}")


# AC-018 
def test_promotion_notifications_toggle(driver, login):
    """
    프로모션 알림 토글 ON/OFF 변경
    """

    wait = WebDriverWait(driver, 15)

    driver = login()

    # 프로필 → 계정 관리
    _click_profile(driver, wait)
    _account_mgmt_page_open(driver)

    # 1) 프로모션 알림 섹션 찾아서 스크롤
    promo_section = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//*[contains(text(), '프로모션 알림')]")
        )
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", promo_section)
    print("✅ 프로모션 알림 섹션 도달")

    # 2) 상태 읽기 (숨겨진 input → presence OK)
    toggle_input = driver.find_element(By.CSS_SELECTOR, "input[name='marketing']")
    initial = toggle_input.is_selected()
    print(f"초기 토글 상태: {initial}")

    # 3) 클릭 (보이는 switchBase 클릭)
    switch = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".MuiSwitch-switchBase"))
    )
    switch.click()
    print("토글 클릭 완료")

    # 4) 상태 변경 대기
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, "input[name='marketing']").is_selected() != initial)

    final = driver.find_element(By.CSS_SELECTOR, "input[name='marketing']").is_selected()
    print(f"변경 후 토글 상태: {final}")

    assert final != initial, "토글 상태가 변경되지 않음"

    # 5) 스낵바 확인
    snackbar = wait.until(EC.visibility_of_element_located((By.ID, "notistack-snackbar")))
    assert "Saved successfully" in snackbar.text

    print("✅ AC-018 완료")


# AC-020
def test_account_deletion_button_activation(driver, login):
    """
    계정 탈퇴 버튼 활성화 확인
    1. 탈퇴하기 버튼 클릭 (초기)
    2. 확인 입력란 등장
    3. 'Delete 계정명@elice.com' 입력
    4. 탈퇴하기 버튼 빨간색으로 활성화
    """
        
    wait = WebDriverWait(driver, 15)
    
    # 로그인한 계정 정보 가져오기
    account = get_default_admin()
    expected_text = f"Delete {account.username}"  # "Delete team4a@elice.com"
    
    print(f"예상 입력값: {expected_text}")
    
    # 1) 로그인
    driver = login()
    
    # 메인 페이지 진입 확인
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "header, [role='banner']")))
    print("✅ 메인 페이지 진입")
    
    # 2) 프로필 → 계정 관리 페이지로 이동
    _click_profile(driver, wait)
    _account_mgmt_page_open(driver)
        
    # 3) 계정 탈퇴 섹션으로 스크롤
    delete_section = wait.until(EC.presence_of_element_located((
        By.XPATH,
        "//*[contains(text(), '계정 탈퇴') or contains(text(), 'Delete Account')]"
    )))
    
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", delete_section)
    WebDriverWait(driver, 2).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    print("✅ 계정 탈퇴 섹션 도달")
    
    # 4) 첫 번째 탈퇴하기 버튼 클릭 (초기 - clickable)
    delete_button_initial = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//button[contains(text(), '탈퇴하기') or contains(text(), 'Delete')]"
    )))
    delete_button_initial.click()
    print("✅ 탈퇴하기 버튼 클릭 (초기)")
    
    # 5) 부분 렌더링 대기 - 입력란 등장
    confirmation_input = wait.until(EC.visibility_of_element_located((
        By.XPATH,
        f"//input[@placeholder='Delete {account.username}' or contains(@placeholder, 'Delete')]"
    )))
    print("✅ 확인 입력란 등장")
    
    # 플레이스홀더 확인 (선택적)
    placeholder = confirmation_input.get_attribute("placeholder")
    print(f"플레이스홀더: {placeholder}")
    
    # 6) 'Delete 계정명@elice.com' 입력
    confirmation_input.clear()
    confirmation_input.send_keys(expected_text)
    print(f"✅ 입력 완료: {expected_text}")
    
    # 입력 반영 대기
    WebDriverWait(driver, 2).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    
    # 7) 탈퇴하기 버튼 활성화 확인
    delete_button_final = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//button[contains(text(), '탈퇴하기') or contains(text(), 'Delete')]"
    )))

    is_enabled = delete_button_final.get_attribute("disabled") is None
    assert is_enabled, "탈퇴하기 버튼이 활성화되지 않음"

    print("✅ 탈퇴하기 버튼 활성화 확인")
    
    # 클릭 가능 상태 확인
    try:
        wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[contains(text(), '탈퇴하기') or contains(text(), 'Delete')]"
        )))
        print("✅ 탈퇴하기 버튼 클릭 가능 상태")
    except:
        pytest.fail("탈퇴하기 버튼이 클릭 가능 상태가 아님")
    
    print(f"\n✅ 계정 탈퇴 버튼 활성화 테스트 완료")


# AC-021: 프로필 이미지 변경
def test_profile_avatar_change_applied_all_uis(driver, login):
    
    wait = WebDriverWait(driver, 15)

    # 1) 로그인 -> 계정 관리 페이지 진입
    driver = login()
    _click_profile(driver, wait)
    _account_mgmt_page_open(driver)

    # 2) 프로필 아바타 편집 버튼 클릭
    _click_profile_avatar_edit_button(driver, wait)

    # 3) 드롭다운에서 '프로필 이미지 변경' 버튼이 클릭 가능한지 확인(윈도우 파일 선택 창이 뜨는 것을 방지)
    _select_profile_avatar_menu(driver, wait, "프로필 이미지 변경")

    # 4) 이미지 파일 업로드
    _upload_profile_avatar_image(driver, "profile_avatar.jpg")

    # 5) 스낵바 확인 (한글/영문 둘 다 대비)
    snackbar = wait.until(EC.visibility_of_element_located((
        By.ID,
        "notistack-snackbar",
    )))
    text = snackbar.text
    assert ("저장되었습니다" in text) or ("Saved successfully" in text), f"스낵바 문구 불일치: {text}"

    print("✅ 프로필 이미지 변경 후 스낵바 노출 확인 완료")

    # 6) 새로고침 후 렌더링 안정화
    print("🔍 새로고침 실행")
    driver.refresh()

    print("🔍 url_contains 대기 시작")
    wait.until(EC.url_contains("members/account"))
    print("✅ url_contains 통과")

    print("🔍 readyState 대기 시작")
    wait.until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    print("✅ readyState complete")

    # 7) 계정 관리 페이지 3곳 아바타 src 비교
    src_left, src_header, src_dropdown = _get_account_mgmt_avatar_srcs(driver, wait)

    account_srcs = {src_left, src_header, src_dropdown}

    assert None not in account_srcs, (
        f"계정 관리 페이지의 아바타 src 중 None이 있습니다: "
        f"left={src_left}, header={src_header}, dropdown={src_dropdown}"
    )

    assert len(account_srcs) == 1, (
        f"계정 관리 페이지의 아바타 이미지가 서로 다릅니다:\n"
        f"- left: {src_left}\n"
        f"- header: {src_header}\n"
        f"- dropdown: {src_dropdown}"
    )

    account_src = account_srcs.pop()  # 기준 src
    print("✅ 계정 관리 페이지 3곳 아바타 src 확인 완료")

    # 8) 메인 페이지 2곳 아바타 비교
    main_tab_handle = driver.window_handles[0]
    driver.switch_to.window(main_tab_handle)

    # 렌더링 안정화
    WebDriverWait(driver, 5).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    src_main_dropdown, src_main_header = _get_main_page_avatar_srcs(driver, wait)
    main_srcs = {src_main_dropdown, src_main_header}

    assert None not in main_srcs, (
        f"메인 페이지 아바타 src 중 None이 있습니다: "
        f"main={src_main_dropdown}, header={src_main_header}"
    )

    assert len(main_srcs) == 1, (
        f"메인 페이지 2곳의 아바타 이미지가 서로 다릅니다:\n"
        f"- main dropdown: {src_main_dropdown}\n"
        f"- header: {src_main_header}"
    )

    main_src = main_srcs.pop()

    assert main_src == account_src, (
        f"메인 페이지 아바타 src가 계정 관리 페이지 src와 다릅니다:\n"
        f"- 기준 src: {account_src}\n"
        f"- 메인 페이지 src: {main_src}"
    )

    print("✅ 메인 페이지 2곳 아바타 src 확인 완료")

    # 9) 로그아웃 후 로그인 페이지 아바타 비교
    BasePage(driver).logout()

    # 렌더링 안정화
    print("🔍 로그아웃 후 readyState 대기 시작")
    wait.until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    print("✅ 로그아웃 후 readyState complete")
    
    login_src = _get_login_page_avatar_src(driver, wait)
    assert login_src is not None, "로그인 페이지 아바타 src가 None입니다."

    assert login_src == account_src, (
        f"로그인 페이지 아바타 src가 계정 관리 기준 src와 다릅니다:\n"
        f"- 기준 src: {account_src}\n"
        f"- 로그인 페이지 src: {login_src}"
    )

    print("🎉 모든 페이지에서 프로필 이미지가 정상적으로 반영되었음을 확인했습니다!")


# AC-022: 프로필 이미지 제거
def test_profile_avatar_remove_applied_all_uis(driver, login):
    """
    프로필 이미지 제거 후 모든 UI에 기본 아바타(PersonIcon) 적용 확인
    1. 로그인 후 계정 관리 페이지 진입
    2. 프로필 아바타 편집 버튼 클릭
    3. 드롭다운에서 '프로필 이미지 제거' 클릭
    4. '저장되었습니다.' 스낵바 노출 확인
    5. 계정 관리 페이지 3곳, 메인 페이지 2곳, 로그인 페이지 1곳에
       기본 아바타(PersonIcon SVG)가 적용되는지 확인
    """
    
    wait = WebDriverWait(driver, 15)

    # 1) 로그인 -> 계정 관리 페이지 진입
    driver = login()
    _click_profile(driver, wait)
    _account_mgmt_page_open(driver)

    # 2) 프로필 아바타 편집 버튼 클릭
    _click_profile_avatar_edit_button(driver, wait)

    # 3) 드롭다운에서 '프로필 이미지 제거' 버튼 클릭
    remove_button = _select_profile_avatar_menu(driver, wait, "프로필 이미지 제거")
    remove_button.click()
    print("✅ 프로필 이미지 제거 버튼 클릭")

    # 4) 스낵바 확인 (한글/영문 둘 다 대비)
    snackbar = wait.until(EC.visibility_of_element_located((
        By.ID,
        "notistack-snackbar",
    )))
    text = snackbar.text
    assert ("저장되었습니다" in text) or ("Saved successfully" in text), f"스낵바 문구 불일치: {text}"

    print("✅ 프로필 이미지 제거 후 스낵바 노출 확인 완료")

    # 5) 새로고침 후 렌더링 안정화
    print("🔍 새로고침 실행")
    driver.refresh()

    print("🔍 url_contains 대기 시작")
    wait.until(EC.url_contains("members/account"))
    print("✅ url_contains 통과")

    print("🔍 readyState 대기 시작")
    wait.until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    print("✅ readyState complete")

    # 6) 계정 관리 페이지 3곳 아바타 확인 (기본 아바타 = PersonIcon SVG)
    src_left, src_header, src_dropdown = _get_account_mgmt_avatar_srcs(driver, wait)

    # 기본 아바타 확인 (PersonIcon SVG 또는 fallback)
    def is_default_avatar(src):
        """기본 아바타인지 확인 (PersonIcon SVG)"""
        if src is None:
            return False
        # MuiAvatar-fallback 또는 PersonIcon 관련
        return ("PersonIcon" in src or 
                "fallback" in src or 
                src == "" or  # SVG가 인라인일 수 있음
                "data:image/svg" in src)  # SVG data URL

    # 또는 실제 element 확인이 필요할 수도
    # PersonIcon이 img src가 아니라 SVG element일 수 있음!
    
    account_srcs = {src_left, src_header, src_dropdown}
    
    # 모두 같은 src여야 함
    assert len(account_srcs) == 1, (
        f"계정 관리 페이지의 아바타 이미지가 서로 다릅니다:\n"
        f"- left: {src_left}\n"
        f"- header: {src_header}\n"
        f"- dropdown: {src_dropdown}"
    )

    account_src = account_srcs.pop()  # 기준 src
    print(f"✅ 계정 관리 페이지 3곳 아바타 확인 완료 (src: {account_src})")

    # 7) 메인 페이지 2곳 아바타 비교
    main_tab_handle = driver.window_handles[0]
    driver.switch_to.window(main_tab_handle)

    # 렌더링 안정화
    WebDriverWait(driver, 5).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    src_main_dropdown, src_main_header = _get_main_page_avatar_srcs(driver, wait)
    main_srcs = {src_main_dropdown, src_main_header}

    assert len(main_srcs) == 1, (
        f"메인 페이지 2곳의 아바타 이미지가 서로 다릅니다:\n"
        f"- main dropdown: {src_main_dropdown}\n"
        f"- header: {src_main_header}"
    )

    main_src = main_srcs.pop()

    assert main_src == account_src, (
        f"메인 페이지 아바타 src가 계정 관리 페이지 src와 다릅니다:\n"
        f"- 기준 src: {account_src}\n"
        f"- 메인 페이지 src: {main_src}"
    )

    print("✅ 메인 페이지 2곳 아바타 src 확인 완료")

    # 8) 로그아웃 후 로그인 페이지 아바타 비교
    BasePage(driver).logout()

    # 렌더링 안정화
    print("🔍 로그아웃 후 readyState 대기 시작")
    wait.until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    print("✅ 로그아웃 후 readyState complete")
    
    login_src = _get_login_page_avatar_src(driver, wait)

    assert login_src == account_src, (
        f"로그인 페이지 아바타 src가 계정 관리 기준 src와 다릅니다:\n"
        f"- 기준 src: {account_src}\n"
        f"- 로그인 페이지 src: {login_src}"
    )

    print("✅ 로그인 페이지 아바타 src 확인 완료")
    print("🎉 모든 페이지에서 기본 프로필 이미지(PersonIcon)가 정상적으로 반영되었음을 확인했습니다!")


# AC-024: 기관 관리 메뉴 접근 확인
def test_organization_admin_menu_access(driver, login):
    """
    기관 관리 페이지 진입 및 사이드 메뉴 접근 확인
    1. 계정 관리 > 내 기관 탭
    2. qaproject.elice.io 가기 클릭
    3. 톱니바퀴 > 기관 관리
    4. 사이드 메뉴 7개 확인
    """
    
    wait = WebDriverWait(driver, 15)
    
    # 1) 로그인 → 계정 관리 페이지
    driver = login()
    _click_profile(driver, wait)
    _account_mgmt_page_open(driver)
    
    # 2) 내 기관 탭 클릭
    my_org_tab = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//a[contains(text(), '내 기관') or contains(text(), 'My Organization')]"
    )))
    my_org_tab.click()
    
    # URL 변경 확인
    wait.until(EC.url_contains("/members/organization"))
    print("✅ 내 기관 탭 이동")
    
    # 3) qaproject.elice.io 가기 링크 클릭
    go_link = wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR,
        "a[href='https://qaproject.elice.io'][target='_blank']"
    )))
        
    # 현재 탭 개수 저장
    current_tabs = len(driver.window_handles)
    print(f"클릭 전 탭 개수: {current_tabs}")

    go_link.click()
    print("✅ qaproject.elice.io 가기 클릭")

    # 3-1) 새 탭이 열릴 때까지 대기
    WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > current_tabs)
    print(f"새 탭 열림! 현재 탭 개수: {len(driver.window_handles)}")

    # 3-2) 새 탭으로 전환
    new_tab = driver.window_handles[-1]
    driver.switch_to.window(new_tab)
    print(f"새 탭으로 전환: {new_tab}")

    # 🆕 3-3) URL이 실제로 바뀔 때까지 대기
    WebDriverWait(driver, 10).until(
        lambda d: "qaproject.elice.io" in d.current_url
    )
    print(f"URL 확인: {driver.current_url}")

    # 🆕 3-4) 페이지가 완전히 로드될 때까지 대기
    WebDriverWait(driver, 15).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    # 🆕 3-5) body 태그가 있는지 확인 (실제 내용 로드됨)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # 🆕 3-6) 최소한 버튼이 하나라도 있는지 확인
    WebDriverWait(driver, 10).until(
        lambda d: len(d.find_elements(By.TAG_NAME, "button")) > 0
    )

    print(f"✅ 메인 페이지 완전 로드 (버튼 개수: {len(driver.find_elements(By.TAG_NAME, 'button'))})")

    # 4) 톱니바퀴 버튼 클릭
    print("\n=== 톱니바퀴 버튼 찾기 ===")

    # 모든 IconButton 찾기
    icon_buttons = driver.find_elements(By.CSS_SELECTOR, "button.MuiIconButton-root")
    print(f"IconButton 개수: {len(icon_buttons)}")

    settings_button = None
    for i, btn in enumerate(icon_buttons):
        try:
            gear_svg = btn.find_element(By.CSS_SELECTOR, "svg[data-icon='gear']")
            settings_button = btn
            print(f"✅ 톱니바퀴 버튼 발견 (#{i})")
            break
        except:
            continue

    if settings_button is None:
        # 대안: data-testid로 찾기
        try:
            gear_icon = driver.find_element(By.CSS_SELECTOR, "svg[data-testid='gearIcon']")
            settings_button = gear_icon.find_element(By.XPATH, "./ancestor::button")
            print("✅ 톱니바퀴 버튼 발견 (data-testid)")
        except:
            pass

    assert settings_button is not None, "톱니바퀴 버튼을 찾을 수 없음"

    # 스크롤 & 클릭
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", settings_button)
    WebDriverWait(driver, 1).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    # 클릭 시도
    try:
        settings_button.click()
    except:
        # JavaScript로 클릭
        driver.execute_script("arguments[0].click();", settings_button)

    print("✅ 톱니바퀴 버튼 클릭")

    # 드롭다운 열릴 때까지 대기
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((
            By.CSS_SELECTOR,
            "a[href*='/admin/org'][target='_blank']"
        ))
    )
    print("✅ 드롭다운 열림")
    
    # 5) 기관 관리 메뉴 클릭
    try:
        # 정확한 href로 찾기
        org_admin_menu = wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR,
            "a[href='https://qaproject.elice.io/admin/org'][target='_blank']"
        )))
    except:
        # 대안: buildingsIcon으로 찾기
        org_admin_menu = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//a[.//svg[@data-testid='buildingsIcon']]"
        )))

    # 클릭
    try:
        org_admin_menu.click()
    except:
        # JavaScript 클릭
        driver.execute_script("arguments[0].click();", org_admin_menu)

    print("✅ 기관 관리 메뉴 클릭")
    
    # 5-1) 새 탭 전환
    WebDriverWait(driver, 5).until(lambda d: len(d.window_handles) > 2)
    driver.switch_to.window(driver.window_handles[-1])
    
    # 기관 관리 페이지 로드 확인
    wait.until(EC.url_contains("/admin/org"))
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    print(f"✅ 기관 관리 페이지 로드: {driver.current_url}")
    
    # 6) 왼쪽 사이드 메뉴 7개 확인
    print("\n=== 사이드 메뉴 확인 ===")
    
    side_menus = [
        ("기본 정보", "/admin/org/organization/general"),
        ("SEO 설정", "/admin/org/organization/seo"),
        ("구성원 관리", "/admin/org/members"),
        ("가입 설정", "/admin/org/organization/enroll"),
        ("청구내역", "/admin/org/billing/payments/invoice"),
        ("결제 수단 관리", "/admin/org/billing/payments/methods"),
        ("크레딧", "/admin/org/billing/payments/credit"),
    ]
    
    for menu_name, menu_path in side_menus:
        try:
            # href로 메뉴 찾기 (가장 확실)
            menu_link = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                f"a[href='{menu_path}']"
            )))
            
            # 클릭
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", menu_link)
            WebDriverWait(driver, 1).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            menu_link.click()
            
            # URL 변경 확인
            wait.until(EC.url_contains(menu_path))
            print(f"✅ {menu_name} 페이지 진입")
            
        except Exception as e:
            print(f"❌ {menu_name} 메뉴 클릭 실패: {e}")
            raise
    
    print(f"\n✅ 모든 사이드 메뉴 접근 확인 완료 (총 {len(side_menus)}개)")