# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator, MinValueValidator, MaxValueValidator
from django.utils.translation import ugettext_lazy as _

class UserProfile(models.Model):
	user = models.OneToOneField(User, related_name = 'profile')
	jabber = models.CharField(max_length = 127, blank = True)
	url = models.CharField(max_length = 255, blank = True)
	signature = models.CharField(max_length = 255, blank = True)
	display_mail = models.BooleanField(default = False, verbose_name = _('display mail'))
	distribution = models.CharField(max_length = 50, blank = True, verbose_name = _('linux distribution'))
	info = models.TextField(validators = [MaxLengthValidator(100000)], blank = True, verbose_name = _('informations'))
	year = models.SmallIntegerField(validators = [MinValueValidator(1900), MaxValueValidator(lambda: 2000)], blank = True, null = True, verbose_name = _('year of birth'))
	def save(self, *args, **kwargs):
		try:
			existing = UserProfile.objects.get(user = self.user)
			self.id = existing.id
		except UserProfile.DoesNotExist:
			pass
		super(UserProfile, self).save(*args, **kwargs)


class UserRating(models.Model):
	user = models.OneToOneField(User, related_name = 'rating')
	comments = models.IntegerField(default = 0)
	articles = models.IntegerField(default = 0)
	helped = models.IntegerField(default = 0)
	news = models.IntegerField(default = 0)
	wiki = models.IntegerField(default = 0)

def update_user_rating_on_create(user, property_name):
	rating = UserRating.objects.get_or_create(user = user)
	setattr(rating, property_name, getattr(rating, property_name) + 1)
	rating.save()


def user_rating_updater(property_name, author_property):
	def update(sender, instance, created, **kwargs):
		if created:
			update_user_rating_on_create(getattr(instance, author_property))
	return update


def create_user_profile(sender, **kwargs):
	user = kwargs['instance']
	if not UserProfile.objects.filter(user = user):
		UserProfile(user = user).save()

post_save.connect(create_user_profile, sender = User)
