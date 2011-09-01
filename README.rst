===========================================================
Nová generácia Shakal CMS
===========================================================

Autor:
   Miroslav Bendík

Závislosti
----------
Povinné:
   - django-mptt - Podpora modifikovaných DFS do django
      https://github.com/django-mptt/django-mptt/

Voliteľné:
   - django-template-preprocessor - Minimalizácia a optimalizácia šablón
      https://github.com/citylive/django-template-preprocessor

Použitie django-template-preprocessor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Django template preprocessor umožňuje minimalizovať veľkosť šablón a
optimalizovať ich načítavanie, takže web, ktorý používa takúto optimalizáciu
bude podstatne rýchlejší. Ukážkové nastavenie preprocesoru vyzerá nasledovne:

::
    TEMPLATE_CACHE_DIR = '/tmp/templates/cache/'
    MEDIA_CACHE_DIR = MEDIA_ROOT + 'cache/'
    MEDIA_CACHE_URL = MEDIA_URL + 'cache/'
    TEMPLATE_LOADERS = TEMPLATE_LOADERS[1:]
    # Wrap template loaders
    if DEBUG:
        TEMPLATE_LOADERS = (
            'shakal.template_dynamicloader.loader_filesystem.Loader',
            #('template_preprocessor.template.loaders.ValidatorLoader',
            ('template_preprocessor.template.loaders.RuntimeProcessedLoader',
                TEMPLATE_LOADERS
            ),
        )
    else:
        TEMPLATE_LOADERS = (
            'shakal.template_dynamicloader.loader_filesystem.Loader',
            ('template_preprocessor.template.loaders.PreprocessedLoader',
                TEMPLATE_LOADERS
            ),
        )


    # Applications
    INSTALLED_APPS += ('template_preprocessor',)

    TEMPLATE_PREPROCESSOR_OPTIONS = {
        # Default settings
        '*': ('html', 'whitespace-compression', ),
        # Override for specific applications
        ('django.contrib.admin', 'django.contrib.admindocs', 'debug_toolbar'): ('no-html',),
    }

Odporúčané závislosti pre vývoj
-------------------------------
django-debug-toolbar - Zobrazovanie rôznych informácii v bočnom paneli.
http://pypi.python.org/pypi/django-debug-toolbar/

Spustenie
---------
Aplikácia Shakal CMS má v zdrojových kódoch súbor settings.py. V prípade
nasadenia na reálny server stačí tento súbor upraviť a doplniť o požadované
informácie.

Pri vývoji nie je vhodné ukladať heslá priamo do settings.py, ale namiesto toho
do samostatného súboru (napr. settings_local.py). Ten sa následne zapíše do
.git/info/exclude, aby bol systémom git v budúcnosti ignorovaný. V nasledujúcom
výpise je ukážka settings_local.py.

::

   from settings import *

   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': 'shakal',
       }
   }

   MIDDLEWARE_CLASSES += (
       'debug_toolbar.middleware.DebugToolbarMiddleware',
   )

   INSTALLED_APPS += (
       'debug_toolbar',
   )

   INTERNAL_IPS = ('127.0.0.1',)

Server je možné spustiť ako python manage.py runserver --settings
settings_local.




