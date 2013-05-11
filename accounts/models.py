# -*- coding: utf-8 -*-
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_save, pre_save, pre_delete
from django.utils.translation import ugettext_lazy as _

from article.models import Article
from news.models import News
from threaded_comments.models import Comment
from wiki.models import Page as WikiPage
from base64 import b64encode
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from django.conf import settings
from rich_editor import get_parser
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField


class User(AbstractUser):
	jabber = models.CharField(max_length = 127, blank = True)
	url = models.CharField(max_length = 255, blank = True)
	signature = models.CharField(_('signature'), max_length = 255, blank = True)
	display_mail = models.BooleanField(_('display mail'), default = False)
	distribution = models.CharField(_('linux distribution'), max_length = 50, blank = True)
	original_info = RichTextOriginalField(verbose_name = _('informations'), validators = [MaxLengthValidator(100000)], blank = True)
	filtered_info = RichTextFilteredField(original_field = "original_info", property_name = "info", parsers = {'html': get_parser('profile')}, blank = True)
	year = models.SmallIntegerField(_('year of birth'), validators = [MinValueValidator(1900), MaxValueValidator(lambda: 2010)], blank = True, null = True)
	encrypted_password = models.TextField(blank = True, null = True)

	def clean_fields(self, exclude = None):
		qs = self._default_manager.filter(email = self.email).exclude(pk = self.pk)
		if qs.exists():
			raise ValidationError({'email': [self.unique_error_message(self.__class__, ['email'])]})
		super(User, self).clean_fields(exclude)

	@models.permalink
	def get_absolute_url(self):
		return ('auth_profile', [], {'pk': self.pk})

	def set_password(self, raw_password):
		super(User, self).set_password(raw_password)
		if hasattr(settings, 'ENCRYPT_KEY'):
			key = RSA.importKey(open(settings.ENCRYPT_KEY).read())
			cipher = PKCS1_OAEP.new(key)
			ciphertext = cipher.encrypt(bytes(raw_password.encode("utf-8")))
			self.encrypted_password = b64encode(ciphertext)

	class Meta:
		db_table = 'auth_user'


class UserRating(models.Model):
	user = models.OneToOneField(User, related_name = 'rating')
	comments = models.IntegerField(default = 0)
	articles = models.IntegerField(default = 0)
	helped = models.IntegerField(default = 0)
	news = models.IntegerField(default = 0)
	wiki = models.IntegerField(default = 0)
	rating = models.IntegerField(default = 0)

	def get_rating_label(self):
		if self.rating < 10:
			return '1'
		elif self.rating < 50:
			return '2'
		elif self.rating < 400:
			return '3'
		elif self.rating < 1000:
			return '4'
		else:
			return '5'


SENDERS = {
	Comment: ('user', 'comments', lambda c: c.is_public and not c.is_removed),
	News: ('author', 'news', lambda c: c.approved),
	WikiPage: ('last_author', 'wiki', lambda c: True),
	Article: ('author', 'articles', lambda c: c.published),
}


RATING_WEIGHTS = {
	'comments': 1,
	'articles': 200,
	'helped': 20,
	'news': 10,
	'wiki': 50,
}


def update_user_rating(instance, author_property, property_name, change):
	user = getattr(instance, author_property)
	if user:
		rating, created = UserRating.objects.get_or_create(user = user)
		setattr(rating, property_name, max(getattr(rating, property_name) + change, 0))
		rating.rating = sum(getattr(rating, w[0]) * w[1] for w in RATING_WEIGHTS.iteritems())
		rating.save()


def update_count_pre_save(sender, instance, **kwargs):
	author_property, property_name, count_fun = SENDERS[sender]
	if instance.pk:
		try:
			instance = instance.__class__.objects.get(pk = instance.pk)
			update_user_rating(instance, author_property, property_name, -int(count_fun(instance)))
		except instance.__class__.DoesNotExist:
			pass


pre_save.connect(update_count_pre_save, sender = Article)
pre_save.connect(update_count_pre_save, sender = Comment)
pre_save.connect(update_count_pre_save, sender = News)
pre_save.connect(update_count_pre_save, sender = WikiPage)
pre_delete.connect(update_count_pre_save, sender = Article)
pre_delete.connect(update_count_pre_save, sender = Comment)
pre_delete.connect(update_count_pre_save, sender = News)
pre_delete.connect(update_count_pre_save, sender = WikiPage)


def update_count_post_save(sender, instance, created, **kwargs):
	author_property, property_name, count_fun = SENDERS[sender]
	update_user_rating(instance, author_property, property_name, int(count_fun(instance)))

post_save.connect(update_count_post_save, sender = Article)
post_save.connect(update_count_post_save, sender = Comment)
post_save.connect(update_count_post_save, sender = News)
post_save.connect(update_count_post_save, sender = WikiPage)
