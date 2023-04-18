import pytest


@pytest.mark.django_db
class TestUserModel:
    def test_email_user(self, user):
        assert user.email_user('subject', 'message')

    def test_is_active(self, user):
        user.active = True
        assert user.is_active

    def test_is_staff(self, user):
        user.staff = True
        assert user.is_staff

    def test_is_admin(self, user):
        user.admin = True
        assert user.is_admin

    def test_str(self, user):
        assert str(user) == user.username
