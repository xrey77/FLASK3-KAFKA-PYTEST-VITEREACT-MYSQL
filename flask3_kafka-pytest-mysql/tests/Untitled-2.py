


#test/test_mfa_activation.py
import json
import pytest # type: ignore
from unittest.mock import MagicMock, patch
from flask_jwt_extended import create_access_token # type: ignore

with patch('confluent_kafka.Producer') as MockProducer:
    mock_producer_instance = MockProducer.return_value
    mock_producer_instance.produce = MagicMock()
    mock_producer_instance.flush = MagicMock()
    
    from config import create_app
    from app.auth.mfa_activate import api_mfa

@pytest.fixture
def app():
    app = create_app()
    app.config["JWT_SECRET_KEY"] = "super-secret-testing-key"    # app.register_blueprint(api_mfa)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    with client.application.app_context():
        token = create_access_token(identity="user123")
        return {"Authorization": f"Bearer {token}"}

def test_mfa_activate_success(client, auth_headers, mocker):
    mocker.patch(
        'app.auth.mfa_activate', 
        return_value={"enabled": True, "qrcodeurl": "otpauth://..."}
    )

    response = client.patch(
        '/auth/mfa/activate/1',
        data=json.dumps({"TwoFactorEnabled": True}),
        headers=auth_headers,
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Multi-Factor Authenticator has been enabled."
    assert "qrcodeurl" in data

    mock_producer_instance.produce.assert_called_once()
    args, kwargs = mock_producer_instance.produce.call_args
    assert args[0] == 'central-topic'
    payload = json.loads(args[1].decode('utf-8'))
    assert payload['event'] == 'user_activate_mfa'
    assert payload['user_id'] == 'user123'
    mock_producer_instance.flush.assert_called_once()

