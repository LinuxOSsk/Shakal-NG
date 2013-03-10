# -*- coding: utf-8 -*-
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_save, pre_save, pre_delete
from django.utils.translation import ugettext_lazy as _

from shakal.article.models import Article
from shakal.news.models import News
from shakal.threaded_comments.models import ThreadedComment
from shakal.wiki.models import Page as WikiPage


class User(AbstractUser):
	jabber = models.CharField(max_length = 127, blank = True)
	url = models.CharField(max_length = 255, blank = True)
	signature = models.CharField(max_length = 255, blank = True, verbose_name = _('signature'))
	display_mail = models.BooleanField(default = False, verbose_name = _('display mail'))
	distribution = models.CharField(max_length = 50, blank = True, verbose_name = _('linux distribution'))
	info = models.TextField(validators = [MaxLengthValidator(100000)], blank = True, verbose_name = _('informations'))
	year = models.SmallIntegerField(validators = [MinValueValidator(1900), MaxValueValidator(lambda: 2010)], blank = True, null = True, verbose_name = _('year of birth'))


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
	ThreadedComment: ('user', 'comments', lambda c: c.is_public and not c.is_removed),
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
pre_save.connect(update_count_pre_save, sender = ThreadedComment)
pre_save.connect(update_count_pre_save, sender = News)
pre_save.connect(update_count_pre_save, sender = WikiPage)
pre_delete.connect(update_count_pre_save, sender = Article)
pre_delete.connect(update_count_pre_save, sender = ThreadedComment)
pre_delete.connect(update_count_pre_save, sender = News)
pre_delete.connect(update_count_pre_save, sender = WikiPage)


def update_count_post_save(sender, instance, created, **kwargs):
	author_property, property_name, count_fun = SENDERS[sender]
	update_user_rating(instance, author_property, property_name, int(count_fun(instance)))

post_save.connect(update_count_post_save, sender = Article)
post_save.connect(update_count_post_save, sender = ThreadedComment)
post_save.connect(update_count_post_save, sender = News)
post_save.connect(update_count_post_save, sender = WikiPage)
