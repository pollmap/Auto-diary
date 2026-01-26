"""Google Gemini LLM 클라이언트"""
import os
from google import genai
from google.genai import types
from config import config


class GeminiClient:
    """Gemini API 클라이언트"""

    def __init__(self):
        # 환경변수에서 API 키 가져오기 (GOOGLE_API_KEY 또는 GEMINI_API_KEY)
        api_key = os.getenv("GOOGLE_API_KEY") or config.GEMINI_API_KEY
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash-lite"

    def generate_briefing_summary(self, market_data: dict) -> str:
        """시황 브리핑 요약 생성"""
        prompt = self._build_prompt(market_data)

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=1000,
            )
        )

        return response.text

    def _build_prompt(self, data: dict) -> str:
        """프롬프트 구성"""
        return f"""
당신은 금융 시황 분석가입니다. 아래 데이터를 바탕으로 간결한 시황 요약을 작성해주세요.

## 작성 규칙
1. 팩트 전달 중심, 보수적 관점
2. 투자 권유나 과도한 예측 금지
3. 전일 대비 주요 변동 사항 강조
4. 200~300자 내외로 작성
5. "~했다", "~이다" 체로 작성 (경어체 X)

## 데이터
{self._format_data_for_prompt(data)}

## 출력 형식
오늘의 핵심 포인트를 2~3문장으로 요약하고, 주목할 섹터나 자산을 언급해주세요.
"""

    def _format_data_for_prompt(self, data: dict) -> str:
        """데이터를 프롬프트용 텍스트로 변환"""
        lines = []

        # 미국 지수
        lines.append("### 미국 증시")
        for name, info in data.get("us_indices", {}).items():
            if info.get("price"):
                lines.append(f"- {name}: {info['price']:,.2f} ({info['change']:+.2f}%)")

        # 섹터 ETF
        lines.append("\n### 미국 섹터 ETF")
        for name, info in data.get("us_sectors", {}).items():
            if info.get("price"):
                lines.append(f"- {name}: {info['price']:,.2f} ({info['change']:+.2f}%)")

        # 글로벌 지수
        lines.append("\n### 글로벌 지수")
        for name, info in data.get("global_indices", {}).items():
            if info.get("price"):
                lines.append(f"- {name}: {info['price']:,.2f} ({info['change']:+.2f}%)")

        # 암호화폐
        lines.append("\n### 암호화폐")
        for name, info in data.get("crypto", {}).items():
            if info.get("price_usd"):
                change = info.get('change_24h', 0) or 0
                lines.append(f"- {name}: ${info['price_usd']:,.2f} ({change:+.2f}%)")

        # 환율
        lines.append("\n### 환율")
        for name, info in data.get("currencies", {}).items():
            if info.get("price"):
                lines.append(f"- {name}: {info['price']:,.2f} ({info['change']:+.2f}%)")

        # 원자재
        lines.append("\n### 원자재")
        for name, info in data.get("commodities", {}).items():
            if info.get("price"):
                lines.append(f"- {name}: {info['price']:,.2f} ({info['change']:+.2f}%)")

        # 농산물
        lines.append("\n### 농산물")
        for name, info in data.get("agriculture", {}).items():
            if info.get("price"):
                lines.append(f"- {name}: {info['price']:,.2f} ({info['change']:+.2f}%)")

        return "\n".join(lines)


if __name__ == "__main__":
    # 테스트용
    client = GeminiClient()
    test_data = {
        "us_indices": {"S&P 500": {"price": 5000.0, "change": 0.5}},
        "crypto": {"BTC": {"price_usd": 100000, "change_24h": 2.5}}
    }
    print(client._format_data_for_prompt(test_data))
