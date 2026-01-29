"""텔레그램 알림 모듈 - 전체 시황 브리핑"""
import asyncio
from datetime import datetime
from telegram import Bot
from config import config
from logger import logger, LogContext


class TelegramNotifier:
    """텔레그램 봇 알림 클라이언트"""

    def __init__(self):
        if not config.validate_telegram():
            logger.warning("텔레그램 설정이 유효하지 않습니다")
        self.bot = Bot(token=config.TELEGRAM_BOT_TOKEN) if config.TELEGRAM_BOT_TOKEN else None
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.max_message_length = config.TELEGRAM_MAX_MESSAGE_LENGTH
        self.message_delay = config.TELEGRAM_MESSAGE_DELAY

    def _format_change(self, val):
        """변동률 포맷팅"""
        if val is None:
            return "-"
        return f"+{val:.2f}%" if val >= 0 else f"{val:.2f}%"

    def _build_full_briefing(self, data: dict, post_url: str) -> list:
        """전체 시황 브리핑 메시지 생성 (여러 메시지로 분할)"""
        now = datetime.now()
        weekdays = ['월', '화', '수', '목', '금', '토', '일']

        messages = []

        # === 메시지 1: 헤더 + 시장심리 + 미국증시 ===
        msg1 = []
        msg1.append(f"📊 *찬희의 투자노트*")
        msg1.append(f"📅 {now.strftime('%Y년 %m월 %d일')} ({weekdays[now.weekday()]}) 오전 6시 기준")
        msg1.append("─" * 20)
        msg1.append("")

        # VIX & 시장 심리
        msg1.append("*📈 시장 심리 지표*")
        msg1.append("")

        vix = data.get("market_indicators", {}).get("VIX (공포지수)", {})
        if vix.get("price"):
            status = "안정" if vix["price"] < 20 else "주의" if vix["price"] < 30 else "공포"
            emoji = "🟢" if vix["price"] < 20 else "🟡" if vix["price"] < 30 else "🔴"
            msg1.append(f"{emoji} VIX: {vix['price']:.1f} ({self._format_change(vix.get('change'))}) - {status}")

        # Fear & Greed
        fear_greed = data.get("fear_greed", {})
        market_fg = fear_greed.get("market", {})
        if market_fg and market_fg.get("value") is not None:
            emoji = "🟢" if market_fg["value"] >= 55 else "🟡" if market_fg["value"] >= 45 else "🔴"
            msg1.append(f"{emoji} 시장심리: {market_fg['value']}/100 ({market_fg.get('classification', '-')})")

        crypto_fg = fear_greed.get("crypto", {})
        if crypto_fg and crypto_fg.get("value") is not None:
            emoji = "🟢" if crypto_fg["value"] >= 55 else "🟡" if crypto_fg["value"] >= 45 else "🔴"
            msg1.append(f"{emoji} 크립토 F&G: {crypto_fg['value']}/100 ({crypto_fg.get('classification', '-')})")

        # 채권 금리
        bonds = data.get("bonds", {})
        if bonds:
            msg1.append("")
            msg1.append("*💵 채권 금리*")
            for name, info in bonds.items():
                if info.get("price"):
                    msg1.append(f"• {name}: {info['price']:.2f}% ({self._format_change(info.get('change'))})")

        msg1.append("")
        msg1.append("─" * 20)
        msg1.append("")

        # 미국 증시
        msg1.append("*🇺🇸 미국 증시*")
        msg1.append("")
        us = data.get("us_indices", {})
        for name, info in us.items():
            if info.get("price"):
                change_val = info.get('change', 0) or 0
                emoji = "🔺" if change_val > 0 else "🔻" if change_val < 0 else "▪️"
                msg1.append(f"{emoji} {name}: {info['price']:,.2f} ({self._format_change(info.get('change'))})")

        messages.append("\n".join(msg1))

        # === 메시지 2: 빅테크 + 섹터 ===
        msg2 = []
        msg2.append("*💻 빅테크 (MAG7)*")
        msg2.append("")
        mag7 = data.get("mag7", {})
        mag7_items = [(k, v) for k, v in mag7.items() if v.get('price') is not None]
        # 정렬 시 None 처리 개선
        mag7_sorted = sorted(
            mag7_items,
            key=lambda x: x[1].get('change') if x[1].get('change') is not None else 0,
            reverse=True
        )
        for name, info in mag7_sorted:
            change_val = info.get('change', 0) or 0
            emoji = "🔺" if change_val > 0 else "🔻" if change_val < 0 else "▪️"
            msg2.append(f"{emoji} {name}: ${info['price']:,.2f} ({self._format_change(info.get('change'))})")

        msg2.append("")
        msg2.append("─" * 20)
        msg2.append("")

        # 섹터 ETF
        msg2.append("*📊 섹터 ETF*")
        msg2.append("")
        sectors = data.get("us_sectors", {})
        sector_items = [(k, v) for k, v in sectors.items() if v.get('price') is not None]
        sector_sorted = sorted(
            sector_items,
            key=lambda x: x[1].get('change') if x[1].get('change') is not None else 0,
            reverse=True
        )
        for name, info in sector_sorted:
            change_val = info.get('change', 0) or 0
            emoji = "🔺" if change_val > 0 else "🔻" if change_val < 0 else "▪️"
            msg2.append(f"{emoji} {name}: ${info['price']:,.2f} ({self._format_change(info.get('change'))})")

        messages.append("\n".join(msg2))

        # === 메시지 3: 글로벌 + 암호화폐 ===
        msg3 = []
        msg3.append("*🌏 글로벌 증시*")
        msg3.append("")

        # 아시아
        msg3.append("_아시아_")
        global_idx = data.get("global_indices", {})
        asia_keys = ["KOSPI", "KOSDAQ", "니케이225", "항셍", "상해종합"]
        for name in asia_keys:
            info = global_idx.get(name, {})
            if info.get("price"):
                change_val = info.get('change', 0) or 0
                emoji = "🔺" if change_val > 0 else "🔻" if change_val < 0 else "▪️"
                msg3.append(f"{emoji} {name}: {info['price']:,.2f} ({self._format_change(info.get('change'))})")

        # 유럽
        msg3.append("")
        msg3.append("_유럽_")
        europe_keys = ["DAX", "FTSE 100"]
        for name in europe_keys:
            info = global_idx.get(name, {})
            if info.get("price"):
                change_val = info.get('change', 0) or 0
                emoji = "🔺" if change_val > 0 else "🔻" if change_val < 0 else "▪️"
                msg3.append(f"{emoji} {name}: {info['price']:,.2f} ({self._format_change(info.get('change'))})")

        msg3.append("")
        msg3.append("─" * 20)
        msg3.append("")

        # 암호화폐
        msg3.append("*🪙 암호화폐*")
        msg3.append("")
        crypto = data.get("crypto", {})
        for name, info in crypto.items():
            if info.get("price_usd"):
                change_val = info.get('change_24h', 0) or 0
                emoji = "🔺" if change_val > 0 else "🔻" if change_val < 0 else "▪️"
                krw = f"₩{info['price_krw']:,.0f}" if info.get('price_krw') else ""
                msg3.append(f"{emoji} {name}: ${info['price_usd']:,.2f} {krw} ({self._format_change(info.get('change_24h'))})")

        messages.append("\n".join(msg3))

        # === 메시지 4: 환율 + 원자재 + 경제지표 ===
        msg4 = []
        msg4.append("*💱 환율*")
        msg4.append("")
        currencies = data.get("currencies", {})
        for name, info in currencies.items():
            if info.get("price"):
                change_val = info.get('change', 0) or 0
                emoji = "🔺" if change_val > 0 else "🔻" if change_val < 0 else "▪️"
                msg4.append(f"{emoji} {name}: {info['price']:,.2f} ({self._format_change(info.get('change'))})")

        msg4.append("")
        msg4.append("─" * 20)
        msg4.append("")

        # 원자재
        msg4.append("*🛢️ 원자재*")
        msg4.append("")
        commodities = data.get("commodities", {})
        for name, info in commodities.items():
            if info.get("price"):
                change_val = info.get('change', 0) or 0
                emoji = "🔺" if change_val > 0 else "🔻" if change_val < 0 else "▪️"
                msg4.append(f"{emoji} {name}: ${info['price']:,.2f} ({self._format_change(info.get('change'))})")

        # 농산물
        agriculture = data.get("agriculture", {})
        if agriculture:
            msg4.append("")
            msg4.append("_농산물_")
            for name, info in agriculture.items():
                if info.get("price"):
                    change_val = info.get('change', 0) or 0
                    emoji = "🔺" if change_val > 0 else "🔻" if change_val < 0 else "▪️"
                    msg4.append(f"{emoji} {name}: ${info['price']:,.2f} ({self._format_change(info.get('change'))})")

        messages.append("\n".join(msg4))

        # === 메시지 5: 경제지표 + 캘린더 + 링크 ===
        msg5 = []
        msg5.append("*📈 주요 경제지표*")
        msg5.append("")

        econ = data.get("economic_indicators", {})

        # 월간 지표 (CPI, 실업률 등)
        monthly = econ.get("monthly", {})
        if monthly:
            for name, info in monthly.items():
                if info and info.get("value") is not None:
                    val = info["value"]
                    if info.get("unit") == "% YoY" or "YoY" in name:
                        msg5.append(f"• {name}: {val:+.2f}% ({info.get('date', '-')})")
                    elif "실업률" in name or "금리" in name:
                        msg5.append(f"• {name}: {val:.2f}% ({info.get('date', '-')})")
                    else:
                        msg5.append(f"• {name}: {val:.2f} ({info.get('date', '-')})")

        msg5.append("")
        msg5.append("─" * 20)
        msg5.append("")

        # 경제 캘린더
        msg5.append("*📅 경제 캘린더*")
        msg5.append("")

        calendar = data.get("economic_calendar", {})
        fed_events = calendar.get("upcoming_fed", [])
        if fed_events:
            msg5.append("_연준 일정_")
            for event in fed_events[:2]:
                msg5.append(f"🔴 {event['display']} {event['event']} ({event['date']})")
            msg5.append("")

        this_week = calendar.get("this_week", {})
        week_events = this_week.get("economic", []) + this_week.get("weekly", [])
        if week_events:
            msg5.append("_이번 주 주요 발표_")
            for event in week_events[:3]:
                importance = event.get("importance", "medium")
                emoji = "🔴" if importance == "high" else "🟡"
                msg5.append(f"{emoji} {event['event']}")

        msg5.append("")
        msg5.append("─" * 20)
        msg5.append("")
        msg5.append(f"👉 [웹에서 전체 보기]({post_url})")
        msg5.append("")
        msg5.append(f"_{now.strftime('%Y.%m.%d')} | 찬희의 투자노트_")

        messages.append("\n".join(msg5))

        return messages

    async def send_full_briefing(self, data: dict, post_url: str) -> bool:
        """전체 시황 브리핑 발송 (여러 메시지)"""
        if not self.bot:
            logger.error("텔레그램 봇이 초기화되지 않았습니다")
            return False

        messages = self._build_full_briefing(data, post_url)

        try:
            with LogContext("텔레그램 메시지 발송"):
                for i, msg in enumerate(messages):
                    await self.bot.send_message(
                        chat_id=self.chat_id,
                        text=msg,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    logger.info(f"메시지 {i + 1}/{len(messages)} 발송 완료")
                    # 메시지 사이 약간의 딜레이
                    if i < len(messages) - 1:
                        await asyncio.sleep(self.message_delay)
            return True
        except Exception as e:
            logger.error(f"텔레그램 발송 오류: {e}")
            return False

    def send_sync(self, data: dict, post_url: str) -> bool:
        """동기 방식 발송 (GitHub Actions용)"""
        if not config.validate_telegram():
            logger.warning("텔레그램 설정이 없어 알림을 건너뜁니다")
            return False
        return asyncio.run(self.send_full_briefing(data, post_url))


if __name__ == "__main__":
    # 테스트용
    notifier = TelegramNotifier()
    logger.info(f"Bot configured with chat_id: {config.TELEGRAM_CHAT_ID}")
