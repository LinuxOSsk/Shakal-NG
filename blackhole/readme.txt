Poznámky k importu dát

Obsah:

Každý obsah je uložený ako node.

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
