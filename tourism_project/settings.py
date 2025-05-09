import os
import secrets
from pathlib import Path

# Django imports
# Create a simple translation function that doesn't depend on Django
def _(text):
    """
    Simple translation function that returns the text unchanged.
    This avoids dependency on Django's translation module.
    In a real application, this would be replaced by Django's gettext_lazy.
    """
    return text

# Define a function to generate a random secret key
def get_random_secret_key():
    """
    Return a 50 character random string usable as a SECRET_KEY setting value.
    """
    return secrets.token_urlsafe(50)

# Define our own config function to avoid dependency issues
def config(key, default=None, cast=None):
    """
    Get configuration from environment variables with fallback to default values.
    Similar to python-decouple's config function.
    """
    value = os.environ.get(key, default)
    if cast is not None and value is not None:
        try:
            if cast == bool:
                if isinstance(value, bool):
                    return value
                return str(value).lower() in ('true', 'yes', '1', 'y')
            return cast(value)
        except (ValueError, TypeError):
            return default
    return value

# Define our own Csv function for parsing comma-separated values
def Csv():
    """
    Parse comma-separated values from environment variables.
    Similar to python-decouple's Csv function.
    """
    def converter(value):
        return value.split(',') if value else []
    return converter

# Define a function to parse database URLs
def parse_db_url(url):
    """
    Parse a database URL into Django database connection settings.
    Similar to dj-database-url's parse function.
    """
    if not url:
        return None

    # Simple parsing for common database URLs
    if url.startswith('sqlite:///'):
        return {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': url[10:],
        }
    elif url.startswith('postgres://') or url.startswith('postgresql://'):
        # Very basic parsing - in production, use the actual dj-database-url package
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'postgres',  # Default values
            'USER': 'postgres',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '5432',
        }

    return None

# Create a simple dj_database_url module-like object
class DatabaseURL:
    def parse(self, url):
        return parse_db_url(url)

dj_database_url = DatabaseURL()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Use environment variable for SECRET_KEY in production

# Get configuration from environment variables
SECRET_KEY = config('SECRET_KEY', default=get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
# Always set to True for development
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    # Admin Interface
    'jazzmin',
    # Django defaults
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # Third-party apps
    'rest_framework',
    'rest_framework.authtoken',
    'allauth',
    'allauth.account',
    # Social account providers disabled due to issues
    # 'allauth.socialaccount',
    # 'allauth.socialaccount.providers.google',
    # 'allauth.socialaccount.providers.facebook',
    'crispy_forms',
    'crispy_tailwind', # Add this line
    'modeltranslation',
    'corsheaders',
    'django_filters',
    'django_ckeditor_5',
    'widget_tweaks',
    # Project apps
    'core',
    'users',
    'tour',
    'booking',
    'blog',
    'reviews',
    'payments',
    'chatbots',
    'analytics',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # Cache middleware
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    # Compression middleware
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    # Performance middleware
    'core.middleware.PageSpeedMiddleware',
    # API performance middleware
    'core.middleware.APIPerformanceMiddleware',
    'core.middleware.APIRequestThrottleMiddleware',
    'core.middleware.APIResponseCompressionMiddleware',
    # Login speedup middleware
    'core.middleware.LoginSpeedupMiddleware',
    # Analytics middleware
    'analytics.middleware.AnalyticsMiddleware',
    # Security middleware
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Error handling middleware
    'core.middleware.SocialAccountErrorMiddleware',
]

ROOT_URLCONF = 'tourism_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'core.context_processors.currency_processor',
                'core.context_processors.loading_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'tourism_project.wsgi.application'

# Database - Use SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Available languages
LANGUAGES = [
    ('ar', _('Arabic')),
    ('en', _('English')),
    ('fr', _('French')),
    ('de', _('German')),
]

MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'
MODELTRANSLATION_LANGUAGES = ('ar', 'en', 'fr', 'de')

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Whitenoise for static files in production
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'users.CustomUser'

# Django AllAuth Configuration
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

# AllAuth settings
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = [
    'email*',
    'first_name*',
    'last_name*',
    'password1*',
    'password2*'
]
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True

ACCOUNT_ADAPTER = 'users.adapters.CustomAccountAdapter'
# SOCIALACCOUNT_ADAPTER = 'users.adapters.CustomSocialAccountAdapter'

ACCOUNT_FORMS = {
    'signup': 'users.forms.CustomSignupForm',
    'login': 'users.forms.CustomLoginForm',
}

# Social account providers disabled due to issues
# SOCIALACCOUNT_PROVIDERS = {
#     'google': {
#         'APP': {
#             'client_id': config('GOOGLE_CLIENT_ID', default=''),
#             'secret': config('GOOGLE_CLIENT_SECRET', default=''),
#             'key': ''
#         },
#         'SCOPE': [
#             'profile',
#             'email',
#         ],
#         'AUTH_PARAMS': {
#             'access_type': 'online',
#         }
#     },
#     'facebook': {
#         'APP': {
#             'client_id': config('FACEBOOK_CLIENT_ID', default=''),
#             'secret': config('FACEBOOK_CLIENT_SECRET', default=''),
#             'key': ''
#         },
#         'METHOD': 'oauth2',
#         'SCOPE': ['email', 'public_profile'],
#         'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
#         'INIT_PARAMS': {'cookie': True},
#         'FIELDS': [
#             'id',
#             'email',
#             'name',
#             'first_name',
#             'last_name',
#             'verified',
#             'locale',
#             'timezone',
#             'link',
#             'gender',
#             'updated_time',
#         ],
#         'EXCHANGE_TOKEN': True,
#         'VERIFIED_EMAIL': False,
#         'VERSION': 'v13.0',
#     }
# }

LOGIN_REDIRECT_URL = 'core:home'
LOGOUT_REDIRECT_URL = 'core:home'

# Crispy Forms Settings
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# Email settings - Use console backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Django REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    # Performance optimizations
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    },
    # Caching
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 15,  # 15 minutes
    # Content negotiation
    'DEFAULT_CONTENT_NEGOTIATION_CLASS': 'rest_framework.negotiation.DefaultContentNegotiation',
}

# CORS settings - Allow all origins for development
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True

# Site URL for building absolute URLs
SITE_URL = 'http://127.0.0.1:8000'
SITE_NAME = 'Tourism Website Development'


# Currency settings
DEFAULT_CURRENCY_CODE = 'USD'
AVAILABLE_CURRENCIES = {
    'USD': {'symbol': '$', 'name': 'US Dollar'},
    'EUR': {'symbol': '€', 'name': 'Euro'},
    'GBP': {'symbol': '£', 'name': 'British Pound'},
    'JPY': {'symbol': '¥', 'name': 'Japanese Yen'},
    'CNY': {'symbol': '¥', 'name': 'Chinese Yuan'},
    'AUD': {'symbol': 'A$', 'name': 'Australian Dollar'},
    'CAD': {'symbol': 'C$', 'name': 'Canadian Dollar'},
    'CHF': {'symbol': 'CHF', 'name': 'Swiss Franc'},
    'EGP': {'symbol': 'E£', 'name': 'Egyptian Pound'},
}

# PayPal settings
PAYPAL_MODE = config('PAYPAL_MODE', default='sandbox')  # sandbox or live
PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID', default='')
PAYPAL_SECRET = config('PAYPAL_SECRET', default='')

# Use SITE_URL for building PayPal URLs
PAYPAL_RETURN_URL = f"{SITE_URL}/en/payments/confirm/"
PAYPAL_CANCEL_URL = f"{SITE_URL}/en/payments/cancel/"

# Enable test mode for offline development
# When True, PayPal integration will use fake responses instead of making real API calls
# This is useful for development without internet connection or when PayPal sandbox is down
PAYPAL_TEST_MODE = config('PAYPAL_TEST_MODE', default=False, cast=bool)

# Celery settings
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Chatbot settings
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
DIALOGFLOW_PROJECT_ID = config('DIALOGFLOW_PROJECT_ID', default='')

# CKEditor 5 settings
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', 'imageUpload'],
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
            ]
        }
    }
}

CKEDITOR_5_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
CKEDITOR_5_UPLOAD_PATH = 'uploads/ckeditor/'

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutes
        'OPTIONS': {
            'MAX_ENTRIES': 2000,  # Increased from 1000
            'CULL_FREQUENCY': 3,  # Fraction of entries to cull when max is reached
        },
    },
    'api': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'api-cache',
        'TIMEOUT': 60,  # 1 minute for API responses
        'OPTIONS': {
            'MAX_ENTRIES': 3000,  # Increased from 2000
            'CULL_FREQUENCY': 2,
        },
    },
    'template_fragments': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'template-fragments',
        'TIMEOUT': 600,  # 10 minutes for template fragments
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        },
    },
    'static': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'static-files',
        'TIMEOUT': 86400,  # 24 hours for static files
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        },
    }
}

# Cache middleware
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 600
CACHE_MIDDLEWARE_KEY_PREFIX = 'tourism'

# Logging for debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
CSRF_USE_SESSIONS = True
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

# Development security settings - Disable security features that would require HTTPS
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_PROXY_SSL_HEADER = None

# Jazzmin Settings
JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Tourism Admin",
    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Tourism",
    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "Tourism Admin",
    # Welcome text on the login screen
    "welcome_sign": "Welcome to the Tourism Administration",
    # Copyright on the footer
    "copyright": "Tourism Ltd",
    # The model admin to search from the search bar
    "search_model": "users.CustomUser",
    # List of model admins to search from the search bar
    "search_models": ["users.CustomUser", "tour.Tour", "booking.Booking"],
    # Field name on user model that contains avatar image
    "user_avatar": "avatar",
    ############
    # Top Menu #
    ############
    # Links to put along the top menu
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        {"model": "users.CustomUser"},
        {"model": "tour.Tour"},
    ],
    #############
    # Side Menu #
    #############
    # Whether to display the side menu
    "show_sidebar": True,
    # Whether to aut expand the menu
    "navigation_expanded": True,
    # Custom icons for side menu apps/models
    "icons": {
        "users": "fas fa-users",
        "users.CustomUser": "fas fa-user",
        "tour.Tour": "fas fa-globe",
        "tour.Destination": "fas fa-map-marker",
        "booking.Booking": "fas fa-calendar",
        "blog.Post": "fas fa-newspaper",
        "reviews.Review": "fas fa-star",
        "analytics.SiteVisit": "fas fa-chart-line",
        "analytics.TourView": "fas fa-eye",
    },
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",
    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": True,
    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": None,
    "custom_js": None,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": True,
    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
}

# Jazzmin UI Customizer settings
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-outline-danger",
        "success": "btn-outline-success"
    }
}

# Loading settings
LOADING_SPINNER_ENABLED = True
LOADING_SPINNER_CSS_CLASSES = 'custom-spinner floating'
LOADING_SPINNER_TEMPLATE = 'partials/loading.html'
LOADING_SPINNER_STYLE = 'dots'  # dots, pulse, bounce, wave
LOADING_SPINNER_SIZE = 'lg'     # sm, md, lg
LOADING_SPINNER_GLASS = True    # Whether to use glass morphism effect
LOADING_SHOW_DELAY_MS = 300
LOADING_HIDE_DELAY_MS = 300

# End of settings file
