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

{self._format_fear_greed(data.get('fear_greed', {}))}

### 채권 금리
{self._format_table(data.get('bonds', {}), ['채권', '금리(%)', '변동'])}

{self._format_economic_indicators(data.get('economic_indicators', {}))}

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

## 📅 경제 캘린더

{self._format_economic_calendar(data.get('economic_calendar', {}))}

---

*{now.strftime('%Y.%m.%d')} | 찬희의 투자노트*
"""

        return front_matter + body

    def _format_table(self, data: Dict, headers: list) -> str:
        """일반 테이블 포맷팅 (kramdown 호환)"""
        if not data:
            return "\n_데이터 없음_\n"

        # kramdown은 테이블 앞뒤에 빈 줄이 필요함
        lines = [
            "",  # 테이블 앞 빈 줄 (중요!)
            f"| {headers[0]} | {headers[1]} | {headers[2]} |",
            "|:------|------:|------:|"  # 정렬: 첫 열 왼쪽, 나머지 오른쪽
        ]

        for name, info in data.items():
            price = info.get('price')
            change = info.get('change')
            if price is not None:
                change_str = f"{change:+.2f}%" if change is not None else "-"
                lines.append(f"| {name} | {price:,.2f} | {change_str} |")

        lines.append("")  # 테이블 뒤 빈 줄
        return "\n".join(lines)

    def _format_filtered_table(self, data: Dict, keys: list, headers: list) -> str:
        """특정 키만 필터링하여 테이블 생성"""
        filtered = {k: v for k, v in data.items() if k in keys}
        return self._format_table(filtered, headers)

    def _format_crypto_table(self, data: Dict) -> str:
        """암호화폐 테이블 포맷팅 (kramdown 호환)"""
        if not data:
            return "\n_데이터 없음_\n"

        lines = [
            "",  # 테이블 앞 빈 줄
            "| 코인 | 가격 (USD) | 가격 (KRW) | 24h 변동 |",
            "|:------|------:|------:|------:|"
        ]

        for name, info in data.items():
            price_usd = info.get('price_usd')
            price_krw = info.get('price_krw')
            change = info.get('change_24h')
            if price_usd is not None:
                change_str = f"{change:+.2f}%" if change is not None else "-"
                krw_str = f"₩{price_krw:,.0f}" if price_krw else "-"
                lines.append(f"| {name} | ${price_usd:,.2f} | {krw_str} | {change_str} |")

        lines.append("")  # 테이블 뒤 빈 줄
        return "\n".join(lines)

    def _format_fear_greed(self, data: Dict) -> str:
        """Fear & Greed Index 포맷팅"""
        lines = []

        # 시장 심리 (VIX 기반)
        market = data.get("market")
        if market:
            value = market.get("value", 0)
            emoji = "🟢" if value >= 55 else "🟡" if value >= 45 else "🔴"
            lines.append(f"### 시장 심리 지수")
            lines.append(f"{emoji} **{value}/100** - {market.get('classification', '-')}")
            if market.get("based_on"):
                lines.append(f"_(기준: {market['based_on']})_")
            lines.append("")

        # 암호화폐 Fear & Greed
        crypto = data.get("crypto")
        if crypto:
            value = crypto.get("value", 0)
            emoji = "🟢" if value >= 55 else "🟡" if value >= 45 else "🔴"
            change = crypto.get("change")
            change_str = f" ({change:+d})" if change is not None else ""
            lines.append(f"### 암호화폐 Fear & Greed")
            lines.append(f"{emoji} **{value}/100** - {crypto.get('classification', '-')}{change_str}")
            lines.append("")

        return "\n".join(lines) if lines else ""

    def _format_economic_indicators(self, data: Dict) -> str:
        """경제지표 포맷팅 (kramdown 호환)"""
        if not data:
            return ""

        lines = ["### 📈 주요 경제지표", ""]

        # 일간 지표
        daily = data.get("daily", {})
        if daily:
            lines.append("**금리 동향**")
            lines.append("")  # 테이블 앞 빈 줄
            lines.append("| 지표 | 값 | 변동 | 기준일 |")
            lines.append("|:------|------:|------:|:--------|")
            for name, info in daily.items():
                if info and info.get("value") is not None:
                    change_str = f"{info['change']:+.2f}%" if info.get('change') is not None else "-"
                    lines.append(f"| {name} | {info['value']:.2f}% | {change_str} | {info.get('date', '-')} |")
            lines.append("")

        # 주간 지표
        weekly = data.get("weekly", {})
        if weekly:
            lines.append("**고용 동향**")
            lines.append("")  # 테이블 앞 빈 줄
            lines.append("| 지표 | 값 | 변동 | 기준일 |")
            lines.append("|:------|------:|------:|:--------|")
            for name, info in weekly.items():
                if info and info.get("value") is not None:
                    val = info['value']
                    change_str = f"{info['change']:+.2f}%" if info.get('change') is not None else "-"
                    lines.append(f"| {name} | {val:,.0f} | {change_str} | {info.get('date', '-')} |")
            lines.append("")

        # 월간 주요 지표
        monthly = data.get("monthly", {})
        if monthly:
            lines.append("**주요 경제지표 (최신)**")
            lines.append("")  # 테이블 앞 빈 줄
            lines.append("| 지표 | 값 | 기준일 |")
            lines.append("|:------|------:|:--------|")
            for name, info in monthly.items():
                if info and info.get("value") is not None:
                    val = info['value']
                    # YoY 지표는 %로 표시
                    if info.get("unit") == "% YoY" or "YoY" in name:
                        val_str = f"{val:+.2f}%"
                    elif "실업률" in name or "금리" in name:
                        val_str = f"{val:.2f}%"
                    elif abs(val) >= 1000:
                        val_str = f"{val:,.0f}"
                    else:
                        val_str = f"{val:.2f}"
                    lines.append(f"| {name} | {val_str} | {info.get('date', '-')} |")
            lines.append("")

        return "\n".join(lines)

    def _format_economic_calendar(self, data: Dict) -> str:
        """경제 캘린더 포맷팅"""
        if not data:
            return "_캘린더 데이터 없음_"

        lines = []

        # 다가오는 FOMC 일정
        fed_events = data.get("upcoming_fed", [])
        if fed_events:
            lines.append("### 🏛️ 연준 일정")
            for event in fed_events[:3]:  # 최대 3개
                emoji = "🔴" if event.get("importance") == "high" else "🟡"
                lines.append(f"- {emoji} **{event['display']}** {event['event']} ({event['date']})")
            lines.append("")

        # 이번 주 주요 이벤트
        this_week = data.get("this_week", {})
        week_events = this_week.get("economic", []) + this_week.get("weekly", [])
        if week_events:
            lines.append("### 📆 이번 주 주요 지표 발표")
            for event in week_events[:5]:  # 최대 5개
                importance = event.get("importance", "medium")
                emoji = "🔴" if importance == "high" else "🟡" if importance == "medium" else "⚪"
                lines.append(f"- {emoji} {event['event']} ({event.get('date', '예정')})")
            lines.append("")

        if not lines:
            lines.append("_이번 주 주요 이벤트 없음_")

        return "\n".join(lines)


if __name__ == "__main__":
    # 테스트용
    generator = PostGenerator()
    test_data = {
        "us_indices": {"S&P 500": {"price": 5000.0, "change": 0.5}},
        "crypto": {"BTC": {"price_usd": 100000, "change_24h": 2.5}}
    }
    print(generator._build_post_content(test_data, "테스트 요약입니다.", datetime.now()))
