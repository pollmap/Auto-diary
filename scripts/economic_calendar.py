"""경제 캘린더 수집 모듈"""
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json


class EconomicCalendarFetcher:
    """경제 이벤트 캘린더 수집"""

    # Trading Economics 캘린더 (비공식 - 무료)
    TRADINGECONOMICS_URL = "https://tradingeconomics.com/calendar"

    # Investing.com 캘린더는 Cloudflare 보호로 직접 스크래핑 어려움
    # 대안: FinnHub (무료 tier), Econdb 등

    # Finnhub 무료 API (일부 캘린더 제공)
    FINNHUB_URL = "https://finnhub.io/api/v1"

    # 한국 경제 캘린더 - 한국은행 API
    BOK_URL = "https://ecos.bok.or.kr/api"

    def __init__(self, finnhub_key: str = None, ecos_key: str = None):
        self.finnhub_key = finnhub_key
        self.ecos_key = ecos_key

    def get_upcoming_fed_events(self) -> List[Dict]:
        """주요 연준 이벤트 일정 (하드코딩 + 동적)"""
        # 2025년 FOMC 일정 (공개 정보)
        fomc_dates_2025 = [
            {"date": "2025-01-29", "event": "FOMC 금리결정", "importance": "high"},
            {"date": "2025-03-19", "event": "FOMC 금리결정", "importance": "high"},
            {"date": "2025-05-07", "event": "FOMC 금리결정", "importance": "high"},
            {"date": "2025-06-18", "event": "FOMC 금리결정", "importance": "high"},
            {"date": "2025-07-30", "event": "FOMC 금리결정", "importance": "high"},
            {"date": "2025-09-17", "event": "FOMC 금리결정", "importance": "high"},
            {"date": "2025-11-05", "event": "FOMC 금리결정", "importance": "high"},
            {"date": "2025-12-17", "event": "FOMC 금리결정", "importance": "high"},
        ]

        # 2026년 FOMC 일정
        fomc_dates_2026 = [
            {"date": "2026-01-28", "event": "FOMC 금리결정", "importance": "high"},
            {"date": "2026-03-18", "event": "FOMC 금리결정", "importance": "high"},
            {"date": "2026-05-06", "event": "FOMC 금리결정", "importance": "high"},
            {"date": "2026-06-17", "event": "FOMC 금리결정", "importance": "high"},
            {"date": "2026-07-29", "event": "FOMC 금리결정", "importance": "high"},
            {"date": "2026-09-16", "event": "FOMC 금리결정", "importance": "high"},
            {"date": "2026-11-04", "event": "FOMC 금리결정", "importance": "high"},
            {"date": "2026-12-16", "event": "FOMC 금리결정", "importance": "high"},
        ]

        all_fomc = fomc_dates_2025 + fomc_dates_2026

        # 오늘 기준 앞으로 30일 이내 이벤트만 필터링
        today = datetime.now().date()
        end_date = today + timedelta(days=30)

        upcoming = []
        for event in all_fomc:
            event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
            if today <= event_date <= end_date:
                days_until = (event_date - today).days
                upcoming.append({
                    **event,
                    "days_until": days_until,
                    "display": f"D-{days_until}" if days_until > 0 else "오늘"
                })

        return upcoming

    def get_key_us_economic_events(self) -> List[Dict]:
        """주요 미국 경제지표 발표 일정"""
        # 일반적인 발표 주기 기반 예상 일정
        today = datetime.now()
        current_month = today.month
        current_year = today.year

        # 매월 발표되는 주요 지표들의 일반적인 발표일
        monthly_events = [
            {"day_range": (1, 7), "event": "ISM 제조업 PMI", "importance": "high"},
            {"day_range": (3, 7), "event": "ISM 서비스업 PMI", "importance": "high"},
            {"day_range": (1, 7), "event": "비농업 고용 (NFP)", "importance": "high"},
            {"day_range": (10, 14), "event": "CPI (소비자물가지수)", "importance": "high"},
            {"day_range": (14, 18), "event": "소매판매", "importance": "medium"},
            {"day_range": (17, 22), "event": "주택착공건수", "importance": "medium"},
            {"day_range": (25, 30), "event": "PCE 물가지수", "importance": "high"},
            {"day_range": (25, 30), "event": "GDP (분기별)", "importance": "high"},
        ]

        events = []
        today_day = today.day

        for evt in monthly_events:
            # 이번 달 발표 예상
            if today_day <= evt["day_range"][1]:
                est_day = (evt["day_range"][0] + evt["day_range"][1]) // 2
                events.append({
                    "date": f"{current_year}-{current_month:02d}-{est_day:02d}",
                    "event": evt["event"],
                    "importance": evt["importance"],
                    "note": "예상 발표일"
                })

        return events

    def get_weekly_indicators_schedule(self) -> List[Dict]:
        """주간 경제지표 일정"""
        # 매주 목요일: 신규 실업수당 청구건수
        today = datetime.now()
        thursday = today + timedelta(days=(3 - today.weekday()) % 7)

        return [
            {
                "date": thursday.strftime("%Y-%m-%d"),
                "event": "신규 실업수당 청구건수",
                "importance": "medium",
                "frequency": "매주 목요일"
            }
        ]

    def get_earnings_highlights(self) -> List[Dict]:
        """주요 기업 실적 발표 일정 (수동 업데이트 필요)"""
        # 실적 시즌에 중요한 기업들 - 분기마다 업데이트 필요
        # Q4 2024 / Q1 2025 실적 시즌 예시
        earnings_calendar = [
            # 이 부분은 실제로는 API나 스크래핑으로 가져와야 함
            # 예시 데이터
        ]

        today = datetime.now().date()
        end_date = today + timedelta(days=14)

        upcoming = []
        for event in earnings_calendar:
            event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
            if today <= event_date <= end_date:
                upcoming.append(event)

        return upcoming

    def get_this_week_highlights(self) -> Dict:
        """이번 주 주요 이벤트 요약"""
        fed_events = self.get_upcoming_fed_events()
        us_events = self.get_key_us_economic_events()
        weekly = self.get_weekly_indicators_schedule()

        # 이번 주만 필터링 (7일 이내)
        today = datetime.now().date()
        week_end = today + timedelta(days=7)

        def filter_this_week(events):
            result = []
            for e in events:
                try:
                    event_date = datetime.strptime(e["date"], "%Y-%m-%d").date()
                    if today <= event_date <= week_end:
                        result.append(e)
                except:
                    pass
            return result

        return {
            "fed": filter_this_week(fed_events),
            "economic": filter_this_week(us_events),
            "weekly": filter_this_week(weekly),
            "earnings": self.get_earnings_highlights()
        }

    def fetch_all(self) -> Dict:
        """전체 캘린더 데이터 수집"""
        return {
            "upcoming_fed": self.get_upcoming_fed_events(),
            "us_economic": self.get_key_us_economic_events(),
            "weekly": self.get_weekly_indicators_schedule(),
            "this_week": self.get_this_week_highlights()
        }


if __name__ == "__main__":
    fetcher = EconomicCalendarFetcher()
    data = fetcher.fetch_all()
    print("Upcoming Fed Events:", data["upcoming_fed"])
    print("\nUS Economic Events:", data["us_economic"])
    print("\nThis Week:", data["this_week"])
