import pytest
from unittest.mock import MagicMock
from parser.main import YandexMapsParser
from parser.classes import Review

class TestYandexMapsParser:
    """Test suite for the YandexMapsParser functionality"""
    
    def test_initialization(self, mock_driver):
        """Test parser initialization with mock driver"""
        parser = YandexMapsParser(mock_driver)
        assert parser.driver == mock_driver
        assert parser.reviews == []
        
    def test_load_page(self, mock_driver):
        """Test page loading functionality"""
        parser = YandexMapsParser(mock_driver)
        org_id = "12345"
        
        parser.load_page(org_id)
        
        mock_driver.get.assert_called_once()
        assert "12345" in mock_driver.get.call_args[0][0]
        
    def test_parse_review(self, mock_driver, sample_review_element):
        """Test single review parsing"""
        parser = YandexMapsParser(mock_driver)
        
        # Configure mock element return values to match Review class expectations
        mock_author = MagicMock()
        mock_author.text = "Test User"
        mock_rating = MagicMock()
        mock_rating.get_attribute.return_value = "4"
        mock_rating.text = "4 stars"
        
        sample_review_element.find_element.return_value = mock_author
        sample_review_element.find_elements.return_value = [mock_rating]
        
        review = parser._parse_review(sample_review_element)
        
        assert isinstance(review, Review)
        assert isinstance(review.author, dict)
        # Check the dictionary contains the expected value
        assert any("Test User" in val for val in review.author.values())
        assert review.review_rating == 4  # Using the actual attribute name
        
    @pytest.mark.integration
    def test_integration_with_live_driver(self, live_driver):
        """Integration test with real WebDriver (marked for manual run)"""
        parser = YandexMapsParser(live_driver)
        # This test would need actual test organization ID
        # parser.load_page("test_org_id")
        # assert len(parser.reviews) > 0
        pass  # Implementation would require test credentials