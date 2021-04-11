# -*- coding: utf-8 -*-
import json
from datetime import timedelta

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import MinValueValidator, MaxValueValidator, MaxLengthValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django_geoposition_field.fields import GeopositionField

from . import accounts_settings
from .utils import get_count_new
from .validators import UsernameValidator
from autoimagefield.fields import AutoImageField
from common_utils import get_default_manager
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField


class User(AbstractUser):
	objects = UserManager()
	username_validator = UsernameValidator()

	jabber = models.CharField(
		verbose_name="jabber",
		max_length=127,
		blank=True
	)
	url = models.CharField(
		verbose_name="webová stránka",
		max_length=255,
		blank=True
	)
	signature = models.CharField(
		verbose_name="podpis",
		max_length=255,
		blank=True
	)
	display_mail = models.BooleanField(
		verbose_name="zobrazovať e-mail",
		default=False
	)
	distribution = models.CharField(
		verbose_name="linuxová distribúcia",
		max_length=50,
		blank=True
	)
	original_info = RichTextOriginalField(
		verbose_name="informácie",
		filtered_field='filtered_info',
		property_name='info',
		parsers={'html': 'profile'},
		validators=[MaxLengthValidator(100000)],
		blank=True
	)
	filtered_info = RichTextFilteredField(
		blank=True
	)
	year = models.SmallIntegerField(
		verbose_name="rok narodenia",
		validators=[MinValueValidator(1900), MaxValueValidator(2015)],
		blank=True,
		null=True
	)
	avatar = AutoImageField(
		verbose_name="fotografia",
		upload_to='accounts/avatars',
		resize_source=dict(size=(512, 512)),
		blank=True
	)
	settings = models.TextField(
		verbose_name="nastavenia",
		blank=True
	)
	geoposition = GeopositionField(
		verbose_name="poloha",
		blank=True
	)

	def clean_fields(self, exclude=None):
		if self.email:
			qs = get_default_manager(self).filter(email=self.email).exclude(pk=self.pk)
			if qs.exists():
				raise ValidationError({'email': ["Používateľ s touto e-mailovou adresou už existuje"]})
		super().clean_fields(exclude)

	def get_absolute_url(self):
		return reverse('accounts:profile', kwargs={'pk': self.pk})

	def get_full_name(self):
		full_name = ('%s %s' % (self.first_name, self.last_name)).strip()
		return full_name or self.username or self.email
	get_full_name.short_description = "celé meno"
	get_full_name.admin_order_field = 'last_name,first_name,username'

	@property
	def user_settings(self):
		try:
			return json.loads(self.settings)
		except ValueError:
			return {}

	@user_settings.setter
	def user_settings(self, val):
		self.settings = json.dumps(val, cls=DjangoJSONEncoder)

	@property
	def count_new(self):
		return {k.replace('.', '_'): v for k, v in get_count_new(self).items()}

	@property
	def last_desktop(self):
		Desktop = apps.get_model('desktops', 'desktop')
		return (Desktop.objects.all()
			.filter(author=self)
			.order_by('-pk')
			.first())

	def __str__(self):
		return self.get_full_name() or self.username

	class Meta:
		db_table = 'auth_user'
		verbose_name = "používateľ"
		verbose_name_plural = "používatelia"


class UserRating(models.Model):
	RATING_WEIGHTS = {
		'comments': 1,
		'articles': 200,
		'helped': 20,
		'news': 10,
		'wiki': 50,
	}

	user = models.OneToOneField(
		User,
		verbose_name="používateľ",
		related_name='rating',
		on_delete=models.CASCADE
	)
	comments = models.IntegerField(
		verbose_name="komentárov",
		default=0
	)
	articles = models.IntegerField(
		verbose_name="článkov",
		default=0
	)
	helped = models.IntegerField(
		verbose_name="pomohol",
		default=0
	)
	news = models.IntegerField(
		verbose_name="správ",
		default=0
	)
	wiki = models.IntegerField(
		verbose_name="wiki stránok",
		default=0
	)
	rating = models.IntegerField(
		verbose_name="hodnotenie",
		default=0
	)

	def get_rating_label(self):
		r = self.rating
		return (r >= 1000 and '5') or (r >= 400 and '4') or (r >= 50 and '3') or (r >= 10 and '2') or '1'

	def __str__(self):
		return self.get_rating_label()

	class Meta:
		verbose_name = "hodnotenie používateľa"
		verbose_name_plural = "hodnotenia používateľov"


class RememberTokenManager(models.Manager):
	def get_by_string(self, token):
		try:
			user_id, token_hash = token.split(':', 1)
		except ValueError:
			return None

		max_age = timezone.now() - timedelta(seconds=accounts_settings.COOKIE_AGE)
		return self.filter(created__gte=max_age, user=user_id, token_hash=token_hash).first()

	def clean_remember_tokens(self):
		max_age = timezone.now() - timedelta(seconds=accounts_settings.COOKIE_AGE)
		return self.all().filter(created__lte=max_age).delete()


class RememberToken(models.Model):
	objects = RememberTokenManager()

	token_hash = models.CharField(
		max_length=255,
		blank=False,
		primary_key=True
	)
	created = models.DateTimeField(
		editable=False,
		blank=True,
		auto_now_add=True
	)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		related_name='remember_me_tokens',
		on_delete=models.CASCADE
	)

	def __str__(self):
		return self.token_hash
