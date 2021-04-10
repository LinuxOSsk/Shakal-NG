#!/bin/sh

PYTHON=python3

#install dependencies as root
echo "Root password for dependencies installation."
su root -c "./install_archlinux_dependencies.sh"
ret=$?
if [[ $ret != 0 ]]; then
    echo "Installation of dependencies failed. Aborting...";
    exit 1
fi

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
pip install -r shakal/requirements/py3.7-requirements.txt
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
