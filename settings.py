from os import environ
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SESSION_CONFIGS = [
    dict(
        name='AIFBEmotExperiment',
        display_name='Alternative Uses Task',
        app_sequence=['experiment'],
        num_demo_participants=1,
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, 
    participation_fee=0.00, 
    doc=""
)

INSTALLED_APPS = [
    'otree',
    'experiment',
    'PreSurvey',
]

# Basic settings
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD', 'changeme')
SECRET_KEY = '6547687159822'
LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

# For channels
ASGI_APPLICATION = 'routing.application'
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

DEBUG = True
ALLOWED_HOSTS = ['*']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Required for Django
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# For storing data between pages
PARTICIPANT_FIELDS = []
SESSION_FIELDS = []