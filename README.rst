===========================================================
Nová generácia Shakal CMS
===========================================================

Autor:
   Miroslav Bendík

Závislosti
----------
django-mptt - Podpora modifikovaných DFS do django
https://github.com/django-mptt/django-mptt/

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

