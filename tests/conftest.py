"""pytest 설정 및 공통 fixtures"""
import sys
from pathlib import Path

import pytest

# scripts 디렉토리를 path에 추가
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))


@pytest.fixture
def sample_market_data():
    """테스트용 샘플 시장 데이터"""
    return {
        "timestamp": "2026-01-29T06:00:00",
        "crypto": {
            "BTC": {"price_usd": 95000, "price_krw": 139000000, "change_24h": 2.5},
            "ETH": {"price_usd": 3200, "price_krw": 4680000, "change_24h": -1.2},
        },
        "us_indices": {
            "S&P 500": {"price": 5850.25, "change": 0.35},
            "NASDAQ": {"price": 18500.50, "change": -0.15},
            "다우존스": {"price": 42500.75, "change": 0.22},
            "러셀 2000": {"price": 2200.30, "change": 0.45},
        },
        "market_indicators": {
            "VIX (공포지수)": {"price": 18.5, "change": -0.8},
        },
        "bonds": {
            "미국 10년물": {"price": 4.25, "change": 0.02},
            "미국 2년물": {"price": 4.05, "change": -0.01},
        },
        "mag7": {
            "애플": {"price": 195.50, "change": 1.25},
            "마이크로소프트": {"price": 420.30, "change": -0.50},
            "엔비디아": {"price": 850.75, "change": 3.20},
            "아마존": {"price": 185.20, "change": 0.80},
            "알파벳": {"price": 155.40, "change": -0.30},
            "메타": {"price": 520.60, "change": 2.10},
            "테슬라": {"price": 280.90, "change": -1.80},
        },
        "us_sectors": {
            "기술 (XLK)": {"price": 210.50, "change": 0.75},
            "금융 (XLF)": {"price": 42.30, "change": 0.25},
        },
        "global_indices": {
            "KOSPI": {"price": 2550.30, "change": 0.85},
            "KOSDAQ": {"price": 750.20, "change": -0.45},
            "니케이225": {"price": 38500.50, "change": 1.20},
            "항셍": {"price": 16800.75, "change": -0.65},
            "상해종합": {"price": 3050.40, "change": 0.15},
            "DAX": {"price": 18200.60, "change": 0.55},
            "FTSE 100": {"price": 7650.30, "change": 0.35},
        },
        "currencies": {
            "USD/KRW": {"price": 1430.50, "change": 0.12},
            "USD/JPY": {"price": 148.25, "change": -0.08},
            "EUR/USD": {"price": 1.0850, "change": 0.05},
            "USD/CNY": {"price": 7.25, "change": 0.03},
        },
        "commodities": {
            "WTI 원유": {"price": 78.50, "change": 1.25},
            "금": {"price": 2050.30, "change": 0.45},
            "은": {"price": 24.50, "change": 0.85},
            "구리": {"price": 4.25, "change": -0.35},
            "천연가스": {"price": 2.85, "change": -2.50},
        },
        "agriculture": {
            "옥수수": {"price": 485.50, "change": 0.65},
            "대두": {"price": 1250.30, "change": -0.25},
            "소맥": {"price": 620.40, "change": 0.15},
        },
        "economic_indicators": {
            "daily": {},
            "weekly": {},
            "monthly": {
                "CPI (YoY)": {"value": 2.9, "date": "2026-01", "unit": "% YoY"},
                "실업률": {"value": 4.1, "date": "2026-01", "unit": "%"},
            },
        },
        "fear_greed": {
            "market": {"value": 55, "classification": "탐욕"},
            "crypto": {"value": 62, "classification": "탐욕", "change": 3},
        },
        "economic_calendar": {
            "upcoming_fed": [
                {"date": "2026-01-29", "event": "FOMC 회의", "display": "D-0", "days_until": 0},
            ],
            "this_week": {
                "economic": [{"event": "GDP 발표", "importance": "high"}],
                "weekly": [],
            },
        },
    }


@pytest.fixture
def sample_all_up_data(sample_market_data):
    """모든 지수가 상승한 데이터"""
    data = sample_market_data.copy()
    data["us_indices"] = {
        "S&P 500": {"price": 5850.25, "change": 0.35},
        "NASDAQ": {"price": 18500.50, "change": 0.25},
        "다우존스": {"price": 42500.75, "change": 0.22},
        "러셀 2000": {"price": 2200.30, "change": 0.45},
    }
    return data


@pytest.fixture
def sample_all_down_data(sample_market_data):
    """모든 지수가 하락한 데이터"""
    data = sample_market_data.copy()
    data["us_indices"] = {
        "S&P 500": {"price": 5850.25, "change": -0.35},
        "NASDAQ": {"price": 18500.50, "change": -0.25},
        "다우존스": {"price": 42500.75, "change": -0.22},
        "러셀 2000": {"price": 2200.30, "change": -0.45},
    }
    return data


@pytest.fixture
def sample_mixed_data(sample_market_data):
    """혼조세 데이터"""
    data = sample_market_data.copy()
    data["us_indices"] = {
        "S&P 500": {"price": 5850.25, "change": -0.01},
        "NASDAQ": {"price": 18500.50, "change": 0.17},
        "다우존스": {"price": 42500.75, "change": -0.05},
        "러셀 2000": {"price": 2200.30, "change": 0.10},
    }
    return data
