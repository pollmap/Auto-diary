"""메인 실행 스크립트"""
import sys
from datetime import datetime
from data_fetcher import DataFetcher
from post_generator import PostGenerator
from telegram_notifier import TelegramNotifier


def generate_simple_summary(data: dict) -> str:
    """데이터 기반 간단 요약 생성 (AI 없이)"""
    lines = []

    # VIX 상태
    vix = data.get("market_indicators", {}).get("VIX (공포지수)", {})
    if vix.get("price"):
        vix_val = vix["price"]
        if vix_val < 15:
            lines.append(f"VIX {vix_val:.1f}로 시장은 낙관적 분위기다.")
        elif vix_val < 20:
            lines.append(f"VIX {vix_val:.1f}로 시장은 안정적이다.")
        elif vix_val < 30:
            lines.append(f"VIX {vix_val:.1f}로 변동성이 다소 높다.")
        else:
            lines.append(f"VIX {vix_val:.1f}로 공포 구간에 진입했다.")

    # 미국 증시 요약
    us = data.get("us_indices", {})
    if us:
        sp500 = us.get("S&P 500", {})
        nasdaq = us.get("NASDAQ", {})
        dow = us.get("다우존스", {})
        if sp500.get("change") is not None:
            direction = "상승" if sp500["change"] > 0 else "하락"
            lines.append(f"미국 증시는 S&P500 {sp500['change']:+.2f}%, 나스닥 {nasdaq.get('change', 0):+.2f}%, 다우 {dow.get('change', 0):+.2f}%로 {direction} 마감.")

    # 빅테크 요약
    mag7 = data.get("mag7", {})
    if mag7:
        best = max(mag7.items(), key=lambda x: x[1].get('change', -999) if x[1].get('change') is not None else -999)
        worst = min(mag7.items(), key=lambda x: x[1].get('change', 999) if x[1].get('change') is not None else 999)
        if best[1].get('change') is not None and worst[1].get('change') is not None:
            lines.append(f"빅테크 중 {best[0]}({best[1]['change']:+.2f}%) 강세, {worst[0]}({worst[1]['change']:+.2f}%) 약세.")

    # 암호화폐 요약
    crypto = data.get("crypto", {})
    if crypto:
        btc = crypto.get("BTC", {})
        eth = crypto.get("ETH", {})
        if btc.get("price_usd") and btc.get("change_24h") is not None:
            direction = "상승" if btc["change_24h"] > 0 else "하락"
            lines.append(f"BTC ${btc['price_usd']:,.0f}({btc['change_24h']:+.2f}%), ETH ${eth.get('price_usd', 0):,.0f}({eth.get('change_24h', 0):+.2f}%).")

    # 환율 요약
    currencies = data.get("currencies", {})
    if currencies:
        usdkrw = currencies.get("USD/KRW", {})
        if usdkrw.get("price"):
            lines.append(f"원/달러 {usdkrw['price']:,.0f}원({usdkrw.get('change', 0):+.2f}%).")

    # 원자재 요약
    commodities = data.get("commodities", {})
    if commodities:
        gold = commodities.get("금", {})
        oil = commodities.get("WTI 원유", {})
        if gold.get("price") and oil.get("price"):
            lines.append(f"금 ${gold['price']:,.0f}, WTI ${oil['price']:.2f}.")

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
    result = notifier.send_sync(market_data, post_url)
    if result:
        print("   - 알림 발송 완료")
    else:
        print("   - 알림 발송 실패 (계속 진행)")

    print(f"[{datetime.now()}] 시황 브리핑 생성 완료!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
