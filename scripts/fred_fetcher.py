"""FRED 경제지표 수집 모듈"""
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional
from config import config


class FREDFetcher:
    """FRED API를 통한 미국 경제지표 수집"""

    BASE_URL = "https://api.stlouisfed.org/fred"

    # 주요 경제지표 시리즈 ID
    INDICATORS = {
        # 물가/인플레이션
        "CPI (소비자물가지수)": "CPIAUCSL",
        "Core CPI (근원 CPI)": "CPILFESL",
        "PCE 물가지수": "PCEPI",
        "Core PCE": "PCEPILFE",

        # 고용
        "실업률": "UNRATE",
        "비농업 고용": "PAYEMS",
        "신규 실업수당 청구": "ICSA",
        "경제활동참가율": "CIVPART",

        # GDP/생산
        "GDP 성장률": "A191RL1Q225SBEA",
        "산업생산지수": "INDPRO",

        # 금리/통화
        "연방기금금리": "FEDFUNDS",
        "10년 국채금리": "DGS10",
        "2년 국채금리": "DGS2",
        "10Y-2Y 스프레드": "T10Y2Y",

        # 소비/심리
        "소매판매": "RSAFS",
        "미시간 소비자심리": "UMCSENT",

        # 주택
        "주택착공건수": "HOUST",
        "기존주택판매": "EXHOSLUSM495S",

        # 제조업
        "ISM 제조업 PMI": "MANEMP",
        "신규주문": "DGORDER",
    }

    # 자주 업데이트되는 주요 지표 (일간/주간)
    KEY_DAILY_INDICATORS = {
        "10년 국채금리": "DGS10",
        "2년 국채금리": "DGS2",
        "10Y-2Y 스프레드": "T10Y2Y",
        "연방기금금리 (실효)": "DFF",
    }

    KEY_WEEKLY_INDICATORS = {
        "신규 실업수당 청구": "ICSA",
        "연속 실업수당 청구": "CCSA",
    }

    def __init__(self):
        self.api_key = config.FRED_API_KEY

    def _fetch_series(self, series_id: str, limit: int = 2) -> Optional[Dict]:
        """FRED 시리즈 데이터 조회"""
        if not self.api_key:
            return None

        try:
            url = f"{self.BASE_URL}/series/observations"
            params = {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": limit
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            observations = data.get("observations", [])

            if observations:
                latest = observations[0]
                prev = observations[1] if len(observations) > 1 else None

                current_val = float(latest["value"]) if latest["value"] != "." else None
                prev_val = float(prev["value"]) if prev and prev["value"] != "." else None

                change = None
                if current_val is not None and prev_val is not None and prev_val != 0:
                    change = ((current_val - prev_val) / abs(prev_val)) * 100

                return {
                    "value": current_val,
                    "date": latest["date"],
                    "prev_value": prev_val,
                    "change": round(change, 2) if change is not None else None
                }

        except Exception as e:
            print(f"FRED fetch error for {series_id}: {e}")

        return None

    def fetch_daily_indicators(self) -> Dict:
        """일간 업데이트 지표 수집"""
        results = {}
        for name, series_id in self.KEY_DAILY_INDICATORS.items():
            data = self._fetch_series(series_id)
            if data:
                results[name] = data
        return results

    def fetch_weekly_indicators(self) -> Dict:
        """주간 업데이트 지표 수집"""
        results = {}
        for name, series_id in self.KEY_WEEKLY_INDICATORS.items():
            data = self._fetch_series(series_id)
            if data:
                results[name] = data
        return results

    def fetch_key_economic_data(self) -> Dict:
        """주요 경제지표 수집 (최신 발표 기준)"""
        key_series = {
            "실업률": "UNRATE",
            "CPI (YoY)": "CPIAUCSL",
            "Core CPI (YoY)": "CPILFESL",
            "연방기금금리": "FEDFUNDS",
            "GDP 성장률 (QoQ)": "A191RL1Q225SBEA",
            "ISM 제조업": "MANEMP",
            "소매판매": "RSAFS",
            "미시간 소비자심리": "UMCSENT",
        }

        results = {}
        for name, series_id in key_series.items():
            data = self._fetch_series(series_id, limit=3)
            if data:
                results[name] = data
        return results

    def fetch_all(self) -> Dict:
        """전체 경제지표 수집"""
        return {
            "daily": self.fetch_daily_indicators(),
            "weekly": self.fetch_weekly_indicators(),
            "monthly": self.fetch_key_economic_data()
        }


if __name__ == "__main__":
    fetcher = FREDFetcher()
    data = fetcher.fetch_all()
    print("Daily indicators:", data.get("daily"))
    print("Weekly indicators:", data.get("weekly"))
    print("Monthly indicators:", data.get("monthly"))
