#!/bin/sh

inkscape penguin_black.svg -e penguin_black.png -d 90
inkscape penguin_black.svg -e penguin_black@2x.png -d 180
inkscape penguin_white.svg -e penguin_white.png -d 90
inkscape penguin_white.svg -e penguin_white@2x.png -d 180

compress_files=(
	penguin_black.png
	penguin_black@2x.png
	penguin_white.png
	penguin_white@2x.png
)

for file in ${compress_files[@]}; do
	pngout-static -k0 $file
	advpng -z -4 $file
	optipng -o7 $file
done
