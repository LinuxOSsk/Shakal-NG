# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from base64 import b64encode
from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_save, pre_save, pre_delete
from django.utils.translation import ugettext_lazy as _

from article.models import Article
from news.models import News
from rich_editor import get_parser
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField
from threaded_comments.models import Comment
from wiki.models import Page as WikiPage


class User(AbstractUser):
	objects = UserManager()

	jabber = models.CharField(max_length=127, blank=True)
	url = models.CharField(max_length=255, blank=True)
	signature = models.CharField(_('signature'), max_length=255, blank=True)
	display_mail = models.BooleanField(_('display mail'), default=False)
	distribution = models.CharField(_('linux distribution'), max_length=50, blank=True)
	original_info = RichTextOriginalField(filtered_field="filtered_info", property_name="info", parsers={'html': get_parser('profile')}, verbose_name=_('informations'), validators=[MaxLengthValidator(100000)], blank=True)
	filtered_info = RichTextFilteredField(blank=True)
	year = models.SmallIntegerField(_('year of birth'), validators=[MinValueValidator(1900), MaxValueValidator(lambda: 2010)], blank=True, null=True)
	encrypted_password = models.TextField(blank=True, null=True)

	def clean_fields(self, exclude=None):
		if self.email:
			qs = self._default_manager.filter(email=self.email).exclude(pk=self.pk)
			if qs.exists():
				raise ValidationError({'email': [self.unique_error_message(self.__class__, ['email'])]})
		super(User, self).clean_fields(exclude)

	@models.permalink
	def get_absolute_url(self):
		return ('auth_profile', [], {'pk': self.pk})

	def set_password(self, raw_password):
		super(User, self).set_password(raw_password)
		if hasattr(settings, 'ENCRYPT_KEY'):
			from Crypto.Cipher import PKCS1_OAEP
			from Crypto.PublicKey import RSA
			key = RSA.importKey(open(settings.ENCRYPT_KEY).read())
			cipher = PKCS1_OAEP.new(key)
			ciphertext = cipher.encrypt(bytes(raw_password.encode("utf-8")))
			self.encrypted_password = b64encode(ciphertext)

	def get_full_name(self):
		full_name = '%s %s' % (self.first_name, self.last_name)
		return full_name.strip()
	get_full_name.short_description = _('full name')
	get_full_name.admin_order_field = 'last_name,first_name,username'

	def __unicode__(self):
		full_name = self.get_full_name()
		if full_name:
			return full_name
		else:
			return self.username

	class Meta:
		db_table = 'auth_user'
		verbose_name = _('user')
		verbose_name_plural = _('users')


class UserRating(models.Model):
	user = models.OneToOneField(User, related_name='rating')
	comments = models.IntegerField(default=0)
	articles = models.IntegerField(default=0)
	helped = models.IntegerField(default=0)
	news = models.IntegerField(default=0)
	wiki = models.IntegerField(default=0)
	rating = models.IntegerField(default=0)

	def get_rating_label(self):
		r = self.rating
		return (r >= 1000 and '5') or (r >= 400 and '4') or (r >= 50 and '3') or (r >= 10 and '2') or '1'

	def __unicode__(self):
		return self.get_rating_label()


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
		rating = UserRating.objects.get_or_create(user=user)[0]
		setattr(rating, property_name, max(getattr(rating, property_name) + change, 0))
		rating.rating = sum(getattr(rating, w[0]) * w[1] for w in RATING_WEIGHTS.iteritems())
		rating.save()


def update_count_pre_save(sender, instance, **kwargs):
	author_property, property_name, count_fun = SENDERS[sender]
	if instance.pk:
		try:
			instance = instance.__class__.objects.get(pk=instance.pk)
			update_user_rating(instance, author_property, property_name, -int(count_fun(instance)))
		except instance.__class__.DoesNotExist:
			pass


pre_save.connect(update_count_pre_save, sender=Article)
pre_save.connect(update_count_pre_save, sender=Comment)
pre_save.connect(update_count_pre_save, sender=News)
pre_save.connect(update_count_pre_save, sender=WikiPage)
pre_delete.connect(update_count_pre_save, sender=Article)
pre_delete.connect(update_count_pre_save, sender=Comment)
pre_delete.connect(update_count_pre_save, sender=News)
pre_delete.connect(update_count_pre_save, sender=WikiPage)


def update_count_post_save(sender, instance, **kwargs):
	author_property, property_name, count_fun = SENDERS[sender]
	update_user_rating(instance, author_property, property_name, int(count_fun(instance)))

post_save.connect(update_count_post_save, sender=Article)
post_save.connect(update_count_post_save, sender=Comment)
post_save.connect(update_count_post_save, sender=News)
post_save.connect(update_count_post_save, sender=WikiPage)
