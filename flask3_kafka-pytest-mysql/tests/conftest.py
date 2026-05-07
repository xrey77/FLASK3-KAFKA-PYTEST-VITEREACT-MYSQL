# tests/conftest.py
import pytest # type: ignore
from run import app as flask_app  # Import your actual app instance

@pytest.fixture(scope="module")
def app():
    # Set testing mode to True to enable error propagation and other test features
    flask_app.config.update({
        "TESTING": True,
    })
    
    # Optional: setup code (e.g., database creation) goes here
    
    yield flask_app
    
    # Optional: teardown code (e.g., clearing database) goes here

@pytest.fixture(scope="module")
def client(app):
    """A test client for the app."""
    return app.test_client()
