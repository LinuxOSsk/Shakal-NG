#!/bin/sh

svg_files=(
	rating_0.svg
	rating_1.svg
	rating_2.svg
	rating_3.svg
	rating_4.svg
	rating_5.svg
	rating_admin.svg
)

compress_files=(
	rating_0.png
	rating_1.png
	rating_2.png
	rating_3.png
	rating_4.png
	rating_5.png
	rating_admin.png
)

transparent_files=(
	rating_0.png
	rating_1.png
	rating_2.png
	rating_3.png
	rating_4.png
	rating_5.png
	rating_admin.png
)

for file in ${svg_files[@]}; do
	inkscape $file -e "`basename $file .svg`.png" -d 90
	inkscape $file -e "`basename $file .svg`@2x.png" -d 180
done

for file in ${transparent_files[@]}; do
	convert -channel alpha -fx 'a*0.5' "`basename $file .png`.png" "`basename $file .png`.png"
	convert -channel alpha -fx 'a*0.5' "`basename $file .png`@2x.png" "`basename $file .png`@2x.png"
done

for file in ${compress_files[@]}; do
	pngout-static -k0 "`basename $file .png`.png"
	advpng -z -4  "`basename $file .png`.png"
	optipng -o7 "`basename $file .png`.png"

	pngout-static -k0 "`basename $file .png`@2x.png"
	advpng -z -4  "`basename $file .png`@2x.png"
	optipng -o7 "`basename $file .png`@2x.png"
done


#convert -fuzz 100% -fill '#ffffff' -opaque '#000000' penguin_black.png penguin_white.png
#convert -fuzz 100% -fill '#ffffff' -opaque '#000000' penguin_black@2x.png penguin_white@2x.png
#convert -fuzz 100% -fill '#ffffff' -opaque '#000000' logo_black.png logo_white.png
#convert -fuzz 100% -fill '#ffffff' -opaque '#000000' logo_black@2x.png logo_white@2x.png
