#!/bin/sh

mkdir -p shakal
cat << 'EOF' > shakal/Makefile
.PHONY: all cimpilesprites migrate

PYTHON=python2.7
VENV_PYTHON=venv/bin/python
DJANGO_MANAGE=cd shakal&&DJANGO_SETTINGS_MODULE=web.settings_local ../venv/bin/django-admin

all: localinstall

.stamp_downloaded:
	git clone --recursive https://github.com/mireq/Shakal-NG.git shakal
	@touch .stamp_downloaded

.stamp_virtualenv: .stamp_downloaded
	wget https://raw.github.com/pypa/virtualenv/master/virtualenv.py -O virtualenv.py
	${PYTHON} virtualenv.py venv --no-setuptools --no-pip -p ${PYTHON}
	rm virtualenv.py*
	@touch .stamp_virtualenv

.stamp_setuptools: .stamp_virtualenv
	wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py -O get-pip.py
	${VENV_PYTHON} get-pip.py
	rm get-pip.py*
	@touch .stamp_setuptools

.stamp_requirements: .stamp_setuptools
	venv/bin/pip install -r shakal/requirements.txt
	venv/bin/pip install -r shakal/requirements.local.txt
	touch .stamp_requirements

.stamp_settings: .stamp_requirements
	cp shakal/web/settings_sample.py shakal/web/settings_local.py
	@touch .stamp_settings

compilesprites: .stamp_settings
	${DJANGO_MANAGE} compilesprites

migrate: .stamp_settings
	${DJANGO_MANAGE} migrate

runserver: .stamp_superuser
	${DJANGO_MANAGE} runserver_plus

update: .stamp_settings
	cd shakal; git pull; git submodule sync --recursive
	${DJANGO_MANAGE} compilesprites
	${DJANGO_MANAGE} migrate

.stamp_superuser: .stamp_settings
	${DJANGO_MANAGE} compilesprites
	${DJANGO_MANAGE} migrate
	${DJANGO_MANAGE} createsuperuser
	@touch .stamp_superuser

localinstall: .stamp_superuser
	@echo "================================================"
	@echo "Inštalácia prebehla úspešne"
	@echo "Pre spustenie zadajte: cd shakal; make runserver"
	@echo "Aktualizácia: cd shakal; make update"
	@echo "================================================"
EOF

make -C shakal
