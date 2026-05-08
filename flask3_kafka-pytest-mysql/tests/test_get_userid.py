# tests/test_get_userid.py
import pytest # type: ignore
import json
from unittest.mock import patch, MagicMock
from config.extensions import db
from flask_jwt_extended import create_access_token # type: ignore
from app.users.getid import api_getuserid
from config import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret'
    return app

@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client

def test_get_user_id_success(client, app):

    with patch('app.users.getid.producer') as mock_producer:    
      with patch('app.users.getid.UserService.get_user_by_id') as mock_get_user:
        mock_get_user.return_value = {
            "id": 1, 
            "email": "test@example.com", 
            "name": "Test User"
        }
        
        with app.app_context():
            token = create_access_token(identity="1")

        headers = {'Authorization': f'Bearer {token}'}

        response = client.get('/api/getuserid/1', headers=headers)

        assert response.status_code == 200
        assert response.json['email'] == "test@example.com"
        
        mock_producer.produce.assert_called_once()
        args, kwargs = mock_producer.produce.call_args
        assert args[0] == 'central-topic'
        assert b'user_get_id' in kwargs['value']


def test_get_user_id_not_found(client, app):
    with patch('app.users.getid.producer') as mock_producer:          
      with patch('app.users.getid.UserService.get_user_by_id') as mock_get_user:        

        mock_get_user.return_value = None 

        with app.app_context():
            token = create_access_token(identity="1")
        headers = {'Authorization': f'Bearer {token}'}        
        response = client.get(f'/api/getuserid/999', headers=headers)
        
        assert response.status_code == 404
        assert response.json['message'] == "User ID not found."
        mock_producer.produce.assert_not_called()
