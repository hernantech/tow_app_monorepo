import pytest
from app.models import operator as operator_dao


@pytest.fixture
def admin_user(app):
    with app.app_context():
        return operator_dao.create('admin', 'admin123', 'Admin User', 'admin')


@pytest.fixture
def admin_token(client, admin_user):
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'admin123',
    })
    return response.get_json()['access_token']


def test_login_success(client, admin_user):
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'admin123',
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert data['operator']['username'] == 'admin'


def test_login_failure(client, admin_user):
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'wrongpassword',
    })
    assert response.status_code == 401


def test_me_with_token(client, admin_token):
    response = client.get('/api/auth/me', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['operator']['username'] == 'admin'


def test_me_without_token(client):
    response = client.get('/api/auth/me')
    assert response.status_code == 401


def test_register_as_admin(client, admin_token):
    response = client.post('/api/auth/register',
        json={
            'username': 'newoperator',
            'password': 'pass123',
            'full_name': 'New Operator',
            'role': 'operator',
        },
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['username'] == 'newoperator'
    assert data['role'] == 'operator'


def test_register_as_non_admin(app, client):
    with app.app_context():
        operator_dao.create('regular', 'pass123', 'Regular User', 'operator')

    # Login as regular user
    response = client.post('/api/auth/login', json={
        'username': 'regular',
        'password': 'pass123',
    })
    token = response.get_json()['access_token']

    # Try to register
    response = client.post('/api/auth/register',
        json={
            'username': 'another',
            'password': 'pass123',
            'full_name': 'Another User',
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 403


def test_register_duplicate_username(client, admin_token):
    # First registration
    client.post('/api/auth/register',
        json={
            'username': 'duplicate',
            'password': 'pass123',
            'full_name': 'First User',
        },
        headers={'Authorization': f'Bearer {admin_token}'}
    )

    # Second with same username
    response = client.post('/api/auth/register',
        json={
            'username': 'duplicate',
            'password': 'pass456',
            'full_name': 'Second User',
        },
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 409
