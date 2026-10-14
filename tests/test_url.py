def test_url_shorten(client, auth_headers):
    res = client.post("/api/v1/urls/shorten",
        headers=auth_headers,
        json={"original_url": "https://google.com"}
    )
    assert res.status_code == 200
    assert "short_code" in res.json()

def test_url_shorten_duplicate(client,auth_headers):
    client.post("/api/v1/urls/shorten",
        headers=auth_headers,
        json={"original_url": "https://google.com"}
    )
    res=client.post("/api/v1/urls/shorten",
        headers=auth_headers,
        json={"original_url": "https://google.com"}
    )

    assert res.status_code==200

def test_url_shorten_without_auth(client):
    res=client.post("/api/v1/urls/shorten",
            json={"original_url": "https://google.com"}
        )
    assert res.status_code==401

def test_url_shorten_invalid_url(client,auth_headers):
    res=client.post(
        "/api/v1/urls/shorten",
        headers=auth_headers,
        json={"original_url": "invalid"}
        )
    assert res.status_code==422
    
def test_url_redirect(client, auth_headers):
    res = client.post("/api/v1/urls/shorten",
        headers=auth_headers,
        json={"original_url": "https://google.com"}
    )
    short_code = res.json()["short_code"]

    res = client.get(f"/api/v1/urls/{short_code}",
        follow_redirects=False
    )
    assert res.status_code == 307

def test_url_redirect_wrong_code(client,auth_headers):
    response=client.get(
        "/api/v1/urls/wrongcode123",
        headers=auth_headers
    )

    assert response.status_code==404

def test_url_analytics(client,auth_headers):
    res = client.post("/api/v1/urls/shorten",
        headers=auth_headers,
        json={"original_url": "https://google.com"}
    )
    short_code = res.json()["short_code"]

    res = client.get(f"/api/v1/urls/{short_code}/analytics",
        headers=auth_headers
    )
    assert res.status_code == 200
    assert "total_click" in res.json()
    assert "short_code" in res.json()
    assert "original_url" in res.json()

def test_url_delete(client,auth_headers):
    res = client.post("/api/v1/urls/shorten",
            headers=auth_headers,
            json={"original_url": "https://google.com"}
        )
    short_code = res.json()["short_code"]

    res=client.delete(f"api/v1/urls/{short_code}"
                  ,headers=auth_headers)
    assert res.status_code==200
    assert res.json()=={
        "message":"URL deactivated successfully!"
    }

    res = client.get(f"/api/v1/urls/{short_code}",
        follow_redirects=False
    )
    assert res.status_code == 404

def test_custom_alias(client, auth_headers):
    res = client.post("/api/v1/urls/shorten",
        headers=auth_headers,
        json={
            "original_url": "https://google.com",
            "custom_alias": "my-google"
        }
    )
    assert res.status_code == 200
    assert res.json()["short_code"] == "my-google"

def test_duplicate_alias(client,auth_headers):
    client.post("/api/v1/urls/shorten",
        headers=auth_headers,
        json={
            "original_url": "https://google.com",
            "custom_alias": "my-google"
        }
    )


    response=client.post("/api/v1/urls/shorten",
        headers=auth_headers,
        json={
            "original_url": "https://instagram.com",
            "custom_alias": "my-google"
        }
    )

    assert response.status_code==400
    assert response.json()=={
        "detail": "This alias is not available"
    }



