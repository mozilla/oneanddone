# This file contains settings that apply only while the test suite is
# running. If the setting value is important to your test, mock it
# instead of using this.

# Speed up tests.
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 60,
    },
}
