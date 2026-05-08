import pytest # type: ignore
import json
from unittest.mock import MagicMock, patch
from flask_jwt_extended import create_access_token # type: ignore
from config import create_app 

@pytest.fixture
def client():
    app = create_app()
    app.config['JWT_SECRET_KEY'] = 'test-secret'
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def auth_header(client):
    access_token = create_access_token(identity='123')
    return {'Authorization': f'Bearer {access_token}'}

@patch('app.users.updateprofile.producer')
def test_update_profile_success(mock_producer, client, auth_header):
    mock_producer.produce = MagicMock()
    mock_producer.flush = MagicMock()

    with patch('app.users.updateprofile.update_user_profile') as mock_service:
        mock_service.return_value = True
        
        # 3. Make the PATCH request
        user_id = 1
        payload = {"name": "New Name", "bio": "Updated bio"}
        response = client.patch(
            f'/api/updateprofile/{user_id}',
            json=payload,
            headers=auth_header
        )
        
        # 4. Assertions
        assert response.status_code == 200
        assert response.json['message'] == "Your profile info has been updated."
        
        # Verify Kafka produce was called
        mock_producer.produce.assert_called_once()
        args, kwargs = mock_producer.produce.call_args
        assert args[0] == 'central-topic'
        assert b'user_profile_update' in kwargs['value']
        
        mock_producer.flush.assert_called_once()

@patch('app.users.updateprofile.producer')
def test_update_profile_failure(mock_producer, client, auth_header):
    # Setup mock to raise exception
    with patch('app.users.updateprofile.update_user_profile') as mock_service:
        mock_service.side_effect = Exception("Database failure")
        
        response = client.patch(
            '/api/updateprofile/1',
            json={"name": "Fail"},
            headers=auth_header
        )
        
        # Assertions
        assert response.status_code == 400
        assert "Database failure" in response.json['message']
        mock_producer.flush.assert_not_called()
