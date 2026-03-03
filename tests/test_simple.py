import pytest
from unittest.mock import patch, MagicMock # MagicMock is used to create a mock object (dummy function) that can be used to replace a real function or method during testing.
mock_func = MagicMock()
import main # import the main module which contains the Flask app and its endpoints

main.READY = True
@pytest.fixture
# initiate a test/fake client which can be used to send requests to the Flask app. 
#This allows us to test the endpoints directly.
def client():
    main.app.config['TESTING'] = True
    with main.app.test_client() as client:
        yield client

# Test the /health endpoint can be used for monitoring health .
def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json["status"] == "ok"

# test the /startup endpoint before the app is ready
def test_startup_before_ready(client):
    main.READY = False
    resp = client.get("/startup")
    assert resp.status_code == 503
    assert resp.json["status"] == "starting"

# test the /startup endpoint after the app is ready
def test_startup_after_ready(client):
    with patch("main.init_app",mock_func): 
        main.READY = True
        resp = client.get("/startup")
        assert resp.status_code == 200
        assert resp.json["status"] == "started"

# test the /live endpoint to check if the app is alive and running
# cant add failure for not alive as no conditions for READY flag is added in main.py.
def test_live_probe(client):
    resp = client.get("/live")
    assert resp.status_code == 200
    assert resp.json["status"] == "alive"

# test the /ready endpoint when the app is ready to serve traffic
def test_ready_probe(client):
    main.READY = True
    resp = client.get("/ready")
    assert resp.status_code == 200
    assert resp.json["status"] == "ready"

# test the /ready endpoint when the app is not ready to serve traffic
def test_not_ready_probe(client):
    main.READY = False
    resp = client.get("/ready")
    assert resp.status_code == 503
    assert resp.json["status"] == "not ready"

# test the /<user> endpoint to fetch gists for a specific user from GitHub API
def test_user_gists(client):
     resp = client.get("/octocat")
     data=resp.json
     assert resp.status_code == 200
     assert data[0]["owner"]["id"] == 583231