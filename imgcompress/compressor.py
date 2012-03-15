# -*- coding: utf-8 -*-
from PIL import Image
from copy import deepcopy
from imgcompress import settings as imgcompress_settings
from pprint import pprint
import termcolor
import os

class Compressor:
	SIZE_WIDTH = 0
	SIZE_HEIGHT = 1
	POS_LEFT = 0;
	POS_TOP = 1;
	POS_RIGHT = 2;
	POS_BOTTOM = 3;


	def __collect_positions(self):
		"""
		Nájdenie konkrétnych pozícii obrázkov a pridelenie atribútu
		computed_pos = (x, y, x + width, y + height)
		"""
		self.images = {}
		images = deepcopy(imgcompress_settings.IMAGES)
		for label, value in images.iteritems():
			print(termcolor.colored("Processing " + label, "green"))
			computed = deepcopy(value)
			del computed['images']
			computed_images = {}
			# Nájdenie minimálnej šírky
			out_size = [1, 1]
			for image in value["images"]:
				if image["mode"] != "repeat-x":
					out_size[self.SIZE_WIDTH] = max(out_size[self.SIZE_WIDTH], image["width"])
			# Nájdenie konkrétnych pozícii obrázkov
			# x, y, x + šírka, y + výška
			last_pos = (0, 0, 0, 0)
			for image in value["images"]:
				size = self.__compute_size(image)
				img_pos = self.__compute_pos(size, last_pos, out_size)
				print(termcolor.colored("  Position " + image['name'] + ' ' + str(img_pos), "green"))
				last_pos = (img_pos[0], img_pos[1], max(img_pos[2], last_pos[2]), max(img_pos[3], last_pos[3]))
				out_size[self.SIZE_HEIGHT] = last_pos[self.POS_BOTTOM]
				image['computed_pos'] = img_pos
				computed_images[image['name']] = image
			computed['images'] = computed_images
			computed['computed_size'] = tuple(out_size)
			self.images[label] = computed


	def __compute_size(self, image):
		"""
		Vráti veľkosť obrázku podľa režimu. Veľkosť pre obrázky s režimom
		opakovania má hodnotu 0 v smere opakovania.
		"""
		if image["mode"] == "no-repeat":
			return (image["width"], image["height"])
		elif image["mode"] == "repeat-x":
			return (0, image["height"])

	def __compute_pos(self, size, last_pos, out_size):
		if size[self.SIZE_WIDTH] == 0:
			return (
				0,
				last_pos[self.POS_BOTTOM],
				out_size[self.SIZE_WIDTH],
				last_pos[self.POS_BOTTOM] + size[self.SIZE_HEIGHT]
			)
		else:
			if last_pos[self.POS_RIGHT] + size[self.SIZE_WIDTH] > out_size[self.SIZE_WIDTH]:
				return (
					0,
					last_pos[self.POS_BOTTOM],
					size[self.SIZE_WIDTH],
					last_pos[self.POS_BOTTOM] + size[self.SIZE_HEIGHT]
				)
			else:
				return (
					last_pos[self.POS_RIGHT],
					last_pos[self.POS_TOP],
					last_pos[self.POS_RIGHT] + size[self.SIZE_WIDTH],
					last_pos[self.POS_TOP] + size[self.SIZE_HEIGHT]
				)


	def __tile_image(self, in_image, target_size):
		out_image = Image.new('RGBA', target_size)
		in_size = in_image.size
		current_pos = (0, 0)
		while current_pos[self.POS_LEFT] < target_size[self.SIZE_WIDTH] and current_pos[self.POS_TOP] < target_size[self.SIZE_HEIGHT]:
			target_pos = current_pos + (current_pos[0] + in_size[0], current_pos[1] + in_size[1])
			# Kontrola pre orezanie
			if target_pos[self.POS_RIGHT] <= target_size[self.SIZE_WIDTH] and target_pos[self.POS_BOTTOM] <= target_size[self.SIZE_HEIGHT]:
				out_image.paste(in_image, target_pos)
			else:
				crop_size = (target_size[0] - target_pos[0], target_size[1] - target_pos[1])
				#out_image.paste(in_image.crop((0, 0) + crop_size), target_pos)
				crop_pos = (target_pos[0], target_pos[1], target_pos[0] + crop_size[0], target_pos[1] + crop_size[1])
				out_image.paste(in_image.crop((0, 0) + crop_size), crop_pos)
				print(crop_size)
				print(target_pos, target_size)
				print("Crop")
			
			if current_pos[self.POS_LEFT] + 1 >= target_size[self.SIZE_WIDTH]:
				current_pos = (0, current_pos[self.POS_TOP] + in_size[self.SIZE_HEIGHT])
			else:
				current_pos = (current_pos[self.POS_LEFT] + in_size[self.SIZE_WIDTH], current_pos[self.POS_TOP])

		return out_image

	def __paste_image(self, image, out_image):
		in_image = Image.open(image['src'])
		mode = image['mode']
		pos = image['computed_pos']
		if mode == 'no-repeat':
			out_image.paste(in_image, image['computed_pos'])
		elif mode == 'repeat-x':
			tiled = self.__tile_image(in_image, (pos[self.POS_RIGHT] - pos[self.POS_LEFT], pos[self.POS_BOTTOM] - pos[self.POS_TOP]))
			out_image.paste(tiled, image['computed_pos'])

	def compressImages(self):
		self.__collect_positions()
		for name, image in self.images.iteritems():
			print(termcolor.colored("Composing " + name, "green"))
			out_image = Image.new('RGBA', image['computed_size'])
			for in_image in image['images'].itervalues():
				self.__paste_image(in_image, out_image)
			out_image.save(os.path.abspath(image['output']))
