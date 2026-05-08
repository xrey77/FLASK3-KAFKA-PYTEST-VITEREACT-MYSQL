import json
import pytest # type: ignore
from flask_jwt_extended import create_access_token # type: ignore
from unittest.mock import MagicMock, patch
from flask import Flask # type: ignore
from config import create_app
from confluent_kafka import Producer # type: ignore
 
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

def test_mfa_activation_success(mocker, mock_producer, auth_header, client):

    mock_producer.poll = MagicMock() 
    mock_producer.return_value = mock_producer

    mock_mfa_service = mocker.patch('app.auth.mfa_activate.mfa_activation')
    mock_producer = mocker.patch('app.auth.mfa_activate.producer')
    
    mock_mfa_service.return_value = {
        "enabled": True, 
        "qrcodeurl": "otpauth://test",
        "message": "Enabled"
    }
    
    
    user_id = '123'
    response = client.patch(
        f'/auth/mfa/activate/{user_id}',
        json={"user_id": user_id ,"TwoFactorEnabled": True},
        headers=auth_header        
    )
    
    assert response.status_code == 200
    assert "qrcodeurl" in response.json

    mock_producer.produce.assert_called_once()
    mock_producer.produce.assert_called()
    mock_producer.flush.assert_called()

    args, kwargs = mock_producer.produce.call_args
    assert args[0] == 'central-topic'
    assert b'user_activate_mfa' in kwargs['value']
    
    mock_producer.flush.assert_called_once()


def test_mfa_activate_no_token(client):
    response = client.patch('/auth/mfa/activate/1', json={"TwoFactorEnabled": True})
    assert response.status_code == 401
