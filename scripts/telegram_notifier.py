"""텔레그램 알림 모듈"""
import asyncio
from datetime import datetime
from telegram import Bot
from config import config


class TelegramNotifier:
    """텔레그램 봇 알림 클라이언트"""

    def __init__(self):
        self.bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
        self.chat_id = config.TELEGRAM_CHAT_ID

    def _format_change(self, val):
        """변동률 포맷팅"""
        if val is None:
            return "-"
        return f"+{val:.2f}%" if val >= 0 else f"{val:.2f}%"

    def _build_detailed_message(self, data: dict, post_url: str) -> str:
        """상세 시황 메시지 생성"""
        now = datetime.now()
        weekdays = ['월', '화', '수', '목', '금', '토', '일']

        lines = [
            f"📊 *찬희의 투자노트*",
            f"📅 {now.strftime('%Y.%m.%d')} ({weekdays[now.weekday()]})",
            ""
        ]

        # VIX
        vix = data.get("market_indicators", {}).get("VIX (공포지수)", {})
        if vix.get("price"):
            emoji = "🟢" if vix["price"] < 20 else "🟡" if vix["price"] < 30 else "🔴"
            lines.append(f"{emoji} *VIX* {vix['price']:.1f} ({self._format_change(vix.get('change'))})")
            lines.append("")

        # 미국 증시
        lines.append("🇺🇸 *미국 증시*")
        us = data.get("us_indices", {})
        for name, info in us.items():
            if info.get("price"):
                lines.append(f"• {name}: {info['price']:,.0f} ({self._format_change(info.get('change'))})")
        lines.append("")

        # 빅테크
        lines.append("💻 *빅테크 (MAG7)*")
        mag7 = data.get("mag7", {})
        mag7_items = [(k, v) for k, v in mag7.items() if v.get('change') is not None]
        mag7_sorted = sorted(mag7_items, key=lambda x: x[1].get('change', 0), reverse=True)
        for name, info in mag7_sorted[:3]:  # Top 3
            lines.append(f"• {name}: ${info['price']:,.2f} ({self._format_change(info.get('change'))})")
        for name, info in mag7_sorted[-2:]:  # Bottom 2
            lines.append(f"• {name}: ${info['price']:,.2f} ({self._format_change(info.get('change'))})")
        lines.append("")

        # 암호화폐
        lines.append("🪙 *암호화폐*")
        crypto = data.get("crypto", {})
        for name in ["BTC", "ETH", "SOL", "XRP"]:
            info = crypto.get(name, {})
            if info.get("price_usd"):
                lines.append(f"• {name}: ${info['price_usd']:,.0f} ({self._format_change(info.get('change_24h'))})")
        lines.append("")

        # 환율
        lines.append("💱 *환율*")
        currencies = data.get("currencies", {})
        usdkrw = currencies.get("USD/KRW", {})
        if usdkrw.get("price"):
            lines.append(f"• 원/달러: {usdkrw['price']:,.0f}원 ({self._format_change(usdkrw.get('change'))})")
        lines.append("")

        # 원자재
        lines.append("🛢️ *원자재*")
        commodities = data.get("commodities", {})
        for name in ["WTI 원유", "금"]:
            info = commodities.get(name, {})
            if info.get("price"):
                lines.append(f"• {name}: ${info['price']:,.2f} ({self._format_change(info.get('change'))})")
        lines.append("")

        # 링크
        lines.append(f"👉 [전체 보기]({post_url})")

        return "\n".join(lines)

    async def send_briefing_alert(self, data: dict, post_url: str) -> bool:
        """시황 브리핑 알림 발송"""
        message = self._build_detailed_message(data, post_url)
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            return True
        except Exception as e:
            print(f"Telegram error: {e}")
            return False

    def send_sync(self, data: dict, post_url: str) -> bool:
        """동기 방식 발송 (GitHub Actions용)"""
        return asyncio.run(self.send_briefing_alert(data, post_url))


if __name__ == "__main__":
    # 테스트용
    notifier = TelegramNotifier()
    print(f"Bot configured with chat_id: {config.TELEGRAM_CHAT_ID}")
