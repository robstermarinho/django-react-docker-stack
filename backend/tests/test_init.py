import pytest


@pytest.mark.django_db
def test_admin_user_creation(admin_user):
    assert admin_user.is_superuser


@pytest.mark.django_db
def test_user_creation(user):
    assert user.pk is not None
    assert user.email.endswith("@example.com")
    assert not user.is_superuser
