#!/bin/sh

#install dependencies
if [[ $EUID -ne 0 ]]; then
    echo "You must be root to proceed in this step" 
    exit 1
fi

pacman -S --needed --noconfirm base-devel python2 libjpeg-turbo freetype2 zlib python2-virtualenv nodejs nodejs-less git
exit 0

