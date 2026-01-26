"""데이터 수집 모듈"""
import time
from datetime import datetime
from typing import Dict
import yfinance as yf
import requests
from config import config


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
            "agriculture": {}
        }

    def fetch_all(self) -> Dict:
        """모든 데이터 수집"""
        self.fetch_crypto()
        self.fetch_yfinance_data(config.US_INDICES, "us_indices")
        self.fetch_yfinance_data(config.MARKET_INDICATORS, "market_indicators")
        self.fetch_yfinance_data(config.BONDS, "bonds")
        self.fetch_yfinance_data(config.MAG7_STOCKS, "mag7")
        self.fetch_yfinance_data(config.US_SECTOR_ETFS, "us_sectors")
        self.fetch_yfinance_data(config.GLOBAL_INDICES, "global_indices")
        self.fetch_yfinance_data(config.CURRENCIES, "currencies")
        self.fetch_yfinance_data(config.COMMODITIES, "commodities")
        self.fetch_yfinance_data(config.AGRICULTURE, "agriculture")
        return self.data

    def fetch_crypto(self) -> None:
        """CoinGecko에서 암호화폐 데이터 수집"""
        try:
            ids = ",".join(config.CRYPTO_IDS)
            url = f"{self.COINGECKO_BASE_URL}/simple/price"
            params = {
                "ids": ids,
                "vs_currencies": "usd,krw",
                "include_24hr_change": "true"
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            raw_data = response.json()

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
        except Exception as e:
            print(f"Crypto fetch error: {e}")

    def fetch_yfinance_data(self, tickers: Dict[str, str], category: str) -> None:
        """yfinance로 주식/지수/원자재 데이터 수집"""
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

                time.sleep(0.5)  # Rate limit 방지

            except Exception as e:
                print(f"yfinance error for {name}: {e}")
                self.data[category][name] = {"price": None, "change": None}


if __name__ == "__main__":
    # 테스트용
    fetcher = DataFetcher()
    data = fetcher.fetch_all()
    print(data)
