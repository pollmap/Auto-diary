"""데이터 수집 모듈"""
import time
from datetime import datetime
from typing import Dict
import yfinance as yf
import requests
from config import config
from logger import logger, LogContext
from retry import retry_on_exception
from fred_fetcher import FREDFetcher
from fear_greed_fetcher import FearGreedFetcher
from economic_calendar import EconomicCalendarFetcher


class DataFetcher:
    """금융 데이터 수집 클래스"""

    COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self):
        self.data = {
            "timestamp": datetime.now().isoformat(),
            "crypto": {},
            "us_indices": {},
            "market_indicators": {},
            "bonds": {},
            "mag7": {},
            "us_sectors": {},
            "global_indices": {},
            "currencies": {},
            "commodities": {},
            "agriculture": {},
            "economic_indicators": {},
            "fear_greed": {},
            "economic_calendar": {}
        }
        self.fred_fetcher = FREDFetcher()
        self.fg_fetcher = FearGreedFetcher()
        self.calendar_fetcher = EconomicCalendarFetcher()

    def fetch_all(self) -> Dict:
        """모든 데이터 수집"""
        with LogContext("전체 데이터 수집"):
            # 기존 yfinance 데이터
            self.fetch_crypto()
            self.fetch_yfinance_data(config.US_INDICES, "us_indices", "미국 지수")
            self.fetch_yfinance_data(config.MARKET_INDICATORS, "market_indicators", "시장 지표")
            self.fetch_yfinance_data(config.BONDS, "bonds", "채권")
            self.fetch_yfinance_data(config.MAG7_STOCKS, "mag7", "MAG7")
            self.fetch_yfinance_data(config.US_SECTOR_ETFS, "us_sectors", "섹터 ETF")
            self.fetch_yfinance_data(config.GLOBAL_INDICES, "global_indices", "글로벌 지수")
            self.fetch_yfinance_data(config.CURRENCIES, "currencies", "환율")
            self.fetch_yfinance_data(config.COMMODITIES, "commodities", "원자재")
            self.fetch_yfinance_data(config.AGRICULTURE, "agriculture", "농산물")

            # 경제지표 (FRED)
            self.fetch_economic_indicators()

            # Fear & Greed Index
            self.fetch_fear_greed()

            # 경제 캘린더
            self.fetch_economic_calendar()

            logger.info(f"총 {len(self.data)} 카테고리 수집 완료")

        return self.data

    def fetch_economic_indicators(self) -> None:
        """FRED 경제지표 수집"""
        if not config.validate_fred():
            logger.warning("FRED API 키가 없어 경제지표 수집 건너뜀")
            return

        try:
            with LogContext("FRED 경제지표 수집"):
                fred_data = self.fred_fetcher.fetch_all()
                self.data["economic_indicators"] = fred_data
        except Exception as e:
            logger.error(f"경제지표 수집 오류: {e}")

    def fetch_fear_greed(self) -> None:
        """Fear & Greed Index 수집"""
        try:
            with LogContext("Fear & Greed 지수 수집"):
                # VIX와 S&P500 변동률 가져오기
                vix = self.data.get("market_indicators", {}).get("VIX (공포지수)", {}).get("price")
                sp500_change = self.data.get("us_indices", {}).get("S&P 500", {}).get("change")

                fg_data = self.fg_fetcher.fetch_all(vix, sp500_change)
                self.data["fear_greed"] = fg_data
        except Exception as e:
            logger.error(f"Fear & Greed 수집 오류: {e}")

    def fetch_economic_calendar(self) -> None:
        """경제 캘린더 수집"""
        try:
            with LogContext("경제 캘린더 수집"):
                calendar_data = self.calendar_fetcher.fetch_all()
                self.data["economic_calendar"] = calendar_data
        except Exception as e:
            logger.error(f"경제 캘린더 수집 오류: {e}")

    @retry_on_exception(
        max_retries=3,
        delay=1.0,
        exceptions=(requests.RequestException,)
    )
    def _fetch_coingecko(self, ids: str) -> dict:
        """CoinGecko API 호출 (재시도 적용)"""
        url = f"{self.COINGECKO_BASE_URL}/simple/price"
        params = {
            "ids": ids,
            "vs_currencies": "usd,krw",
            "include_24hr_change": "true"
        }
        response = requests.get(url, params=params, timeout=config.REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def fetch_crypto(self) -> None:
        """CoinGecko에서 암호화폐 데이터 수집"""
        try:
            with LogContext("암호화폐 데이터 수집"):
                ids = ",".join(config.CRYPTO_IDS)
                raw_data = self._fetch_coingecko(ids)

                # 데이터 정리
                name_map = {
                    "bitcoin": "BTC",
                    "ethereum": "ETH",
                    "ripple": "XRP",
                    "solana": "SOL",
                    "cardano": "ADA",
                    "dogecoin": "DOGE",
                    "chainlink": "LINK"
                }

                for coin_id, coin_name in name_map.items():
                    if coin_id in raw_data:
                        self.data["crypto"][coin_name] = {
                            "price_usd": raw_data[coin_id].get("usd"),
                            "price_krw": raw_data[coin_id].get("krw"),
                            "change_24h": raw_data[coin_id].get("usd_24h_change")
                        }
                logger.info(f"암호화폐 {len(self.data['crypto'])}개 수집")
        except Exception as e:
            logger.error(f"암호화폐 수집 오류: {e}")

    def fetch_yfinance_data(self, tickers: Dict[str, str], category: str, category_name: str = None) -> None:
        """yfinance로 주식/지수/원자재 데이터 수집"""
        category_name = category_name or category
        success_count = 0

        for name, symbol in tickers.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")

                if len(hist) >= 1:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2] if len(hist) >= 2 else current
                    change = ((current - prev) / prev) * 100 if prev != 0 else 0

                    self.data[category][name] = {
                        "price": round(float(current), 2),
                        "change": round(float(change), 2)
                    }
                    success_count += 1

                time.sleep(config.RATE_LIMIT_DELAY)

            except Exception as e:
                logger.warning(f"{category_name} '{name}' 수집 실패: {e}")
                self.data[category][name] = {"price": None, "change": None}

        logger.info(f"{category_name}: {success_count}/{len(tickers)}개 수집")


if __name__ == "__main__":
    # 테스트용
    fetcher = DataFetcher()
    data = fetcher.fetch_all()
    print(data)
