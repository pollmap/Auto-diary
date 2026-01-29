"""설정 관리 모듈"""
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class ConfigError(Exception):
    """설정 관련 오류"""
    pass


@dataclass
class Config:
    """애플리케이션 설정"""

    # === API Keys ===
    GEMINI_API_KEY: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    TELEGRAM_BOT_TOKEN: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))
    TELEGRAM_CHAT_ID: str = field(default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID", ""))
    FRED_API_KEY: str = field(default_factory=lambda: os.getenv("FRED_API_KEY", ""))

    # 한국 금융 API (Phase 2용)
    OPENDART_API_KEY: str = field(default_factory=lambda: os.getenv("OPENDART_API_KEY", ""))
    KOREA_INVESTMENT_APP_KEY: str = field(default_factory=lambda: os.getenv("KOREA_INVESTMENT_APP_KEY", ""))
    KOREA_INVESTMENT_APP_SECRET: str = field(default_factory=lambda: os.getenv("KOREA_INVESTMENT_APP_SECRET", ""))
    ECOS_API_KEY: str = field(default_factory=lambda: os.getenv("ECOS_API_KEY", ""))

    # === 네트워크 설정 ===
    REQUEST_TIMEOUT: int = 10  # API 요청 타임아웃 (초)
    MAX_RETRIES: int = 3  # 최대 재시도 횟수
    RETRY_DELAY: float = 1.0  # 재시도 기본 대기 시간 (초)
    RETRY_BACKOFF: float = 2.0  # 재시도 지수 백오프 배수
    RATE_LIMIT_DELAY: float = 0.5  # API 호출 간 대기 시간 (초)

    # === 텔레그램 설정 ===
    TELEGRAM_MESSAGE_DELAY: float = 0.5  # 메시지 간 대기 시간 (초)
    TELEGRAM_MAX_MESSAGE_LENGTH: int = 4000  # 메시지 최대 길이

    # === 사이트 설정 ===
    SITE_URL: str = field(default_factory=lambda: os.getenv("SITE_URL", "https://pollmap.github.io/Auto-diary"))
    SITE_AUTHOR: str = field(default_factory=lambda: os.getenv("SITE_AUTHOR", "이찬희"))

    # === 데이터 수집 대상 ===
    CRYPTO_IDS: List[str] = field(default_factory=list)
    US_INDICES: Dict[str, str] = field(default_factory=dict)
    US_SECTOR_ETFS: Dict[str, str] = field(default_factory=dict)
    GLOBAL_INDICES: Dict[str, str] = field(default_factory=dict)
    CURRENCIES: Dict[str, str] = field(default_factory=dict)
    COMMODITIES: Dict[str, str] = field(default_factory=dict)
    AGRICULTURE: Dict[str, str] = field(default_factory=dict)
    MARKET_INDICATORS: Dict[str, str] = field(default_factory=dict)
    BONDS: Dict[str, str] = field(default_factory=dict)
    MAG7_STOCKS: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """데이터 수집 대상 초기화"""
        self.CRYPTO_IDS = ["bitcoin", "ethereum", "ripple", "solana", "cardano", "dogecoin", "chainlink"]

        self.US_INDICES = {
            "S&P 500": "^GSPC",
            "NASDAQ": "^IXIC",
            "다우존스": "^DJI",
            "러셀 2000": "^RUT"
        }

        self.MARKET_INDICATORS = {
            "VIX (공포지수)": "^VIX"
        }

        self.BONDS = {
            "미국 10년물": "^TNX",
            "미국 2년물": "^IRX"
        }

        self.MAG7_STOCKS = {
            "애플": "AAPL",
            "마이크로소프트": "MSFT",
            "엔비디아": "NVDA",
            "아마존": "AMZN",
            "알파벳": "GOOGL",
            "메타": "META",
            "테슬라": "TSLA"
        }

        self.US_SECTOR_ETFS = {
            "기술 (XLK)": "XLK",
            "금융 (XLF)": "XLF",
            "에너지 (XLE)": "XLE",
            "헬스케어 (XLV)": "XLV",
            "경기소비재 (XLY)": "XLY",
            "필수소비재 (XLP)": "XLP",
            "산업재 (XLI)": "XLI",
            "소재 (XLB)": "XLB",
            "유틸리티 (XLU)": "XLU",
            "부동산 (XLRE)": "XLRE",
            "커뮤니케이션 (XLC)": "XLC"
        }

        self.GLOBAL_INDICES = {
            "KOSPI": "^KS11",
            "KOSDAQ": "^KQ11",
            "니케이225": "^N225",
            "항셍": "^HSI",
            "상해종합": "000001.SS",
            "DAX": "^GDAXI",
            "FTSE 100": "^FTSE"
        }

        self.CURRENCIES = {
            "USD/KRW": "KRW=X",
            "USD/JPY": "JPY=X",
            "EUR/USD": "EURUSD=X",
            "USD/CNY": "CNY=X"
        }

        self.COMMODITIES = {
            "WTI 원유": "CL=F",
            "금": "GC=F",
            "은": "SI=F",
            "구리": "HG=F",
            "천연가스": "NG=F"
        }

        self.AGRICULTURE = {
            "옥수수": "ZC=F",
            "대두": "ZS=F",
            "소맥": "ZW=F"
        }

    def validate_required_keys(self) -> Dict[str, bool]:
        """필수 API 키 검증

        Returns:
            각 API 키의 유효성 여부를 담은 딕셔너리
        """
        return {
            "GEMINI_API_KEY": bool(self.GEMINI_API_KEY and len(self.GEMINI_API_KEY) > 10),
            "TELEGRAM_BOT_TOKEN": bool(self.TELEGRAM_BOT_TOKEN and ":" in self.TELEGRAM_BOT_TOKEN),
            "TELEGRAM_CHAT_ID": bool(self.TELEGRAM_CHAT_ID and self.TELEGRAM_CHAT_ID.lstrip("-").isdigit()),
            "FRED_API_KEY": bool(self.FRED_API_KEY and len(self.FRED_API_KEY) >= 32),
        }

    def validate_telegram(self) -> bool:
        """텔레그램 설정 검증"""
        keys = self.validate_required_keys()
        return keys["TELEGRAM_BOT_TOKEN"] and keys["TELEGRAM_CHAT_ID"]

    def validate_fred(self) -> bool:
        """FRED API 설정 검증"""
        return self.validate_required_keys()["FRED_API_KEY"]

    def validate_gemini(self) -> bool:
        """Gemini API 설정 검증"""
        return self.validate_required_keys()["GEMINI_API_KEY"]

    def get_validation_summary(self) -> str:
        """API 키 검증 결과 요약 문자열 반환"""
        keys = self.validate_required_keys()
        lines = ["=== API 키 검증 결과 ==="]
        for name, valid in keys.items():
            status = "✅ 유효" if valid else "❌ 없음/무효"
            lines.append(f"  {name}: {status}")
        return "\n".join(lines)


config = Config()
