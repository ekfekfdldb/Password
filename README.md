# 아이디/비밀번호 저장 프로그램

로컬에서 안전하게 아이디와 비밀번호를 저장하고 관리할 수 있는 **개인용 비밀번호 관리자 프로그램**입니다.  
PyInstaller로 빌드하여 **독립 실행형(.exe)** 으로 사용 가능합니다.

---

## 주요 기능

- **로컬 데이터베이스(SQLite)** 에 암호화(AES-GCM)된 형태로 저장
- **마스터 비밀번호 기반** 전체 잠금 기능
- **자동 잠금**: 일정 시간 미사용 시 앱 자동 잠김
- **비밀번호 생성기**: 안전한 랜덤 비밀번호 생성
- **클립보드 자동 삭제**: 일정 시간 후 자동으로 클립보드 내용 삭제
- **검색 기능**: 계정 이름으로 빠르게 검색 가능
- **실행 파일(.exe)** 생성으로 인터넷 없이 로컬에서 사용 가능

---

## 프로젝트 구조

```plaintext
password/
├── app/                     # 메인 애플리케이션 코드
│   ├── __pycache__/         # Python 캐시 (자동 생성, 무시)
│   ├── crypto.py            # 암호화(AES-GCM) 관련 코드
│   ├── generator.py         # 비밀번호 생성기 로직
│   ├── main.py              # 앱 실행 엔트리포인트
│   ├── store.py             # 데이터베이스 관리
│   ├── ui.py                # Tkinter UI
│   ├── utils.py             # 경로 처리, 공용 유틸 함수
│   └── version.py           # 버전 정보
├── build/                   # PyInstaller 빌드 캐시 (자동 생성)
├── dist/                    # 최종 빌드 산출물(.exe)
├── build.bat                # 윈도우 빌드 스크립트
├── icon.ico                 # 앱 아이콘
├── myvault_version.txt      # EXE 버전 정보(선택)
├── MyVault.spec             # PyInstaller 설정 파일(자동 생성)
├── README.md                # 프로젝트 설명 문서
├── requirements.txt         # 파이썬 패키지 의존성
└── run_app.py               # 빌드용 실행 진입점
```

---
## 설치 및 실행

### 1. 가상환경 설정 (선택)

```bush
python -m venv .venv
.\.venv\Scripts\activate   # Windows
```

### 2. 패키지 설치

```bush
pip install -r requirements.txt
```

### 실행 (개발 모드)

```bush
python run_app.py
```

---

## 빌드 방법 (Windows)

```bush
pyinstaller --onefile --noconsole --name MyVault --icon icon.ico --add-data "icon.ico;." run_app.py
```
빌드가 완료되면 dist/MyVault.exe에서 실행 파일을 확인할 수 있습니다.

---

## 보안 유의사항
- 마스터 비밀번호는 절대 분실 시 복구 불가.
- 모든 데이터는 AES-GCM 암호화 후 로컬 DB에 저장됩니다.
- 이 앱은 로컬 사용을 전제로 하며, 네트워크 통신은 하지 않습니다.

---

## 라이선스

이 프로젝트는 개인 학습/연습용으로 제작되었습니다.