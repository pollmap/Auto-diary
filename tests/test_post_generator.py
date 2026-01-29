"""post_generator.py 테스트"""
import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from post_generator import PostGenerator


class TestPostGenerator:
    """PostGenerator 클래스 테스트"""

    def test_initialization(self):
        """초기화 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = PostGenerator(posts_dir=tmpdir)
            assert generator.posts_dir.exists()

    def test_format_table_empty(self):
        """빈 테이블 포맷팅"""
        generator = PostGenerator()
        result = generator._format_table({}, ["지수", "종가", "변동"])
        assert result == "_데이터 없음_"

    def test_format_table_with_data(self):
        """데이터 있는 테이블 포맷팅"""
        generator = PostGenerator()
        data = {
            "S&P 500": {"price": 5850.25, "change": 0.35},
            "NASDAQ": {"price": 18500.50, "change": -0.15},
        }
        result = generator._format_table(data, ["지수", "종가", "변동"])
        assert "S&P 500" in result
        assert "5,850.25" in result
        assert "+0.35%" in result
        assert "-0.15%" in result

    def test_format_crypto_table(self):
        """암호화폐 테이블 포맷팅"""
        generator = PostGenerator()
        data = {
            "BTC": {"price_usd": 95000, "price_krw": 139000000, "change_24h": 2.5},
            "ETH": {"price_usd": 3200, "price_krw": 4680000, "change_24h": -1.2},
        }
        result = generator._format_crypto_table(data)
        assert "BTC" in result
        assert "$95,000.00" in result
        assert "₩139,000,000" in result
        assert "+2.50%" in result

    def test_format_fear_greed(self):
        """Fear & Greed 포맷팅"""
        generator = PostGenerator()
        data = {
            "market": {"value": 55, "classification": "탐욕", "based_on": "VIX"},
            "crypto": {"value": 62, "classification": "탐욕", "change": 3},
        }
        result = generator._format_fear_greed(data)
        assert "55/100" in result
        assert "62/100" in result
        assert "탐욕" in result

    def test_format_filtered_table(self):
        """필터링된 테이블 포맷팅"""
        generator = PostGenerator()
        data = {
            "KOSPI": {"price": 2550.30, "change": 0.85},
            "KOSDAQ": {"price": 750.20, "change": -0.45},
            "니케이225": {"price": 38500.50, "change": 1.20},
        }
        result = generator._format_filtered_table(
            data, ["KOSPI", "KOSDAQ"], ["지수", "종가", "변동"]
        )
        assert "KOSPI" in result
        assert "KOSDAQ" in result
        assert "니케이225" not in result

    def test_build_post_content(self, sample_market_data):
        """포스트 내용 생성"""
        generator = PostGenerator()
        now = datetime.now()
        content = generator._build_post_content(sample_market_data, "테스트 요약", now)

        # Front matter 확인
        assert "layout: post" in content
        assert "title:" in content
        assert "categories:" in content

        # 섹션 확인
        assert "오늘의 핵심" in content
        assert "테스트 요약" in content
        assert "미국 증시" in content
        assert "글로벌 증시" in content
        assert "암호화폐" in content
        assert "외환" in content
        assert "원자재" in content

    def test_generate_briefing_post_creates_file(self, sample_market_data):
        """포스트 파일 생성 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = PostGenerator(posts_dir=tmpdir)
            filepath = generator.generate_briefing_post(sample_market_data, "테스트 요약")

            assert Path(filepath).exists()
            content = Path(filepath).read_text(encoding="utf-8")
            assert "테스트 요약" in content

    def test_format_economic_indicators(self, sample_market_data):
        """경제지표 포맷팅 테스트"""
        generator = PostGenerator()
        econ_data = sample_market_data["economic_indicators"]
        result = generator._format_economic_indicators(econ_data)

        assert "CPI" in result or "주요 경제지표" in result

    def test_format_economic_calendar(self, sample_market_data):
        """경제 캘린더 포맷팅 테스트"""
        generator = PostGenerator()
        calendar_data = sample_market_data["economic_calendar"]
        result = generator._format_economic_calendar(calendar_data)

        assert "FOMC" in result or "연준" in result
