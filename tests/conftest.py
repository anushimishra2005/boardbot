import os

from api.core.config import settings


# Tests must always use the dedicated test database.
test_database_url = settings.database_url.rsplit("/", 1)[0] + "/boardbot_test"
settings.database_url = test_database_url