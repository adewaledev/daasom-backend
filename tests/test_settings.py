from datetime import timedelta

import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from config import settings as project_settings


def test_session_timeout_is_one_hour_of_inactivity():
    assert settings.SESSION_COOKIE_AGE == 60 * 60
    assert settings.SESSION_SAVE_EVERY_REQUEST is True


def test_jwt_access_token_lifetime_is_one_hour():
    assert settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] == timedelta(hours=1)


def test_jwt_security_settings_are_enabled():
    assert settings.SIMPLE_JWT["ROTATE_REFRESH_TOKENS"] is True
    assert settings.SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"] is True
    assert settings.SIMPLE_JWT["CHECK_REVOKE_TOKEN"] is True
    assert "rest_framework_simplejwt.token_blacklist" in settings.INSTALLED_APPS
    assert settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["auth_login"] == "10/min"


def test_validate_secret_key_requires_env_in_production():
    with pytest.raises(ImproperlyConfigured):
        project_settings.validate_secret_key(
            project_settings.DEFAULT_DEV_SECRET_KEY,
            False,
            ["manage.py", "runserver"],
        )


def test_validate_secret_key_allows_debug_and_pytest():
    project_settings.validate_secret_key(
        project_settings.DEFAULT_DEV_SECRET_KEY,
        True,
        ["manage.py", "runserver"],
    )
    project_settings.validate_secret_key(
        project_settings.DEFAULT_DEV_SECRET_KEY,
        False,
        ["pytest", "tests/test_settings.py"],
    )
