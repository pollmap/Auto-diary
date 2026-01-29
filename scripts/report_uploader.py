"""보고서 업로드 도구

사용자가 작성한 보고서를 쉽게 블로그에 올릴 수 있도록 도와주는 스크립트입니다.

사용법:
    python report_uploader.py                    # 대화형 모드
    python report_uploader.py --file report.md   # 파일 직접 지정
    python report_uploader.py --category analysis --title "테슬라 분석"  # 카테고리와 제목 지정
"""
import argparse
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import config
from logger import logger


# 카테고리별 디렉토리 매핑
CATEGORY_MAP = {
    "analysis": ("기업분석", "_posts/analysis"),
    "market": ("시황", "_posts/market"),
    "crypto": ("크립토", "_posts/crypto"),
    "essays": ("에세이", "_posts/essays"),
    "realestate": ("임장", "_posts/realestate"),
}


def slugify(text: str) -> str:
    """한글/영문 텍스트를 URL-safe 슬러그로 변환"""
    # 한글은 그대로, 영문은 소문자로
    text = text.lower().strip()
    # 공백을 하이픈으로
    text = re.sub(r'\s+', '-', text)
    # 특수문자 제거 (한글, 영문, 숫자, 하이픈만 허용)
    text = re.sub(r'[^\w가-힣-]', '', text)
    return text


def create_front_matter(
    title: str,
    category: str,
    tags: list[str],
    author: str = None,
    excerpt: str = None,
    downloadable: bool = True
) -> str:
    """Jekyll front matter 생성"""
    now = datetime.now()
    author = author or config.SITE_AUTHOR

    front_matter = f"""---
layout: post
title: "{title}"
date: {now.strftime('%Y-%m-%d %H:%M:%S')} +0900
categories: [{category}]
tags: [{', '.join(tags)}]
author: {author}
downloadable: {str(downloadable).lower()}
"""
    if excerpt:
        front_matter += f'excerpt: "{excerpt}"\n'

    front_matter += "---\n"
    return front_matter


def process_markdown_file(
    input_path: Path,
    category: str,
    title: Optional[str] = None,
    tags: Optional[list[str]] = None,
    output_dir: Optional[Path] = None
) -> Path:
    """마크다운 파일 처리 및 포스트 생성

    Args:
        input_path: 입력 마크다운 파일 경로
        category: 카테고리 (analysis, market, crypto, essays, realestate)
        title: 포스트 제목 (없으면 파일명에서 추출)
        tags: 태그 리스트
        output_dir: 출력 디렉토리 (없으면 자동 결정)

    Returns:
        생성된 포스트 파일 경로
    """
    # 파일 읽기
    content = input_path.read_text(encoding="utf-8")

    # 제목 추출 (없으면 파일명에서)
    if not title:
        # 첫 번째 # 헤더를 제목으로 사용
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            # 제목 라인 제거
            content = content.replace(title_match.group(0), '', 1).strip()
        else:
            title = input_path.stem

    # 태그 추출 (없으면 기본값)
    if not tags:
        tags = [CATEGORY_MAP.get(category, ("기타", ""))[0]]

    # 출력 디렉토리 결정
    if not output_dir:
        base_dir = Path(__file__).parent.parent
        category_info = CATEGORY_MAP.get(category, ("기타", "_posts"))
        output_dir = base_dir / category_info[1]

    output_dir.mkdir(parents=True, exist_ok=True)

    # 파일명 생성
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(title)
    filename = f"{date_str}-{slug}.md"
    output_path = output_dir / filename

    # front matter + 내용
    front_matter = create_front_matter(title, category, tags)
    full_content = front_matter + "\n" + content

    # 저장
    output_path.write_text(full_content, encoding="utf-8")
    logger.info(f"포스트 생성 완료: {output_path}")

    return output_path


def interactive_mode():
    """대화형 모드로 보고서 업로드"""
    print("\n=== 보고서 업로드 도구 ===\n")

    # 카테고리 선택
    print("카테고리를 선택하세요:")
    for i, (key, (name, _)) in enumerate(CATEGORY_MAP.items(), 1):
        print(f"  {i}. {name} ({key})")

    while True:
        choice = input("\n선택 (1-5): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= 5:
            category = list(CATEGORY_MAP.keys())[int(choice) - 1]
            break
        print("올바른 번호를 입력하세요.")

    # 파일 경로 입력
    while True:
        file_path = input("\n마크다운 파일 경로: ").strip()
        path = Path(file_path).expanduser()
        if path.exists() and path.suffix.lower() in ['.md', '.markdown']:
            break
        print("유효한 마크다운 파일 경로를 입력하세요.")

    # 제목 입력 (선택)
    title = input("\n제목 (엔터로 자동 추출): ").strip() or None

    # 태그 입력 (선택)
    tags_input = input("태그 (쉼표로 구분, 엔터로 기본값): ").strip()
    tags = [t.strip() for t in tags_input.split(",")] if tags_input else None

    # 처리
    output_path = process_markdown_file(path, category, title, tags)

    print(f"\n✅ 포스트가 생성되었습니다: {output_path}")
    print("\n다음 단계:")
    print("  1. git add -A")
    print("  2. git commit -m '새 포스트 추가'")
    print("  3. git push")
    print("\n푸시하면 GitHub Pages가 자동으로 업데이트됩니다.")


def main():
    parser = argparse.ArgumentParser(description="보고서 업로드 도구")
    parser.add_argument("--file", "-f", type=str, help="마크다운 파일 경로")
    parser.add_argument(
        "--category", "-c",
        choices=list(CATEGORY_MAP.keys()),
        help="카테고리"
    )
    parser.add_argument("--title", "-t", type=str, help="포스트 제목")
    parser.add_argument("--tags", type=str, help="태그 (쉼표로 구분)")

    args = parser.parse_args()

    if args.file:
        # 명령줄 모드
        path = Path(args.file).expanduser()
        if not path.exists():
            print(f"파일을 찾을 수 없습니다: {path}")
            return 1

        category = args.category or "essays"
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else None

        output_path = process_markdown_file(path, category, args.title, tags)
        print(f"포스트 생성 완료: {output_path}")
    else:
        # 대화형 모드
        interactive_mode()

    return 0


if __name__ == "__main__":
    exit(main())
