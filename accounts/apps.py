# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.contrib.auth.signals import user_logged_out
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, pre_save, pre_delete, post_delete
from django.utils.functional import cached_property

from .auth_remember_utils import preset_cookie


class AccountsConfig(AppConfig):
	name = 'accounts'
	verbose_name = 'Používateľské kontá'

	@cached_property
	def user_content(self):
		from article.models import Article
		from comments.models import Comment
		from news.models import News
		from wiki.models import Page as WikiPage

		return {
			Comment: ('user', 'comments', lambda c: c.is_public and not c.is_removed),
			News: ('author', 'news', lambda c: c.approved),
			WikiPage: ('last_author', 'wiki', lambda c: True),
			Article: ('author', 'articles', lambda c: c.published),
		}

	def update_user_rating(self, instance, author_property, property_name, change):
		UserRating = self.get_model('UserRating')
		user = getattr(instance, author_property)
		if user:
			rating = UserRating.objects.get_or_create(user=user)[0]
			setattr(rating, property_name, max(getattr(rating, property_name) + change, 0))
			rating.rating = sum(getattr(rating, w[0]) * w[1] for w in UserRating.RATING_WEIGHTS.items())
			rating.save()

	def update_count_post_save(self, sender, instance, **kwargs):
		if not sender in self.user_content:
			return
		author_property, property_name, count_fun = self.user_content[sender]
		self.update_user_rating(instance, author_property, property_name, int(count_fun(instance)))

	def update_count_pre_save(self, sender, instance, **kwargs):
		if not sender in self.user_content:
			return
		author_property, property_name, count_fun = self.user_content[sender]
		if instance.pk:
			try:
				instance = instance.__class__.objects.get(pk=instance.pk)
				self.update_user_rating(instance, author_property, property_name, -int(count_fun(instance)))
			except ObjectDoesNotExist:
				pass

	def remove_auth_token(self, sender, **kwargs): #pylint: disable=unused-argument
		request = kwargs['request']
		user = request.user
		preset_cookie(request, '')
		RememberToken = self.get_model('RememberToken')
		RememberToken.objects.all().filter(user=user).delete()

	def set_inactive(self, request, user, **kwargs): #pylint: disable=unused-argument
		from allauth.account.models import EmailAddress
		new_email_address = EmailAddress.objects.get(user=user, primary=True)
		new_email_address.send_confirmation(request, signup=True)

		user.is_active = False
		user.is_staff = False
		user.save()

	def set_active(self, request, email_address, **kwargs): #pylint: disable=unused-argument
		user = email_address.user
		user.is_active = True
		user.save()

	def set_registration_active(self):
		from allauth.account.signals import user_signed_up, email_confirmed
		user_signed_up.connect(self.set_inactive)
		email_confirmed.connect(self.set_active)

	def clear_last_objects_cache(self):
		from .utils import clear_last_objects_cache

		post_save.connect(clear_last_objects_cache)
		post_delete.connect(clear_last_objects_cache)

	def ready(self):
		pre_save.connect(self.update_count_pre_save)
		pre_delete.connect(self.update_count_pre_save)
		post_save.connect(self.update_count_post_save)
		user_logged_out.connect(self.remove_auth_token)
		self.set_registration_active()
		self.clear_last_objects_cache()
