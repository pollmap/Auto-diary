"""retry.py 테스트"""
import pytest
import time
from retry import retry_on_exception, retry_request


class TestRetryOnException:
    """retry_on_exception 데코레이터 테스트"""

    def test_success_on_first_try(self):
        """첫 시도에 성공하면 재시도 없음"""
        call_count = 0

        @retry_on_exception(max_retries=3, delay=0.01)
        def success_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = success_func()
        assert result == "success"
        assert call_count == 1

    def test_retry_on_failure(self):
        """실패 시 재시도"""
        call_count = 0

        @retry_on_exception(max_retries=3, delay=0.01, backoff=1.0)
        def fail_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("fail")
            return "success"

        result = fail_twice()
        assert result == "success"
        assert call_count == 3

    def test_max_retries_exceeded(self):
        """최대 재시도 횟수 초과 시 예외 발생"""
        call_count = 0

        @retry_on_exception(max_retries=2, delay=0.01, backoff=1.0)
        def always_fail():
            nonlocal call_count
            call_count += 1
            raise ValueError("always fail")

        with pytest.raises(ValueError):
            always_fail()
        assert call_count == 3  # 초기 1회 + 재시도 2회

    def test_specific_exception_only(self):
        """특정 예외만 재시도"""
        call_count = 0

        @retry_on_exception(max_retries=3, delay=0.01, exceptions=(ValueError,))
        def raise_type_error():
            nonlocal call_count
            call_count += 1
            raise TypeError("not retried")

        with pytest.raises(TypeError):
            raise_type_error()
        assert call_count == 1  # 재시도 없음

    def test_on_retry_callback(self):
        """재시도 콜백 호출"""
        retry_calls = []

        def on_retry(exc, attempt):
            retry_calls.append((str(exc), attempt))

        @retry_on_exception(max_retries=2, delay=0.01, backoff=1.0, on_retry=on_retry)
        def fail_once():
            if len(retry_calls) == 0:
                raise ValueError("first fail")
            return "success"

        result = fail_once()
        assert result == "success"
        assert len(retry_calls) == 1
        assert retry_calls[0][1] == 1


class TestRetryRequest:
    """retry_request 함수 테스트"""

    def test_retry_request_success(self):
        """retry_request 성공"""
        def success():
            return "ok"

        result = retry_request(success, max_retries=2, delay=0.01)
        assert result == "ok"

    def test_retry_request_with_args(self):
        """retry_request 인자 전달"""
        def add(a, b):
            return a + b

        result = retry_request(add, 2, 3, max_retries=2, delay=0.01)
        assert result == 5

    def test_retry_request_eventual_success(self):
        """retry_request 재시도 후 성공"""
        attempt = [0]

        def eventual_success():
            attempt[0] += 1
            if attempt[0] < 2:
                raise ValueError("not yet")
            return "done"

        result = retry_request(eventual_success, max_retries=3, delay=0.01, backoff=1.0)
        assert result == "done"
        assert attempt[0] == 2
