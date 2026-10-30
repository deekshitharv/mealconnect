from tests.helpers import auth_headers, hours, make_meal, make_user, meal_payload


# ---------- 1. Health ----------
def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# ---------- 2-6. Authentication ----------
def test_user_registration(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Asha Rao", "email": "Asha@Example.com", "password": "StrongPass123", "role": "USER"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "asha@example.com"  # lowercased
    assert body["role"] == "USER"
    assert "password" not in response.text


def test_duplicate_email_is_rejected(client):
    payload = {"name": "Asha Rao", "email": "asha@example.com", "password": "StrongPass123"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    assert client.post("/api/v1/auth/register", json=payload).status_code == 409


def test_register_validation_and_no_admin_signup(client):
    short = {"name": "Asha", "email": "a@example.com", "password": "abc"}
    assert client.post("/api/v1/auth/register", json=short).status_code == 422
    admin = {"name": "Sneaky", "email": "s@example.com", "password": "StrongPass123", "role": "ADMIN"}
    assert client.post("/api/v1/auth/register", json=admin).status_code == 422


def test_login_returns_token(client, db):
    make_user(db, "user@example.com")
    response = client.post("/api/v1/auth/login", json={"email": "user@example.com", "password": "StrongPass123"})
    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["user"]["email"] == "user@example.com"


def test_invalid_login_is_rejected(client, db):
    make_user(db, "user@example.com")
    wrong_password = client.post("/api/v1/auth/login", json={"email": "user@example.com", "password": "WrongPass999"})
    unknown_email = client.post("/api/v1/auth/login", json={"email": "nobody@example.com", "password": "StrongPass123"})
    assert wrong_password.status_code == 401
    assert unknown_email.status_code == 401


def test_authenticated_user_endpoint(client, db):
    make_user(db, "user@example.com")
    headers = auth_headers(client, "user@example.com")
    assert client.get("/api/v1/auth/me", headers=headers).json()["email"] == "user@example.com"
    assert client.get("/api/v1/auth/me").status_code == 401
    assert client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"}).status_code == 401


# ---------- 7-11. Meals ----------
def test_meal_creation(client, db, base):
    make_user(db, "provider@example.com", "PROVIDER")
    make_user(db, "user@example.com", "USER")
    payload = meal_payload(**base)

    created = client.post("/api/v1/meals", json=payload, headers=auth_headers(client, "provider@example.com"))
    assert created.status_code == 201
    assert created.json()["quantity"] == 10
    assert created.json()["display_status"] == "AVAILABLE"

    assert client.post("/api/v1/meals", json=payload).status_code == 401
    assert client.post("/api/v1/meals", json=payload, headers=auth_headers(client, "user@example.com")).status_code == 403


def test_meal_validation(client, db, base):
    make_user(db, "provider@example.com", "PROVIDER")
    headers = auth_headers(client, "provider@example.com")
    assert client.post("/api/v1/meals", json=meal_payload(**base, quantity=0), headers=headers).status_code == 422
    assert client.post("/api/v1/meals", json=meal_payload(**base, quantity=-3), headers=headers).status_code == 422
    past = meal_payload(**base, available_from=hours(-10).isoformat(), available_until=hours(-2).isoformat())
    assert client.post("/api/v1/meals", json=past, headers=headers).status_code == 422
    bad_category = meal_payload(base["category_id"] + 99, base["location_id"])
    assert client.post("/api/v1/meals", json=bad_category, headers=headers).status_code == 422


def test_meal_retrieval_search_and_pagination(client, db, base):
    provider = make_user(db, "provider@example.com", "PROVIDER")
    for name in ["Veg fried rice", "Lemon rice", "Paneer wrap"]:
        make_meal(db, provider.id, base["category_id"], base["location_id"], name=name)

    listing = client.get("/api/v1/meals")
    assert listing.status_code == 200
    assert listing.json()["total"] == 3

    assert client.get("/api/v1/meals?search=rice").json()["total"] == 2
    assert client.get("/api/v1/meals?category=Lunch").json()["total"] == 3
    assert client.get("/api/v1/meals?location=Bangalore").json()["total"] == 3
    assert client.get("/api/v1/meals?category=Bakery").json()["total"] == 0

    page = client.get("/api/v1/meals?limit=2&page=2").json()
    assert len(page["items"]) == 1
    assert page["total_pages"] == 2

    meal_id = listing.json()["items"][0]["id"]
    assert client.get(f"/api/v1/meals/{meal_id}").status_code == 200
    assert client.get("/api/v1/meals/999999").status_code == 404
    assert client.get("/api/v1/meals?limit=500").status_code == 422


def test_meal_update(client, db, base):
    provider = make_user(db, "provider@example.com", "PROVIDER")
    meal = make_meal(db, provider.id, base["category_id"], base["location_id"])
    headers = auth_headers(client, "provider@example.com")

    update = meal_payload(**base, name="Updated name", quantity=4)
    response = client.put(f"/api/v1/meals/{meal.id}", json=update, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated name"
    assert response.json()["quantity"] == 4


def test_unauthorized_meal_modification(client, db, base):
    owner = make_user(db, "provider@example.com", "PROVIDER")
    make_user(db, "other@example.com", "PROVIDER")
    make_user(db, "user@example.com", "USER")
    meal = make_meal(db, owner.id, base["category_id"], base["location_id"])
    update = meal_payload(**base, name="Hacked")

    other = auth_headers(client, "other@example.com")
    assert client.put(f"/api/v1/meals/{meal.id}", json=update, headers=other).status_code == 403
    assert client.delete(f"/api/v1/meals/{meal.id}", headers=other).status_code == 403

    user = auth_headers(client, "user@example.com")
    assert client.put(f"/api/v1/meals/{meal.id}", json=update, headers=user).status_code == 403
    assert client.get(f"/api/v1/meals/{meal.id}").json()["name"] == "Test meal"


def test_meal_deletion(client, db, base):
    provider = make_user(db, "provider@example.com", "PROVIDER")
    meal = make_meal(db, provider.id, base["category_id"], base["location_id"])
    headers = auth_headers(client, "provider@example.com")

    assert client.delete(f"/api/v1/meals/{meal.id}", headers=headers).status_code == 204
    assert client.get(f"/api/v1/meals/{meal.id}").status_code == 404


# ---------- 12-15. Reservations ----------
def test_reservation_reduces_quantity_and_fills_up(client, db, base):
    provider = make_user(db, "provider@example.com", "PROVIDER")
    make_user(db, "user1@example.com")
    make_user(db, "user2@example.com")
    meal = make_meal(db, provider.id, base["category_id"], base["location_id"], quantity=10)

    first = client.post(
        "/api/v1/reservations", json={"meal_id": meal.id, "quantity": 3}, headers=auth_headers(client, "user1@example.com")
    )
    assert first.status_code == 201
    assert first.json()["status"] == "RESERVED"
    assert client.get(f"/api/v1/meals/{meal.id}").json()["quantity"] == 7

    second = client.post(
        "/api/v1/reservations", json={"meal_id": meal.id, "quantity": 7}, headers=auth_headers(client, "user2@example.com")
    )
    assert second.status_code == 201
    after = client.get(f"/api/v1/meals/{meal.id}").json()
    assert after["quantity"] == 0
    assert after["status"] == "FULLY_RESERVED"

    third = client.post(
        "/api/v1/reservations", json={"meal_id": meal.id, "quantity": 1}, headers=auth_headers(client, "user1@example.com")
    )
    assert third.status_code == 409


def test_insufficient_quantity(client, db, base):
    provider = make_user(db, "provider@example.com", "PROVIDER")
    make_user(db, "user@example.com")
    meal = make_meal(db, provider.id, base["category_id"], base["location_id"], quantity=2)
    headers = auth_headers(client, "user@example.com")

    too_many = client.post("/api/v1/reservations", json={"meal_id": meal.id, "quantity": 5}, headers=headers)
    assert too_many.status_code == 409
    zero = client.post("/api/v1/reservations", json={"meal_id": meal.id, "quantity": 0}, headers=headers)
    assert zero.status_code == 422
    negative = client.post("/api/v1/reservations", json={"meal_id": meal.id, "quantity": -1}, headers=headers)
    assert negative.status_code == 422
    assert client.get(f"/api/v1/meals/{meal.id}").json()["quantity"] == 2  # unchanged


def test_expired_meal_cannot_be_reserved(client, db, base):
    provider = make_user(db, "provider@example.com", "PROVIDER")
    make_user(db, "user@example.com")
    expired = make_meal(db, provider.id, base["category_id"], base["location_id"], start_h=-10, end_h=-2)
    headers = auth_headers(client, "user@example.com")

    response = client.post("/api/v1/reservations", json={"meal_id": expired.id, "quantity": 1}, headers=headers)
    assert response.status_code == 409
    assert "expired" in response.json()["error"]["message"].lower()
    assert client.get(f"/api/v1/meals/{expired.id}").json()["display_status"] == "EXPIRED"


def test_reservation_cancellation_restores_quantity(client, db, base):
    provider = make_user(db, "provider@example.com", "PROVIDER")
    make_user(db, "user@example.com")
    make_user(db, "other@example.com")
    meal = make_meal(db, provider.id, base["category_id"], base["location_id"], quantity=5)
    headers = auth_headers(client, "user@example.com")

    reservation = client.post("/api/v1/reservations", json={"meal_id": meal.id, "quantity": 5}, headers=headers).json()
    assert client.get(f"/api/v1/meals/{meal.id}").json()["status"] == "FULLY_RESERVED"

    other = auth_headers(client, "other@example.com")
    assert client.put(f"/api/v1/reservations/{reservation['id']}/cancel", headers=other).status_code == 403

    cancelled = client.put(f"/api/v1/reservations/{reservation['id']}/cancel", headers=headers)
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "CANCELLED"
    assert cancelled.json()["cancelled_at"] is not None

    meal_after = client.get(f"/api/v1/meals/{meal.id}").json()
    assert meal_after["quantity"] == 5
    assert meal_after["status"] == "AVAILABLE"

    assert client.put(f"/api/v1/reservations/{reservation['id']}/cancel", headers=headers).status_code == 409


def test_provider_collects_reservation(client, db, base):
    provider = make_user(db, "provider@example.com", "PROVIDER")
    make_user(db, "other@example.com", "PROVIDER")
    make_user(db, "user@example.com")
    meal = make_meal(db, provider.id, base["category_id"], base["location_id"], quantity=5)
    user_headers = auth_headers(client, "user@example.com")
    reservation = client.post(
        "/api/v1/reservations", json={"meal_id": meal.id, "quantity": 2}, headers=user_headers
    ).json()
    url = f"/api/v1/reservations/{reservation['id']}/collect"

    assert client.put(url, headers=user_headers).status_code == 403                           # user cannot
    assert client.put(url, headers=auth_headers(client, "other@example.com")).status_code == 403  # other provider cannot

    collected = client.put(url, headers=auth_headers(client, "provider@example.com"))
    assert collected.status_code == 200
    assert collected.json()["status"] == "COLLECTED"
    assert collected.json()["collected_at"] is not None

    assert client.put(url, headers=auth_headers(client, "provider@example.com")).status_code == 409
    assert client.put(f"/api/v1/reservations/{reservation['id']}/cancel", headers=user_headers).status_code == 409


def test_reservation_visibility(client, db, base):
    provider = make_user(db, "provider@example.com", "PROVIDER")
    make_user(db, "user@example.com")
    make_user(db, "other@example.com")
    meal = make_meal(db, provider.id, base["category_id"], base["location_id"])
    reservation = client.post(
        "/api/v1/reservations", json={"meal_id": meal.id, "quantity": 1}, headers=auth_headers(client, "user@example.com")
    ).json()
    url = f"/api/v1/reservations/{reservation['id']}"

    assert client.get(url, headers=auth_headers(client, "user@example.com")).status_code == 200
    assert client.get(url, headers=auth_headers(client, "provider@example.com")).status_code == 200
    assert client.get(url, headers=auth_headers(client, "other@example.com")).status_code == 403
    assert client.get("/api/v1/reservations/999999", headers=auth_headers(client, "user@example.com")).status_code == 404

    mine = client.get("/api/v1/reservations/my", headers=auth_headers(client, "user@example.com")).json()
    assert mine["total"] == 1
    assert client.get("/api/v1/reservations/my", headers=auth_headers(client, "other@example.com")).json()["total"] == 0


# ---------- 16. Role authorization ----------
def test_role_authorization(client, db):
    make_user(db, "user@example.com", "USER")
    make_user(db, "provider@example.com", "PROVIDER")
    make_user(db, "admin@example.com", "ADMIN")
    user = auth_headers(client, "user@example.com")
    provider = auth_headers(client, "provider@example.com")
    admin = auth_headers(client, "admin@example.com")

    assert client.post("/api/v1/categories", json={"name": "Desserts"}, headers=user).status_code == 403
    assert client.post("/api/v1/categories", json={"name": "Desserts"}, headers=provider).status_code == 403
    assert client.post("/api/v1/categories", json={"name": "Desserts"}, headers=admin).status_code == 201
    assert client.post("/api/v1/categories", json={"name": "dessERTS"}, headers=admin).status_code == 409

    assert client.get("/api/v1/admin/stats", headers=user).status_code == 403
    assert client.get("/api/v1/admin/stats", headers=provider).status_code == 403
    assert client.get("/api/v1/admin/stats", headers=admin).status_code == 200
    assert client.get("/api/v1/admin/users", headers=user).status_code == 403
    assert client.get("/api/v1/provider/stats", headers=user).status_code == 403
    assert client.get("/api/v1/provider/stats", headers=provider).status_code == 200


def test_admin_can_manage_everything(client, db, base):
    provider = make_user(db, "provider@example.com", "PROVIDER")
    victim = make_user(db, "victim@example.com", "USER")
    admin_user = make_user(db, "admin@example.com", "ADMIN")
    meal = make_meal(db, provider.id, base["category_id"], base["location_id"])
    admin = auth_headers(client, "admin@example.com")

    stats = client.get("/api/v1/admin/stats", headers=admin).json()
    assert stats["total_users"] == 1
    assert stats["total_providers"] == 1
    assert stats["total_meals"] == 1

    providers_only = client.get("/api/v1/admin/users?role=PROVIDER", headers=admin).json()
    assert providers_only["total"] == 1

    assert client.delete(f"/api/v1/meals/{meal.id}", headers=admin).status_code == 204
    assert client.delete(f"/api/v1/admin/users/{victim.id}", headers=admin).status_code == 204
    assert client.delete(f"/api/v1/admin/users/{admin_user.id}", headers=admin).status_code == 409


def test_error_format_is_consistent(client):
    not_found = client.get("/api/v1/meals/999999").json()
    assert set(not_found["error"]) >= {"status", "type", "message"}
    invalid = client.post("/api/v1/auth/register", json={"name": "x"}).json()
    assert invalid["error"]["type"] == "validation_error"
    assert invalid["error"]["details"]