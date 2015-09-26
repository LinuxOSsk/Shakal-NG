===========================================================
Nová generácia Shakal CMS
===========================================================

Autor:
   Miroslav Bendík

Inštalácia
----------

Závislosti
^^^^^^^^^^

Debian 8

::

    sudo apt-get --yes install libjpeg-dev build-essential python-dev libfreetype6-dev git

Arch linux:

::

    pacman -S --needed --noconfirm base-devel python2 libjpeg-turbo freetype2 zlib python2-virtualenv git

Inštalácia virtuálneho prostredia
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    wget https://raw.github.com/mireq/Shakal-NG/master/install.sh&&chmod +x install.sh&&. ./install.sh


Skript vytvára v podadresári shakal súbor Makefile, ktorý následne stiahne
a nainštaluje zvyšné závislosti pod bežným používateľom (nie je potrebný root).

V prípade zlyhania v niektorom kroku je možné vykonať nápravu a spustením `make`
v podadresári shakal pokračovať v inštalácii.


Spustenie a aktualizácia
------------------------

Súbor Makefile v podaresári shakal sa dá použiť aj na spúšťanie webu a jeho
aktualizáciu z gitu.

::

    # spustenie
    make run

    # aktualizacia
    make update


Vytvorenie novej db
-------------------

Zatiaľ nie je dokončený prechod na db migrácie. V niektorých prípadoch môže po
aktualizácii prestať fungovať aplikácia kvôli zmene db modelu. Ak nevadí
vymazanie celej databázy je možné vytvoriť novú db príkazom:

::

    make resetdb


====
TODO
====

- opraviť editor komentárov (static/js/richeditor/editor.js) [1]_
- pripraviť responzívny web (http://localhost:8000/?switch_template=new pre
  zobrazenie v akom je stave) [2]_


.. [1] Chýba plain text editor. Pôvodný je zakomentovaný. V podstate ho stačí
   prepísať tak, aby využíval css štýly dodávané s CKEditorom. Po prepnutí na
   plain text editor sa musí nastaviť cookie.

   V admin rozhraní nastaviť predvolený formát raw (nefiltrovaný text) a editor
   defaultne plain textový s možnosťou prepnúť na CKEditor (zase zaznamenať do
   cookies, ale samostatne pre admin a samostatne pre web). Využiť utility pre
   prácu s cookies zo static/js/utils.js

.. [2] Využiť podľa možnosti čo najviac súčasného kódu (nerobiť zbytočne
   template overridy). V CSS podľa možnosti nepoužívať gradienty a tiene,
   spomaľujú zbytočne renderovanie. Sprity sa generujú príkazom
   `python manage.py compilesprites`
