"""config.py 테스트"""
import pytest
from config import Config, config


class TestConfig:
    """Config 클래스 테스트"""

    def test_config_initialization(self):
        """Config 초기화 테스트"""
        cfg = Config()
        assert cfg.CRYPTO_IDS is not None
        assert len(cfg.CRYPTO_IDS) == 7
        assert "bitcoin" in cfg.CRYPTO_IDS

    def test_us_indices_initialized(self):
        """미국 지수 설정 테스트"""
        assert len(config.US_INDICES) == 4
        assert "S&P 500" in config.US_INDICES
        assert config.US_INDICES["S&P 500"] == "^GSPC"

    def test_mag7_stocks_initialized(self):
        """MAG7 주식 설정 테스트"""
        assert len(config.MAG7_STOCKS) == 7
        assert "애플" in config.MAG7_STOCKS
        assert config.MAG7_STOCKS["애플"] == "AAPL"

    def test_network_settings(self):
        """네트워크 설정 기본값 테스트"""
        assert config.REQUEST_TIMEOUT == 10
        assert config.MAX_RETRIES == 3
        assert config.RETRY_DELAY == 1.0
        assert config.RETRY_BACKOFF == 2.0

    def test_telegram_settings(self):
        """텔레그램 설정 기본값 테스트"""
        assert config.TELEGRAM_MESSAGE_DELAY == 0.5
        assert config.TELEGRAM_MAX_MESSAGE_LENGTH == 4000

    def test_validate_required_keys_format(self):
        """API 키 검증 메서드 형식 테스트"""
        result = config.validate_required_keys()
        assert isinstance(result, dict)
        assert "GEMINI_API_KEY" in result
        assert "TELEGRAM_BOT_TOKEN" in result
        assert "TELEGRAM_CHAT_ID" in result
        assert "FRED_API_KEY" in result

    def test_validate_telegram_without_keys(self):
        """텔레그램 키 없을 때 검증 테스트"""
        cfg = Config()
        cfg.TELEGRAM_BOT_TOKEN = ""
        cfg.TELEGRAM_CHAT_ID = ""
        assert cfg.validate_telegram() == False

    def test_validate_telegram_with_valid_keys(self):
        """텔레그램 키 있을 때 검증 테스트"""
        cfg = Config()
        cfg.TELEGRAM_BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
        cfg.TELEGRAM_CHAT_ID = "-1001234567890"
        assert cfg.validate_telegram() == True

    def test_get_validation_summary(self):
        """검증 요약 메서드 테스트"""
        summary = config.get_validation_summary()
        assert "=== API 키 검증 결과 ===" in summary
        assert "GEMINI_API_KEY" in summary

    def test_commodities_config(self):
        """원자재 설정 테스트"""
        assert len(config.COMMODITIES) == 5
        assert "WTI 원유" in config.COMMODITIES
        assert config.COMMODITIES["금"] == "GC=F"

    def test_currencies_config(self):
        """환율 설정 테스트"""
        assert len(config.CURRENCIES) == 4
        assert "USD/KRW" in config.CURRENCIES
