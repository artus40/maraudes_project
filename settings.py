
from .base_settings import *

# Added settings

INSTALLED_APPS += [
    # Design
    'bootstrap3',
    'django_select2',
    # Search Engine
    'watson',
    # Graph package
    'graphos',
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
    'base_url': os.path.join(STATIC_URL, 'css', 'bootstrap/'),
    'jquery_url': os.path.join(STATIC_URL, 'scripts', 'jquery.min.js'),
    'include_jquery': True,
    # Label class to use in horizontal forms
    'horizontal_label_class': 'col-md-2',
    # Field class to use in horizontal forms
    'horizontal_field_class': 'col-md-10',
    }

# Django-select2 Configuration
SELECT2_JS = 'scripts/select2.min.js'
SELECT2_CSS = 'css/select2.min.css'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
AUTHENTICATION_BACKENDS = [
    'website.backends.MyBackend'
    ]


