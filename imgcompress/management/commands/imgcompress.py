# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from shakal.imgcompress.compressor import Compressor

class Command(BaseCommand):
	args = ''
	help = "Compress images"

	def handle(self, *args, **kwargs):
		compressor = Compressor()
		compressor.compressImages()

