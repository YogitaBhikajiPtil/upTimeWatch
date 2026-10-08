from app import alerts, checker


def test_register_login_and_me(client):
    r = client.post("/api/auth/register", json={"email": "Bob@Example.com", "password": "password123"})
    assert r.status_code == 201

    dup = client.post("/api/auth/register", json={"email": "bob@example.com", "password": "password123"})
    assert dup.status_code == 409  # emails are normalised to lowercase

    bad = client.post("/api/auth/login", json={"email": "bob@example.com", "password": "wrongpass1"})
    assert bad.status_code == 401

    ok = client.post("/api/auth/login", json={"email": "bob@example.com", "password": "password123"})
    token = ok.json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["email"] == "bob@example.com"


def test_requires_auth(client):
    assert client.get("/api/monitors").status_code == 401


def test_create_list_update_delete(client, auth_headers):
    r = client.post(
        "/api/monitors", headers=auth_headers,
        json={"name": "Local", "url": "http://127.0.0.1:9", "interval_seconds": 60},
    )
    assert r.status_code == 201
    mid = r.json()["id"]

    assert len(client.get("/api/monitors", headers=auth_headers).json()) == 1

    r = client.patch(f"/api/monitors/{mid}", headers=auth_headers, json={"is_active": False})
    assert r.json()["is_active"] is False

    assert client.delete(f"/api/monitors/{mid}", headers=auth_headers).status_code == 204
    assert client.get("/api/monitors", headers=auth_headers).json() == []


def test_users_cannot_see_each_others_monitors(client, auth_headers):
    mid = client.post(
        "/api/monitors", headers=auth_headers, json={"name": "Mine", "url": "http://127.0.0.1:9"}
    ).json()["id"]

    other = client.post("/api/auth/register", json={"email": "b@example.com", "password": "password123"})
    other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}

    assert client.get("/api/monitors", headers=other_headers).json() == []
    assert client.delete(f"/api/monitors/{mid}", headers=other_headers).status_code == 404


def test_rejects_bad_urls(client, auth_headers):
    r = client.post("/api/monitors", headers=auth_headers, json={"name": "x", "url": "ftp://example.com"})
    assert r.status_code == 400


def test_private_urls_blocked_by_default(monkeypatch):
    monkeypatch.setattr(checker.settings, "allow_private_urls", False)
    assert checker.validate_url("http://127.0.0.1:8000") == "Private or internal addresses are not allowed"


def test_check_now_and_uptime(client, auth_headers, fake_fetch):
    mid = client.post(
        "/api/monitors", headers=auth_headers, json={"name": "Site", "url": "http://127.0.0.1:9"}
    ).json()["id"]

    r = client.post(f"/api/monitors/{mid}/check", headers=auth_headers)
    assert r.json()["is_up"] is True

    monitor = client.get("/api/monitors", headers=auth_headers).json()[0]
    assert monitor["status"] == "up"
    assert monitor["uptime_24h"] == 100.0
    assert monitor["last_response_ms"] == 25


def test_down_after_threshold_sends_one_alert(client, auth_headers, fake_fetch, monkeypatch):
    sent = []
    monkeypatch.setattr(checker, "send_alert", lambda *args: sent.append(args))

    mid = client.post(
        "/api/monitors", headers=auth_headers, json={"name": "Site", "url": "http://127.0.0.1:9"}
    ).json()["id"]
    client.post(f"/api/monitors/{mid}/check", headers=auth_headers)  # up

    fake_fetch["result"] = (None, None, "Timed out")
    client.post(f"/api/monitors/{mid}/check", headers=auth_headers)  # failure 1 -> still up
    assert client.get("/api/monitors", headers=auth_headers).json()[0]["status"] == "up"
    assert sent == []

    client.post(f"/api/monitors/{mid}/check", headers=auth_headers)  # failure 2 -> down
    assert client.get("/api/monitors", headers=auth_headers).json()[0]["status"] == "down"
    assert len(sent) == 1 and sent[0][2] == "down"

    client.post(f"/api/monitors/{mid}/check", headers=auth_headers)  # still down -> no new alert
    assert len(sent) == 1


def test_results_history(client, auth_headers, fake_fetch):
    mid = client.post(
        "/api/monitors", headers=auth_headers, json={"name": "Site", "url": "http://127.0.0.1:9"}
    ).json()["id"]
    for _ in range(3):
        client.post(f"/api/monitors/{mid}/check", headers=auth_headers)
    results = client.get(f"/api/monitors/{mid}/results", headers=auth_headers).json()
    assert len(results) == 3
    assert results[0]["checked_at"].endswith("Z")
