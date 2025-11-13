import os
from dotenv import load_dotenv

load_dotenv()

# 기본 설정
BASE_URL = os.getenv("BASE_URL", "https://qaproject.elice.io/ai-helpy-chat")
DEFAULT_TIMEOUT = int(os.getenv("TIMEOUT", "10"))
HEADLESS = os.getenv("HEADLESS", "0") == "1"

# ========================================
# 관리자 계정 설정                          ------(11/13 황지애 추가)
# ========================================

class AdminAccount:
    """관리자 계정"""
    def __init__(self, username, password, description=""):
        self.username = username
        self.password = password
        self.description = description
    
    def __repr__(self):
        return f"<Admin: {self.username}>"

# 관리자 계정 정의
ADMIN1 = AdminAccount(
    username=os.getenv("ADMIN1_USERNAME"),
    password=os.getenv("ADMIN1_PASSWORD"),
    description="관리자 1"
)

ADMIN2 = AdminAccount(
    username=os.getenv("ADMIN2_USERNAME"),
    password=os.getenv("ADMIN2_PASSWORD"),
    description="관리자 2"
)

ADMIN3 = AdminAccount(
    username=os.getenv("ADMIN3_USERNAME"),
    password=os.getenv("ADMIN3_PASSWORD"),
    description="관리자 3"
)

ALL_ADMINS = [ADMIN1, ADMIN2, ADMIN3]

def get_default_admin():
    """
    기본 관리자 계정 반환
    - MY_ADMIN_ACCOUNT 환경변수 있으면 → 고정 계정
    - 없으면 → 랜덤 선택
    """
    import random
    
    account_name = os.getenv("MY_ADMIN_ACCOUNT")
    
    if account_name:
        mapping = {
            "ADMIN1": ADMIN1,
            "ADMIN2": ADMIN2,
            "ADMIN3": ADMIN3
        }
        account = mapping.get(account_name)
        if account:
            print(f"[고정 계정] {account_name} 사용")
            return account
        else:
            print(f"⚠️ 알 수 없는 계정: {account_name}, 랜덤 선택")
    
    account = random.choice(ALL_ADMINS)
    print(f"[랜덤 계정] {account.description} 선택")
    return account
