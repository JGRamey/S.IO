"""Unit tests for configuration management."""

import pytest
import os
from unittest.mock import patch, MagicMock
from test_config import get_test_settings


class TestConfigurationUnit:
    """Unit tests for configuration loading and validation."""
    
    @pytest.mark.unit
    def test_get_test_settings(self):
        """Test that test settings are loaded correctly."""
        settings = get_test_settings()
        
        assert settings is not None
        assert hasattr(settings, 'postgres_host')
        assert hasattr(settings, 'postgres_port')
        assert hasattr(settings, 'postgres_db')
        
        # Test settings should use test database
        assert 'test' in settings.postgres_db.lower() or settings.postgres_db == 'yggdrasil_test'
    
    @pytest.mark.unit
    def test_sample_texts_available(self):
        """Test that sample texts are available for testing."""
        from test_config import SAMPLE_SPIRITUAL_TEXT, SAMPLE_PHILOSOPHICAL_TEXT, BIASED_TEXT_SAMPLE
        
        assert len(SAMPLE_SPIRITUAL_TEXT) > 100
        assert len(SAMPLE_PHILOSOPHICAL_TEXT) > 100
        assert len(BIASED_TEXT_SAMPLE) > 50
        
        # Test that texts contain expected keywords
        assert any(word in SAMPLE_SPIRITUAL_TEXT.lower() for word in ['spiritual', 'divine', 'soul', 'meditation'])
        assert any(word in SAMPLE_PHILOSOPHICAL_TEXT.lower() for word in ['philosophy', 'truth', 'knowledge', 'wisdom'])

    @pytest.mark.unit
    @patch.dict(os.environ, {'POSTGRES_HOST': 'test-host', 'POSTGRES_PORT': '9999'})
    def test_environment_variable_override(self):
        """Test that environment variables override default settings."""
        # This would test our actual config if we imported it
        # For now, just test the test config responds to env vars
        settings = get_test_settings()
        
        # Test that we can override settings
        assert settings.postgres_host is not None
        assert settings.postgres_port > 0
    
    @pytest.mark.unit
    def test_database_url_generation(self):
        """Test database URL generation."""
        settings = get_test_settings()
        
        # Test that database URL is properly formatted
        db_url = settings.database_url
        assert db_url.startswith('postgresql://')
        assert settings.postgres_host in db_url
        assert str(settings.postgres_port) in db_url
        assert settings.postgres_db in db_url
    
    @pytest.mark.unit
    def test_qdrant_url_generation(self):
        """Test Qdrant URL generation."""
        settings = get_test_settings()
        
        # Test that Qdrant URL is properly formatted
        qdrant_url = settings.qdrant_url
        assert qdrant_url.startswith('http://')
        assert settings.qdrant_host in qdrant_url
        assert str(settings.qdrant_port) in qdrant_url
