import os
from .base_settings import *

""" These are the default settings. 
    You may set them up to your needs. 
"""

# Localisation settings
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'

# Default settings for created Maraudeur objects.
MARAUDEURS = { 
    # Default password, TODO: users shall be asked to change it on first login.
    'password': "test",
    # The institution to which professionnals belongs.
    'organisme': {
        'nom': "ALSA",
        'email': "direction@alsa68.org"
    },
}

# END OF SETTINGS

""" Custom settings for 'maraudes_project' application.
    DO NOT MODIFY the following settings,
    unless you know what you are doing.
"""

LOGIN_URL = 'index'

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else: #TODO: configure a real backend
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

AUTHENTICATION_BACKENDS = [
    'utilisateurs.backends.CustomUserAuthentication'
    ]

# Extra settings to default template engine. 
# Context processors
TEMPLATES[0]['OPTIONS']['context_processors'] += [
    "website.context_processors.website_processor",
    ]
# Template directories
TEMPLATES[0]['DIRS'] += [
    os.path.join(BASE_DIR, "templates"), # Custom admin templates
    ]

# Applications
INSTALLED_APPS += [
    # Design
    'bootstrap3',
    'django_select2',
    # Search Engine
    'watson',
    # Graph package
    'graphos',
    # Tests
    'django_nose',
    # Project apps
    'website',
    'maraudes',
    'notes',
    'utilisateurs',
    'statistiques',
]

# django-nose
TEST_RUNNER = "django_nose.NoseTestSuiteRunner"
NOSE_ARGS = [
    "--with-coverage",
    "--cover-package=website,maraudes,notes,utilisateurs",
]

# bootstrap3
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

# django-select2
SELECT2_JS = 'scripts/select2.min.js'
SELECT2_CSS = 'css/select2.min.css'
