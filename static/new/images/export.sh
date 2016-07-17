#!/bin/sh

svg_files=(
	delete.svg
	eye.svg
	gear.svg
	lock.svg
	reply.svg
	rss.svg
	search.svg
	star.svg
	tick.svg
	rating_0.svg
	rating_1.svg
	rating_2.svg
	rating_3.svg
	rating_4.svg
	rating_5.svg
	rating_admin.svg
)

compress_files=(
	delete.png
	eye.png
	gear.png
	lock.png
	reply.png
	rss.png
	search.png
	star.png
	tick.png
	rating_0.png
	rating_1.png
	rating_2.png
	rating_3.png
	rating_4.png
	rating_5.png
	rating_admin.png
)

transparent_files=(
	delete.png
	eye.png
	gear.png
	lock.png
	reply.png
	rss.png
	search.png
	star.png
	tick.png
	delete_invert.png
	eye_invert.png
	gear_invert.png
	lock_invert.png
	reply_invert.png
	rss_invert.png
	search_invert.png
	star_invert.png
	tick_invert.png
	rating_0.png
	rating_1.png
	rating_2.png
	rating_3.png
	rating_4.png
	rating_5.png
	rating_admin.png
)

invert_files=(
	delete.png
	eye.png
	gear.png
	lock.png
	reply.png
	rss.png
	search.png
	star.png
	tick.png
)

for file in ${svg_files[@]}; do
	inkscape $file -e "`basename $file .svg`.png" -d 90
	inkscape $file -e "`basename $file .svg`@2x.png" -d 180
done

for file in ${invert_files[@]}; do
	convert -negate "`basename $file .png`.png" "`basename $file .png`_invert.png"
	convert -negate "`basename $file .png`@2x.png" "`basename $file .png`_invert@2x.png"
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
