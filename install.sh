#!/bin/sh

PYTHON=python2.7

mkdir shakal
git clone https://github.com/mireq/Shakal-NG.git shakal/shakal-src
mv -f shakal/shakal-src/* shakal
mv -f shakal/shakal-src/.git shakal
mv -f shakal/shakal-src/.gitignore shakal
rmdir shakal/shakal-src
wget https://raw.github.com/pypa/virtualenv/master/virtualenv.py -O shakal/virtualenv.py
$PYTHON shakal/virtualenv.py --distribute shakal/venv -p $PYTHON
. shakal/venv/bin/activate
pip install -r shakal/requirements.txt
cd shakal
cd venv
npm -l i less
cd bin
ln -s ../node_modules/less/bin/lessc .
cd ../..
python manage.py syncdb
python manage.py compress_images
python manage.py compress_less
