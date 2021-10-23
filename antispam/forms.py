# -*- coding: utf-8 -*-
import operator
import random
from collections import Counter
from math import factorial

from django.utils.encoding import force_str

from antispam.fields import AntispamField
from fulltext.utils import unaccent
from web.middlewares.threadlocal import get_current_request


def get_permutations(text):
	total = 1
	for word in text.split():
		count = factorial(len(word))
		repeatations = Counter(word)
		for repeatation in repeatations.values():
			if repeatation > 1:
				count = count // factorial(repeatation)
		total *= count
	return total


def make_permutation(text, prefix=0):
	prefix, text = text[:prefix], text[prefix:]
	words = text.split(' ')
	words = [list(word) for word in words]
	for word in words:
		random.shuffle(word)
	words = [''.join(word) for word in words]
	text = ' '.join(words).lower()
	text = prefix + text
	return text[:1].upper() + text[1:].lower()


def get_permutation_distance(src, dst):
	swaps = 0
	for i in range(len(src)):
		if src[i] == dst[i]:
			continue
		pos = i + dst[i:].index(src[i])
		dst = dst[:i] + dst[pos] + dst[i:pos] + dst[pos+1:]
		swaps += 1
	return swaps


class AntispamFormMixin(object):
	CITIES = [
		'Bánovce nad Bebravou',
		'Banská Bystrica',
		'Banská Štiavnica',
		'Bardejov',
		'Bratislava',
		'Brezno',
		'Bytča',
		'Čadca',
		'Detva',
		'Dolný Kubín',
		'Dunajská Streda',
		'Galanta',
		'Gelnica',
		'Hlohovec',
		'Humenné',
		'Ilava',
		'Kežmarok',
		'Komárno',
		'Košice',
		'Krupina',
		'Kysucké Nové Mesto',
		'Levice',
		'Levoča',
		'Liptovský Mikuláš',
		'Lučenec',
		'Malacky',
		'Martin',
		'Medzilaborce',
		'Michalovce',
		'Myjava',
		'Námestovo',
		'Nitra',
		'Nové Mesto nad Váhom',
		'Nové Zámky',
		'Partizánske',
		'Pezinok',
		'Piešťany',
		'Poltár',
		'Poprad',
		'Považská Bystrica',
		'Prešov',
		'Prievidza',
		'Púchov',
		'Revúca',
		'Rimavská Sobota',
		'Rožňava',
		'Ružomberok',
		'Sabinov',
		'Senec',
		'Senica',
		'Skalica',
		'Snina',
		'Sobrance',
		'Spišská Nová Ves',
		'Stará Ľubovňa',
		'Stropkov',
		'Svidník',
		'Šaľa',
		'Topoľčany',
		'Trebišov',
		'Trenčín',
		'Trnava',
		'Turčianske Teplice',
		'Tvrdošín',
		'Veľký Krtíš',
		'Vranov nad Topľou',
		'Zlaté Moravce',
		'Zvolen',
		'Žarnovica',
		'Žiar nad Hronom',
		'Žilina',
	]

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		request = get_current_request()
		if not request.user.is_authenticated:
			self.fields['captcha'] = AntispamField(required=True)
			self.process_antispam(get_current_request())

	def generate_antispam(self):
		return self.generate_city_antispam()

	def generate_math_antispam(self):
		operators = (
			('+', operator.add, operator.sub, False),
			('-', operator.sub, operator.add, True),
			('/', operator.floordiv, operator.mul, True),
			('*', operator.mul, operator.floordiv, False),
		)

		sign, operation, inverse_operation, answer_first = random.choice(operators)

		answer = random.randrange(1, 10)
		num_2 = random.randrange(1, 10)
		num_1 = inverse_operation(num_2, answer) if answer_first else random.randrange(1, 10)
		answer = operation(num_1, num_2)
		return ("{0} {1} {2} plus tisíc (číslom) ".format(num_1, sign, num_2), force_str(answer + 1000))

	def generate_antispam(self):
		word = random.choice(self.CITIES)
		word_ascii = unaccent(word).lower()
		permutations = get_permutations(word_ascii)
		if permutations > 10000:
			prefix = 2
		else:
			prefix = 1

		for __ in range(10):
			permutation = make_permutation(word, prefix)
			distance = get_permutation_distance(unaccent(word).lower(), unaccent(permutation).lower())
			if distance > max(len(word) // 5, 1):
				break

		return f"Opravte názov „{permutation}“ (vlastné podstatné meno)", word_ascii

	def process_antispam(self, request):
		if request.method == 'GET' or not 'antispam' in request.session:
			request.session['antispam'] = self.generate_antispam()
		self.set_antispam_widget_attributes(request.session['antispam'])

	def set_antispam_widget_attributes(self, antispam):
		if 'captcha' in self.fields:
			self.fields['captcha'].widget.attrs['question'] = antispam[0]
			self.fields['captcha'].widget.attrs['answer'] = antispam[1]
