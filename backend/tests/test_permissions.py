from uuid import uuid4

from app.models.user import User
from app.services.permissions import ensure_school_access


def test_admin_can_access_any_school():
    user = User(name="Admin", email="admin@test.com", password_hash="x", role="admin")
    ensure_school_access(user, uuid4())

