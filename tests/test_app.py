import os
os.environ['SECRET_KEY']='test-secret'
from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

def test_health():
    r=client.get('/health'); assert r.status_code==200; assert r.json()['status']=='ok'

def test_register_and_home():
    email='test@example.com'
    client.post('/api/register',json={'name':'Test User','email':email,'password':'secret123'})
    r=client.post('/api/login',json={'email':email,'password':'secret123'})
    assert r.status_code==200
    token=r.json()['access_token']
    r=client.post('/api/generate-home',headers={'Authorization':'Bearer '+token},json={'budget':50000,'rooms':['Living Room'],'style':'Modern','items':{},'notes':''})
    assert r.status_code==200
    assert r.json()['planner']=='home'
