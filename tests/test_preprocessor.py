"""Tests for text preprocessing module."""

import pytest

from sentiment_analyser.models.preprocessing import TextPreprocessor


class TestTextPreprocessor:
    """Test TextPreprocessor class."""
    
    def test_lowercase_conversion(self):
        """Test that text is converted to lowercase."""
        preprocessor = TextPreprocessor(lowercase=True)
        text = "HELLO World"
        result = preprocessor.clean(text)
        assert result == "hello world"
    
    def test_url_removal(self):
        """Test URL removal from text."""
        preprocessor = TextPreprocessor(remove_urls=True)
        text = "Check this out https://example.com amazing!"
        result = preprocessor.clean(text)
        assert "https://example.com" not in result
        assert "Check this out" in result.lower()
    
    def test_mention_removal(self):
        """Test @mention removal."""
        preprocessor = TextPreprocessor(remove_mentions=True)
        text = "Hey @user how are you?"
        result = preprocessor.clean(text)
        assert "@user" not in result
        assert "hey" in result.lower()
    
    def test_hashtag_removal(self):
        """Test #hashtag removal."""
        preprocessor = TextPreprocessor(remove_hashtags=True)
        text = "Great day! #python #coding"
        result = preprocessor.clean(text)
        assert "#python" not in result
        assert "#coding" not in result
    
    def test_whitespace_normalization(self):
        """Test extra whitespace removal."""
        preprocessor = TextPreprocessor(remove_extra_whitespace=True)
        text = "Too    many     spaces"
        result = preprocessor.clean(text)
        assert "  " not in result
    
    def test_batch_processing(self):
        """Test batch text processing."""
        preprocessor = TextPreprocessor(lowercase=True)
        texts = ["Hello", "WORLD", "Test"]
        results = preprocessor.clean_batch(texts)
        assert results == ["hello", "world", "test"]
    
    def test_extract_hashtags(self):
        """Test hashtag extraction."""
        preprocessor = TextPreprocessor()
        text = "Love #python and #machinelearning"
        hashtags = preprocessor.extract_hashtags(text)
        assert "python" in hashtags
        assert "machinelearning" in hashtags
        assert len(hashtags) == 2
    
    def test_extract_mentions(self):
        """Test mention extraction."""
        preprocessor = TextPreprocessor()
        text = "Thanks @alice and @bob!"
        mentions = preprocessor.extract_mentions(text)
        assert "alice" in mentions
        assert "bob" in mentions
        assert len(mentions) == 2
    
    def test_extract_urls(self):
        """Test URL extraction."""
        preprocessor = TextPreprocessor()
        text = "Visit https://example.com or http://test.org"
        urls = preprocessor.extract_urls(text)
        assert len(urls) == 2
        assert any("example.com" in url for url in urls)
    
    def test_empty_text(self):
        """Test handling of empty text."""
        preprocessor = TextPreprocessor()
        assert preprocessor.clean("") == ""
        assert preprocessor.clean("   ") == ""
    
    def test_combined_cleaning(self):
        """Test multiple cleaning operations together."""
        preprocessor = TextPreprocessor(
            lowercase=True,
            remove_urls=True,
            remove_mentions=True,
            remove_hashtags=True,
            remove_extra_whitespace=True
        )
        text = "Hey @user check https://example.com #awesome"
        result = preprocessor.clean(text)
        assert "@user" not in result
        assert "https://example.com" not in result
        assert "#awesome" not in result
        assert result == "hey check"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
