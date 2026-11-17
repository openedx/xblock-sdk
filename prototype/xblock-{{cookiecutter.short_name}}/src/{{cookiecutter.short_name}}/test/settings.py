from uuid import uuid4

# Changes each test run.
SECRET_KEY = str(uuid4())

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

LMS_ROOT_URL = "http://local.openedx.io:8000"
COURSE_AUTHORING_MICROFRONTEND_URL = "http://apps.local.openedx.io:2001/authoring"
