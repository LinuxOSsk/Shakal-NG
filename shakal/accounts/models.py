# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.signals import post_save, pre_save
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


from shakal.threaded_comments.models import ThreadedComment
from shakal.news.models import News
from shakal.wiki.models import Page as WikiPage

SENDERS = {
	ThreadedComment: ('user', 'comments'),
	News: ('author', 'news'),
	WikiPage: ('last_author', 'wiki'),
}


def update_user_rating(instance, author_property, property_name, change):
	user = getattr(instance, author_property)
	rating, created = UserRating.objects.get_or_create(user = user)
	setattr(rating, property_name, max(getattr(rating, property_name) + change, 0))
	rating.save()


def update_count_pre_save(sender, instance, **kwargs):
	author_property, property_name = SENDERS[sender]
	if instance.pk:
		instance = instance.__class__.objects.get(pk = instance.pk)
		update_user_rating(instance, author_property, property_name, -1)

pre_save.connect(update_count_pre_save, sender = ThreadedComment)
pre_save.connect(update_count_pre_save, sender = News)
pre_save.connect(update_count_pre_save, sender = WikiPage)


def update_count_post_save(sender, instance, created, **kwargs):
	author_property, property_name = SENDERS[sender]
	update_user_rating(instance, author_property, property_name, 1)

post_save.connect(update_count_post_save, sender = ThreadedComment)
post_save.connect(update_count_post_save, sender = News)
post_save.connect(update_count_post_save, sender = WikiPage)


def create_user_profile(sender, **kwargs):
	user = kwargs['instance']
	if not UserProfile.objects.filter(user = user):
		UserProfile(user = user).save()

post_save.connect(create_user_profile, sender = User)
