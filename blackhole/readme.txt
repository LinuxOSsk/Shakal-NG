Poznámky k importu dát

Obsah
-----

- tabuľka node

 desc node;
+----------+------------------+------+-----+---------+----------------+
| Field    | Type             | Null | Key | Default | Extra          |
+----------+------------------+------+-----+---------+----------------+
| nid      | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
| type     | varchar(32)      | NO   | MUL |         |                |
| title    | varchar(128)     | NO   | MUL |         |                |
| uid      | int(10)          | NO   | MUL | 0       |                |
| status   | int(4)           | NO   | MUL | 1       |                |
| created  | int(11)          | NO   | MUL | 0       |                |
| changed  | int(11)          | NO   | MUL | 0       |                |
| comment  | int(2)           | NO   |     | 0       |                |
| promote  | int(2)           | NO   | MUL | 0       |                |
| moderate | int(2)           | NO   | MUL | 0       |                |
| sticky   | int(2)           | NO   |     | 0       |                |
| vid      | int(10) unsigned | NO   | PRI | 0       |                |
+----------+------------------+------+-----+---------+----------------+


Zaujíjamvé:
nid -> číslo uzla
type -> typ obsahu
title -> nadpis
uid -> autor
status -> 0 nepublikované, 1 publikované
created -> čas vytvorenia (timestamp)
changed -> čas zmeny (timestamp)
comment -> či sú komentáre poolen, 0 - skryté, 1 - diskusia uzatvorená, 2 - povolená
promote -> na úvodnej stránke
sticky -> vždy viditeľné
vid -> ID revízie

Kategórie:

desc term_data;
+-------------+------------------+------+-----+---------+----------------+
| Field       | Type             | Null | Key | Default | Extra          |
+-------------+------------------+------+-----+---------+----------------+
| tid         | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
| vid         | int(10) unsigned | NO   | MUL | 0       |                |
| name        | varchar(255)     | NO   |     |         |                |
| description | longtext         | YES  |     | NULL    |                |
| weight      | tinyint(4)       | NO   |     | 0       |                |
+-------------+------------------+------+-----+---------+----------------+

vid -> 1 - tu sú kategórie

desc term_hierarchy;
+--------+------------------+------+-----+---------+-------+
| Field  | Type             | Null | Key | Default | Extra |
+--------+------------------+------+-----+---------+-------+
| tid    | int(10) unsigned | NO   | PRI | 0       |       |
| parent | int(10) unsigned | NO   | PRI | 0       |       |
+--------+------------------+------+-----+---------+-------+

desc term_node;
+-------+------------------+------+-----+---------+-------+
| Field | Type             | Null | Key | Default | Extra |
+-------+------------------+------+-----+---------+-------+
| nid   | int(10) unsigned | NO   | PRI | 0       |       |
| tid   | int(10) unsigned | NO   | PRI | 0       |       |
+-------+------------------+------+-----+---------+-------+


Komentáre:

http://anothercoffee.net/drupal-to-wordpress-migration-comments-table-mapping/
http://shutterfreak.net/blogs/olivier-biot/2010-06-24/rearranging-comments-drupal

desc comments;
+-----------+---------------------+------+-----+---------+----------------+
| Field     | Type                | Null | Key | Default | Extra          |
+-----------+---------------------+------+-----+---------+----------------+
| cid       | int(10)             | NO   | PRI | NULL    | auto_increment |
| pid       | int(10)             | NO   |     | 0       |                |
| nid       | int(10)             | NO   | MUL | 0       |                |
| uid       | int(10)             | NO   |     | 0       |                |
| subject   | varchar(64)         | NO   |     |         |                |
| comment   | longtext            | NO   |     | NULL    |                |
| hostname  | varchar(128)        | NO   |     |         |                |
| timestamp | int(11)             | NO   |     | 0       |                |
| score     | mediumint(9)        | NO   |     | 0       |                |
| status    | tinyint(3) unsigned | NO   |     | 0       |                |
| format    | int(4)              | NO   |     | 0       |                |
| thread    | varchar(255)        | NO   |     |         |                |
| users     | longtext            | YES  |     | NULL    |                |
| name      | varchar(60)         | YES  |     | NULL    |                |
| mail      | varchar(64)         | YES  |     | NULL    |                |
| homepage  | varchar(255)        | YES  |     | NULL    |                |
+-----------+---------------------+------+-----+---------+----------------+

cid -> primárny kľúč
pid -> nadradený kľúč
nid -> ID node
uid -> ID autora
subject -> predmet
comment -> komentár (rôzny formát)
hostname -> 127.0.0.1, neviem načo slúži
timestamp -> čas
score -> 0 (asi sa nepoužívalo)
format -> mapované na filter_formats
thread -> poradie a štruktúra
name -> meno autora
mail -> mail autora
homepage -> domovská stránka
