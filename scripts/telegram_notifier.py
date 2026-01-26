"""텔레그램 알림 모듈"""
import asyncio
from telegram import Bot
from config import config


class TelegramNotifier:
    """텔레그램 봇 알림 클라이언트"""

    def __init__(self):
        self.bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
        self.chat_id = config.TELEGRAM_CHAT_ID

    async def send_briefing_alert(self, summary: str, post_url: str) -> bool:
        """시황 브리핑 알림 발송"""
        message = f"""📊 *오늘의 시황 브리핑*

{summary}

👉 [전체 보기]({post_url})
"""
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

    def send_sync(self, summary: str, post_url: str) -> bool:
        """동기 방식 발송 (GitHub Actions용)"""
        return asyncio.run(self.send_briefing_alert(summary, post_url))


if __name__ == "__main__":
    # 테스트용
    notifier = TelegramNotifier()
    print(f"Bot configured with chat_id: {config.TELEGRAM_CHAT_ID}")
