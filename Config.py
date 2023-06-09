import os
from typing import get_type_hints, Union
from dotenv import load_dotenv

load_dotenv()


class AppConfigError(Exception):
    pass


def _parse_bool(val: Union[str, bool]) -> bool:  # pylint: disable=E1136
    return val if type(val) == bool else val.lower() in ['true', 'yes', '1']


# AppConfig class with required fields, default values, type checking, and typecasting for int and bool values
class AppConfig:
    DEBUG: bool = False
    SECRET_KEY: str = ''
    ALLOWED_HOSTS: str = ''
    DB_HOST_IP: str = ''
    DB_HOST_PORT: int = 0
    DB_NAME: str = ''
    DB_USER: str = ''
    DB_PASSWORD: str = ''
    GLOBAL_SITE_NAME: str = ''
    SERVER_TIMEZONE: str = ''
    LIVE_SITE_OPEN: bool = False
    EMAIL_BACKEND: str = ''
    EMAIL_USE_TLS: bool = False
    EMAIL_HOST: str = ''
    EMAIL_HOST_USER: str = ''
    EMAIL_HOST_PASSWORD: str = ''
    EMAIL_PORT = 587
    AWS_ACCESS_KEY_ID: str = ''
    AWS_SECRET_ACCESS_KEY: str = ''
    AWS_STORAGE_BUCKET_NAME: str = ''
    AWS_S3_ENDPOINT_URL: str = ''
    AWS_LOCATION: str = ''


    """
    Map environment variables to class fields according to these rules:
      - Field won't be parsed unless it has a type annotation
      - Field will be skipped if not in all caps
      - Class field and environment variable name are the same
    """

    def __init__(self, env):
        for field in self.__annotations__:
            if not field.isupper():
                continue

            # Raise AppConfigError if required field not supplied
            default_value = getattr(self, field, None)
            if default_value is None and env.get(field) is None:
                raise AppConfigError('The {} field is required'.format(field))

            # Cast env var value to expected type and raise AppConfigError on failure
            try:
                var_type = get_type_hints(AppConfig)[field]
                if var_type == bool:
                    value = _parse_bool(env.get(field, default_value))
                else:
                    value = var_type(env.get(field, default_value))

                self.__setattr__(field, value)
            except ValueError:
                raise AppConfigError('Unable to cast value of "{}" to type "{}" for "{}" field'.format(
                    env[field],
                    var_type,
                    field
                )
                )

    def __repr__(self):
        return str(self.__dict__)


# Expose Config object for app to import
Config = AppConfig(os.environ)
