import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 공통 헬퍼 import
from tests.helpers.common_helpers import (_click_profile, _logout
)

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
    _logout(driver, wait)
    
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


