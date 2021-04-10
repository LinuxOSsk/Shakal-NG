Nová generácia Shakal CMS
=========================

Autor:
:   Miroslav Bendík

Inštalácia
----------

### Závislosti

Debian 8

    sudo apt-get --yes install libjpeg-dev build-essential python3-dev python3-venv libfreetype6-dev git gettext

Arch linux:

    pacman -S --needed --noconfirm base-devel python3 libjpeg-turbo freetype2 zlib git

### Inštalácia virtuálneho prostredia

    curl -L https://raw.githubusercontent.com/LinuxOSsk/Shakal-NG/master/install.sh > install.sh&&chmod +x install.sh&&. ./install.sh

Skript vytvára v podadresári shakal súbor Makefile, ktorý následne
stiahne a nainštaluje zvyšné závislosti pod bežným používateľom (nie je
potrebný root).

V prípade zlyhania v niektorom kroku je možné vykonať nápravu a
spustením make v podadresári shakal pokračovať v inštalácii.

Spustenie a aktualizácia
------------------------

Súbor Makefile v podaresári shakal sa dá použiť aj na spúšťanie webu a
jeho aktualizáciu z gitu.

    # spustenie
    make runserver

    # aktualizacia
    make update

Vytvorenie novej db
-------------------

Zatiaľ nie je dokončený prechod na db migrácie. V niektorých prípadoch
môže po aktualizácii prestať fungovať aplikácia kvôli zmene db modelu.
Ak nevadí vymazanie celej databázy je možné vytvoriť novú db príkazom:

    make resetdb

Docker
-----

Spustenie vyvojoveho prostredia je mozne aj pomocou docker-compose


    git clone https://github.com/LinuxOSsk/Shakal-NG.git
    cd Shakal-NG
    git submodule init
    git submodule update
    sudo docker-compose up


TODO
====

-   integrovať <https://linuxjourney.com/>
-   hodnotenie článku
-   zaplatiť autorovi kávu
-   nahlásenie chyby článku
-   ponuky práce
-   bazár
