
def test_auth_register(client):
    response=client.post(
            "/auth/register",
            json={"email":"abc@gmail.com","password":"abc123"}
        )

    assert response.status_code==200

def test_auth_register_duplicate(client):
    client.post(
            "/auth/register",
            json={"email":"abc@gmail.com","password":"abc123"}
        )

    response=client.post(
            "/auth/register",
            json={"email":"abc@gmail.com","password":"abc123"}
        )

    assert response.status_code==401
    assert response.json()=={
        "detail": "User already exists!"
    }

def test_auth_login(client):
    reg=client.post(
                "/auth/register",
                json={"email":"xyzw@gmail.com","password":"xyzw123"}
            )
    # print("REGISTER:", reg.status_code, reg.json())
    response=client.post(
                "/auth/login",
                json={"email":"xyzw@gmail.com","password":"xyzw123"}
            )
    # print("LOGIN:", response.status_code, response.json())
    assert response.status_code==200
    
def test_auth_login_wrong_password(client):


    client.post(
        "/auth/register",
        json={
            "email": "abc@gmail.com",
            "password": "abc123"
        }
    )
    res=client.post(
                "/auth/login",
                json={"email":"abc@gmail.com","password":"wrongpassword"}
            )
    assert res.status_code==401
    assert res.json()=={
    "detail": "Invalid credentials"
    }

def test_auth_login_wrong_email(client):
    response=client.post(
        "/auth/login",
        json={
            "email":"nouserexists@gmail.com",
            "password":"xyz"
        }
    )

    assert response.status_code==401
    assert response.json()=={
        "detail": "Invalid credentials"
    }

def test_auth_refresh_token(client):
    client.post(
            "/auth/register",
            json={
                "email":"xyz@gmail.com",
                "password":"xyz"
            }
        )

    response=client.post(
                    "/auth/login",
                    json={"email":"xyz@gmail.com","password":"xyz"}
                )

    token=response.json()["refresh_token"]

    res=client.post(
        "/auth/refresh",
        json={
            "refresh_token":token
        }
        )

    assert res.status_code==200
    assert "access_token" in res.json()

def test_auth_logout(client):
    client.post(
                "/auth/register",
                json={
                    "email":"xyz@gmail.com",
                    "password":"xyz"
                }
            )
    
    response=client.post(
                        "/auth/login",
                        json={"email":"xyz@gmail.com","password":"xyz"}
                    )

    access_token=response.json()["access_token"]
    refresh_token=response.json()["refresh_token"]

    res=client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "refresh_token":refresh_token
        }
    )

    assert res.status_code==200
    assert res.json()=={
        "message": "Logged out successfully"
    }

    res = client.get("/api/v1/urls/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert res.status_code == 401

def test_auth_logout_invalid_token(client):
    res = client.post("/auth/logout",
        headers={"Authorization": "Bearer invalidtoken"},
        json={"refresh_token": "invalidtoken"}
    )
    assert res.status_code == 401

