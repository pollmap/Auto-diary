# 이찬희의 디지털 두뇌

금융 시황 브리핑 자동 발행 + 개인 블로그 시스템

## 개요

- **플랫폼**: GitHub Pages + Jekyll
- **자동화**: GitHub Actions + Python
- **LLM**: Google Gemini Flash-Lite
- **알림**: Telegram Bot

## 기능

### 1. 시황 브리핑 (자동)
- 매일 오전 6시 (KST) 자동 발행
- 미국/글로벌 증시, 암호화폐, 환율, 원자재 데이터 수집
- AI 요약 생성 및 Telegram 알림

### 2. 수동 포스트
- 기업분석
- 임장 (부동산)
- 크립토
- 에세이

## 디렉토리 구조

```
├── _posts/           # 블로그 포스트
│   ├── market/       # 시황 브리핑 (자동)
│   ├── analysis/     # 기업분석 (수동)
│   └── ...
├── scripts/          # Python 자동화 스크립트
├── pages/            # 정적 페이지
├── _layouts/         # Jekyll 레이아웃
├── _includes/        # Jekyll 컴포넌트
├── assets/           # CSS, JS, 이미지
└── .github/workflows/ # GitHub Actions
```

## 설정

### 1. GitHub Secrets 등록

Repository Settings > Secrets and variables > Actions에서 등록:

- `GEMINI_API_KEY`: Google Gemini API 키
- `TELEGRAM_BOT_TOKEN`: Telegram Bot 토큰
- `TELEGRAM_CHAT_ID`: Telegram 채팅 ID

### 2. 로컬 개발

```bash
# Python 환경 설정
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Jekyll 설정
bundle install

# 로컬 서버 실행
bundle exec jekyll serve
```

### 3. 수동 시황 브리핑 생성

```bash
cd scripts
python main.py
```

## GitHub Actions

### daily-briefing.yml
- 매일 오전 6시 (KST) 자동 실행
- 수동 실행: Actions 탭 > workflow_dispatch

### jekyll-gh-pages.yml
- main 브랜치 push 시 자동 배포

## 데이터 소스

- **암호화폐**: CoinGecko API (무료)
- **주식/지수/원자재**: yfinance (무료)
- **AI 요약**: Google Gemini Flash-Lite (무료 티어)

## 라이선스

MIT License

---

*작성일 2026.01.26 | 이찬희*