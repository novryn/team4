### 4팀
AI Helpy Chat 서비스를 대상으로 한 QA 프로젝트입니다.
버그를 씹어먹고, 품질을 삼키는 팀 F.A.Q의 테스트 기록과 결과를 담고 있습니다.



### 📌 팀 소개

이홍주  | 팀장　　　  | TC제작, 테스트 자동화, 자료 작성
김은아   | 테스트 엔지니어  | TC제작, 테스트 자동화, 자료 작성
황지애   | 테스트 엔지니어  | TC제작, 테스트 자동화, 자료 작성, CI/CD 구현



### 📌 프로젝트 개요

프로젝트명: AI Helpy Chat QA 프로젝트

팀명: 4팀

목표: 이용자 중심의 웹 서비스 품질을 관리하며, 주요 기능의 정상 작동을 보장합니다.

대상 서비스: AI Helpy Chat 사이트



### 📌 테스트 케이스

https://docs.google.com/spreadsheets/d/1ZZv05y546QGz5dKMhhKX0-m8CWsCX8QYq6n-RxrV8to/edit?usp=sharing



### 📌 테스트 범위

# 1. 회원가입
- 회원가입 기능

# 2. 로그인
- 비밀번호 표시/가리기 기능
- 로그인 기능

# 3. 홈
- 혼자 먹기, 같이 먹기, 회식 하기에서 음식 추천 받는 기능
- 메뉴 추천 기능
- 나의 취향 분석 확인

# 4. 팀 피드
- 팀 변경 기능
- 팀 프로필 수정 기능
- 팀이 먹은 메뉴 확인
- 새로운 후기, 또 먹은 후기 기능

# 5. 히스토리
- 추천 받은 메뉴 확인
- 추천 후기 기능

# 6. 개인 피드
- 개인 프로필 수정 기능
- 새로운 후기, 또 먹은 후기 기능
- 내가 먹은 메뉴 확인



### 📌 진행 기간/ 일정

- 11.04 : 프로젝트 시작 / 역할 분담 / 테스트 케이스 설계

- 11.05 : TC 세분화 / 자동화 코드 작성

- 11.12 : 피드백 / 코드 수정

- 11.19: CI/CD 및 제줄 자료 작성

- 11.20 : 최종 정리 및 결과물 제출



### 📌 테스트 환경

# OS 및 사용 IDE:
- Windows 11 (25H2) / VisualStudioCode
- Windows 11 (24H2) / VisualStudioCode
- Windows 10 Pro (22H2) / VisualStudioCode
- Browser: Chrome


### 📌 테스트 방식

사용 언어: Python
자동화 테스트: Selenium, Pytest, Jenkins

<img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54">
<img src="https://img.shields.io/badge/-selenium-%43B02A?style=for-the-badge&logo=selenium&logoColor=white">
<img src="https://img.shields.io/badge/pytest-%23ffffff.svg?style=for-the-badge&logo=pytest&logoColor=2f9fe3">
<img src="https://img.shields.io/badge/jenkins-%232C5263.svg?style=for-the-badge&logo=jenkins&logoColor=white">



### 📌 설치할 프로그램

- JDK 17  
- python3-pip3  
- python3-venv  
- Google Chrome  
- Jenkins

### 📌 젠킨스 - 필수 플러그인

- git client
- git plugin
- gitlab api plugin
- gitlab plugin



### 📌 프로그램 실행 방법(Windows CMD/PowerShell)

1. 설치 방법

파이썬과 pip 라이브러리 명령어:

- `$ python -m venv venv`
- `$ venv/scripts/activate`
- `$ pip install -r requirements.txt`

2. 실행 방법

가상환경 활성화(비활성화 상태 시 실행):

- `$ venv/scripts/activate`

3. 파이테스트 실행:

- `$ pytest tests --html=reports/report.html --self-contained-html`

4. 가상환경 해제 방법

- `$ deactivate`



### 📌 Commit Conventions
| Message  | Description                   |
| -------- | ----------------------------- |
| fix      | fixed bugs and errors         |
| feat     | added new feature             |
| refactor | updated existing feature/code |
| docs     | added/updated docs            |
| img      | added/updated images          |
| init     | added initial files           |
| ver      | updated version               |
| chore    | add library                   |