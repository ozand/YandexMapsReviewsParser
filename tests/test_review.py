import pytest
from datetime import datetime
from parser.classes import Review

class TestReview:
    """Test suite for the Review class functionality"""
    
    def test_review_initialization(self):
        """Test basic Review object creation"""
        test_data = {
            'author': 'Test User',
            'rating': 4,
            'date': '2025-04-15',
            'text': 'Sample review text',
            'likes': 5,
            'dislikes': 1
        }
        
        review = Review(**test_data)
        
        assert review.author == 'Test User'
        assert review.rating == 4
        assert review.date == '2025-04-15'
        assert review.text == 'Sample review text'
        assert review.likes == 5
        assert review.dislikes == 1
        
    def test_to_dict_method(self):
        """Test the to_dict serialization method"""
        test_data = {
            'author': 'Test User',
            'rating': 4,
            'date': '2025-04-15',
            'text': 'Sample review text',
            'likes': 5,
            'dislikes': 1
        }
        
        review = Review(**test_data)
        result = review.to_dict()
        
        assert isinstance(result, dict)
        assert result == test_data
        
    @pytest.mark.parametrize("rating,expected", [
        (1, "★☆☆☆☆"),
        (2, "★★☆☆☆"), 
        (3, "★★★☆☆"),
        (4, "★★★★☆"),
        (5, "★★★★★")
    ])
    def test_star_representation(self, rating, expected):
        """Test the star rating representation"""
        review = Review(author="Test", rating=rating, date="2025-01-01", text="Test")
        assert review.stars == expected