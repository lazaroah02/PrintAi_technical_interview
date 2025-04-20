import logging
import pytest
from unittest.mock import MagicMock, patch
from selenium.common.exceptions import NoSuchElementException
from app.scraping.scrape_hn import go_to_next_page


# 1. Test when "More" link exists
@patch("time.sleep")
def test_go_to_next_page_success(mock_sleep):
    # Crear un mock del driver y del botón
    mock_driver = MagicMock()
    mock_more_link = MagicMock()

    # Simular que se encuentra el enlace y se puede hacer click
    mock_driver.find_element.return_value = mock_more_link

    # Llamar a la función
    result = go_to_next_page(mock_driver)

    # Aserciones
    mock_driver.find_element.assert_called_once_with("link text", "More")
    mock_more_link.click.assert_called_once()
    mock_sleep.assert_called_once_with(2)
    assert result is True


# 2. Test when "More" link is not found (NoSuchElementException)
def test_go_to_next_page_no_more_link(caplog):
    mock_driver = MagicMock()
    mock_driver.find_element.side_effect = NoSuchElementException

    with caplog.at_level(logging.INFO):
        result = go_to_next_page(mock_driver)

    assert result is False
    assert "No more pages to scrape." in caplog.text


# 3. Test that returns False on other exceptions (optional enhancement)
def test_go_to_next_page_other_exception():
    mock_driver = MagicMock()
    mock_driver.find_element.side_effect = Exception("Unexpected error")

    # Si no capturas errores generales, este test debe fallar
    with pytest.raises(Exception, match="Unexpected error"):
        go_to_next_page(mock_driver)
