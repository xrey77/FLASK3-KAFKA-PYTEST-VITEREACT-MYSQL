import json
import pytest # type: ignore
from unittest.mock import patch, MagicMock
from config import create_app
from config.extensions import db
from app.auth.login import api_signin

@patch('app.auth.login.producer') # Mock the instance created in login.py
@patch('app.services.auth_service.authenticate_user')
def test_user_login_success(mock_auth, mock_producer, client):

    # 1. Setup Mock for Authentication Service
    mock_auth.return_value = (None, {
        "id": 1,
        "email": "rey@yahoo.com",
        "username": "Rey"
    })

    # 2. Define the payload
    login_payload = {
        "username": "Rey",
        "password": "rey"
    }

    # 3. Make the request to the Blueprint route
    response = client.post('/auth/signin', json=login_payload)

    # print(response.get_json())     

    # 4. Assertions
    assert response.status_code == 200
    data = response.get_json()
    assert data['username'] == "Rey"
    assert data['email'] == "rey@yahoo.com"

    # # 5. Verify Kafka Producer was called
    mock_producer.produce.assert_called_once()
    args, kwargs = mock_producer.produce.call_args
    assert args[0] == 'central-topic'
    assert b'user_login' in kwargs['value']

