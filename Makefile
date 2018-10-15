.PHONY: all compilesprites migrate update update2 resetdb

PIP=pip3
DJANGO_MANAGE=/opt/shakal/manage.py

all: localinstall
dev: sampledata banner runserver

runserver: 
	${DJANGO_MANAGE} runserver 0.0.0.0:8000

update: 
	${PIP} install --no-cache-dir -r requirements.dev.txt --src /usr/local/src
	${DJANGO_MANAGE} compilesprites
	${DJANGO_MANAGE} makemigrations	
	${DJANGO_MANAGE} migrate
	${DJANGO_MANAGE} compilemessages
pull: 
	cd /opt/shakal && git submodule init && git submodule update 
sampledata: 
	rm -f db.sqlite3
	${DJANGO_MANAGE} compilesprites
	${DJANGO_MANAGE} makemigrations
	${DJANGO_MANAGE} migrate
	${DJANGO_MANAGE} compilemessages
	${DJANGO_MANAGE} loaddata forum/data/categories.json
	${DJANGO_MANAGE} loaddata news/data/categories.json
	${DJANGO_MANAGE} create_sample_data --verbosity 2
	${DJANGO_MANAGE} loaddata wiki/data/pages.json
	${DJANGO_MANAGE} rebuild_index --noinput

resetdb:
	rm -f db.sqlite3
	${DJANGO_MANAGE} migrate
	${DJANGO_MANAGE} loaddata forum/data/categories.json
	${DJANGO_MANAGE} loaddata news/data/categories.json
	${DJANGO_MANAGE} create_sample_data
	${DJANGO_MANAGE} loaddata wiki/data/pages.json
	${DJANGO_MANAGE} rebuild_index --noinput

banner:
	@echo "================================================"
	@echo "Inštalácia prebehla úspešne"
	@echo "Používateľské meno je admin, heslo demo"
	@echo "================================================"
