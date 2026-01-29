"""메인 실행 스크립트"""
import sys
from datetime import datetime
from pathlib import Path

from config import config
from logger import logger, LogContext
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
        sp_chg = sp500.get("change")
        nas_chg = nasdaq.get("change")
        dow_chg = dow.get("change")

        if sp_chg is not None:
            # 상승/하락/혼조 판단: 모든 지수 고려
            changes = [c for c in [sp_chg, nas_chg, dow_chg] if c is not None]
            up_count = sum(1 for c in changes if c > 0)
            down_count = sum(1 for c in changes if c < 0)

            if up_count == len(changes):
                direction = "상승"
            elif down_count == len(changes):
                direction = "하락"
            else:
                direction = "혼조"

            lines.append(f"미국 증시는 S&P 500 {sp_chg:+.2f}%, 나스닥 {nas_chg or 0:+.2f}%, 다우 {dow_chg or 0:+.2f}%로 {direction} 마감.")

    # 빅테크 요약
    mag7 = data.get("mag7", {})
    if mag7:
        valid_items = [(k, v) for k, v in mag7.items() if v.get('change') is not None]
        if valid_items:
            best = max(valid_items, key=lambda x: x[1]['change'])
            worst = min(valid_items, key=lambda x: x[1]['change'])
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

    # Fear & Greed 요약
    fear_greed = data.get("fear_greed", {})
    crypto_fg = fear_greed.get("crypto", {})
    if crypto_fg and crypto_fg.get("value"):
        lines.append(f"암호화폐 Fear & Greed {crypto_fg['value']}({crypto_fg.get('classification', '-')}).")

    # FOMC 일정 (가까우면 알림)
    calendar = data.get("economic_calendar", {})
    fed_events = calendar.get("upcoming_fed", [])
    if fed_events:
        next_fomc = fed_events[0]
        if next_fomc.get("days_until", 999) <= 7:
            lines.append(f"📅 FOMC {next_fomc['display']}.")

    return " ".join(lines) if lines else "오늘의 시황 데이터를 확인하세요."


def main():
    """시황 브리핑 자동 생성 메인 함수"""
    with LogContext("시황 브리핑 생성"):
        # API 키 검증 결과 출력
        logger.info(config.get_validation_summary())

        # 1. 데이터 수집
        logger.info("1. 데이터 수집 시작...")
        fetcher = DataFetcher()
        market_data = fetcher.fetch_all()
        logger.info(f"   데이터 수집 완료: {len(market_data)} 카테고리")

        # 2. 간단 요약 생성 (AI 없이)
        logger.info("2. 요약 생성 중...")
        summary = generate_simple_summary(market_data)
        logger.info(f"   요약 생성 완료: {len(summary)}자")

        # 3. 포스트 생성
        logger.info("3. 마크다운 포스트 생성 중...")
        generator = PostGenerator()
        post_path = generator.generate_briefing_post(market_data, summary)
        logger.info(f"   포스트 생성: {post_path}")

        # 4. 텔레그램 알림
        logger.info("4. 텔레그램 알림 발송 중...")
        date_str = datetime.now().strftime("%Y/%m/%d")
        post_url = f"{config.SITE_URL}/market/briefing/{date_str}/daily-market-briefing"

        notifier = TelegramNotifier()
        result = notifier.send_sync(market_data, post_url)
        if result:
            logger.info("   알림 발송 완료")
        else:
            logger.warning("   알림 발송 실패 또는 건너뜀")

    logger.info("시황 브리핑 생성 완료!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
