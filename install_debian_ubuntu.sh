#!/bin/sh

# Install dependency
sudo apt-get --yes install build-essential python-dev libjpeg8-dev libfreetype6-dev zlib1g-dev python2.7 python2.7-dev  python-virtualenv npm

PYTHON=python2.7

if which npm > /dev/null
	then echo "Node.js .. OK"
else
	echo "No Node.js"
	exit
fi

if which git > /dev/null
	then echo "git .. OK"
else
	echo "No git"
	exit
fi

if which $PYTHON > /dev/null
	then echo "${PYTHON} .. OK"
else
	echo "No ${PYTHON}"
	exit
fi

mkdir shakal
git clone https://github.com/LinuxOSsk/Shakal-NG.git shakal/shakal-src
mv -f shakal/shakal-src/* shakal
mv -f shakal/shakal-src/.git shakal
mv -f shakal/shakal-src/.gitignore shakal
rmdir shakal/shakal-src
virtualenv venv
. venv/bin/activate
pip install -r shakal/requirements.txt
cd shakal
mkdir venv
cd venv
npm -l i less
mkdir bin
cd bin
ln -s ../node_modules/less/bin/lessc .
cd ../..
python manage.py compilemessages
python manage.py syncdb
python manage.py compress_images
