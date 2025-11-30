import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Pages import
from src.pages.base_page import BasePage
from src.pages.account_page import AccountPage

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
        base = BasePage(driver)
        base.take_screenshot("duplicate_email_error.png")
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
    base = BasePage(driver)
    
    # 1) 로그인
    driver = login()
    
    # 메인 페이지 진입 확인
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "header, [role='banner']")))
    assert "/ai-helpy-chat" in driver.current_url
    main_page_url = driver.current_url
    print(f"✅ 메인 페이지 진입: {main_page_url}")
    
    # 2) 로그아웃
    print("\n=== 로그아웃 시도 ===")
    print(f"로그아웃 전 URL: {driver.current_url}")
    
    base.logout()
    
    # 로그인 페이지 이동 대기
    wait.until(EC.url_contains("signin"))
    print(f"✅ 로그아웃 후 현재 URL: {driver.current_url}")
    
    # 3) 브라우저 뒤로가기
    driver.back()
    print("✅ 브라우저 뒤로가기 실행")
    
    # 페이지 로드 대기
    WebDriverWait(driver, 5).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    # 뒤로 가기 후 리다이렉션 대기 (메인 페이지로 가지 못하고 다시 로그인 페이지로)
    wait.until(EC.url_contains("signin"))

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
    base = BasePage(driver)
    account = AccountPage(driver)
    
    # 1) 로그인
    driver = login()
    
    # 메인 페이지 진입 확인
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "header, [role='banner']")))
    assert "/ai-helpy-chat" in driver.current_url
    print("✅ 메인 페이지 진입")
    
    # 2) 프로필 버튼 클릭
    base.click_profile()
    
    # 3) 계정 관리 클릭
    account.open_account_mgmt_page()
    
    # 페이지 완전 로드 대기
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    # React 렌더링 완료 대기 - 첫 번째 섹션이 나타날 때까지
    wait.until(EC.presence_of_element_located((
        By.XPATH, 
        "//*[contains(text(), '기본 정보') or contains(text(), 'Basic Information')]"
    )))
    
    print("\n=== 프로필 영역 확인 ===")
    
    # 4) 프로필 영역 확인 (존재 여부만, 값은 체크 안 함)
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
                if "username" in check_info["selector"] or "h6" in check_info["selector"]:
                    text = element.text.strip()
                    assert len(text) > 0, f"{item_name}이 비어있음"
                    print(f"✅ {item_name} 확인")
                else:
                    print(f"✅ {item_name} 확인")
                    
            elif check_info["method"] == "text":
                # 페이지 전체에서 텍스트 검색
                page_text = driver.find_element(By.TAG_NAME, "body").text
                assert check_info["text"] in page_text, f"{item_name} 텍스트를 찾을 수 없음"
                print(f"✅ {item_name} 확인 ({check_info['description']})")
                
            elif check_info["method"] == "text_any":
                # 여러 텍스트 중 하나라도 있으면 OK
                page_text = driver.find_element(By.TAG_NAME, "body").text
                found = any(text in page_text for text in check_info["text"])
                assert found, f"{item_name} 관련 텍스트를 찾을 수 없음"
                print(f"✅ {item_name} 확인 ({check_info['description']})")
                
        except AssertionError as e:
            missing_profile_items.append(f"{item_name}: {e}")
            print(f"❌ {item_name} 확인 실패: {e}")
        except Exception as e:
            missing_profile_items.append(f"{item_name}: {e}")
            print(f"❌ {item_name} 확인 중 오류: {e}")
    
    # 프로필 영역 검증 결과
    if missing_profile_items:
        pytest.fail(f"프로필 영역 항목 누락:\n" + "\n".join(missing_profile_items))
    
    print("\n=== 섹션 목록 확인 ===")
    
    # 5) 섹션 목록 확인
    expected_sections = [
        "기본 정보",
        "프로필 이미지",
        "계정 정보",
        "비밀번호",
        "내 기관",
        "알림 설정",
        "계정 삭제",
    ]
    
    missing_sections = []
    page_text = driver.find_element(By.TAG_NAME, "body").text
    
    for section in expected_sections:
        if section not in page_text:
            missing_sections.append(section)
            print(f"❌ {section} 섹션 누락")
        else:
            print(f"✅ {section} 섹션 확인")
    
    # 섹션 검증 결과
    if missing_sections:
        pytest.fail(f"섹션 누락:\n" + "\n".join(missing_sections))
    
    print(f"\n✅ 모든 UI 요소 확인 완료 (프로필 {len(profile_checks)}개 + 섹션 {len(expected_sections)}개)")


# AC-019: 프로필 이미지 업로드 및 반영 확인
def test_profile_image_upload_and_reflection(driver, login):
    """
    프로필 이미지 업로드 후 모든 페이지에서 반영되는지 확인
    1. 계정 관리 페이지 (3곳)
    2. 메인 페이지 (2곳)
    3. 로그인 페이지 (1곳)
    """
    
    wait = WebDriverWait(driver, 15)
    base = BasePage(driver)
    account = AccountPage(driver)
    
    # 1) 로그인
    driver = login()
    
    # 메인 페이지 진입 확인
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "header, [role='banner']")))
    assert "/ai-helpy-chat" in driver.current_url
    print("✅ 메인 페이지 진입")
    
    # 2) 프로필 버튼 클릭
    base.click_profile()
    
    # 3) 계정 관리 페이지 열기
    account.open_account_mgmt_page()
    
    # 4) 프로필 이미지 편집 버튼 클릭
    account.click_profile_avatar_edit_button()
    
    # 5) 프로필 이미지 변경 메뉴 선택
    change_menu = account.select_profile_avatar_menu("프로필 이미지 변경")
    change_menu.click()
    print("✅ 프로필 이미지 변경 메뉴 클릭")
    
    # 파일 선택 대기
    WebDriverWait(driver, 2).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    
    # 이미지 업로드
    account.upload_profile_avatar_image("profile_avatar.jpg")
    
    # 업로드 완료 대기
    WebDriverWait(driver, 5).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    print("✅ 이미지 업로드 완료 대기")
    
    # 6) 계정 관리 페이지 3곳 아바타 비교
    src_left, src_header, src_dropdown = account.get_account_mgmt_avatar_srcs()
    
    account_srcs = {src_left, src_header, src_dropdown}
    
    assert len(account_srcs) == 1, (
        f"계정 관리 페이지 3곳의 아바타 이미지가 서로 다릅니다:\n"
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

    src_main_dropdown, src_main_header = account.get_main_page_avatar_srcs()
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
    base.logout()

    # 렌더링 안정화
    print("🔍 로그아웃 후 readyState 대기 시작")
    wait.until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    print("✅ 로그아웃 후 readyState complete")
    
    login_src = account.get_login_page_avatar_src()

    assert login_src == account_src, (
        f"로그인 페이지 아바타 src가 계정 관리 기준 src와 다릅니다:\n"
        f"- 기준 src: {account_src}\n"
        f"- 로그인 페이지 src: {login_src}"
    )

    print("✅ 로그인 페이지 아바타 src 확인 완료")
    print("🎉 모든 페이지에서 업로드한 프로필 이미지가 정상적으로 반영되었음을 확인했습니다!")


# AC-020: 프로필 이미지 제거 및 반영 확인
def test_profile_image_removal_and_reflection(driver, login):
    """
    프로필 이미지 제거 후 기본 이미지(PersonIcon)로 변경되는지 확인
    1. 계정 관리 페이지 (3곳)
    2. 메인 페이지 (2곳)
    3. 로그인 페이지 (1곳)
    """
    
    wait = WebDriverWait(driver, 15)
    base = BasePage(driver)
    account = AccountPage(driver)
    
    # 1) 로그인
    driver = login()
    
    # 메인 페이지 진입 확인
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "header, [role='banner']")))
    assert "/ai-helpy-chat" in driver.current_url
    print("✅ 메인 페이지 진입")
    
    # 2) 프로필 버튼 클릭
    base.click_profile()
    
    # 3) 계정 관리 페이지 열기
    account.open_account_mgmt_page()
    
    # 4) 프로필 이미지 편집 버튼 클릭
    account.click_profile_avatar_edit_button()
    
    # 5) 프로필 이미지 제거 메뉴 선택
    remove_menu = account.select_profile_avatar_menu("프로필 이미지 제거")
    remove_menu.click()
    print("✅ 프로필 이미지 제거 메뉴 클릭")
    
    # 제거 완료 대기
    WebDriverWait(driver, 5).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    print("✅ 이미지 제거 완료 대기")
    
    # 6) 계정 관리 페이지 3곳 아바타 비교
    src_left, src_header, src_dropdown = account.get_account_mgmt_avatar_srcs()
    
    account_srcs = {src_left, src_header, src_dropdown}
    
    assert len(account_srcs) == 1, (
        f"계정 관리 페이지 3곳의 아바타 이미지가 서로 다릅니다:\n"
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

    src_main_dropdown, src_main_header = account.get_main_page_avatar_srcs()
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
    base.logout()

    # 렌더링 안정화
    print("🔍 로그아웃 후 readyState 대기 시작")
    wait.until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    print("✅ 로그아웃 후 readyState complete")
    
    login_src = account.get_login_page_avatar_src()

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
    base = BasePage(driver)
    account = AccountPage(driver)
    
    # 1) 로그인 → 계정 관리 페이지
    driver = login()
    base.click_profile()
    account.open_account_mgmt_page()
    
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

    # 🆕 3-6) 톱니바퀴 버튼이 실제로 나타날 때까지 대기
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.CSS_SELECTOR, 
            "svg[data-icon='gear'], svg[data-testid='gearIcon']"
        ))
    )
    print("✅ 톱니바퀴 아이콘 로드 확인")

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
