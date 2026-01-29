"""Fear & Greed Index 수집 모듈"""
import requests
from typing import Dict, Optional
from datetime import datetime


class FearGreedFetcher:
    """CNN Fear & Greed Index 및 Crypto Fear & Greed 수집"""

    # Alternative.me Crypto Fear & Greed API (무료)
    CRYPTO_FG_URL = "https://api.alternative.me/fng/"

    # CNN Fear & Greed는 공식 API가 없어서 대안 사용
    # rapid api나 스크래핑 대신 계산된 값 사용

    def fetch_crypto_fear_greed(self) -> Optional[Dict]:
        """암호화폐 Fear & Greed Index 수집"""
        try:
            params = {"limit": 2, "format": "json"}
            response = requests.get(self.CRYPTO_FG_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            fg_data = data.get("data", [])

            if fg_data:
                latest = fg_data[0]
                prev = fg_data[1] if len(fg_data) > 1 else None

                current_val = int(latest["value"])
                prev_val = int(prev["value"]) if prev else None

                return {
                    "value": current_val,
                    "classification": latest["value_classification"],
                    "timestamp": latest["timestamp"],
                    "prev_value": prev_val,
                    "change": current_val - prev_val if prev_val else None,
                    "interpretation": self._interpret_value(current_val)
                }

        except Exception as e:
            print(f"Crypto Fear & Greed fetch error: {e}")

        return None

    def _interpret_value(self, value: int) -> str:
        """Fear & Greed 값 해석"""
        if value <= 25:
            return "극도의 공포"
        elif value <= 45:
            return "공포"
        elif value <= 55:
            return "중립"
        elif value <= 75:
            return "탐욕"
        else:
            return "극도의 탐욕"

    def calculate_market_sentiment(self, vix: float = None, sp500_change: float = None) -> Optional[Dict]:
        """VIX와 S&P500 변동률 기반 시장 심리 계산"""
        if vix is None:
            return None

        # VIX 기반 점수 (0-100, 낮을수록 탐욕)
        # VIX < 12: 극도의 탐욕 (90-100)
        # VIX 12-17: 탐욕 (70-90)
        # VIX 17-22: 중립 (45-55)
        # VIX 22-30: 공포 (25-45)
        # VIX > 30: 극도의 공포 (0-25)

        if vix < 12:
            score = 95 - (vix * 0.4)
        elif vix < 17:
            score = 90 - ((vix - 12) * 4)
        elif vix < 22:
            score = 55 - ((vix - 17) * 2)
        elif vix < 30:
            score = 45 - ((vix - 22) * 2.5)
        else:
            score = max(0, 25 - ((vix - 30) * 0.5))

        # S&P500 변동률 반영 (보조 지표)
        if sp500_change is not None:
            if sp500_change > 1:
                score = min(100, score + 5)
            elif sp500_change < -1:
                score = max(0, score - 5)

        score = int(round(score))

        return {
            "value": score,
            "classification": self._interpret_value(score),
            "based_on": f"VIX {vix:.1f}" + (f", S&P500 {sp500_change:+.2f}%" if sp500_change else ""),
            "interpretation": self._interpret_value(score)
        }

    def fetch_all(self, vix: float = None, sp500_change: float = None) -> Dict:
        """모든 Fear & Greed 지표 수집"""
        return {
            "crypto": self.fetch_crypto_fear_greed(),
            "market": self.calculate_market_sentiment(vix, sp500_change)
        }


if __name__ == "__main__":
    fetcher = FearGreedFetcher()

    # 암호화폐 Fear & Greed
    crypto_fg = fetcher.fetch_crypto_fear_greed()
    print("Crypto Fear & Greed:", crypto_fg)

    # 시장 심리 계산 (VIX 20, S&P500 +0.5% 가정)
    market_sentiment = fetcher.calculate_market_sentiment(20.0, 0.5)
    print("Market Sentiment:", market_sentiment)
