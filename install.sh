#!/bin/bash

DUMPMAKE=
DOCKER=
while true; do
	case "$1" in
		--dumpmake ) DUMPMAKE="$2"; shift 2 ;;
		--docker ) DUMPMAKE="/opt/shakal/Makefile"; DOCKER=1; shift 1 ;;
		-- ) shift; break ;;
		* ) break ;;
	esac
done

MAKEFILE=$DUMPMAKE
if [[ "$DUMPMAKE" == "" ]]
then
	MAKEFILE="shakal/Makefile"
fi

if [ -f $MAKEFILE ]; then
	exit
fi

mkdir -p shakal
cat << 'EOF' > ${MAKEFILE}
.PHONY: all compilesprites migrate update update2 resetdb rundocker fakeinstall

PYTHON=python3
PIP=venv/bin/pip
CD_SHAKAL=cd shakal;
VENV_PYTHON=venv/bin/python
DJANGO_MANAGE=${CD_SHAKAL} DJANGO_SETTINGS_MODULE=web.settings_local ../venv/bin/python manage.py

all: localinstall

.stamp_downloaded:
	git clone https://github.com/LinuxOSsk/Shakal-NG.git shakal
	${CD_SHAKAL} git submodule init
	${CD_SHAKAL} git submodule update
	@touch .stamp_downloaded

.stamp_virtualenv: .stamp_downloaded
	${PYTHON} -m venv venv
	@touch .stamp_virtualenv

.stamp_requirements: .stamp_virtualenv
	${PIP} install -r shakal/requirements/py3.7-requirements.txt
	${PIP} install -r shakal/requirements.live.txt
	${PIP} install django-extensions ipython pylint-django watchdog werkzeug
	@touch .stamp_requirements

.stamp_settings: .stamp_requirements
	${CD_SHAKAL} cp web/settings_sample.py web/settings_local.py
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
	${CD_SHAKAL} git pull; git submodule sync --recursive
	@./shakal/install.sh --dumpmake Makefile
	make update2

update2: .stamp_settings
	${PIP} install -r shakal/requirements/py3.7-requirements.txt
	${PIP} install -r shakal/requirements.live.txt
	${PIP} install django-extensions ipython pylint-django watchdog werkzeug
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
	${DJANGO_MANAGE} fulltext update
	@touch .stamp_sampledata

resetdb:
	rm -f shakal/db.sqlite3
	${DJANGO_MANAGE} migrate
	${DJANGO_MANAGE} loaddata forum/data/categories.json
	${DJANGO_MANAGE} create_sample_data
	${DJANGO_MANAGE} loaddata wiki/data/pages.json
	${DJANGO_MANAGE} rebuild_index --noinput

rundocker: fakeinstall banner
	${DJANGO_MANAGE} runserver_plus 0.0.0.0:8000

localinstall: .stamp_sampledata
	@echo "================================================"
	@echo "Inštalácia prebehla úspešne"
	@echo "Používateľské meno je admin, heslo demo"
	@echo "Pre spustenie zadajte: cd shakal; make runserver"
	@echo "Aktualizácia: cd shakal; make update"
	@echo "================================================"

banner:
	@echo "================================================"
	@echo "Inštalácia prebehla úspešne"
	@echo "Používateľské meno je admin, heslo demo"
	@echo "================================================"

fakeinstall:
	@if [ ! -f .stamp_downloaded ]; then touch .stamp_downloaded; fi
	@if [ ! -f .stamp_virtualenv ]; then touch .stamp_virtualenv; fi
	@if [ ! -f .stamp_requirements ]; then touch .stamp_requirements; fi
EOF

if [[ "$DUMPMAKE" == "" ]]
then
	make -C shakal
fi

if [[ "$DOCKER" == 1 ]]
then
	sed -i 's/CD_SHAKAL=.*/CD_SHAKAL=cd .;/g' /opt/shakal/Makefile
	sed -i 's/PIP=.*/PIP=pip3/g' /opt/shakal/Makefile
	sed -i 's/DJANGO_MANAGE=.*/DJANGO_MANAGE=\/opt\/shakal\/manage.py/g' /opt/shakal/Makefile
fi
