"""데이터 수집 모듈 - yfinance 안정화 버전"""
import time
from datetime import datetime
from typing import Dict, List
import requests
from config import config
from logger import logger, LogContext
from retry import retry_on_exception

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    logger.warning("yfinance를 불러올 수 없습니다")

try:
    from fred_fetcher import FREDFetcher
    FRED_AVAILABLE = True
except ImportError:
    FRED_AVAILABLE = False

try:
    from fear_greed_fetcher import FearGreedFetcher
    FG_AVAILABLE = True
except ImportError:
    FG_AVAILABLE = False

try:
    from economic_calendar import EconomicCalendarFetcher
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False


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

    def fetch_all(self) -> Dict:
        """모든 데이터 수집"""
        with LogContext("전체 데이터 수집"):
            # 암호화폐 (CoinGecko)
            self.fetch_crypto()

            # yfinance 데이터 - 배치 다운로드로 rate limit 방지
            self._fetch_all_yfinance()

            # 경제지표 (FRED)
            self._fetch_economic_indicators()

            # Fear & Greed Index
            self._fetch_fear_greed()

            # 경제 캘린더
            self._fetch_economic_calendar()

            # 결과 요약
            filled = sum(1 for k, v in self.data.items()
                         if isinstance(v, dict) and v and k != "timestamp")
            logger.info(f"데이터 수집 완료: {filled}/{len(self.data)-1} 카테고리")

        return self.data

    # ==========================================================
    # yfinance 배치 다운로드 (핵심 수정!)
    # ==========================================================
    def _fetch_all_yfinance(self) -> None:
        """yfinance로 모든 데이터를 배치 다운로드"""
        if not YFINANCE_AVAILABLE:
            logger.error("yfinance를 사용할 수 없습니다")
            return

        # 모든 심볼 수집
        all_categories = {
            "us_indices": config.US_INDICES,
            "market_indicators": config.MARKET_INDICATORS,
            "bonds": config.BONDS,
            "mag7": config.MAG7_STOCKS,
            "us_sectors": config.US_SECTOR_ETFS,
            "global_indices": config.GLOBAL_INDICES,
            "currencies": config.CURRENCIES,
            "commodities": config.COMMODITIES,
            "agriculture": config.AGRICULTURE,
        }

        # 심볼 → (카테고리, 이름) 역매핑
        symbol_map = {}
        all_symbols = []
        for category, tickers in all_categories.items():
            for name, symbol in tickers.items():
                symbol_map[symbol] = (category, name)
                all_symbols.append(symbol)

        logger.info(f"yfinance 배치 다운로드: {len(all_symbols)}개 심볼")

        # 방법 1: yf.download 배치 (한 번에 다운로드)
        try:
            batch_data = self._batch_download(all_symbols)
            if batch_data:
                self._process_batch_data(batch_data, symbol_map)
                return
        except Exception as e:
            logger.warning(f"배치 다운로드 실패: {e}")

        # 방법 2: 개별 다운로드 (fallback)
        logger.info("개별 다운로드로 전환...")
        for category, tickers in all_categories.items():
            self._fetch_category_individual(tickers, category)

    @retry_on_exception(max_retries=3, delay=2.0, exceptions=(Exception,))
    def _batch_download(self, symbols: List[str]) -> dict:
        """yf.download으로 배치 다운로드 (재시도 적용)"""
        import pandas as pd

        symbols_str = " ".join(symbols)
        logger.info(f"yf.download 호출: {len(symbols)}개 심볼")

        df = yf.download(
            symbols_str,
            period="5d",
            group_by="ticker",
            auto_adjust=True,
            threads=True,
            progress=False
        )

        if df is None or df.empty:
            raise ValueError("yf.download이 빈 결과를 반환했습니다")

        logger.info(f"yf.download 성공: {df.shape}")
        return df

    def _process_batch_data(self, df, symbol_map: dict) -> None:
        """배치 다운로드 결과 처리"""
        import pandas as pd

        success_count = 0
        fail_count = 0

        for symbol, (category, name) in symbol_map.items():
            try:
                # 단일 심볼이면 컬럼 구조가 다름
                if len(symbol_map) == 1:
                    ticker_df = df
                else:
                    if symbol not in df.columns.get_level_values(0):
                        logger.warning(f"  심볼 없음: {symbol} ({name})")
                        fail_count += 1
                        continue
                    ticker_df = df[symbol]

                # Close 데이터가 있는 행만 필터링
                close_data = ticker_df['Close'].dropna()

                if len(close_data) >= 1:
                    current = float(close_data.iloc[-1])
                    prev = float(close_data.iloc[-2]) if len(close_data) >= 2 else current
                    change = ((current - prev) / prev) * 100 if prev != 0 else 0

                    self.data[category][name] = {
                        "price": round(current, 2),
                        "change": round(change, 2)
                    }
                    success_count += 1
                else:
                    fail_count += 1

            except Exception as e:
                logger.warning(f"  처리 실패: {symbol} ({name}): {e}")
                fail_count += 1

        logger.info(f"배치 처리 결과: 성공 {success_count}, 실패 {fail_count}")

    def _fetch_category_individual(self, tickers: Dict[str, str], category: str) -> None:
        """개별 종목 다운로드 (fallback)"""
        for name, symbol in tickers.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d")

                if len(hist) >= 1:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2] if len(hist) >= 2 else current
                    change = ((current - prev) / prev) * 100 if prev != 0 else 0

                    self.data[category][name] = {
                        "price": round(float(current), 2),
                        "change": round(float(change), 2)
                    }

                time.sleep(config.RATE_LIMIT_DELAY)

            except Exception as e:
                logger.warning(f"개별 수집 실패 {name} ({symbol}): {e}")

    # ==========================================================
    # CoinGecko (암호화폐)
    # ==========================================================
    @retry_on_exception(max_retries=3, delay=1.0, exceptions=(requests.RequestException,))
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

    # ==========================================================
    # FRED 경제지표
    # ==========================================================
    def _fetch_economic_indicators(self) -> None:
        """FRED 경제지표 수집"""
        if not FRED_AVAILABLE:
            logger.info("FRED fetcher를 사용할 수 없습니다")
            return
        if not config.validate_fred():
            logger.warning("FRED API 키가 없어 경제지표 수집 건너뜀")
            return

        try:
            with LogContext("FRED 경제지표 수집"):
                fetcher = FREDFetcher()
                self.data["economic_indicators"] = fetcher.fetch_all()
        except Exception as e:
            logger.error(f"경제지표 수집 오류: {e}")

    # ==========================================================
    # Fear & Greed
    # ==========================================================
    def _fetch_fear_greed(self) -> None:
        """Fear & Greed Index 수집"""
        if not FG_AVAILABLE:
            logger.info("Fear & Greed fetcher를 사용할 수 없습니다")
            return

        try:
            with LogContext("Fear & Greed 지수 수집"):
                fetcher = FearGreedFetcher()
                vix = self.data.get("market_indicators", {}).get("VIX (공포지수)", {}).get("price")
                sp500_change = self.data.get("us_indices", {}).get("S&P 500", {}).get("change")
                self.data["fear_greed"] = fetcher.fetch_all(vix, sp500_change)
        except Exception as e:
            logger.error(f"Fear & Greed 수집 오류: {e}")

    # ==========================================================
    # 경제 캘린더
    # ==========================================================
    def _fetch_economic_calendar(self) -> None:
        """경제 캘린더 수집"""
        if not CALENDAR_AVAILABLE:
            logger.info("경제 캘린더 fetcher를 사용할 수 없습니다")
            return

        try:
            with LogContext("경제 캘린더 수집"):
                fetcher = EconomicCalendarFetcher()
                self.data["economic_calendar"] = fetcher.fetch_all()
        except Exception as e:
            logger.error(f"경제 캘린더 수집 오류: {e}")


if __name__ == "__main__":
    fetcher = DataFetcher()
    data = fetcher.fetch_all()
    print(data)
