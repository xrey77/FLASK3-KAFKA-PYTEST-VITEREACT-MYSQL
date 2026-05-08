import json
import pytest # type: ignore
from unittest.mock import MagicMock, patch
from flask_jwt_extended import create_access_token # type: ignore
from config import create_app 
from app.models.user import Users
from werkzeug.exceptions import NotFound # type: ignore

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "JWT_SECRET_KEY": "super-secret-key" # Required for JWT
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def auth_header(client, app):
    with app.app_context():
        access_token = create_access_token(identity='123')
        return {"Authorization": f"Bearer {access_token}"}
    

def test_change_password_success(client, auth_header, app):
    mock_user = Users(id=1, username="testuser")
    
    with app.app_context():
     with patch('app.users.changepassword.db.get_or_404') as mock_get_or_404, \
         patch('app.users.changepassword.db.session.commit') as mock_commit, \
         patch('app.users.changepassword.producer') as mock_producer:
        
        mock_get_or_404.return_value = mock_user
        mock_producer.produce = MagicMock()
        
        # 4. Make Request
        response = client.patch(
            '/api/changepassword/1',
            data=json.dumps({'password': 'newpassword123'}),
            content_type='application/json',
            headers=auth_header
        )

        # 5. Assertions
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'You have change your password successfully.'
        
        # Verify DB changes
        assert mock_user.password is not None
        mock_commit.assert_called_once()
        
        # Verify Kafka production
        mock_producer.produce.assert_called_once()
        args, _ = mock_producer.produce.call_args
        assert args[0] == 'central-topic'
        assert response.status_code == 200
        assert response.json['message'] == "You have change your password successfully."


def test_change_password_user_not_found(client, auth_header, app):
    with app.app_context():
     with patch('app.users.changepassword.db.get_or_404') as mock_get_or_404:
        mock_get_or_404.side_effect = NotFound()                
        response = client.patch(
            '/api/changepassword/999',
            data=json.dumps({'password': 'newpassword123'}),
            content_type='application/json',
            headers=auth_header
        )
        
        assert response.status_code == 404
