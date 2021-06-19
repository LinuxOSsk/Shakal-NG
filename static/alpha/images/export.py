# -*- coding: utf-8 -*-
import glob
import os
import subprocess
from PIL import Image


SIZES = (
	(1, ''),
	(2, '@2x'),
)

DPI = 96


def convert_svg_files():
	svg_files = [os.path.splitext(os.path.basename(filename))[0] for filename in glob.glob("scalable/*.svg")]
	for basename in svg_files:
		convert_svg_file(basename)


def convert_svg_file(basename):
	exported = False
	for size, suffix in SIZES:
		output_filename = 'tmp/%s%s.png' % (basename, suffix)
		if not os.path.exists(output_filename):
			cmd_args = ['inkscape', 'scalable/%s.svg' % basename, '--export-filename=' + output_filename, '-d', str(DPI * size)]
			subprocess.call(cmd_args)
			exported = True
	if exported:
		normalize_size(basename)


def normalize_size(basename):
	base_size = None
	for size, suffix in SIZES:
		image_name = 'tmp/%s%s.png' % (basename, suffix)
		if base_size is None:
			with open(image_name, 'rb') as fp:
				im = Image.open(fp)
				base_size = (im.size[0] // size, im.size[1] // size)
		else:
			target_size = (base_size[0] * size, base_size[1] * size)
			with open(image_name, 'rb') as fp:
				im = Image.open(fp)
				if im.size != target_size:
					output_image = Image.new(im.mode, target_size)
					output_image.paste(im, (0, 0))
					output_image.save(image_name)


def process_image(basename, shaders, output_filename):
	output_path = 'png/' + output_filename + '.png'
	if os.path.exists(output_path):
		return
	im = Image.open('tmp/%s.png' % basename)
	px = im.load()
	for shader in shaders:
		for y in range(im.size[1]):
			for x in range(im.size[0]):
				px[x, y] = shader(*px[x, y])
	im.save(output_path)
	subprocess.call(['pngout-static', '-k0', output_path])
	subprocess.call(['advpng', '-z', '-4', output_path])
	subprocess.call(['optipng', '-o7', output_path])


def process_images(basename, shaders, suffix=''):
	for __, size in SIZES:
		process_image(basename + size, shaders, basename + suffix + size)


INVERT_SHADER = lambda r, g, b, a: (255-r, 255-g, 255-b, a)
SEMI_TRANSPARENT = lambda r, g, b, a: (r, g, b, a // 2)
LIGHT_TRANSPARENT = lambda r, g, b, a: (r, g, b, a // 4)


def make_light_dark(basename):
	process_images(basename, [], '_dark')
	process_images(basename, [INVERT_SHADER], '_light')

def make_transparent_light_dark(basename):
	process_images(basename, [SEMI_TRANSPARENT], '_transparent_dark')
	process_images(basename, [INVERT_SHADER, SEMI_TRANSPARENT], '_transparent_light')

def make_lighttransparent_light_dark(basename):
	process_images(basename, [LIGHT_TRANSPARENT], '_transparent_dark')
	process_images(basename, [INVERT_SHADER, SEMI_TRANSPARENT], '_transparent_light')

def make_identity(basename):
	process_images(basename, [], '')

def make_colorized(basename, color, suffix=''):
	process_images(basename, [lambda r, g, b, a: (color[0], color[1], color[2], a)], suffix)

def main():
	if not os.path.exists('tmp'):
		os.makedirs('tmp')
	if not os.path.exists('png'):
		os.makedirs('png')
	convert_svg_files()

	make_identity('avatar_placeholder')
	make_identity('logo')
	make_identity('logo_mini')

	make_light_dark('arrow_down')
	make_light_dark('gear')
	make_light_dark('menu')
	make_light_dark('menu_back')
	make_light_dark('search')
	make_light_dark('user')
	make_light_dark('rss')

	make_transparent_light_dark('block')
	make_transparent_light_dark('eye')
	make_transparent_light_dark('flag')
	make_transparent_light_dark('gear')
	make_transparent_light_dark('lock')
	make_transparent_light_dark('pencil')
	make_transparent_light_dark('reply')
	make_transparent_light_dark('parent')
	make_transparent_light_dark('search')
	make_transparent_light_dark('star')
	make_transparent_light_dark('tick')
	make_transparent_light_dark('rating_0')
	make_transparent_light_dark('rating_1')
	make_transparent_light_dark('rating_2')
	make_transparent_light_dark('rating_3')
	make_transparent_light_dark('rating_4')
	make_transparent_light_dark('rating_5')
	make_transparent_light_dark('rating_admin')
	make_transparent_light_dark('foldable_open')
	make_transparent_light_dark('foldable_closed')
	make_transparent_light_dark('trashcan')
	make_transparent_light_dark('unlock')
	make_transparent_light_dark('voting_down')
	make_transparent_light_dark('voting_up')

	make_lighttransparent_light_dark('comments')

	make_colorized('star', (221, 221, 0), '_yellow')
	make_colorized('tick', (102, 221, 102), '_green')
	make_colorized('eye', (102, 102, 221), '_blue')
	make_colorized('delete', (221, 102, 102), '_red')


if __name__ == "__main__":
	main()
