===========================================================
Nová generácia Shakal CMS
===========================================================

Autor:
   Miroslav Bendík

Inštalácia
----------

Pre pohodlnejšiu prácu odporúčam nainštalovať virtualenvwrapper. Následne
spustiť source `source cest/k/virtualenvwrapper.sh`. Pre vytvorenie nového
prostredia pre shakal sa použije príkaz `mkvirtualenv shakal` a prostredie sa
aktivuje príkazom `workon django`.

Závislosti
^^^^^^^^^^

Závislosti sa dajú automaticky nainštalovať nástrojom `pip`:

::

    pip install -r requirements.txt
