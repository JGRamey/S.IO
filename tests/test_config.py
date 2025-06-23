"""Test configuration for S.IO project."""

import os
from yggdrasil.config import settings

# Test Database Configuration
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    "postgresql://postgres:test_password@localhost:5431/yggdrasil_test"
)

TEST_QDRANT_URL = os.getenv(
    "TEST_QDRANT_URL",
    "http://localhost:6333"
)

# Override settings for testing
def get_test_settings():
    """Get settings configured for testing."""
    test_settings = settings.copy()
    test_settings.postgres_db = "yggdrasil_test"
    test_settings.debug = True
    test_settings.log_level = "DEBUG"
    return test_settings

# Test data
SAMPLE_SPIRITUAL_TEXT = """
In the beginning was the Word, and the Word was with God, and the Word was God.
This passage from John 1:1 has been interpreted many ways throughout history.
Some see it as evidence of the Trinity, while others interpret it differently.
"""

SAMPLE_PHILOSOPHICAL_TEXT = """
The unexamined life is not worth living. This famous quote from Socrates
challenges us to think deeply about our existence and purpose. However,
we must be careful not to fall into the trap of overthinking every aspect
of our lives to the point of paralysis.
"""

BIASED_TEXT_SAMPLE = """
Obviously, Western civilization represents the pinnacle of human achievement.
Any reasonable person can see that traditional Eastern philosophies are
primitive and outdated compared to our modern, scientific worldview.
"""
