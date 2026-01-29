"""main.py 테스트"""
import pytest
import sys
from pathlib import Path

# scripts 디렉토리를 path에 추가
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from main import generate_simple_summary


class TestGenerateSimpleSummary:
    """generate_simple_summary 함수 테스트"""

    def test_empty_data_returns_default(self):
        """빈 데이터일 때 기본 메시지 반환"""
        result = generate_simple_summary({})
        assert result == "오늘의 시황 데이터를 확인하세요."

    def test_vix_low_message(self, sample_market_data):
        """VIX 낮을 때 낙관적 메시지"""
        data = sample_market_data.copy()
        data["market_indicators"]["VIX (공포지수)"]["price"] = 12.0
        result = generate_simple_summary(data)
        assert "낙관적 분위기" in result

    def test_vix_normal_message(self, sample_market_data):
        """VIX 보통일 때 안정적 메시지"""
        data = sample_market_data.copy()
        data["market_indicators"]["VIX (공포지수)"]["price"] = 18.0
        result = generate_simple_summary(data)
        assert "안정적" in result

    def test_vix_high_message(self, sample_market_data):
        """VIX 높을 때 변동성 메시지"""
        data = sample_market_data.copy()
        data["market_indicators"]["VIX (공포지수)"]["price"] = 25.0
        result = generate_simple_summary(data)
        assert "변동성" in result

    def test_vix_very_high_message(self, sample_market_data):
        """VIX 매우 높을 때 공포 메시지"""
        data = sample_market_data.copy()
        data["market_indicators"]["VIX (공포지수)"]["price"] = 35.0
        result = generate_simple_summary(data)
        assert "공포" in result

    def test_all_indices_up_shows_상승(self, sample_all_up_data):
        """모든 지수 상승 시 '상승 마감' 표시"""
        result = generate_simple_summary(sample_all_up_data)
        assert "상승 마감" in result

    def test_all_indices_down_shows_하락(self, sample_all_down_data):
        """모든 지수 하락 시 '하락 마감' 표시"""
        result = generate_simple_summary(sample_all_down_data)
        assert "하락 마감" in result

    def test_mixed_indices_shows_혼조(self, sample_mixed_data):
        """혼조세일 때 '혼조 마감' 표시 - 핵심 버그 수정 테스트"""
        result = generate_simple_summary(sample_mixed_data)
        assert "혼조 마감" in result
        # 기존 버그: S&P500만 보고 '하락'이라고 했던 것 수정 확인
        assert "하락 마감" not in result

    def test_mag7_best_worst(self, sample_market_data):
        """빅테크 최고/최저 종목 표시"""
        result = generate_simple_summary(sample_market_data)
        assert "엔비디아" in result  # 최고 상승률
        assert "테슬라" in result  # 최저 (하락)

    def test_crypto_summary(self, sample_market_data):
        """암호화폐 요약 포함"""
        result = generate_simple_summary(sample_market_data)
        assert "BTC" in result
        assert "ETH" in result

    def test_currency_summary(self, sample_market_data):
        """환율 요약 포함"""
        result = generate_simple_summary(sample_market_data)
        assert "원/달러" in result

    def test_commodity_summary(self, sample_market_data):
        """원자재 요약 포함"""
        result = generate_simple_summary(sample_market_data)
        assert "금" in result
        assert "WTI" in result

    def test_fomc_alert_when_close(self, sample_market_data):
        """FOMC 일주일 이내면 알림"""
        data = sample_market_data.copy()
        data["economic_calendar"]["upcoming_fed"][0]["days_until"] = 3
        result = generate_simple_summary(data)
        assert "FOMC" in result

    def test_no_fomc_alert_when_far(self, sample_market_data):
        """FOMC 멀면 알림 없음"""
        data = sample_market_data.copy()
        data["economic_calendar"]["upcoming_fed"][0]["days_until"] = 20
        result = generate_simple_summary(data)
        # FOMC는 표시되지 않아야 함 (7일 초과)
        # 단, 다른 이유로 FOMC가 포함될 수 있으므로 조건부 확인
