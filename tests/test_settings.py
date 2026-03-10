from datetime import timedelta

from django.conf import settings


def test_session_timeout_is_one_hour_of_inactivity():
    assert settings.SESSION_COOKIE_AGE == 60 * 60
    assert settings.SESSION_SAVE_EVERY_REQUEST is True


def test_jwt_access_token_lifetime_is_one_hour():
    assert settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] == timedelta(hours=1)
