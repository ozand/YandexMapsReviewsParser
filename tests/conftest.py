import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from unittest.mock import MagicMock

@pytest.fixture(scope="session")
def mock_driver():
    """Fixture providing a mocked WebDriver instance"""
    driver = MagicMock()
    driver.find_element.return_value = MagicMock()
    driver.find_elements.return_value = [MagicMock(), MagicMock()]
    return driver

@pytest.fixture(scope="session")
def live_driver():
    """Fixture providing a real WebDriver instance for integration tests"""
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    yield driver
    driver.quit()

@pytest.fixture
def sample_review_element():
    """Fixture providing a mock review element"""
    elem = MagicMock()
    elem.find_element.return_value = MagicMock()
    elem.find_elements.return_value = [MagicMock()]
    return elem