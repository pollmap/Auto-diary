"""설정 관리 모듈"""
import os
from dataclasses import dataclass, field
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """애플리케이션 설정"""

    # API Keys
    GEMINI_API_KEY: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    TELEGRAM_BOT_TOKEN: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))
    TELEGRAM_CHAT_ID: str = field(default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID", ""))

    # 한국 금융 API (Phase 2용)
    OPENDART_API_KEY: str = field(default_factory=lambda: os.getenv("OPENDART_API_KEY", ""))
    KOREA_INVESTMENT_APP_KEY: str = field(default_factory=lambda: os.getenv("KOREA_INVESTMENT_APP_KEY", ""))
    KOREA_INVESTMENT_APP_SECRET: str = field(default_factory=lambda: os.getenv("KOREA_INVESTMENT_APP_SECRET", ""))
    ECOS_API_KEY: str = field(default_factory=lambda: os.getenv("ECOS_API_KEY", ""))
    FRED_API_KEY: str = field(default_factory=lambda: os.getenv("FRED_API_KEY", ""))

    # 데이터 수집 대상
    CRYPTO_IDS: List[str] = field(default_factory=list)
    US_INDICES: Dict[str, str] = field(default_factory=dict)
    US_SECTOR_ETFS: Dict[str, str] = field(default_factory=dict)
    GLOBAL_INDICES: Dict[str, str] = field(default_factory=dict)
    CURRENCIES: Dict[str, str] = field(default_factory=dict)
    COMMODITIES: Dict[str, str] = field(default_factory=dict)
    AGRICULTURE: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self.CRYPTO_IDS = ["bitcoin", "ethereum", "ripple", "dogecoin", "chainlink"]

        self.US_INDICES = {
            "S&P 500": "^GSPC",
            "NASDAQ": "^IXIC",
            "DOW": "^DJI"
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


config = Config()
