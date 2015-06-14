===========================================================
Nová generácia Shakal CMS
===========================================================

Autor:
   Miroslav Bendík

Inštalácia
----------

Pre inštaláciu sú potrebné niektoré závislosti. Pre debian 6 sú to konkrétne
balíky:

::

    build-essential python-dev libjpeg8-dev libfreetype6-dev zlib1g-dev python2.7 python2.7-dev

Chýbajúce balíky sa dajú nájsť v repozitári http://mirror.cse.iitk.ac.in/debian/

::

    wget https://raw.github.com/mireq/Shakal-NG/master/install.sh&&chmod +x install.sh&&. ./install.sh


Spustenie
---------


::

    python manage.py runserver
