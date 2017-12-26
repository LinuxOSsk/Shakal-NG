# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import glob
import os
import subprocess
from PIL import Image


def process_image(basename, shaders, output_filename):
	im = Image.open(basename + '_tmp.png')
	sources = im.split()
	result = []
	for shader, source in zip(shaders, sources):
		result.append(source.point(shader))
	result_image = Image.merge(im.mode, result)
	result_image.save(output_filename)
	subprocess.call(['pngout-static', '-k0', output_filename])
	subprocess.call(['advpng', '-z', '-4', output_filename])
	subprocess.call(['optipng', '-o7', output_filename])


def process_images(basename, shaders, suffix=''):
	process_image(basename, shaders, basename + suffix + '.png')
	process_image(basename + '@2x', shaders, basename + suffix + '@2x.png')


def make_identity(basename, suffix=''):
	shaders = [
		lambda i: i,
		lambda i: i,
		lambda i: i,
		lambda i: i,
	]
	process_images(basename, shaders, suffix)


def make_transparent_gray(basename, suffix=''):
	shaders = [
		lambda i: i,
		lambda i: i,
		lambda i: i,
		lambda i: i / 2,
	]
	process_images(basename, shaders, suffix)


def make_colorized(basename, color, suffix=''):
	shaders = [
		lambda i: color[0],
		lambda i: color[1],
		lambda i: color[2],
		lambda i: i,
	]
	process_images(basename, shaders, suffix)


def convert_svg():
	svg_files = [os.path.splitext(filename)[0] for filename in glob.glob("*.svg")]
	for filename in svg_files:
		if not os.path.exists(filename + '_tmp.png'):
			cmd_args = ['inkscape', filename + '.svg', '-e', filename + '_tmp.png', '-d', '90']
			subprocess.call(cmd_args)
		if not os.path.exists(filename + '@2x_tmp.png'):
			cmd_args = ['inkscape', filename + '.svg', '-e', filename + '@2x_tmp.png', '-d', '180']
			subprocess.call(cmd_args)


def main():
	convert_svg()
	make_transparent_gray('delete')
	make_transparent_gray('gear')
	make_transparent_gray('lock')
	make_transparent_gray('reply')
	make_transparent_gray('rss')
	make_transparent_gray('search')
	make_transparent_gray('star')
	make_transparent_gray('tick')
	make_transparent_gray('rating_0')
	make_transparent_gray('rating_1')
	make_transparent_gray('rating_2')
	make_transparent_gray('rating_3')
	make_transparent_gray('rating_4')
	make_transparent_gray('rating_5')
	make_transparent_gray('rating_admin')
	make_colorized('star', (221, 221, 0), '_yellow')
	make_colorized('tick', (102, 221, 102), '_green')
	make_colorized('eye', (102, 102, 221), '_blue')
	make_colorized('gear', (255, 255, 255), '_white')
	make_colorized('arrow_down', (255, 255, 255), '_white')
	make_identity('avatar_placeholder')
	make_identity('user')


if __name__ == "__main__":
	main()
