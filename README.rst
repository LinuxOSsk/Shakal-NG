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

    sudo apt-get --yes install build-essential python-dev libjpeg8-dev libfreetype6-dev zlib1g-dev python2.7 python2.7-dev  python-virtualenv

Pre Arch linux:

::

    pacman -S --needed --noconfirm base-devel python2 libjpeg-turbo freetype2 zlib python2-virtualenv git


Chýbajúce balíky sa dajú nájsť v repozitári http://mirror.cse.iitk.ac.in/debian/

::

    wget https://raw.github.com/mireq/Shakal-NG/master/install.sh&&chmod +x install.sh&&. ./install.sh


Spustenie
---------


::

    python manage.py runserver
