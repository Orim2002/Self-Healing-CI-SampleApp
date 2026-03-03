import pytest
import app as app_module
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def reset_state():
    app_module.is_healthy = True
    app_module.total_requests = 0
    app_module.total_errors = 0
    yield

def test_health_returns_200(client):
    response = client.get('/health')
    assert response.status_code == 200

def test_health_returns_metrics(client):
    response = client.get('/health')
    data = response.get_json()
    assert 'status' in data
    assert 'total_requests' in data
    assert 'error_rate' in data

def test_fail_activates_failure_mode(client):
    client.get('/fail')
    response = client.get('/health')
    assert response.status_code == 503

def test_recover_restores_health(client):
    client.get('/fail')
    client.get('/recover')
    response = client.get('/health')
    assert response.status_code == 200