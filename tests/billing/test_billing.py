import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# ======================
# ✅ helper functions
# ======================
def _click_sidebar_link_payments(driver, wait, max_steps=20):
    """
    보이는(MUI Drawer) 사이드바 안에서 virtuso 리스트를 스크롤하며
    /admin/org/billing/payments 링크(credit 제외)를 찾아 클릭한다.
    """
    # 1) 보이는 Drawer (숨김 배제)
    drawer = wait.until(EC.presence_of_element_located((
        By.CSS_SELECTOR, ".MuiDrawer-root[aria-hidden='false'], .MuiDrawer-root:not([aria-hidden])"
    )))

    # 2) 보이는 Drawer 안의 Virtuoso 리스트 컨테이너(있으면 스크롤 타깃)
    #    없으면 Drawer 자체를 스크롤 타깃으로 사용
    try:
        list_container = drawer.find_element(By.CSS_SELECTOR, "[data-testid='virtuoso-item-list']")
    except Exception:
        list_container = drawer

    # 3) 현재 보이는 링크들에서 먼저 탐색 (credit 제외)
    def find_visible_payments():
        elems = drawer.find_elements(By.CSS_SELECTOR, "a[href*='/admin/org/billing/payments']")
        for a in elems:
            href = a.get_attribute("href") or ""
            if "/credit" in href:
                continue
            # '보이는지' 판별
            visible = driver.execute_script(
                "const el=arguments[0];"
                "return !!(el && el.offsetParent !== null && getComputedStyle(el).visibility!=='hidden');", a
            )
            if visible:
                return a
        return None

    target = find_visible_payments()
    if not target:
        # 4) 가상 스크롤: 아래로 조금씩 스크롤하며 탐색
        for _ in range(max_steps):
            driver.execute_script("arguments[0].scrollTop = (arguments[0].scrollTop||0) + 300;", list_container)
            # 스크롤 후 짧은 텀
            WebDriverWait(driver, 2).until(lambda d: True)
            target = find_visible_payments()
            if target:
                break

    # 5) 마지막 백업: 페이지 전역에서 가시 링크 탐색
    if not target:
        all_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/admin/org/billing/payments']")
        for a in all_links:
            href = a.get_attribute("href") or ""
            if "/credit" in href:
                continue
            visible = driver.execute_script(
                "const el=arguments[0];"
                "return !!(el && el.offsetParent !== null && getComputedStyle(el).visibility!=='hidden');", a
            )
            if visible:
                target = a
                break

    assert target is not None, "사이드바에서 '결제 수단 관리' 링크를 찾지 못했습니다."

    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", target)
    driver.execute_script("arguments[0].click()", target)
    wait.until(EC.url_contains("/billing/payments"))

def _dump(name, driver):
    path = os.path.join(os.getcwd(), name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    driver.save_screenshot(name.replace(".html", ".png"))
    print("디버그 저장:", path)

def switch_to_frame_with_element(driver, by, value, timeout=12):
    """모든 가시 iframe을 재귀 탐색해서 해당 요소가 보이는 프레임으로 진입."""
    driver.switch_to.default_content()
    end = WebDriverWait(driver, timeout)
    end.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "iframe")) > 0)

    def dfs():
        # 현재 프레임에서 찾기
        if driver.find_elements(by, value):
            return True
        # 하위 iframe 재귀
        frames = driver.find_elements(By.CSS_SELECTOR, "iframe")
        for fr in frames:
            if not fr.is_displayed(): 
                continue
            driver.switch_to.frame(fr)
            if dfs():
                return True
            driver.switch_to.parent_frame()
        return False

    return dfs()

def click_all_agree_btn(driver):
    # ① 백드롭/애니메이션 사라지길 잠깐 대기
    try:
        WebDriverWait(driver, 3).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".MuiBackdrop-root[aria-hidden='false']"))
        )
    except: 
        pass

    btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "BTN_ALL_CHECK")))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", btn)

    # ② JS 클릭
    try:
        driver.execute_script("arguments[0].click()", btn)
    except Exception:
        pass

    # ③ 안 먹히면 일반 click
    try:
        btn.click()
    except Exception:
        pass

    # ④ 그래도 안 되면 포커스+Space 키 (키보드 상호작용)
    try:
        driver.execute_script("arguments[0].focus()", btn)
        btn.send_keys("\ue00d")  # Enter
        btn.send_keys(" ")       # Space
    except Exception:
        pass

    # ⑤ 최후: 좌표 클릭(오버레이 미세 충돌 우회)
    try:
        ActionChains(driver).move_to_element(btn).pause(0.05).click().perform()
    except Exception:
        pass

    # ⑥ 선택(토글) 확인: 버튼 클래스/체크박스 상태 둘 중 하나
    ok = False
    try:
        ok = "on" in (btn.get_attribute("class") or "")
    except:
        pass
    if not ok:
        cbs = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        if cbs:
            ok = all(cb.is_selected() for cb in cbs if cb.is_displayed())

    assert ok, "‘전체 동의’가 켜지지 않았습니다."

# ======================
# ✅ test functions
# ======================
def test_register_payment_method_flow(driver, login):
    try:
        # 1. 로그인
        driver = login("team4@elice.com", "team4elice!@")
        # 로그인 성공 → 헤더가 보여야 한다
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "header, [role='banner']"))
        )

        assert "/ai-helpy-chat" in driver.current_url

        # 2. Credit 버튼 (우상단)
        credit = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href$='/admin/org/billing/payments/credit']"))
        )
        credit.click()

        # 2-1. 탭 전환 (새 탭 열린 경우)
        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) >= 1)

        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])

        # 2-2. 페이지 로딩 대기
        WebDriverWait(driver, 15).until(EC.url_contains("/billing/payments/credit"))

        
        # 3. 좌측 메뉴 → 결제 수단 관리 (정확 href만)
        # 3-1. 사이드바가 접혀 있으면 열기(있으면)
        try:
            driver.find_element(By.CSS_SELECTOR, "button[aria-label*='메뉴'], button[aria-label*='menu']").click()
        except Exception:
            pass

        # 3-2. 가장 정확: 텍스트로 지정
        try:
            pay = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,
                    "//a[normalize-space()='결제 수단 관리' or contains(.,'Payment Methods')]"))
            )
        except Exception:
            # 3-3. 백업: href로 지정 (invoice/credit 제외)
            pay = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                    "aside a[href='/admin/org/billing/payments'], nav a[href='/admin/org/billing/payments'], \
                    a[href$='/admin/org/billing/payments']:not([href*='/invoice']):not([href*='/credit'])"))
            )

        driver.execute_script("arguments[0].scrollIntoView({block:'center'})", pay)
        driver.execute_script("arguments[0].click()", pay)

        # 3-4. 진입 검증(다른 메뉴로 새는 것 방지)
        WebDriverWait(driver, 15).until(
            lambda d: "/admin/org/billing/payments" in d.current_url
                    and "invoice" not in d.current_url
                    and "credit"  not in d.current_url
        ) 

        # 4. 결제 수단 등록 버튼
        #    - 라벨이 바뀌기 쉬우니 data-test가 없을 경우 XPATH 텍스트 매칭
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space()='결제 수단 등록' or contains(.,'결제 수단 등록')]")
        )).click()

        # 5. KRW 선택
        driver.find_element(By.CSS_SELECTOR, "input[name='paymentCurrency'][value='KRW']").click()

        # 6. 확인 버튼 (통화 선택 다이얼로그)
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@role='dialog']//button[normalize-space()='확인']")
        )).click()
        
        # 7. 전체 동의 버튼 클릭
        # (새 탭이면 전환)
        WebDriverWait(driver, 2).until(lambda d: len(d.window_handles) >= 1)
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])

        # ▶ 전체동의 버튼이 있는 프레임으로 “재귀 진입”
        ok = switch_to_frame_with_element(driver, By.ID, "BTN_ALL_CHECK", timeout=15)
        assert ok, "BTN_ALL_CHECK가 담긴 iframe을 찾지 못했습니다."

        # ▶ 실제 상호작용으로 전체동의 켜기
        click_all_agree_btn(driver)

        # 끝나면 원래 문서로 복귀
        driver.switch_to.default_content()

        # 8. 카드번호 입력 (4칸 구조 대응)
        card_inputs = driver.find_elements(By.CSS_SELECTOR, "input[maxlength='4'], input[autocomplete='cc-number']")
        for elem, val in zip(card_inputs, ["1111", "2222", "3333", "4444"]):
            elem.clear()
            elem.send_keys(val)

        # 9. 유효기간 입력 (MM/YY 또는 MMYY 한칸 입력 대응)
        exp_month = driver.find_elements(By.CSS_SELECTOR, "input[placeholder*='MM']")
        exp_year  = driver.find_elements(By.CSS_SELECTOR, "input[placeholder*='YY'], input[placeholder*='년']")
        if exp_month: exp_month[0].send_keys("12")
        if exp_year: exp_year[0].send_keys("29")

        # 10. 다음 버튼이 활성화될 때까지 기다리기
        next_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'다음') or contains(.,'Next')]"))
        )

        # ✅ 지금은 **클릭하지 않고 활성화만 확인**
        assert next_btn.is_enabled()

        # 프레임 빠져나오기
        driver.switch_to.default_content()
    
    except Exception as e:
        driver.save_screenshot("debug_fail.png")
        print("DEBUG URL:", driver.current_url)
        print("DEBUG ERROR:", repr(e))
        raise
    
    finally:
        input("Press Enter to quit browser...")
