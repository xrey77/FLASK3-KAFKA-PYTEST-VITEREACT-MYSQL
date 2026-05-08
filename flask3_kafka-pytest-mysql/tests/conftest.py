# tests/conftest.py
import pytest # type: ignore
from unittest.mock import MagicMock
import confluent_kafka  # type: ignore

@pytest.fixture
def mock_producer(mocker):
    """
    Mocks the confluent_kafka.Producer class.
    """
    # Patch the Producer class directly
    mock_prod = mocker.patch("confluent_kafka.Producer")
    
    # Create a mock instance
    instance = mock_prod.return_value
    
    # Mock the produce and flush methods
    instance.produce = MagicMock()
    instance.flush = MagicMock()
    
    return instance
