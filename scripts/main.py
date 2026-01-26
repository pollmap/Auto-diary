"""메인 실행 스크립트"""
import sys
from datetime import datetime
from data_fetcher import DataFetcher
from post_generator import PostGenerator
from telegram_notifier import TelegramNotifier


def generate_simple_summary(data: dict) -> str:
    """데이터 기반 간단 요약 생성 (AI 없이)"""
    lines = []

    # 미국 증시 요약
    us = data.get("us_indices", {})
    if us:
        sp500 = us.get("S&P 500", {})
        nasdaq = us.get("NASDAQ", {})
        if sp500.get("change"):
            direction = "상승" if sp500["change"] > 0 else "하락"
            lines.append(f"미국 증시는 S&P 500 {sp500['change']:+.2f}%, 나스닥 {nasdaq.get('change', 0):+.2f}%로 {direction} 마감했다.")

    # 암호화폐 요약
    crypto = data.get("crypto", {})
    if crypto:
        btc = crypto.get("BTC", {})
        if btc.get("change_24h"):
            direction = "상승" if btc["change_24h"] > 0 else "하락"
            lines.append(f"비트코인은 24시간 기준 {btc['change_24h']:+.2f}% {direction}했다.")

    # 환율 요약
    currencies = data.get("currencies", {})
    if currencies:
        usdkrw = currencies.get("USD/KRW", {})
        if usdkrw.get("price"):
            lines.append(f"원/달러 환율은 {usdkrw['price']:,.2f}원이다.")

    return " ".join(lines) if lines else "오늘의 시황 데이터를 확인하세요."


def main():
    """시황 브리핑 자동 생성 메인 함수"""
    print(f"[{datetime.now()}] 시황 브리핑 생성 시작...")

    # 1. 데이터 수집
    print("1. 데이터 수집 중...")
    fetcher = DataFetcher()
    market_data = fetcher.fetch_all()
    print(f"   - 수집 완료: {len(market_data)} 카테고리")

    # 2. 간단 요약 생성 (AI 없이)
    print("2. 요약 생성 중...")
    summary = generate_simple_summary(market_data)
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
