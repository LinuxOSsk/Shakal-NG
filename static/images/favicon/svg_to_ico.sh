#!/bin/bash
inkscape favicon.svg -e favicon-0.png -d 90
inkscape favicon.svg -e favicon-1.png -d 135
inkscape favicon.svg -e favicon-2.png -d 180
inkscape favicon.svg -e favicon-3.png -d 405
inkscape favicon.svg -e favicon-4.png -d 720
icotool -c favicon-0.png favicon-1.png favicon-2.png favicon-3.png favicon-4.png -o favicon.ico
