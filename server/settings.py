import os
import logging

#logging
LOGGING_PATH = "erserver.log"
LOGGING_LVL = logging.INFO

# setup logging
logging.basicConfig(
    filename=LOGGING_PATH,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S',
    level=LOGGING_LVL)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'c%!3i5w!h&d1)0e)c717q_l=+5^4w64lu4du+-j*dfq4^9s_%z'

DEBUG = True

ALLOWED_HOSTS = [
    '*',
]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'panel',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'panel/static')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'server.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'quest.db.sqlite3'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

BUTTONS_LIMIT = 5

STATIC_ROOT = os.path.join(BASE_DIR, "static/")
STATIC_URL = '/static/'
# STATICFILES_DIRS = [
#    os.path.join(BASE_DIR, "static"),
# ]

# MEDIA_ROOT = os.path.join(BASE_DIR,  'erp/media/')
MEDIA_ROOT = os.path.join(BASE_DIR,  'sound/')
DEFAULT_DIR = MEDIA_ROOT + 'default/'
# MEDIA_URL = '/erp/media/'
MEDIA_URL = '/sound/'

MEDIA_PATH =  "sound"
HINT_PATH = os.path.join(os.getcwd(), MEDIA_PATH, "hint/")
ACTION_PATH = os.path.join(os.getcwd(), MEDIA_PATH,"action/")
AUTO_PATH = os.path.join(os.getcwd(), MEDIA_PATH, "hint_auto/")
BACK_PATH = os.path.join(os.getcwd(), MEDIA_PATH, "background/")
DEFAULT_PATH = os.path.join(os.getcwd(), MEDIA_PATH, "default/")


USERS = {
}

MQTT_PORT = 1883
MQTT_HOST = "192.168.10.1"
TIMER_SUBSCRIBE = ["/ers/timer", "/ers/timer/period"]
TIMER_TOPIC_OUT = "/er/timer/client/sec"
LOGGING_PATH = "erserver.log"
LOGGING_LVL = logging.INFO


AUTO_TOPIC_OUT = "/er/async/auto/play"
AUTO_SUBSCRIBE = ["/er/cmd", "/er/async", "/erp/auto/hint"]


PLAYER_SUBSCRIBE = [
    "/er/async/play",
    "/er/async/stop",
    "/er/async/reset",
    "/er/async/hint/play",
    "/er/async/auto/play",
    "/er/async/vol/set",

    "/er/music/play",
    "/er/music/stop",
    "/er/mc1/pause",
    "/er/mc1/resume",
    "/er/mc1/vol/set",

    "/er/musicback/play",
    "/er/musicback/stop",
    "/er/mc2/pause",
    "/er/mc2/resume",
    "/er/mc2/vol/set"]
