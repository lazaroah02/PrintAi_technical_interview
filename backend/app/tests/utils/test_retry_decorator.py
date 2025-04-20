import pytest
from unittest.mock import patch, call
from app.scraping.scrape_books import retry


# Dummy function to use with the decorator
@retry(max_attempts=3, delay=1)
def dummy_function(should_fail: bool):
    if should_fail:
        raise Exception("Function failed")
    return "Success"


# 1. Test Successful Execution (no retries)
def test_retry_decorator_success():
    result = dummy_function(should_fail=False)
    # Function should complete successfully
    assert result == "Success"
    # Ensure the decorator didn't change the function name
    assert dummy_function.__name__ == "dummy_function"


# 2. Test Retrying on Failure (retries a set number of times)
@patch("time.sleep", return_value=None)  # Mocking time.sleep to avoid delays
def test_retry_decorator_retry(mock_sleep):
    with patch("app.scraping.scrape_books.logging.warning") as mock_warning:
        with pytest.raises(Exception):
            dummy_function(should_fail=True)

        # Check that the function retried 3 times
        # 3 retry attempts, one for each failure
        assert mock_warning.call_count == 3
        assert "Attempt 1 failed" in str(mock_warning.call_args_list[0])
        assert "Attempt 2 failed" in str(mock_warning.call_args_list[1])
        assert "Attempt 3 failed" in str(mock_warning.call_args_list[2])


# 3. Test Max Retries Reached (final failure)
@patch("time.sleep", return_value=None)
def test_retry_decorator_max_retries(mock_sleep):
    with patch("app.scraping.scrape_books.logging.error") as mock_error:
        with pytest.raises(Exception):
            dummy_function(should_fail=True)

        # Ensure the error is logged after the max retries are reached
        assert mock_error.call_count == 1
        assert "Max retries reached. Giving up." in str(
            mock_error.call_args[0][0]
            )


# 4. Test Retry Delay (check if sleep occurs between retries)
@patch("time.sleep", return_value=None)
def test_retry_decorator_delay(mock_sleep):
    try:
        dummy_function(should_fail=True)
    except Exception:
        pass  # Expecting an exception after retries

    # Ensure that the sleep function was called 2 times
    # (after the 1st and 2nd attempt)
    assert mock_sleep.call_count == 2
    assert mock_sleep.call_args_list[0] == call(1)  # delay of 1 second
    assert mock_sleep.call_args_list[1] == call(1)  # delay of 1 second


# 5. Test Logging Warnings on Retry (logging on each retry attempt)
@patch("time.sleep", return_value=None)
@patch("app.scraping.scrape_books.logging.warning")  # Mocking logging.warning
def test_retry_decorator_logging_warning(mock_warning, mock_sleep):
    with pytest.raises(Exception):
        dummy_function(should_fail=True)

    # Ensure warnings are logged for each failed attempt
    assert mock_warning.call_count == 3  # One warning for each attempt
    assert "Attempt 1 failed" in str(mock_warning.call_args_list[0][0])
    assert "Attempt 2 failed" in str(mock_warning.call_args_list[1][0])
    assert "Attempt 3 failed" in str(mock_warning.call_args_list[2][0])


# 6. Test No Retry on Immediate Success
@patch("time.sleep", return_value=None)
def test_retry_decorator_no_retry_on_success(mock_sleep):
    result = dummy_function(should_fail=False)

    # Ensure the function was executed once and not retried
    assert result == "Success"
    # No delay should be introduced for a successful execution
    assert mock_sleep.call_count == 0
