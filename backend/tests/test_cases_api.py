import pytest
from app.models import case as case_dao
from app.models import operator as operator_dao
from app.models import message as message_dao


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


@pytest.fixture
def sample_cases(app):
    with app.app_context():
        c1 = case_dao.create('user1', 'tow_truck')
        c2 = case_dao.create('user2', 'body_shop')
        case_dao.update(c2.id, status='pending_review')
        return c1, c2


def test_list_cases(client, admin_token, sample_cases):
    response = client.get('/api/cases/', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['cases']) == 2


def test_filter_cases_by_status(client, admin_token, sample_cases):
    response = client.get('/api/cases/?status=collecting_info', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['cases']) == 1
    assert data['cases'][0]['status'] == 'collecting_info'


def test_get_case(app, client, admin_token, sample_cases):
    c1, _ = sample_cases
    with app.app_context():
        message_dao.create('user1', 'inbound', 'Help!', case_id=c1.id)

    response = client.get(f'/api/cases/{c1.id}', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['case']['id'] == c1.id
    assert 'messages' in data
    assert 'notes' in data
    assert len(data['messages']) == 1


def test_get_case_404(client, admin_token):
    response = client.get('/api/cases/9999', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    assert response.status_code == 404


def test_update_case(client, admin_token, sample_cases):
    c1, _ = sample_cases
    response = client.patch(f'/api/cases/{c1.id}',
        json={'customer_name': 'Updated Name', 'status': 'assigned'},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['customer_name'] == 'Updated Name'
    assert data['status'] == 'assigned'


def test_update_invalid_field(client, admin_token, sample_cases):
    c1, _ = sample_cases
    response = client.patch(f'/api/cases/{c1.id}',
        json={'invalid_field': 'value'},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 400


def test_add_note(client, admin_token, sample_cases):
    c1, _ = sample_cases
    response = client.post(f'/api/cases/{c1.id}/notes',
        json={'note': 'Customer called again'},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['note'] == 'Customer called again'


def test_auth_required(client, sample_cases):
    response = client.get('/api/cases/')
    assert response.status_code == 401


def test_update_case_404(client, admin_token):
    response = client.patch('/api/cases/9999',
        json={'status': 'assigned'},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 404
