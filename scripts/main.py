"""메인 실행 스크립트"""
import sys
from datetime import datetime
from data_fetcher import DataFetcher
from gemini_client import GeminiClient
from post_generator import PostGenerator
from telegram_notifier import TelegramNotifier


def main():
    """시황 브리핑 자동 생성 메인 함수"""
    print(f"[{datetime.now()}] 시황 브리핑 생성 시작...")

    # 1. 데이터 수집
    print("1. 데이터 수집 중...")
    fetcher = DataFetcher()
    market_data = fetcher.fetch_all()
    print(f"   - 수집 완료: {len(market_data)} 카테고리")

    # 2. AI 요약 생성
    print("2. AI 요약 생성 중...")
    gemini = GeminiClient()
    summary = gemini.generate_briefing_summary(market_data)
    print(f"   - 요약 생성 완료: {len(summary)}자")

    # 3. 포스트 생성
    print("3. 마크다운 포스트 생성 중...")
    generator = PostGenerator()
    post_path = generator.generate_briefing_post(market_data, summary)
    print(f"   - 포스트 생성: {post_path}")

    # 4. 텔레그램 알림
    print("4. 텔레그램 알림 발송 중...")
    # GitHub Pages URL 구성
    date_str = datetime.now().strftime("%Y/%m/%d")
    post_url = f"https://pollmap.github.io/Auto-diary/market/briefing/{date_str}/daily-market-briefing"

    notifier = TelegramNotifier()
    result = notifier.send_sync(summary, post_url)
    if result:
        print("   - 알림 발송 완료")
    else:
        print("   - 알림 발송 실패 (계속 진행)")

    print(f"[{datetime.now()}] 시황 브리핑 생성 완료!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
