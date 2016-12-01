
from .base_settings import *

# Added settings

INSTALLED_APPS += [
    # Design
    'bootstrap3',
    'django_select2',
    # Search Engine
    'watson',
    # Project apps
    'maraudes',
    'sujets',
    'notes',
    'suivi',
    'utilisateurs',
    'website',
    'statistiques',
]


LOGIN_URL = 'index'

BOOTSTRAP3 = {
    # The URL to the jQuery JavaScript file
    'base_url': os.path.join(STATIC_URL, 'bootstrap/'),
    'jquery_url': '//code.jquery.com/jquery.min.js',
    'include_jquery': True,
    # Label class to use in horizontal forms
    'horizontal_label_class': 'col-md-2',
    # Field class to use in horizontal forms
    'horizontal_field_class': 'col-md-10',
    }

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
AUTHENTICATION_BACKENDS = [
    'website.backends.MyBackend'
    ]


