"""구조화된 로깅 모듈"""
import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logger(name: str = "auto-diary", level: str = "INFO") -> logging.Logger:
    """로거 설정 및 반환

    Args:
        name: 로거 이름
        level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        설정된 Logger 인스턴스
    """
    logger = logging.getLogger(name)

    # 이미 핸들러가 있으면 중복 추가 방지
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # 포맷터 설정
    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러 (선택적)
    log_dir = Path(__file__).parent.parent / "logs"
    if log_dir.exists() or _try_create_log_dir(log_dir):
        log_file = log_dir / f"auto-diary-{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def _try_create_log_dir(log_dir: Path) -> bool:
    """로그 디렉토리 생성 시도"""
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


# 기본 로거 인스턴스
logger = setup_logger()


class LogContext:
    """컨텍스트 매니저로 작업 단위 로깅"""

    def __init__(self, task_name: str, log: logging.Logger = None):
        self.task_name = task_name
        self.log = log or logger
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        self.log.info(f"[시작] {self.task_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if exc_type:
            self.log.error(f"[실패] {self.task_name} ({elapsed:.2f}초) - {exc_val}")
        else:
            self.log.info(f"[완료] {self.task_name} ({elapsed:.2f}초)")
        return False  # 예외를 다시 발생시킴
