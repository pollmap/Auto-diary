"""telegram_notifier.py 테스트"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from telegram_notifier import TelegramNotifier


class TestTelegramNotifier:
    """TelegramNotifier 클래스 테스트"""

    def test_format_change_positive(self):
        """양수 변동률 포맷팅"""
        with patch("telegram_notifier.config") as mock_config:
            mock_config.validate_telegram.return_value = False
            mock_config.TELEGRAM_BOT_TOKEN = ""
            mock_config.TELEGRAM_CHAT_ID = ""
            mock_config.TELEGRAM_MAX_MESSAGE_LENGTH = 4000
            mock_config.TELEGRAM_MESSAGE_DELAY = 0.5

            notifier = TelegramNotifier()
            assert notifier._format_change(2.5) == "+2.50%"

    def test_format_change_negative(self):
        """음수 변동률 포맷팅"""
        with patch("telegram_notifier.config") as mock_config:
            mock_config.validate_telegram.return_value = False
            mock_config.TELEGRAM_BOT_TOKEN = ""
            mock_config.TELEGRAM_CHAT_ID = ""
            mock_config.TELEGRAM_MAX_MESSAGE_LENGTH = 4000
            mock_config.TELEGRAM_MESSAGE_DELAY = 0.5

            notifier = TelegramNotifier()
            assert notifier._format_change(-1.5) == "-1.50%"

    def test_format_change_zero(self):
        """0 변동률 포맷팅"""
        with patch("telegram_notifier.config") as mock_config:
            mock_config.validate_telegram.return_value = False
            mock_config.TELEGRAM_BOT_TOKEN = ""
            mock_config.TELEGRAM_CHAT_ID = ""
            mock_config.TELEGRAM_MAX_MESSAGE_LENGTH = 4000
            mock_config.TELEGRAM_MESSAGE_DELAY = 0.5

            notifier = TelegramNotifier()
            assert notifier._format_change(0) == "+0.00%"

    def test_format_change_none(self):
        """None 변동률 포맷팅"""
        with patch("telegram_notifier.config") as mock_config:
            mock_config.validate_telegram.return_value = False
            mock_config.TELEGRAM_BOT_TOKEN = ""
            mock_config.TELEGRAM_CHAT_ID = ""
            mock_config.TELEGRAM_MAX_MESSAGE_LENGTH = 4000
            mock_config.TELEGRAM_MESSAGE_DELAY = 0.5

            notifier = TelegramNotifier()
            assert notifier._format_change(None) == "-"

    def test_build_full_briefing_returns_5_messages(self, sample_market_data):
        """브리핑이 5개 메시지로 분할되는지 테스트"""
        with patch("telegram_notifier.config") as mock_config:
            mock_config.validate_telegram.return_value = False
            mock_config.TELEGRAM_BOT_TOKEN = ""
            mock_config.TELEGRAM_CHAT_ID = ""
            mock_config.TELEGRAM_MAX_MESSAGE_LENGTH = 4000
            mock_config.TELEGRAM_MESSAGE_DELAY = 0.5

            notifier = TelegramNotifier()
            messages = notifier._build_full_briefing(
                sample_market_data,
                "https://example.com/post"
            )

            assert len(messages) == 5

    def test_message_1_contains_market_indicators(self, sample_market_data):
        """메시지 1: 시장 지표 포함 확인"""
        with patch("telegram_notifier.config") as mock_config:
            mock_config.validate_telegram.return_value = False
            mock_config.TELEGRAM_BOT_TOKEN = ""
            mock_config.TELEGRAM_CHAT_ID = ""
            mock_config.TELEGRAM_MAX_MESSAGE_LENGTH = 4000
            mock_config.TELEGRAM_MESSAGE_DELAY = 0.5

            notifier = TelegramNotifier()
            messages = notifier._build_full_briefing(
                sample_market_data,
                "https://example.com/post"
            )

            msg1 = messages[0]
            assert "VIX" in msg1
            assert "미국 증시" in msg1
            assert "S&P 500" in msg1

    def test_message_2_contains_mag7(self, sample_market_data):
        """메시지 2: MAG7 포함 확인"""
        with patch("telegram_notifier.config") as mock_config:
            mock_config.validate_telegram.return_value = False
            mock_config.TELEGRAM_BOT_TOKEN = ""
            mock_config.TELEGRAM_CHAT_ID = ""
            mock_config.TELEGRAM_MAX_MESSAGE_LENGTH = 4000
            mock_config.TELEGRAM_MESSAGE_DELAY = 0.5

            notifier = TelegramNotifier()
            messages = notifier._build_full_briefing(
                sample_market_data,
                "https://example.com/post"
            )

            msg2 = messages[1]
            assert "빅테크" in msg2 or "MAG7" in msg2
            assert "섹터 ETF" in msg2

    def test_message_3_contains_global_and_crypto(self, sample_market_data):
        """메시지 3: 글로벌/암호화폐 포함 확인"""
        with patch("telegram_notifier.config") as mock_config:
            mock_config.validate_telegram.return_value = False
            mock_config.TELEGRAM_BOT_TOKEN = ""
            mock_config.TELEGRAM_CHAT_ID = ""
            mock_config.TELEGRAM_MAX_MESSAGE_LENGTH = 4000
            mock_config.TELEGRAM_MESSAGE_DELAY = 0.5

            notifier = TelegramNotifier()
            messages = notifier._build_full_briefing(
                sample_market_data,
                "https://example.com/post"
            )

            msg3 = messages[2]
            assert "글로벌" in msg3
            assert "암호화폐" in msg3
            assert "KOSPI" in msg3
            assert "BTC" in msg3

    def test_message_5_contains_link(self, sample_market_data):
        """메시지 5: 웹사이트 링크 포함 확인"""
        with patch("telegram_notifier.config") as mock_config:
            mock_config.validate_telegram.return_value = False
            mock_config.TELEGRAM_BOT_TOKEN = ""
            mock_config.TELEGRAM_CHAT_ID = ""
            mock_config.TELEGRAM_MAX_MESSAGE_LENGTH = 4000
            mock_config.TELEGRAM_MESSAGE_DELAY = 0.5

            notifier = TelegramNotifier()
            post_url = "https://example.com/post"
            messages = notifier._build_full_briefing(sample_market_data, post_url)

            msg5 = messages[4]
            assert post_url in msg5
            assert "웹에서 전체 보기" in msg5

    def test_send_sync_without_telegram_config(self, sample_market_data):
        """텔레그램 설정 없을 때 send_sync가 False 반환"""
        with patch("telegram_notifier.config") as mock_config:
            mock_config.validate_telegram.return_value = False
            mock_config.TELEGRAM_BOT_TOKEN = ""
            mock_config.TELEGRAM_CHAT_ID = ""
            mock_config.TELEGRAM_MAX_MESSAGE_LENGTH = 4000
            mock_config.TELEGRAM_MESSAGE_DELAY = 0.5

            notifier = TelegramNotifier()
            result = notifier.send_sync(sample_market_data, "https://example.com")
            assert result == False

    def test_mag7_sorted_by_change(self, sample_market_data):
        """MAG7가 변동률 순으로 정렬되는지 테스트"""
        with patch("telegram_notifier.config") as mock_config:
            mock_config.validate_telegram.return_value = False
            mock_config.TELEGRAM_BOT_TOKEN = ""
            mock_config.TELEGRAM_CHAT_ID = ""
            mock_config.TELEGRAM_MAX_MESSAGE_LENGTH = 4000
            mock_config.TELEGRAM_MESSAGE_DELAY = 0.5

            notifier = TelegramNotifier()
            messages = notifier._build_full_briefing(
                sample_market_data,
                "https://example.com/post"
            )

            msg2 = messages[1]
            # 엔비디아(+3.20%)가 테슬라(-1.80%)보다 먼저 나와야 함
            nvidia_pos = msg2.find("엔비디아")
            tesla_pos = msg2.find("테슬라")
            assert nvidia_pos < tesla_pos
