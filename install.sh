#!/bin/sh

DUMPMAKE=
while true; do
	case "$1" in
		--dumpmake ) DUMPMAKE="$2"; shift 2 ;;
		-- ) shift; break ;;
		* ) break ;;
	esac
done

MAKEFILE=$DUMPMAKE
if [[ "$DUMPMAKE" == "" ]]
then
	MAKEFILE="shakal/Makefile"
fi

mkdir -p shakal
cat << 'EOF' > ${MAKEFILE}
.PHONY: all cimpilesprites migrate update update2 resetdb

PYTHON=python2.7
VENV_PYTHON=venv/bin/python
DJANGO_MANAGE=cd shakal&&DJANGO_SETTINGS_MODULE=web.settings_local ../venv/bin/python manage.py

all: localinstall

.stamp_downloaded:
	git clone --recursive https://github.com/mireq/Shakal-NG.git shakal
	@touch .stamp_downloaded

.stamp_virtualenv: .stamp_downloaded
	wget https://raw.github.com/pypa/virtualenv/master/virtualenv.py -O virtualenv.py
	${PYTHON} virtualenv.py venv --no-setuptools --no-pip --no-wheel -p ${PYTHON}
	rm virtualenv.py*
	@touch .stamp_virtualenv

.stamp_setuptools: .stamp_virtualenv
	wget https://bootstrap.pypa.io/get-pip.py -O get-pip.py
	${VENV_PYTHON} get-pip.py
	rm get-pip.py*
	@touch .stamp_setuptools

.stamp_requirements: .stamp_setuptools
	venv/bin/pip install -r shakal/requirements.dev.txt
	touch .stamp_requirements

.stamp_settings: .stamp_requirements
	cp shakal/web/settings_sample.py shakal/web/settings_local.py
	@touch .stamp_settings

compilesprites: .stamp_settings
	${DJANGO_MANAGE} compilesprites

migrate: .stamp_settings
	${DJANGO_MANAGE} migrate

compilemessages: .stamp_settings
	${DJANGO_MANAGE} compilemessages

runserver: .stamp_sampledata
	${DJANGO_MANAGE} runserver_plus

update: .stamp_settings
	cd shakal; git pull; git submodule sync --recursive
	@./shakal/install.sh --dumpmake Makefile
	make update2

update2: .stamp_settings
	venv/bin/pip install -r shakal/requirements.dev.txt
	${DJANGO_MANAGE} compilesprites
	${DJANGO_MANAGE} migrate
	${DJANGO_MANAGE} compilemessages

.stamp_sampledata: .stamp_settings
	${DJANGO_MANAGE} compilesprites
	${DJANGO_MANAGE} migrate
	${DJANGO_MANAGE} compilemessages
	${DJANGO_MANAGE} loaddata forum/data/categories.json
	${DJANGO_MANAGE} loaddata news/data/categories.json
	${DJANGO_MANAGE} create_sample_data --verbosity 2
	${DJANGO_MANAGE} loaddata wiki/data/pages.json
	${DJANGO_MANAGE} rebuild_index --noinput
	@touch .stamp_sampledata

resetdb:
	rm -f shakal/db.sqlite3
	${DJANGO_MANAGE} migrate
	${DJANGO_MANAGE} loaddata forum/data/categories.json
	${DJANGO_MANAGE} create_sample_data
	${DJANGO_MANAGE} loaddata wiki/data/pages.json
	${DJANGO_MANAGE} rebuild_index --noinput

localinstall: .stamp_sampledata
	@echo "================================================"
	@echo "Inštalácia prebehla úspešne"
	@echo "Používateľské meno je admin, heslo demo"
	@echo "Pre spustenie zadajte: cd shakal; make runserver"
	@echo "Aktualizácia: cd shakal; make update"
	@echo "================================================"
EOF

if [[ "$DUMPMAKE" == "" ]]
then
	make -C shakal
fi
