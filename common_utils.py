# -*- coding: utf-8 -*-

import os

def clean_dir(path, root_path):
	path = os.path.abspath(path)
	root_path = os.path.abspath(root_path)

	current_dir = path
	while len(os.path.split(current_dir)) and current_dir.startswith(root_path) and current_dir != root_path:
		try:
			os.rmdir(current_dir)
		except OSError:
			return
		current_dir = os.path.join(*os.path.split(current_dir)[:-1])
