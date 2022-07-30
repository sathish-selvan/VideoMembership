import pytest
from app.users.models import User
from app import db


@pytest.fixture(scope='module')
def setup():
    session = db.get_session()
    yield session
    q = User.objects.filter(email="test@test.com")
    if q.count() != 0:
        q.delete()
    session.shutdown()

def test_user(setup):
    user = User.create_user(email="test@test.com", password='abc123')


def test_duplicate_user(setup):
    with pytest.raises(Exception):
        User.create_user(email="test@test.com", password='abc123')


def test_invalid_email(setup):
    with pytest.raises(Exception):
        User.create_user(email="test@gmail", password="1234")

def test_validate_password(setup):
    q = User.objects.filter(email="test@test.com")
    assert q.count() == 1
    user_obj = q.first()
    assert user_obj.verify_password("abc123") == True
    assert user_obj.verify_password("abc12344") == False


