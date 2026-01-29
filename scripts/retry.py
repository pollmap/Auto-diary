"""재시도 로직 유틸리티"""
import time
from functools import wraps
from typing import Callable, TypeVar, Any, Tuple, Type
from config import config
from logger import logger

T = TypeVar("T")


def retry_on_exception(
    max_retries: int = None,
    delay: float = None,
    backoff: float = None,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Callable[[Exception, int], None] = None
):
    """예외 발생 시 재시도하는 데코레이터

    Args:
        max_retries: 최대 재시도 횟수 (기본값: config.MAX_RETRIES)
        delay: 재시도 기본 대기 시간 (기본값: config.RETRY_DELAY)
        backoff: 지수 백오프 배수 (기본값: config.RETRY_BACKOFF)
        exceptions: 재시도할 예외 타입들
        on_retry: 재시도 시 호출할 콜백 함수

    Returns:
        데코레이터 함수
    """
    max_retries = max_retries if max_retries is not None else config.MAX_RETRIES
    delay = delay if delay is not None else config.RETRY_DELAY
    backoff = backoff if backoff is not None else config.RETRY_BACKOFF

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"[재시도 {attempt + 1}/{max_retries}] "
                            f"{func.__name__} 실패: {e}. {current_delay:.1f}초 후 재시도..."
                        )
                        if on_retry:
                            on_retry(e, attempt + 1)
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"[최종 실패] {func.__name__}: {max_retries}회 재시도 후 실패 - {e}"
                        )

            raise last_exception

        return wrapper
    return decorator


def retry_request(
    func: Callable[..., T],
    *args,
    max_retries: int = None,
    delay: float = None,
    backoff: float = None,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    **kwargs
) -> T:
    """함수를 재시도와 함께 실행

    데코레이터 대신 직접 호출할 때 사용

    Args:
        func: 실행할 함수
        *args: 함수에 전달할 위치 인자
        max_retries: 최대 재시도 횟수
        delay: 재시도 기본 대기 시간
        backoff: 지수 백오프 배수
        exceptions: 재시도할 예외 타입들
        **kwargs: 함수에 전달할 키워드 인자

    Returns:
        함수 실행 결과
    """
    max_retries = max_retries if max_retries is not None else config.MAX_RETRIES
    delay = delay if delay is not None else config.RETRY_DELAY
    backoff = backoff if backoff is not None else config.RETRY_BACKOFF

    last_exception = None
    current_delay = delay

    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except exceptions as e:
            last_exception = e
            if attempt < max_retries:
                logger.warning(
                    f"[재시도 {attempt + 1}/{max_retries}] "
                    f"{func.__name__} 실패: {e}. {current_delay:.1f}초 후 재시도..."
                )
                time.sleep(current_delay)
                current_delay *= backoff
            else:
                logger.error(
                    f"[최종 실패] {func.__name__}: {max_retries}회 재시도 후 실패 - {e}"
                )

    raise last_exception
