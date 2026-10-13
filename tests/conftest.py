import pytest
import os
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine
from app.core.rate_limit import limiter


#auto cleanup after every test
@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)   
    Base.metadata.create_all(bind=engine) 
    yield
    Base.metadata.drop_all(bind=engine)

#disabling rate limiting for test
@pytest.fixture(autouse=True)
def disable_rate_limit():
    limiter.enabled = False
    yield
    limiter.enabled = True

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def auth_headers(client):
    
    client.post("/auth/register", json={
        "email": "xyz@gmail.com",
        "password": "xyz123"
    })
    
    response = client.post("/auth/login", json={
        "email": "xyz@gmail.com",
        "password": "xyz123"
    })

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}





    
