"""Jekyll 포스트 생성 모듈"""
from datetime import datetime
from pathlib import Path
from typing import Dict


class PostGenerator:
    """마크다운 포스트 생성기"""

    def __init__(self, posts_dir: str = "../_posts/market"):
        self.posts_dir = Path(__file__).parent / posts_dir
        self.posts_dir.mkdir(parents=True, exist_ok=True)

    def generate_briefing_post(self, data: Dict, summary: str) -> str:
        """시황 브리핑 포스트 생성"""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        filename = f"{date_str}-daily-market-briefing.md"

        content = self._build_post_content(data, summary, now)

        filepath = self.posts_dir / filename
        filepath.write_text(content, encoding="utf-8")

        return str(filepath)

    def _build_post_content(self, data: Dict, summary: str, now: datetime) -> str:
        """포스트 내용 구성"""

        # 요일 한글 변환
        weekdays = ['월', '화', '수', '목', '금', '토', '일']
        weekday_kr = weekdays[now.weekday()]

        front_matter = f"""---
layout: post
title: "3분 시황 브리핑 - {now.strftime('%Y년 %m월 %d일')}"
date: {now.strftime('%Y-%m-%d %H:%M:%S')} +0900
categories: [market, briefing]
tags: [시황, 증시, 암호화폐, 원자재]
author: 이찬희
---

"""

        # VIX 값 가져오기
        vix_data = data.get('market_indicators', {}).get('VIX (공포지수)', {})
        vix_value = vix_data.get('price', '-')
        vix_change = vix_data.get('change', 0)
        vix_status = "안정" if vix_value != '-' and vix_value < 20 else "주의" if vix_value != '-' and vix_value < 30 else "공포"

        body = f"""
> {now.strftime('%Y년 %m월 %d일')} ({weekday_kr}) 오전 6:00 기준

---

## 📋 오늘의 핵심

{summary}

---

## 📊 시장 심리 지표

| 지표 | 값 | 변동 | 상태 |
|------|-----|------|------|
| VIX (공포지수) | {vix_value} | {vix_change:+.2f}% | {vix_status} |

{self._format_table(data.get('bonds', {}), ['채권', '금리(%)', '변동'])}

---

## 🇺🇸 미국 증시

### 주요 지수
{self._format_table(data.get('us_indices', {}), ['지수', '종가', '변동'])}

### 빅테크 (MAG7)
{self._format_table(data.get('mag7', {}), ['종목', '주가($)', '변동'])}

### 섹터 ETF
{self._format_table(data.get('us_sectors', {}), ['섹터', '종가', '변동'])}

---

## 🌏 글로벌 증시

### 아시아
{self._format_filtered_table(data.get('global_indices', {}), ['KOSPI', 'KOSDAQ', '니케이225', '항셍', '상해종합'], ['지수', '종가', '변동'])}

### 유럽
{self._format_filtered_table(data.get('global_indices', {}), ['DAX', 'FTSE 100'], ['지수', '종가', '변동'])}

---

## 🪙 암호화폐

{self._format_crypto_table(data.get('crypto', {}))}

---

## 💱 외환

{self._format_table(data.get('currencies', {}), ['통화쌍', '환율', '변동'])}

---

## 🛢️ 원자재

### 에너지 & 금속
{self._format_table(data.get('commodities', {}), ['품목', '가격', '변동'])}

### 농산물
{self._format_table(data.get('agriculture', {}), ['품목', '가격', '변동'])}

---

*{now.strftime('%Y.%m.%d')} | 찬희의 투자노트*
"""

        return front_matter + body

    def _format_table(self, data: Dict, headers: list) -> str:
        """일반 테이블 포맷팅"""
        if not data:
            return "_데이터 없음_"

        lines = [
            f"| {headers[0]} | {headers[1]} | {headers[2]} |",
            "|------|------|------|"
        ]

        for name, info in data.items():
            price = info.get('price')
            change = info.get('change')
            if price is not None:
                change_str = f"{change:+.2f}%" if change is not None else "-"
                lines.append(f"| {name} | {price:,.2f} | {change_str} |")

        return "\n".join(lines)

    def _format_filtered_table(self, data: Dict, keys: list, headers: list) -> str:
        """특정 키만 필터링하여 테이블 생성"""
        filtered = {k: v for k, v in data.items() if k in keys}
        return self._format_table(filtered, headers)

    def _format_crypto_table(self, data: Dict) -> str:
        """암호화폐 테이블 포맷팅"""
        if not data:
            return "_데이터 없음_"

        lines = [
            "| 코인 | 가격 (USD) | 가격 (KRW) | 24h 변동 |",
            "|------|-----------|-----------|---------|"
        ]

        for name, info in data.items():
            price_usd = info.get('price_usd')
            price_krw = info.get('price_krw')
            change = info.get('change_24h')
            if price_usd is not None:
                change_str = f"{change:+.2f}%" if change is not None else "-"
                krw_str = f"₩{price_krw:,.0f}" if price_krw else "-"
                lines.append(f"| {name} | ${price_usd:,.2f} | {krw_str} | {change_str} |")

        return "\n".join(lines)


if __name__ == "__main__":
    # 테스트용
    generator = PostGenerator()
    test_data = {
        "us_indices": {"S&P 500": {"price": 5000.0, "change": 0.5}},
        "crypto": {"BTC": {"price_usd": 100000, "change_24h": 2.5}}
    }
    print(generator._build_post_content(test_data, "테스트 요약입니다.", datetime.now()))
