import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"
os.environ["JWT_SECRET"] = "test-secret"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.db.session import Base, get_db
from app.main import app
from app.models.entities import ApiVersion, MockApi, RequestLog, RequestSchema, ResponseTemplate, User
from app.core.security import hash_password


engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base.metadata.create_all(bind=engine)


def override_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db
client = TestClient(app)


def seed_api():
    db = TestingSessionLocal()
    db.query(RequestLog).delete()
    db.query(ResponseTemplate).delete()
    db.query(RequestSchema).delete()
    db.query(ApiVersion).delete()
    db.query(MockApi).delete()
    db.query(User).delete()
    user = User(email="dev@example.com", name="Dev", password_hash=hash_password("secret"))
    api = MockApi(owner=user, name="Users", method="GET", path="/users/{id}", visibility="public", auth_mode="none")
    version = ApiVersion(version="v1", is_default=True, response_delay_ms=0)
    version.request_schema = RequestSchema(query_schema={"type": "object"}, headers_schema=None, body_schema=None)
    version.response_templates = [
        ResponseTemplate(scenario="success", status_code=200, body={"id": 123, "name": "Ada"}, is_default=True),
        ResponseTemplate(scenario="not-found", status_code=404, body={"error": "Missing"}, is_default=False),
    ]
    api.versions.append(version)
    db.add(user)
    db.commit()
    db.close()


def test_dynamic_mock_returns_default_response():
    seed_api()
    response = client.get("/mock/users/123")
    assert response.status_code == 200
    assert response.json() == {"id": 123, "name": "Ada"}


def test_dynamic_mock_can_select_scenario():
    seed_api()
    response = client.get("/mock/users/123?scenario=not-found")
    assert response.status_code == 404
    assert response.json() == {"error": "Missing"}
