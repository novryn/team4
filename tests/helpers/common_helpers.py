from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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


def _logout(driver, wait):
    """로그아웃"""
    try:
        # 프로필 클릭
        _click_profile(driver, wait)
        
        # Logout 버튼이 클릭 가능할 때까지 대기
        logout_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//*[contains(text(), 'Logout') or contains(text(), '로그아웃')]")
        ))
        logout_btn.click()
        
        # 로그인 페이지 이동 확인
        wait.until(EC.url_contains("signin"))
        print("✅ 로그아웃 완료")
        
    except Exception as e:
        print(f"⚠️ UI 로그아웃 실패, 쿠키 삭제로 대체: {e}")
        driver.delete_all_cookies()
        driver.refresh()


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