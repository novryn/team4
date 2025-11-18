# Defectives 🕵🏻‍♀️🕵🏻‍♂️🕵🏻‍♀️ 디펙티브즈 #

Bug + Detective = Defective

버그가 사라지는 순간까지 추적하는 사람들

문제의 근본 원인을 해부하고,

사용자의 경험을 더 나은 방향으로 밀어붙이는 품질 탐정단 입니다.

<br><br>

### 📌 팀 소개

- 이홍주(팀장) : TC제작, 테스트 자동화, 자료 작성
- 김은아(테스트 엔지니어): TC제작, 테스트 자동화, 자료 작성
- 황지애(테스트 엔지니어): TC제작, 테스트 자동화, 자료 작성, CI/CD 구현
- 이준혁(X)

<br><br>

### 📌 프로젝트 개요

프로젝트명: AI Helpy Chat QA 프로젝트

팀명: Defectives 디펙티브즈

목표: 이용자 중심의 웹 서비스 품질을 관리하며, 주요 기능의 정상 작동을 보장합니다.

대상 서비스: AI Helpy Chat 사이트

<br><br>

### 📌 테스트 케이스

[AI Helpy Chat QA 프로젝트 - 테스트 케이스 링크] → 🖱️클릭!
(https://docs.google.com/spreadsheets/d/1ZZv05y546QGz5dKMhhKX0-m8CWsCX8QYq6n-RxrV8to/edit?usp=sharing)

<br><br>

### 📌 테스트 범위

1.**빌링 & 이용내역**
- 크레딧 시스템: AI 서비스 이용량에 따른 선불 결제 방식
- 크레딧 충전: 다양한 금액 단위로 미리 충전
- 자동 충전: 크레딧 잔액이 설정 금액 이하로 떨어지면 자동 충전
- 결제 수단 관리: 카드 등록 및 기본 결제 수단 설정
- 이용 내역: 크레딧 충전/사용 내역, 기간별 사용량 조회

2.**채팅 히스토리**
- 새 채팅 시작: 새 대화 버튼으로 새로운 대화 세션 생성
- 히스토리 검색: 검색 기능으로 과거 대화 내용 검색
- 에이전트 탐색: 에이전트 검색으로 사용가능한 에이전트 목록 조회
- 대화 목록: 사이드바에서 과거 채팅 세션들을 시간순으로 표시
- 히스토리 타이틀 수정: 각 대화 세션의 제목 편집 가능
- 히스토리 보기: 선택한 대화 세션의 전체 내용 조회

3. **채팅 기본기능**
- AI 대화: 자연어로 AI와 실시간 질문/답변 대화
- 멀티모달 AI: 텍스트, 이미지, 문서 등 다양한 형태의 입력을 이해하고 처리하는 AI 기능
- 클립보드 복사: AI 응답 내용을 클립보드에 복사
- 응답 메시지 피드백: AI 답변에 대한 좋아요/싫어요 평가
- 메시지 수정: 사용자가 보낸 메시지 내용 편집
- 최근메시지 보기로 이동: 대화 중 가장 최근 메시지로 스크롤 이동

4. **채팅 고급기능**
- 파일업로드: 문서, 이미지 등 파일을 업로드하여 AI가 분석
- 심층조사: 주제에 대한 깊이 있는 리서치 및 분석 제공
- 구글검색: 실시간 웹 검색을 통한 최신 정보 활용
- PPT 제작: 주제와 조건에 따른 프레젠테이션 슬라이드 자동 생성
    - 입력: Topic(주제), Instructions(지시사항), Slides Count(슬라이드 수), Sections(섹션), Contexts(맥락)
    - 산출: 슬라이드별 텍스트와 필요한 이미지·차트·표로 구성
    - 활용: 생성 슬라이드를 참고해 실제 자료 제작 가속, 텍스트·PPT·PDF 요약 지원
- 퀴즈 생성: 학습 자료 기반 다양한 난이도와 유형의 퀴즈 제작
    - 입력: 난이도(쉬움/보통/어려움), 문제 유형(객관식 단일·복수, 주관식)
- 이미지 생성: 프로필, 아이콘, 보조 이미지 등 맞춤형 이미지 생성
    - 세부 기능: 프로필 일러스트, 강의용 아이콘, 시각화 보조 이미지 등 생성/편집

5. **맞춤화 기능**
- 커스텀 에이전트: 특정 목적과 역할에 맞게 맞춤 설정된 AI 어시스턴트
    - 생성:
        - AI와 대화로 생성하기
        - 설정: 에이전트 이미지 업로드, 이름, 설명, 규칙(목적·운영·제한사항), 시작 대화, 지식 파일 업로드, 기능 선택
    - 조회: 목록/미리보기에서 기본 정보 확인
    - 수정: 생성 시 입력한 모든 필드 수정 가능
    - 삭제: 불필요한 에이전트 제거
    - 공개범위 및 권한:
        - 전체기관공개: 전체기관의 모든 구성원들에게 보임 (엘리스관리자의 에이전트 관리권한 필요)
        - 나만보기: 해당기관내에서 본인만 보임

<br><br>

### 📌 진행 기간/ 일정

- 11.04 : 프로젝트 시작 / 역할 분담 / 테스트 케이스 설계

- 11.05 : TC 세분화 / 자동화 코드 작성

- 11.12 : 피드백 / 코드 수정

- 11.19: CI/CD 및 제줄 자료 작성

- 11.20 : 최종 정리 및 결과물 제출

<br><br>

### 📌 테스트 환경

**OS 및 사용 IDE:**
- Windows 11 (25H2) / VisualStudioCode
- Windows 11 (24H2) / VisualStudioCode
- Windows 10 Pro (22H2) / VisualStudioCode
- Browser: Chrome

<br><br>

### 📌 테스트 방식

<img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54">
<img src="https://img.shields.io/badge/-selenium-%43B02A?style=for-the-badge&logo=selenium&logoColor=white">
<img src="https://img.shields.io/badge/pytest-%23ffffff.svg?style=for-the-badge&logo=pytest&logoColor=2f9fe3">
<img src="https://img.shields.io/badge/jenkins-%232C5263.svg?style=for-the-badge&logo=jenkins&logoColor=white">

<br><br>

### 📌 설치할 프로그램

- JDK 17  
- python3-pip3  
- python3-venv  
- Google Chrome  
- Jenkins

<br><br>

### 📌 젠킨스 - 필수 플러그인

- git client
- git plugin
- gitlab api plugin
- gitlab plugin

<br><br>

### 📌 프로그램 실행 방법(Windows CMD/PowerShell)

1. 설치 방법

**파이썬과 pip 라이브러리 명령어:**

- `$ python -m venv venv`
- `$ venv/scripts/activate`
- `$ pip install -r requirements.txt`

2. 실행 방법

**가상환경 활성화(비활성화 상태 시 실행):**

- `$ venv/scripts/activate`

3. 파이테스트 실행:

- `$ pytest tests --html=reports/report.html --self-contained-html`

4. 가상환경 해제 방법

- `$ deactivate`

<br><br>

### 📌 Commit Conventions
| Message  | Description                   |
| -------- | ----------------------------- |      |
| feat     | added new feature             |
| refactor | updated existing feature/code |
| docs     | added/updated docs            |
| img      | added/updated images          |
| init     | added initial files           |
| ver      | updated version               |
| chore    | add library                   |