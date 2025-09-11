import pytest


@pytest.fixture
def admin_user(django_user_model, db):
    return django_user_model.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="admin123",
    )


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username="user",
        email="user@example.com",
        password="user123",
    )
