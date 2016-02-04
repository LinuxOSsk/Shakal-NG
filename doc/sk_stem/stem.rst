===========================================================
Slovenský stemmer
===========================================================

Shakal používa knižnicu Xapian pre fulltext vyhľadávanie. Tá podporuje
získavanie základu slova pomocou frameworku snowball - http://snowballstem.org/

Akturálna (moja) verzia stemmeru pre slovenčinu je tu:
https://github.com/LinuxOSsk/Shakal-NG/blob/master/doc/sk_stem/stem_Unicode.sbl

Je totálne nekompletná, netestovaná a zrejme chybná. Nie som dobrý v slovenčine,
takže podľa toho vyzerá aj stemmer.

Ako rozbehať stemmer
^^^^^^^^^^^^^^^^^^^^

::

    $ git clone git@github.com:snowballstem/snowball.git

- upraviť GNUmakefile, do zoznamu `libstemmer_algorithms` pridať slovak.
- upraviť modules_utf8.txt a pridať riadok:

::

    slovak          UTF_8                   slovak,sk

- skopírovať stem_Unicode.sbl do `algorithms/slovak/` (adresár je potrebné
  vytvoriť)
- spustiť make

::

    $ make&&echo "Linuxová\ndistribúcia"|./stemwords -l slovak -p2
    make: Nothing to be done for 'all'.
    linuxová                      linux
    distribúcia                   distribuci

Užitočné odkazy
^^^^^^^^^^^^^^^

- http://korpus.sk/morphology_database.html - morfologická databáza
- http://vi.ikt.ui.sav.sk/Projekty/Projekty_2008%2F%2F2009/Hana_Pifkov%C3%A1_-_Stemer - implementácia v jave
- http://vi.ikt.ui.sav.sk/Projekty/Projekty_2008%2F%2F2009/Stanislav_Balocky - (dosť slabá) implementácia v snowballe
- https://github.com/elastic/hunspell/blob/master/src/test-resources/stemming-data/sk.txt - malé testovacie dáta pre myspell
