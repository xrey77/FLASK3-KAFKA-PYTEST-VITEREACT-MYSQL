import json
import pytest # type: ignore
from flask import Flask # type: ignore
from unittest.mock import MagicMock, patch
from config import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config.update({"TESTING": True})
    yield app


@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_header(app):
    from flask_jwt_extended import create_access_token # type: ignore
    with app.app_context():
        token = create_access_token(identity="123")
        return {"Authorization": f"Bearer {token}"}

def test_verify_otp_success(mocker, mock_producer, auth_header, client):
    
    mock_producer.poll = MagicMock() 
    mock_producer.return_value = mock_producer

    mock_mfa_service = mocker.patch('app.auth.mfa_verifyotp.verify_user_totp')
    mock_producer = mocker.patch('app.auth.mfa_verifyotp.producer')

    mock_mfa_service.return_value = {
        "otp": "123456",
        "username": "Batman",
        "message": "OTP code has been verified successfully."
    }

    user_id = '123'
    response = client.patch(
        f'/auth/mfa/verifytotp/{user_id}',
        json={"otp": "123456"},
        headers=auth_header
    )
    
    assert response.status_code == 200
    assert response.json['message'] == "OTP code has been verified successfully."
    assert response.json['username'] == "Batman"

    mock_producer.produce.assert_called_once()
    mock_producer.produce.assert_called()
    mock_producer.flush.assert_called()

    args, kwargs = mock_producer.produce.call_args
    assert args[0] == 'central-topic'
    assert b'user_mfa_verification' in kwargs['value']
    
    mock_producer.flush.assert_called_once()


def test_verify_otp_missing_data(mocker, mock_producer, auth_header, client):        
    response = client.patch(
        '/auth/mfa/verifytotp/123',
        json={"otp": ""}, 
        headers=auth_header
    )
    
    assert response.status_code == 400
    assert response.json['message'] == "OTP is required"
    
    mock_producer.produce.assert_not_called()

def test_verify_otp_unauthorized(client):
    response = client.patch('/auth/mfa/verifytotp/123', json={"otp": "123456"})
    assert response.status_code == 401
